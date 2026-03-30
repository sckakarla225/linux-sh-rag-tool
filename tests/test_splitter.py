import pytest
from pathlib import Path
from collections import Counter

from constants import TARGET_COMMAND_SECTIONS
from splitter import ManPageSplitter, ManPageChunk

# sample set of man pages to test (run each manually -- TEST_MAN_PAGE_COMMANDS[0-4])
TEST_MAN_PAGE_COMMANDS = ['curl', 'head', 'rsync', 'gawk', 'ping']
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

# setup the splitter: run once for each man page in TEST_MAN_PAGE_COMMANDS (edit index below)
@pytest.fixture
def setup_splitter(man_page_path):
    command_name = TEST_MAN_PAGE_COMMANDS[0]
    source_file = man_page_path / f"{command_name}.txt"
    # check that the source file exists
    assert source_file.is_file(), source_file
    # setup the splitter
    splitter = ManPageSplitter(str(source_file), command_name)
    adjacent_sections = TEST_MAN_PAGE_ADJACENT_SECTIONS[command_name]
    return splitter, adjacent_sections, command_name

# tester for chunking NAME sections
def test_chunk_name(setup_splitter):
    splitter, adjacent_sections, command_name = setup_splitter
    
    # check that the sections are correct
    target_sections = ["NAME"]
    
    sections = splitter.get_sections("NAME")
    assert Counter[str](sections) == Counter[str](target_sections)

# tester for chunking SYNOPSIS sections
def test_chunk_synopsis(setup_splitter):
    splitter, adjacent_sections, command_name = setup_splitter
    
    # check that the sections are correct
    target_sections = ["SYNOPSIS"]
    
    sections = splitter.get_sections("SYNOPSIS")
    assert Counter[str](sections) == Counter[str](target_sections)

# tester for chunking DESCRIPTION sections
def test_chunk_description(setup_splitter):
    splitter, adjacent_sections, command_name = setup_splitter
    
    # check that the sections are correct
    target_sections = adjacent_sections["DESCRIPTION"] + ["DESCRIPTION"]
    print(target_sections)
    
    sections = splitter.get_sections("DESCRIPTION")
    print(sections)
    assert Counter[str](sections) == Counter[str](target_sections)

# tester for chunking OPTIONS sections
def test_chunk_options(setup_splitter):
    splitter, adjacent_sections, command_name = setup_splitter
    
    # check that the sections are correct
    target_sections = adjacent_sections["OPTIONS"] + ["OPTIONS"]
    
    sections = splitter.get_sections("OPTIONS")
    assert Counter[str](sections) == Counter[str](target_sections)

# tester for chunking (REGULAR) EXPRESSIONS sections
def test_chunk_expressions(setup_splitter):
    splitter, adjacent_sections, command_name = setup_splitter
    
    # check that the sections are correct
    if "EXPRESSIONS" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = adjacent_sections["EXPRESSIONS"] + ["EXPRESSIONS"]
    elif "REGULAR EXPRESSIONS" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = adjacent_sections["EXPRESSIONS"] + ["REGULAR EXPRESSIONS"]
    else:
        target_sections = adjacent_sections["EXPRESSIONS"]
    
    sections = splitter.get_sections("(REGULAR) EXPRESSIONS")
    assert Counter[str](sections) == Counter[str](target_sections)

# tester for chunking ENVIRONMENT (VARIABLES) sections
def test_chunk_environment(setup_splitter):
    splitter, adjacent_sections, command_name = setup_splitter
    
    # check that the sections are correct
    if "ENVIRONMENT" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = ["ENVIRONMENT"]
    elif "ENVIRONMENT VARIABLES" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = ["ENVIRONMENT VARIABLES"]
    else:
        target_sections = []
    
    sections = splitter.get_sections("ENVIRONMENT (VARIABLES)")
    assert Counter[str](sections) == Counter[str](target_sections)

# tester for chunking OUTPUT (FORMAT) sections
def test_chunk_output(setup_splitter):
    splitter, adjacent_sections, command_name = setup_splitter
    # check that the sections are correct
    if "OUTPUT" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = adjacent_sections["OUTPUT"] + ["OUTPUT"]
    elif "OUTPUT FORMAT" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = adjacent_sections["OUTPUT"] + ["OUTPUT FORMAT"]
    else:
        target_sections = adjacent_sections["OUTPUT"]

    sections = splitter.get_sections("OUTPUT (FORMAT)")
    assert Counter[str](sections) == Counter[str](target_sections)

# tester for chunking EXAMPLES sections
def test_chunk_examples(setup_splitter):
    splitter, adjacent_sections, command_name = setup_splitter
    
    # check that the sections are correct
    if "EXAMPLES" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = ["EXAMPLES"]
    else:
        target_sections = []

    sections = splitter.get_sections("EXAMPLES")
    assert Counter[str](sections) == Counter[str](target_sections)