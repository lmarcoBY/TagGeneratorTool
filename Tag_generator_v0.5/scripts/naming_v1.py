#!/usr/bin/env python3

import yaml
import re
from collections import Counter

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class NamingEngine:

    def __init__(self, dictionary):

        self.dictionary = dictionary

        self.naming_order = [
            "systems",
            "object_specifiers",
            "object_standalones",
            "object_types",
            "modifiers",
            "locations",
            "attributes",
            "states",
            "actions",
            "ambiguous",
            "device_classes",
            "signal_roles",
            "signal_types",
        ]

    def camelCompose(self, list):
        """Compose a list of values into a camelCase-style string."""
        values = [v for v in list if v]

        if not values:
            return ''

        composed = values[0]

        for value in values[1:]:
            composed += value[:1].upper() + value[1:]

        return composed

    #def apply_naming_rules(self, recognized_variable):

    def infer_system(self, recognized_variable):
        """ ADD LOGIC TO INFER SYSTEM FROM OTHER CATEGORIES IF SYSTEM IS NOT RECOGNIZED """
        systems = recognized_variable.get("systems", [])

        # No system recognized, try to infer later from other categories
        if len(systems) == 0:
            return ''   # ADD HERE FUNCTION FOR SEMANTIC INFERENCE

        # If only one system is recognized, return it
        if len(systems) == 1:
            return systems[0]

        # If multiple systems are recognized, return the most common one
        if len(systems) > 1:
            most_common = Counter(systems).most_common(1)[0][0]
            return most_common

        return ''

    def get_tag_code(self, category, token):

        # Token is in dictionary
        if token in self.dictionary["category_values"][category]:
            tag_code = self.dictionary["category_values"][category][token]["tag_code"]

        # Token is not in dictionary - search token without id 
        else:
            prefix_match = re.match(r'^(\d+)', token)
            suffix_match = re.search(r'(\d+)$', token)
            prefix_id = prefix_match.group(1) if prefix_match else ''
            suffix_id = suffix_match.group(1) if suffix_match else ''

            token_without_id = re.sub(r'^\d+|\d+$', '', token)
            tag_code = self.dictionary["category_values"][category][token_without_id]["tag_code"]
            # Reattach IDs
            tag_code = prefix_id + tag_code + suffix_id

        return tag_code

    def build(self, recognized_variable):

        # Re-categorize by the means of Rules - - - - not implemented yet
        #recognized_variable = self.apply_naming_rules(recognized_variable)

        # Get system 
        recognized_variable['systems'] = self.infer_system(recognized_variable)

        parts = []
        component = []
        pending_component = False

        # Build de tag code based on the naming order defined in the dictionary
        for category in self.naming_order:

            # Get the values for the current category from the recognized variable
            values = recognized_variable.get(category, [])

            # If the category has no values, skip it
            if not values:
                continue

            # If the values are a string, convert them to a list
            if isinstance(values, str):
                values = [values]
            
            # 1. Convert token to tag_code
            tag_codes = [
                self.get_tag_code(category, token)
                for token in values
            ]

            # 2. Merge tokens into same category
            composed = self.camelCompose(tag_codes)
            
            # 3. Volver a buscar si el compuesto existe
            try:
                composed = self.get_tag_code(
                    category,
                    composed
                )
            except KeyError:
                pass

            # 4. Add the composed tag code to the parts list if it's not empty
            # camelCompose component = object_specifier + object_type + object_standalone
            # --------------------------- Revisar esta ultima parte -------------------------------------------------
            if composed == '':
                continue

            component_categories = ['object_specifiers', 'object_standalones', 'object_types']

            if category in component_categories:
                component.append(composed)
                pending_component = True
            else:
                # Categoría diferente: terminar composición
                if pending_component:
                    component_str = self.camelCompose(component)
                    parts.append(component_str)
                    component = []
                    pending_component = False
                
                parts.append(composed)

        # Después del loop, componer si queda pendiente
        if pending_component:
            component_str = self.camelCompose(component)
            parts.append(component_str)

        # Join all parts to form the final generated tag
        generated_variable = recognized_variable
        generated_variable['Generated Tag'] = '_'.join(parts)
        return generated_variable