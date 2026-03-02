import re
from pydantic import BaseModel

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
from constants import (
    ADJACENT_SECTIONS, 
    TARGET_COMMAND_SECTIONS,
    CONTENT_INDENT,
    COMMAND_CATEGORIES
)

class ManPageChunk(BaseModel):
    chunk_id: str
    chunk_content: str
    metadata: (
        NAMEMetadataModel | 
        SYNOPSISMetadataModel | 
        DESCRIPTIONMetadataModel | 
        OPTIONSMetadataModel | 
        EXPRESSIONSMetadataModel | 
        EXAMPLESMetadataModel | 
        ENVIRONMENTMetadataModel | 
        OUTPUTMetadataModel
    )

class ManPageSplitter:
    def __init__(self, man_page_path: str, command_name: str):
        self.man_page_path = man_page_path
        self.man_page_content = self.read_man_page()
        self.command_name = command_name
        self.command_sections = TARGET_COMMAND_SECTIONS[command_name]

    def read_man_page(self) -> str:
        with open(self.man_page_path, "r") as file:
            return file.read()

    def is_section_header(self, line: str) -> bool:
        stripped_line = line.strip()
        if not stripped_line:
            return False

        # 0-indented lines match
        if line != line.lstrip():
            return False
        # section headers are all CAPS, no additional chars
        return bool(re.fullmatch(r"[A-Z0-9][A-Z0-9 \t\(\)\-]*", stripped_line))

    def fix_section_content_indent(self, section_content: str) -> str:
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
    
    def get_section_content(self, section_name: str) -> str | None:
        lines = self.man_page_content.splitlines(keepends=True)
        target = section_name.strip()
        in_section = False
        content_parts: list[str] = []

        for line in lines:
            if not in_section:
                if line.strip() == target and self.is_section_header(line):
                    in_section = True
                continue

            if self.is_section_header(line):
                break
            
            content_parts.append(line)
        
        if not in_section:
            return None
        
        content = "".join(content_parts).strip()
        formatted_content = self.fix_section_content_indent(content)
        return formatted_content.strip()

    def get_command_category(self, command_name: str) -> str:
        if command_name in COMMAND_CATEGORIES["FILE_PROCESSING"]:
            return "FILE_PROCESSING"
        if command_name in COMMAND_CATEGORIES["NETWORKING"]:
            return "NETWORKING"
        return "UNKNOWN"

    def chunk_name(self) -> list[ManPageChunk]:
        content = self.get_section_content("NAME")
        if content is None or not content.strip():
            print(f"No chunks found for NAME section")
            return []

        metadata = NAMEMetadataModel(
            command_name=self.command_name,
            section_category="NAME",
            command_category=self.get_command_category(self.command_name),
            source_file=self.man_page_path,
            utility="LOW"
        )

        chunk_id = f"{self.command_name}_name_summary"
        chunk = ManPageChunk(
            chunk_id=chunk_id,
            chunk_content=content,
            metadata=metadata
        )
        return [chunk]

    def chunk_synopsis(self) -> list[ManPageChunk]:
        return

    def chunk_description(self) -> list[ManPageChunk]:
        return

    def chunk_options(self) -> list[ManPageChunk]:
        return

    def chunk_expressions(self) -> list[ManPageChunk]:
        return

    def chunk_examples(self) -> list[ManPageChunk]:
        return

    def chunk_environment(self) -> list[ManPageChunk]:
        return

    def chunk_output(self) -> list[ManPageChunk]:
        return

if __name__ == "__main__":
    print("Splitting man page...")
    splitter = ManPageSplitter("data/curl.txt", "curl")

    content = splitter.get_section_content("NAME")
    if content:
        name_chunks = splitter.chunk_name()
        print(name_chunks)
    else:
        print("no content found")
