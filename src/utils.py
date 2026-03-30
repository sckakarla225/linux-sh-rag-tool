import re
from transformers import AutoTokenizer

from constants import (
    COMMAND_CATEGORIES,
    CONTENT_INDENT,
    MAX_TOKEN_LIMIT,
    MPNET_TOKENIZER_ID,
    MPNET_TOKENIZER
)

def get_mpnet_tokenizer() -> AutoTokenizer:
    global MPNET_TOKENIZER
    if MPNET_TOKENIZER is None:
        MPNET_TOKENIZER = AutoTokenizer.from_pretrained(MPNET_TOKENIZER_ID)
        MPNET_TOKENIZER.model_max_length = 10_000
    return MPNET_TOKENIZER

def is_section_header(line: str) -> bool:
    stripped_line = line.strip()
    if not stripped_line:
        return False

    # 0-indented lines match
    if line != line.lstrip():
        return False
    # section headers are all CAPS, no additional chars
    return bool(re.fullmatch(r"[A-Z0-9][A-Z0-9 \t\(\)\-]*", stripped_line))

def get_command_category(command_name: str) -> str:
    if command_name in COMMAND_CATEGORIES["FILE_PROCESSING"]:
        return "FILE_PROCESSING"
    if command_name in COMMAND_CATEGORIES["NETWORKING"]:
        return "NETWORKING"
    return "UNKNOWN"

def fix_section_content_indent(section_content: str) -> str:
    if not section_content:
        return section_content
    
    # remove 1-indent from every line
    lines = section_content.splitlines(keepends=True)
    result = []
    for line in lines:
        if line.startswith(CONTENT_INDENT):
            line = line[len(CONTENT_INDENT):]
        result.append(line)
    
    return "".join(result).strip()

def starts_with_command_name(line: str, command_name: str) -> bool:
    # replacement for startswith() to ensure exact match
    stripped_line = line.strip()
    if not command_name or not stripped_line.startswith(command_name):
        return False

    # should be a space or nothing after the command name (not alphanumeric or a hyphen)
    chars_after_command = stripped_line[len(command_name):]
    if not chars_after_command:
        return True
    return not chars_after_command[0].isalnum() and chars_after_command[0] != "-"

def count_tokens(text: str) -> int:
    tokenizer = get_mpnet_tokenizer()
    return len(tokenizer.encode(text, add_special_tokens=False))

def overlap_text(
    text: str, 
    max_tokens: int = MAX_TOKEN_LIMIT,
    overlap_tokens: int = int(MAX_TOKEN_LIMIT * 0.15)
) -> list[str]:
    tokenizer = get_mpnet_tokenizer()

    # overlap not necessary for short text
    tokens = tokenizer.encode(text, add_special_tokens=False)
    if len(tokens) <= max_tokens:
        return [text.strip()] if text.strip() else []

    # calculate the stride for the overlap
    stride = max_tokens - overlap_tokens
    chunks: list[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
        if chunk_text.strip():
            chunks.append(chunk_text.strip())
        start += stride
    
    return chunks

def starts_with_indent(line: str) -> bool:
    return line.startswith(CONTENT_INDENT)

def starts_with_dash(line: str) -> bool:
    stripped_line = line.strip()
    if not stripped_line.startswith("-"):
        return False

    return stripped_line == stripped_line.lstrip()

def split_text_by_tokens(
    text: str, 
    max_tokens: int = MAX_TOKEN_LIMIT
) -> list[str]:
    tokenizer = get_mpnet_tokenizer()

    stripped_text = text.strip()
    if not stripped_text:
        return []
    
    tokens = tokenizer.encode(stripped_text, add_special_tokens=False)
    if len(tokens) <= max_tokens:
        return [stripped_text]

    # split the text into chunks of size = max_tokens
    chunks: list[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
        if chunk_text.strip():
            chunks.append(chunk_text.strip())
        start = end

    return chunks