import pytest
from typing import Any

from constants import CONTENT_INDENT, MAX_TOKEN_LIMIT
from utils import (
    get_mpnet_tokenizer,
    is_section_header,
    get_command_category,
    fingerprint_text,
    normalize_text,
    count_tokens,
    starts_with_command_name,
    fix_section_content_indent,
    split_text_by_tokens,
    starts_with_dash,
    starts_with_indent,
    overlap_text
)

# setup the sample text for testing some of utils
@pytest.fixture
def setup_sample_text():
    token_unit = "word "
    sample_text = token_unit
    
    # setup a sample text that is 10 more tokens than the max token limit
    while count_tokens(sample_text) <= MAX_TOKEN_LIMIT + 10:
        sample_text += token_unit
        if len(sample_text) > 500_000:
            raise ValueError("sample text is too long")

    return sample_text

# unit tests for all functions in utils.py:

def test_get_mpnet_tokenizer():
    tokenizer_1 = get_mpnet_tokenizer()
    tokenizer_2 = get_mpnet_tokenizer()

    assert tokenizer_1 is not None
    assert tokenizer_2 is not None
    assert tokenizer_1 is tokenizer_2

def test_is_section_header():
    section_headers = [
        "NAME", 
        "SYNOPSIS", 
        "DESCRIPTION", 
        "ANCHORING INCLUDE/EXCLUDE PATTERNS",
        "PROGRESS METER",
        "LIST-CLEARING FILTER RULE",
        "FILE NAME MATCHING OPTIONS"
    ]
    not_section_headers = ["", "   ", "       NAME", "Name", "synopsis", "NAME:", "NAME: VALUES"]

    for line in section_headers:
        assert is_section_header(line), f"Expected True for: {line}"
    
    for line in not_section_headers:
        assert not is_section_header(line), f"Expected False for: {line}"

def test_get_command_category():
    file_processing_commands = [
        "find", "grep", "gawk", "tar", "rsync", "chmod", "cat", 
        "sed", "sort", "cut", "tr", "wc", "head", "tail", "uniq"
    ]
    networking_commands = [
        "ip", "ss", "ping", "traceroute", "dig", "tcpdump", "nmap",
        "nslookup", "curl", "ethtool"
    ]
    unknown_commands = ["ls", "mkdir", "rm", "cp", "mv"]
    
    for cmd in file_processing_commands:
        assert get_command_category(cmd) == "FILE_PROCESSING"
    
    for cmd in networking_commands:
        assert get_command_category(cmd) == "NETWORKING"
    
    for cmd in unknown_commands:
        assert get_command_category(cmd) == "UNKNOWN"

def test_fingerprint_text():
    sample_1 = "Hello, world!" # same string should have the same fingerprint
    sample_2 = "Hello,     world!" # test whitespace normalization
    sample_3 = "linus" # test diff text should have diff fingerprints
    sample_4 = "torvalds" # test diff text should have diff fingerprints

    assert fingerprint_text(sample_1) == fingerprint_text(sample_1)
    assert fingerprint_text(sample_1) == fingerprint_text(sample_2)
    assert fingerprint_text(sample_3) != fingerprint_text(sample_4)

def test_normalize_text():
    # test whitespace normalization across different strings
    assert normalize_text("  hello \n\t world  ") == "hello world"
    assert normalize_text("  VERBOSITY     AND    DEBUGGING  OPTIONS  ") == "VERBOSITY AND DEBUGGING OPTIONS"
    assert normalize_text("VERBOSITY\nAND\tDEBUGGING OPTIONS") == "VERBOSITY AND DEBUGGING OPTIONS"
    assert normalize_text("    word    ") == "word"

def test_count_tokens():
    assert count_tokens("") == 0
    assert count_tokens("Hello, world!") > 0
    assert count_tokens("Hello, world!") == count_tokens("Hello, world!")

def test_starts_with_command_name():
    assert starts_with_command_name("curl", "curl")
    assert starts_with_command_name("curl ", "curl")
    assert starts_with_command_name("curl -I https://example.com", "curl")
    assert starts_with_command_name("  curl --help", "curl")

    assert not starts_with_command_name("curlish", "curl")
    assert not starts_with_command_name("curl-abc", "curl")
    assert not starts_with_command_name("curl:", "curl")

    assert not starts_with_command_name("anything", "")
    assert not starts_with_command_name("", "curl")

def test_fix_section_content_indent():
    sample_text = f"{CONTENT_INDENT}linus\n{CONTENT_INDENT}torvalds"
    assert fix_section_content_indent(sample_text) == "linus\ntorvalds"
    sample_text_2 = f"{CONTENT_INDENT} linus\n{CONTENT_INDENT} torvalds" # test only 1-indent removal
    assert fix_section_content_indent(sample_text_2) == "linus\n torvalds" # starting whitespace should get stripped
    sample_text_3 = f"  linus\n     torvalds" # no spaces should get stripped
    assert fix_section_content_indent(sample_text_3) == "linus\n     torvalds" # starting whitespace should get stripped

    assert fix_section_content_indent("") == ""
    assert fix_section_content_indent("no indent") == "no indent"
    
def test_split_text_by_tokens(setup_sample_text):
    assert split_text_by_tokens("") == [] # test empty text
    assert split_text_by_tokens("  \n   ") == [] # test empty lines

    # test text that is less than max tokens (only one chunk)
    short_text = "under the token limit text"
    assert split_text_by_tokens(short_text) == [short_text]

    # test text that is greater than max tokens (multiple chunks)
    chunks = split_text_by_tokens(setup_sample_text)
    assert len(chunks) >= 2 # multiple chunks
    # check that the chunks are not empty, not whitespace, and below token limit
    for chunk in chunks:
        assert chunk.strip() != ""
        assert chunk.strip() == chunk
        assert count_tokens(chunk) <= MAX_TOKEN_LIMIT

def test_starts_with_dash():
    assert starts_with_dash("-a")
    assert starts_with_dash("--a")
    assert starts_with_dash("   -b, --brief") # test whitespace normalization
    assert not starts_with_dash("flag -a for all") # - in the middle of line
    assert not starts_with_dash("abc")

def test_starts_with_indent():
    assert starts_with_indent(f"{CONTENT_INDENT}linus torvalds")
    assert not starts_with_indent("linus torvalds")
    assert not starts_with_indent("      linus torvalds")
    assert not starts_with_indent(f"{CONTENT_INDENT}  linus torvalds")
    assert not starts_with_indent(f"linus torvalds{CONTENT_INDENT}")

def test_overlap_text(setup_sample_text):
    assert overlap_text("") == [] # test empty text
    assert overlap_text("   \n   ") == [] # test empty lines

    # test text that is less than max tokens (only one chunk)
    short_text = "under the token limit text"
    assert overlap_text(short_text) == [short_text]

    # test text that is greater than max tokens (multiple chunks)
    chunks = overlap_text(setup_sample_text)
    assert len(chunks) >= 2 # multiple chunks
    # check that the chunks are not empty, not whitespace, and below token limit
    for chunk in chunks:
        assert chunk.strip() != ""
        assert chunk.strip() == chunk
        assert count_tokens(chunk) <= MAX_TOKEN_LIMIT

    # test overlap functionality
    unique_longer_text = " ".join(f"word{i}" for i in range(100))
    max_tokens = 20
    overlap_tokens = int(max_tokens * 0.15)
    stride = max_tokens - overlap_tokens

    chunks = overlap_text(unique_longer_text, max_tokens, overlap_tokens)
    assert len(chunks) >= 2 # multiple chunks

    tokenizer = get_mpnet_tokenizer()
    all_tokens = tokenizer.encode(unique_longer_text, add_special_tokens=False)

    # check expected token windows for each chunk
    start_tokens = []
    start = 0
    # find starting token indices for each chunk
    while start < len(all_tokens):
        start_tokens.append(start)
        start += stride
    
    assert len(start_tokens) == len(chunks) # starting token indices should match # of chunks

    for i, chunk in enumerate[Any](chunks):
        start_token = start_tokens[i]
        end_token = min(start_token + max_tokens, len(all_tokens))
        expected_token_window = all_tokens[start_token:end_token]
        expected_token_window_decoded = tokenizer.decode(expected_token_window, skip_special_tokens=True).strip()

        assert expected_token_window_decoded == chunk
