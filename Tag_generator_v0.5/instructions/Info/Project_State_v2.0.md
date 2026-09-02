PLC TAG RENAMING PROJECT

Project State v2.0

Last Updated: August 2026



\# 1. Project Objective



Develop a deterministic PLC tag recognition and renaming system for yacht automation projects.



The purpose of the system is to convert raw PLC variable names into standardized, canonical tags that can be reused consistently across projects.



Example:



In34\_Wand\_lead\_Anch\_windlass\_in

↓

Hyd\_anchorWindlass\_in\_DI



The system is intended to:

\- reduce manual engineering effort

\- improve naming consistency

\- accelerate PLC migrations and refactoring projects

\- create a reusable domain knowledge base



\# 2. Core Design Philosophy



Knowledge-Driven Architecture



Python = Execution Engine

YAML = Knowledge Base



Python should execute rules.

Python should not contain yacht-specific knowledge that can be represented in YAML.



\# 3. High-Level Architecture



Master\_Dictionary.yaml

&#x20;           ↓

Recognition Engine

&#x20;           ↓

Semantic Structure

&#x20;           ↓

Naming Engine

&#x20;           ↓

Canonical Tag



\# 4. Current System Components



\## 4.1 Master Dictionary



The Master Dictionary is the central knowledge repository.



It contains:

\- Systems

\- Components

\- Actions

\- Modifiers

\- Locations

\- Roles

\- Signal Types

\- Aliases

\- Patterns



The dictionary is considered the source of truth.



\### Alias Strategy



Aliases are the only normalization mechanism.



Examples:

\- stbd → sb

\- boomvang → vang

\- bkstay → backstay

\- furle → furl



Current philosophy:



Canonical Concept

&#x20;        ↓

All alternative spellings stored as aliases



This includes:

\- abbreviations

\- project-specific naming

\- legacy naming

\- spelling mistakes



\# 5. Recognition Engine



\## Responsibility



The Recognition Engine does NOT generate tags.



It only:

\- tokenizes

\- removes technical PLC information

\- normalizes tokens

\- classifies tokens

\- generates a semantic structure



\## Current Flow



Raw PLC Tag

&#x20;     ↓

Tokenization

&#x20;     ↓

Technical Token Removal

&#x20;     ↓

Alias Resolution

&#x20;     ↓

Classification

&#x20;     ↓

Semantic Structure



\## Signal Type Detection



Implemented.



Current logic:

\- PLC Input → DI

\- PLC Output → DO



Signal type is generated during Recognition and passed to Naming.



***Future versions may infer signal type using additional project metadata.***



\## Recognition Debug Output



Token\_Recognition\_output.csv



Purpose:

\- classification validation

\- alias validation

\- unknown token review

\- dictionary improvement



\# 6. Naming Engine



\## Responsibility



The Naming Engine receives a semantic structure.



It is responsible for:

\- system inference

\- entity composition

\- alias resolution of composed entities

\- canonical tag generation



\## Current Flow



Semantic Structure

&#x20;       ↓

Category Composition

&#x20;       ↓

Alias Resolution

&#x20;       ↓

System Inference

&#x20;       ↓

Canonical Tag



\## Category Composition



Multiple elements are merged using camelCase.



Example:

components:

\- anchor

\- windlass



↓



anchorWindlass



\## Alias Resolution After Composition



Implemented.



The Naming Engine now:



Compose Category

&#x20;      ↓

Check Alias Dictionary

&#x20;      ↓

Use Canonical Name



This allows future support for composite aliases.



\## System Inference



Current hierarchy:



1\. Explicit System → 100% confidence

2\. Component Default System → 100% confidence

3\. Possible Systems Voting → calculated confidence



\## Naming Debug Output



Generated through tag\_generator.py



Current output includes:

\- original\_name

\- canonical\_tag

\- system

\- system\_confidence

\- component

\- action

\- modifier

\- side

\- location

\- role

\- signal\_type

\- unknown\_tokens

\- inference\_reason



\# 7. Current Category Model



Current categories:

\- systems

\- components

\- actions

\- modifiers

\- locations

\- roles

\- signal\_type



\## Current Discussion



The following concepts are currently stored as modifiers:

\- pressure

\- temperature

\- level

\- flow



These may later migrate to components if this produces more meaningful semantic entities such as:

\- oilLevel

\- oilTemperature

\- pressureFilter



***No final decision has been made.***



\# 8. Known Limitations



The goal is NOT:

100% automatic correctness.



The goal is:

High automation + Efficient human review.



Certain tags remain inherently ambiguous without project context.



\# 9. Next Development Topics



\## Review Workflow



***Possible future addition:***

***- review\_required***



Based on:

\- unknown tokens

\- low system confidence

\- missing semantic information



\## Extended Canonical Tag



***Possible future outputs:***

***- canonical\_tag***

***- canonical\_tag\_extended***



Where unknown tokens are preserved for engineering review.



\## AI-Assisted Validation



Potential workflow:



Tag Generator Output

&#x20;         ↓

AI Review

&#x20;         ↓

Engineer Validation



The intended role of AI is quality assurance, not deterministic tag generation.



\# 10. Current Project Status



Recognition Engine

✅ Stable

✅ Semantic structure generation

✅ Alias normalization

✅ Signal-type generation

✅ CSV debug output



Naming Engine

✅ System inference

✅ CamelCase composition

✅ Composite alias resolution

✅ Canonical tag generation

✅ Confidence reporting

✅ CSV debug output



Architecture

✅ Knowledge-driven

✅ YAML-centric

✅ Deterministic

✅ Recognition/Naming separation



\# Guiding Rule



Before implementing any new feature:



Is this domain knowledge?



If YES:

Put it in YAML.



If NO:

Implement it in Python.



