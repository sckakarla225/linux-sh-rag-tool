import pytest
import json
from pathlib import Path
from collections import Counter
from typing import Any

from constants import TARGET_COMMAND_SECTIONS
from splitter import ManPageSplitter, ManPageChunk
from metadata import (
    NAMEMetadataModel,
    SYNOPSISMetadataModel,
    DESCRIPTIONMetadataModel,
    OPTIONSMetadataModel,
    EXPRESSIONSMetadataModel,
    EXAMPLESMetadataModel,
    ENVIRONMENTMetadataModel,
    OUTPUTMetadataModel
)
from utils import count_tokens, starts_with_command_name, fingerprint_text
from constants import MAX_TOKEN_LIMIT

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
            "PATTERNS", "ACTIONS", "OPERATORS",
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
TEST_MAN_PAGE_COMMAND_CATEGORIES = {
    "curl": "NETWORKING",
    "head": "FILE_PROCESSING",
    "rsync": "FILE_PROCESSING",
    "gawk": "FILE_PROCESSING",
    "ping": "NETWORKING"
}
TEST_MAN_PAGE_CASES_PATH = Path(__file__).resolve().parent / "cases" / "test_splitter.json"
with TEST_MAN_PAGE_CASES_PATH.open("r", encoding="utf-8") as file:
    TEST_MAN_PAGE_CASES = json.load(file)

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
    # get the case data for command
    case_data = TEST_MAN_PAGE_CASES[command_name]
    assert case_data is not None
    return splitter, adjacent_sections, command_name, case_data

# tester for chunking NAME sections
def test_chunk_name(setup_splitter):
    splitter, adjacent_sections, command_name, case_data = setup_splitter
    
    # check that the sections are correct
    target_sections = ["NAME"]
    
    sections = splitter.get_sections("NAME")
    assert Counter[str](sections) == Counter[str](target_sections)

    name_chunks = splitter.chunk_name()
    # base checks
    assert len(name_chunks) == 1
    assert isinstance(name_chunks[0], ManPageChunk)
    assert isinstance(name_chunks[0].metadata, NAMEMetadataModel)

    chunk_id = name_chunks[0].chunk_id
    chunk_content = name_chunks[0].chunk_content
    chunk_metadata = name_chunks[0].metadata

    # other basic checks
    assert chunk_id == f"{command_name}_name_summary"
    assert chunk_content != ""
    assert chunk_content == chunk_content.strip()
    assert count_tokens(chunk_content) <= MAX_TOKEN_LIMIT

    # metadata checks
    assert chunk_metadata.command_name == command_name
    assert chunk_metadata.section_category == "NAME"
    assert chunk_metadata.command_category == TEST_MAN_PAGE_COMMAND_CATEGORIES[command_name]
    assert chunk_metadata.utility == "LOW"

# tester for chunking SYNOPSIS sections
def test_chunk_synopsis(setup_splitter):
    splitter, adjacent_sections, command_name, case_data = setup_splitter
    
    # check that the sections are correct
    target_sections = ["SYNOPSIS"]
    
    sections = splitter.get_sections("SYNOPSIS")
    assert Counter[str](sections) == Counter[str](target_sections)

    synopsis_chunks = splitter.chunk_synopsis()
    # base checks
    assert len(synopsis_chunks) >= 1
    for i, chunk in enumerate[Any](synopsis_chunks):
        assert isinstance(chunk, ManPageChunk)
        assert isinstance(chunk.metadata, SYNOPSISMetadataModel)
        
        chunk_id = chunk.chunk_id
        chunk_content = chunk.chunk_content
        chunk_metadata = chunk.metadata

        # other basic checks
        assert chunk_id == f"{command_name}_synopsis_{i + 1}"
        assert chunk_content != ""
        assert chunk_content == chunk_content.strip()
        assert count_tokens(chunk_content) <= MAX_TOKEN_LIMIT

        # metadata checks
        assert chunk_metadata.command_name == command_name
        assert chunk_metadata.section_category == "SYNOPSIS"
        assert chunk_metadata.command_category == TEST_MAN_PAGE_COMMAND_CATEGORIES[command_name]
        assert chunk_metadata.utility == "HIGH"
        assert chunk_metadata.syntax_skeleton == True
        assert chunk_metadata.command_variant_count >= 1
    
    # content checks
    synopsis_case_data = case_data["SYNOPSIS"]
    assert synopsis_case_data is not None
    assert "line_unit_count" in synopsis_case_data
    assert "line_unit_hashes" in synopsis_case_data
    expected_line_count = synopsis_case_data["line_unit_count"]
    expected_line_hashes = synopsis_case_data["line_unit_hashes"]

    all_lines: list[str] = [] # collect all lines from chunks
    for chunk in synopsis_chunks:
        for line in chunk.chunk_content.splitlines():
            stripped_line = line.strip() # reformat line (matches splitter)
            if stripped_line:
                all_lines.append(stripped_line)
    
    line_units: list[str] = [] # reconstruct line units from all lines
    current_line_unit: list[str] = []
    for line in all_lines:
        if starts_with_command_name(line, command_name):
            if current_line_unit:
                line_units.append(" ".join(current_line_unit))
            current_line_unit = [line]
        else:
            if current_line_unit:
                current_line_unit.append(line)
    
    if current_line_unit:
        line_units.append(" ".join(current_line_unit))
    
    assert len(line_units) == expected_line_count
    for unit in line_units:
        assert starts_with_command_name(unit, command_name) # must start with command name
        assert fingerprint_text(unit) in expected_line_hashes # must exist
    # frequencies of line hashes should match case data
    line_hashes = [fingerprint_text(unit) for unit in line_units]
    assert Counter[str](line_hashes) == Counter[str](expected_line_hashes)

# tester for chunking DESCRIPTION sections
def test_chunk_description(setup_splitter):
    splitter, adjacent_sections, command_name, case_data = setup_splitter
    
    # check that the sections are correct
    target_sections = adjacent_sections["DESCRIPTION"] + ["DESCRIPTION"]
    print(target_sections)
    
    sections = splitter.get_sections("DESCRIPTION")
    print(sections)
    assert Counter[str](sections) == Counter[str](target_sections)

    if len(target_sections) > 0:
        for section_name in target_sections:
            description_chunks = splitter.chunk_description(section_name)

# tester for chunking OPTIONS sections
def test_chunk_options(setup_splitter):
    splitter, adjacent_sections, command_name, case_data = setup_splitter
    
    # check that the sections are correct
    target_sections = adjacent_sections["OPTIONS"] + ["OPTIONS"]
    
    sections = splitter.get_sections("OPTIONS")
    assert Counter[str](sections) == Counter[str](target_sections)

    if len(target_sections) > 0:
        for section_name in target_sections:
            options_chunks = splitter.chunk_options(section_name)

# tester for chunking (REGULAR) EXPRESSIONS sections
def test_chunk_expressions(setup_splitter):
    splitter, adjacent_sections, command_name, case_data = setup_splitter
    
    # check that the sections are correct
    if "EXPRESSIONS" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = adjacent_sections["EXPRESSIONS"] + ["EXPRESSIONS"]
    elif "REGULAR EXPRESSIONS" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = adjacent_sections["EXPRESSIONS"] + ["REGULAR EXPRESSIONS"]
    else:
        target_sections = adjacent_sections["EXPRESSIONS"]

    sections = splitter.get_sections("(REGULAR) EXPRESSIONS")
    assert Counter[str](sections) == Counter[str](target_sections)

    if len(target_sections) > 0:
        for section_name in target_sections:
            expressions_chunks = splitter.chunk_expressions(section_name)

# tester for chunking ENVIRONMENT (VARIABLES) sections
def test_chunk_environment(setup_splitter):
    splitter, adjacent_sections, command_name, case_data = setup_splitter
    
    # check that the sections are correct
    if "ENVIRONMENT" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = ["ENVIRONMENT"]
    elif "ENVIRONMENT VARIABLES" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = ["ENVIRONMENT VARIABLES"]
    else:
        target_sections = []
    
    sections = splitter.get_sections("ENVIRONMENT (VARIABLES)")
    assert Counter[str](sections) == Counter[str](target_sections)

    if len(target_sections) > 0:
        assert len(target_sections) == 1
        environment_chunks = splitter.chunk_environment(target_sections[0])

# tester for chunking OUTPUT (FORMAT) sections
def test_chunk_output(setup_splitter):
    splitter, adjacent_sections, command_name, case_data = setup_splitter
    # check that the sections are correct
    if "OUTPUT" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = adjacent_sections["OUTPUT"] + ["OUTPUT"]
    elif "OUTPUT FORMAT" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = adjacent_sections["OUTPUT"] + ["OUTPUT FORMAT"]
    else:
        target_sections = adjacent_sections["OUTPUT"]

    sections = splitter.get_sections("OUTPUT (FORMAT)")
    assert Counter[str](sections) == Counter[str](target_sections)
    
    if len(target_sections) > 0:
        for section_name in target_sections:
            output_chunks = splitter.chunk_output(section_name)

# tester for chunking EXAMPLES sections
def test_chunk_examples(setup_splitter):
    splitter, adjacent_sections, command_name, case_data = setup_splitter
    
    # check that the sections are correct
    if "EXAMPLES" in TARGET_COMMAND_SECTIONS[command_name]:
        target_sections = ["EXAMPLES"]
    else:
        target_sections = []

    sections = splitter.get_sections("EXAMPLES")
    assert Counter[str](sections) == Counter[str](target_sections)

    if len(target_sections) > 0:
        examples_chunks = splitter.chunk_examples()