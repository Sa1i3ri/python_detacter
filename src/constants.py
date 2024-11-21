import json
import os

# CWEs IDs and names
CWES = {
    "cwe-20": "improper input validation",
    "cwe-22": "path traversal",
    "cwe-79": "cross-site scripting",
    "cwe-89": "SQL injection",
    "cwe-190": "integer overflow",
    "cwe-209": "information exposure",
    "cwe-327": "use of a broken or risky cryptographic algorithm",
    "cwe-400": "uncontrolled resource consumption",
    "cwe-502": "deserialization of untrusted data",
    "cwe-732": "incorrect permission assignment",
}

# CWEs definitions from MITRE website
def load_cwe_definitions():
    cwe_path = os.path.join(os.path.dirname(__file__), "../datasets/mitre-cwe-definitions.json")
    with open(cwe_path, "r", encoding='utf-8') as f:
        return json.load(f)

# CWEs languages
LANG = {
    "cwe-20": "py",
    "cwe-22": "py",
    "cwe-79": "py",
    "cwe-89": "py",
    "cwe-190": "py",
    "cwe-209": "py",
    "cwe-327": "py",
    "cwe-400": "py",
    "cwe-502": "py",
    "cwe-732": "py",
}

# Map for Prompts types
PROMPTS_MAP = {
    'promptS1': ('ZS', 'TO'),
    'promptS2': ('ZS', 'RO'),
    'promptS3': ('ZS', 'RO'),
    'promptS4': ('ZS', 'RO'),
    'promptS5': ('FS', 'TO'),
    'promptS6': ('FS', 'RO'),
    'promptR1': ('ZS', 'TO'),
    'promptR2': ('ZS', 'RO'),
    'promptR3': ('ZS', 'TO'),
    'promptR4': ('FS', 'RO'),
    'promptR5': ('FS', 'RO'),
    'promptR6': ('FS', 'TO'),
    'promptD1': ('ZS', 'TO'),
    'promptD2': ('ZS', 'RO'),
    'promptD3': ('FS', 'RO'),
    'promptD4': ('FS', 'RO'),
    'promptD5': ('FS', 'TO'),
}