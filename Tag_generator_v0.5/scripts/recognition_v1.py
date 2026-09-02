
import csv
import json
import re
import sys
import yaml
from pathlib import Path
from collections import Counter
from pprint import pprint

def load_yaml(path):
    """Load YAML configuration data from disk."""
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def build_dictionary(dictionary):
    """Build a dictionary structure from the YAML input"""
    # Create list 'aliases' of pairs alias-canonical
    aliases = {}
    for canonical, values in (dictionary.get('aliases', {}) or {}).items():
        aliases[canonical.lower()] = canonical
        for value in values:
            aliases[str(value).lower()] = canonical

   # Get categories from the dictionary, filtering out any non-dictionary entries or those without a "values" field
    categories = [
        key for key, category_fields in dictionary.items()
        # Check that the category is a dictionary and contains a "values" field
        if isinstance(category_fields, dict) and "values" in category_fields
    ]

    # Creates dictionary relating each token with its category and converts to lowercase
    category_values = {}
    for category in categories:
        values = dictionary.get(category, {}).get("values", [])

        category_values[category] = {
            key.lower(): value for key, value in values.items()
        } 

    return {
        'aliases': aliases,
        'categories': categories,
        'category_values': category_values,
    }

class RecognitionEngine:
    """Encapsulates variable recognition and tokenization logic."""

    def __init__(self, dictionary, recognition):
        """Store the dictionary and recognition configuration used for processing."""
        self.dictionary = dictionary
        self.recognition = recognition

    def _build_result(self):
        """Build result structure from the dictionary in desired order"""
        result = {
            'original_name' : [],
            'normalized_tokens' : [],
            'Generated Tag' : ''
        }

        # Create automaticly categories from Dictionary File (yaml)
        result.update({
            category : []
            for category in self.dictionary['categories']
        })

        result['numeric_values'] = []
        result['unknown_tokens'] = []
        result['technical_tokens'] = []
        
        return result

    def _tokenize_var(self, variable):
        """For every variable, replace spaces with underscores, split underscores into tokens, and remove any technical I/O tokens."""
        variable = (
            variable
            .replace(' ', '_')
            .replace(';', '_')
            .replace(':', '_')
            .replace('/', '_')
            .replace(',', '')
            .replace('(', '')
            .replace(')', '')
            .replace('{', '')
            .replace('}', '')
            .replace('[', '')
            .replace(']', '')
            .replace('%', 'percent')
        )

        raw_tokens = [t for t in variable.split('_') if t]

        return raw_tokens

    def _normalize_token(self, token):
        """Checks if token (without instance number) is an alias and returns the canonical form. """
        """If token is not an alias, returns token"""
        t = token.lower()

        # Check if token has a number suffix (id)
        hasNumber = re.match(r"([a-z]+)(\d*)$", t)

        if hasNumber:
            t = hasNumber.group(1)
            id = hasNumber.group(2)
        else:
            id = ""

        if t in self.dictionary['aliases']:
            t = self.dictionary['aliases'][t]

        return t.lower() + id

    def _merge_instance_numbers(self, tokens):
        """Merge instance numbers with their corresponding tokens."""
        merged_tokens = []
        for token in tokens:
            if token.isdigit():
                if merged_tokens[-1] in self.dictionary["category_values"]["object_types"] or merged_tokens[-1] in self.dictionary["category_values"]["object_standalones"]:

                    merged_tokens[-1] += token
            else:
                merged_tokens.append(token)
                 
        return merged_tokens

    def merge_compound_tokens(self, normalized_tokens):
        """Merge adjacent tokens if their concatenation exists in any category of the dictionary. """

        merged_tokens = []
        i = 0

        while i < len(normalized_tokens):

            if i < len(normalized_tokens) - 1:
                compound_key = (
                    normalized_tokens[i] +
                    normalized_tokens[i + 1]
                ).lower()

                found = False

                for values in self.dictionary["category_values"].values():
                    if compound_key in values:
                        merged_tokens.append(compound_key)
                        found = True
                        break

                if found:
                    i += 2
                    continue

            merged_tokens.append(normalized_tokens[i])
            i += 1

        return merged_tokens

    def _classify_token(self, token):
        """Classify a token by finding its category in the dictionary."""
        dictionary_categories = self.dictionary["category_values"]

        token_without_id = re.sub(r'^\d+|\d+$', '', token)

        for category in dictionary_categories:
            values = dictionary_categories[category]

            if (token_without_id in values) or (token in values):
                return category

    def _remove_technical_tokens(self, tokens):
        """Remove technical I/O tokens from the token list and keep track of their direction/number."""
        input_pattern = '^In[0-9]+$'
        output_pattern = '^Out[0-9]+$'

        not_technical = []
        technical = []
        io_direction = ''
        io_number = ''

        for token in tokens:
            matched = False

            if re.match(input_pattern, token, re.IGNORECASE):
                technical.append(token)
                io_direction = 'input'
                io_number = ''.join(c for c in token if c.isdigit())
                matched = True

            if matched:
                continue

            if re.match(output_pattern, token, re.IGNORECASE):
                technical.append(token)
                io_direction = 'output'
                io_number = ''.join(c for c in token if c.isdigit())
                matched = True

            if not matched:
                not_technical.append(token)

        return not_technical, technical, io_direction, io_number

    def _get_prefix_patterns(self):
        """Get the input/output token patterns used to identify technical PLC prefixes."""
        tp = self.recognition.get('technical_prefixes', {}) or {}
        return (
            tp.get('input_patterns', ['^In[0-9]+$']),
            tp.get('output_patterns', ['^Out[0-9]+$'])
        )

    def _get_signal_type(self, io_direction, variable_struct):
        """Infer the PLC signal type from available information."""
        # Explicit direction recognized from technical token
        if io_direction == 'input':
            return 'di'

        if io_direction == 'output':
            return 'do'

        # Implicit direction inferred from signal scores in the dictionary
        scores = {
            "di": 0,
            "do": 0,
            "ai": 0,
            "ao": 0
        }

        for category, values in variable_struct.items():

            if category not in self.dictionary["category_values"]:
                continue
            if isinstance(values, str):
                values = [values]

            for value in values:
                info = self.dictionary["category_values"][category].get(value)

                if not info:
                    continue

                for signal_type, score in info.get("signal_scores", {}).items():
                    scores[signal_type] += score

        return max(scores, key=scores.get)

    def process_variable(self, variable):
        """Process one variable name and return its recognized semantic structure."""
        # Get raw tokens from the variable name and normalize them using the dictionary
        raw_tokens = self._tokenize_var(variable)
        normalized_tokens = [self._normalize_token(t) for t in raw_tokens]

        normalized_tokens, technical_tokens, io_direction, io_number = self._remove_technical_tokens(
            normalized_tokens
        )

        normalized_tokens = self.merge_compound_tokens(normalized_tokens)

        normalized_tokens = self._merge_instance_numbers(normalized_tokens)
               
      
        # Create the result structure.
        result = self._build_result()
        result['original_name'].append(variable)
        result['normalized_tokens'] = normalized_tokens
        result['technical_tokens'] = technical_tokens
        
        
        possible_systems = []
        
        # Classify each token and add it to the appropriate category in the result structure.
        for index, token in enumerate(normalized_tokens):
            category = self._classify_token(token)
            
            if category in self.dictionary["categories"]:
                result[category].append(token)
            else:
                result['unknown_tokens'].append(token)

            # Get possible systems for object_types, object_standalones, and object_specifiers 
            if category == 'object_types' or category == 'object_standalones' or category == 'object_specifiers': 
                # Remove numbers from token
                clean_token = re.sub(r'\d+$', '', token)

                if token in self.dictionary["category_values"][category]:
                    object_data = self.dictionary["category_values"][category][token]

                # Check if token without number is in the dictionary
                elif clean_token in self.dictionary["category_values"][category]:
                    object_data = self.dictionary["category_values"][category][clean_token]

                possible_systems.extend(object_data["possible_system"])
                possible_systems = [system.lower() for system in possible_systems]

        if not result['systems']:
            result['systems'].extend(possible_systems)  

        result['signal_types'] = self._get_signal_type(io_direction, result)

        return result

def process_variable(variable, dictionary, recognition):
    """Process one variable name and return its recognized semantic structure."""
    engine = RecognitionEngine(dictionary, recognition)
    return engine.process_variable(variable)
    
def result_to_csv_row(variable_struct):
    """Convert the semantic result into a flat row suitable for CSV output."""

    row = {}

    for category, values in variable_struct.items():
        if isinstance(values, list):
            row[category] = ';'.join(values)
        else:
            row[category] = values

    return row

def export_csv(variable_struct_list, output_file):
    """Export recognition results to CSV and print recognition statistics."""

    csv_rows = []

    for variable in variable_struct_list:

        csv_rows.append(result_to_csv_row(variable))

    with open(
        output_file,
        'w',
        newline='',
        encoding='utf-8'
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=list(csv_rows[0].keys())
        )

        writer.writeheader()
        writer.writerows(csv_rows)

def get_recognition_statistics(recognized_variables):

    print('\n--- Dictionary Coverage ---')

    variables_processed = len(recognized_variables)

    unique_tokens = set()
    unknown_tokens = set()

    for recognized_variable in recognized_variables:

        for token in recognized_variable['normalized_tokens']:
            unique_tokens.add(token)

        for token in recognized_variable['unknown_tokens']:
            unknown_tokens.add(token)

    recognized_tokens = unique_tokens - unknown_tokens

    coverage = 100

    if unique_tokens:
        coverage = (
            len(recognized_tokens)
            / len(unique_tokens)
        ) * 100

    print(f'Variables processed: {variables_processed}')
    print(f'Unique tokens found: {len(unique_tokens)}')
    print(f'Unique tokens recognized: {len(recognized_tokens)}')
    print(f'Unique tokens unknown: {len(unknown_tokens)}')
    print(f'Dictionary coverage: {coverage:.1f}%')

    if unknown_tokens:

        print('\nUnknown tokens:')

        for token in sorted(unknown_tokens):
            print(f'  - {token}')


if __name__ == '__main__':

    # Main entry point: load the configuration files, process each variable name,
    # write the recognized output to CSV, and print a short summary of unknown tokens.
    if len(sys.argv) != 2:
        print(
            '******************************************************\n'
            'Usage: py scripts\\recognitionTool_v1.py <inputFile.txt>'
        )
        sys.exit(1)

    project_dir = Path(__file__).resolve().parent.parent
    INPUT_FILE = project_dir / 'inputs' / sys.argv[1]
    OUTPUT_FILE = project_dir / 'results' / 'generated' / 'Token_Recognition_output.csv'
    DICTIONARY_FILE = project_dir / 'yaml' / 'Master_Dictionary_v2.1.yaml'
    RECOGNITION_FILE = project_dir / 'yaml' / 'Recognition_Engine_v0.3.yaml'

    dictionary = build_dictionary(load_yaml(str(DICTIONARY_FILE)))
    recognition = load_yaml(str(RECOGNITION_FILE))


    recognized_variables = []

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    
            for line in f:
                v = line.strip()
    
                if v:
    
                    recognized_variable = process_variable(
                        v,
                        dictionary,
                        recognition
                    )

                    recognized_variables.append(recognized_variable)

    export_csv(recognized_variables, str(OUTPUT_FILE))

    get_recognition_statistics(recognized_variables)
    #print(yaml.dump(result, sort_keys=False))