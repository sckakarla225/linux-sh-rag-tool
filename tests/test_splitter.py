import pytest

from src.constants import ADJACENT_SECTIONS, TARGET_COMMAND_SECTIONS
from src.splitter import ManPageSplitter, ManPageChunk

# sample set of man pages to test (run each manually -- TEST_MAN_PAGE_PATHS[0-4])
TEST_MAN_PAGES = [
    ('curl', 'data/curl.txt'),
    ('head', 'data/head.txt'),
    ('rsync', 'data/rsync.txt'),
    ('gawk', 'data/gawk.txt'),
    ('ping', 'data/ping.txt')
]
TEST_MAN_PAGE_ADJACENT_SECTIONS = {
    "curl": {
        "DESCRIPTION": ["PROTOCOLS", "VERSION"],
        "OPTIONS": [],
        "EXPRESSIONS": ["URL", "GLOBBING", "VARIABLES", "PROXY PROTOCOL PREFIXES"],
        "OUTPUT": ["PROGRESS METER"]
    },
    "head": {
        "DESCRIPTION": [],
        "OPTIONS": [],
        "EXPRESSIONS": [],
        "OUTPUT": []
    },
    "rsync": {
        "DESCRIPTION": [
            "GENERAL", "SETUP", "USAGE", "SORTED TRANSFER ORDER", 
            "MULTI-HOST SECURITY", "CONNECTING TO AN RSYNC DAEMON",
            "USING RSYNC-DAEMON FEATURES VIA A REMOTE-SHELL CONNECTION",
            "STARTING AN RSYNC DAEMON TO ACCEPT CONNECTIONS", 
            "BATCH MODE", "SYMBOLIC LINKS"
        ],
        "OPTIONS": ["DAEMON OPTIONS"],
        "EXPRESSIONS": [
            "COPYING TO A DIFFERENT NAME", "ADVANCED USAGE", 
            "FILTER RULES", "TRANSFER RULES", "SIMPLE INCLUDE/EXCLUDE RULES",
            "FILTER RULES WHEN DELETING", "FILTER RULES IN DEPTH",
            "PATTERN MATCHING RULES", "FILTER RULE MODIFIERS",
            "MERGE-FILE FILTER RULES", "LIST-CLEARING FILTER RULE",
            "ANCHORING INCLUDE/EXCLUDE PATTERNS",
            "PER-DIRECTORY RULES AND DELETE"
        ],
        "OUTPUT": []
    },
    "gawk": {
        "DESCRIPTION": [
            "SIGNALS", "POSIX COMPATIBILITY", "GNU EXTENSIONS",
            "AWK PROGRAM EXECUTION", 
        ],
        "OPTIONS": [],
        "EXPRESSIONS": [
            "VARIABLES, RECORDS AND FIELDS OVERVIEW", "RECORDS", "FIELDS",
            "BUILT-IN VARIABLES", "ARRAYS", "NAMESPACES", 
            "VARIABLE TYPING AND CONVERSION", "OCTAL AND HEXADECIMAL CONSTANTS",
            "STRING CONSTANTS", "REGEXP CONSTANTS", "PATTERNS AND ACTIONS OVERVIEW",
            "PATTERNS", "REGULAR EXPRESSIONS", "ACTIONS", "OPERATORS",
            "CONTROL STATEMENTS", "I/O STATEMENTS", "THE PRINTF STATEMENT",
            "SPECIAL FILE NAMES", "NUMERIC FUNCTIONS", "STRING FUNCTIONS",
            "TIME FUNCTIONS", "INTERNATIONALIZATION"
        ],
        "OUTPUT": []
    },
    "ping": {
        "DESCRIPTION": [
            "IPV6 LINK-LOCAL DESTINATIONS", "ICMP PACKET DETAILS",
            "DUPLICATE AND DAMAGED PACKETS", "ID COLLISIONS",
            "TRYING DIFFERENT DATA PATTERNS", "TTL DETAILS"
        ],
        "OPTIONS": [],
        "EXPRESSIONS": [],
        "OUTPUT": []
    },
}

# run once for each man page in TEST_MAN_PAGES (edit index below)
command_name, man_page_path = TEST_MAN_PAGES[0]
splitter = ManPageSplitter(man_page_path, command_name)
adjacent_sections = TEST_MAN_PAGE_ADJACENT_SECTIONS[command_name]

# tester for chunking NAME sections
def test_chunk_name():
    return

# tester for chunking SYNOPSIS sections
def test_chunk_synopsis():
    return

# tester for chunking DESCRIPTION sections
def test_chunk_description():
    target_sections = adjacent_sections["DESCRIPTION"].append("DESCRIPTION")
    return

# tester for chunking OPTIONS sections
def test_chunk_options():
    target_sections = adjacent_sections["OPTIONS"].append("OPTIONS")

# tester for chunking (REGULAR) EXPRESSIONS sections
def test_chunk_expressions():
    if "EXPRESSIONS" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = adjacent_sections["EXPRESSIONS"].append("EXPRESSIONS")
    elif "REGULAR EXPRESSIONS" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = adjacent_sections["EXPRESSIONS"].append("REGULAR EXPRESSIONS")
    else:
        target_sections = adjacent_sections["EXPRESSIONS"]

# tester for chunking ENVIRONMENT (VARIABLES) sections
def test_chunk_environment():
    return

# tester for chunking OUTPUT (FORMAT) sections
def test_chunk_output():
    return