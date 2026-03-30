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
    MAX_TOKEN_LIMIT,
)
from utils import (
    is_section_header,
    get_command_category,
    fix_section_content_indent,
    starts_with_command_name,
    count_tokens,
    overlap_text,
    starts_with_indent,
    starts_with_dash,
    split_text_by_tokens
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
    
    def get_section_content(self, section_name: str) -> str | None:
        lines = self.man_page_content.splitlines(keepends=True)
        target = section_name.strip()
        in_section = False
        content_parts: list[str] = []

        for line in lines:
            if not in_section:
                if line.strip() == target and is_section_header(line):
                    in_section = True
                continue

            if is_section_header(line):
                break
            
            content_parts.append(line)
        
        if not in_section:
            return None
        
        content = "".join(content_parts).strip()
        formatted_content = fix_section_content_indent(content)
        return formatted_content.strip()

    def chunk_name(self) -> list[ManPageChunk]:
        content = self.get_section_content("NAME")
        if content is None or not content.strip():
            print("No chunks found for NAME section")
            return []

        metadata = NAMEMetadataModel(
            command_name=self.command_name,
            section_category="NAME",
            command_category=get_command_category(self.command_name),
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
        content = self.get_section_content("SYNOPSIS")
        if content is None or not content.strip():
            print("No chunks found for SYNOPSIS section")
            return []
        
        # split the content into line units
        line_units: list[str] = []
        lines = content.splitlines()
        
        current_line: list[str] = []
        for line in lines:
            stripped_line = line.strip()
            if starts_with_command_name(stripped_line, self.command_name):
                if current_line:
                    line_units.append("".join(current_line))
                    current_line = []
                current_line.append(stripped_line.strip())
            else:
                if current_line:
                    current_line.append(stripped_line.strip())
        
        if current_line:
            line_units.append("\n".join(current_line))

        # form chunks from the line units
        chunks: list[ManPageChunk] = []
        current_chunk: list[str] = []
        current_chunk_tokens = 0
        
        for line in line_units:
            num_tokens = count_tokens(line)
            if current_chunk_tokens + num_tokens > MAX_TOKEN_LIMIT:
                # finish the current chunk
                if current_chunk:
                    metadata = SYNOPSISMetadataModel(
                        command_name=self.command_name,
                        section_category="SYNOPSIS",
                        command_category=get_command_category(self.command_name),
                        source_file=self.man_page_path,
                        utility="HIGH",
                        syntax_skeleton=True,
                        command_variant_count=len(line_units)
                    )
                    
                    chunk_id = f"{self.command_name}_synopsis_{len(chunks) + 1}"
                    chunk_content = "\n".join(current_chunk)
                    chunk = ManPageChunk(
                        chunk_id=chunk_id,
                        chunk_content=chunk_content,
                        metadata=metadata
                    )
                    chunks.append(chunk)
                    current_chunk = []
                    current_chunk_tokens = 0

                # edge case handling for longer line units (301-384 tokens)
                if num_tokens > MAX_TOKEN_LIMIT:
                    # store the line as a chunk (301-384 tokens)
                    current_chunk = [line]
                    current_chunk_tokens = num_tokens
                else:
                    # store the line normally (1-300 tokens)
                    current_chunk = [line]
                    current_chunk_tokens = num_tokens
            else:
                current_chunk.append(line)
                current_chunk_tokens += num_tokens

        # finish the last chunk
        if current_chunk:
            chunk_content = "\n".join(current_chunk)
            metadata = SYNOPSISMetadataModel(
                command_name=self.command_name,
                section_category="SYNOPSIS",
                command_category=get_command_category(self.command_name),
                source_file=self.man_page_path,
                utility="HIGH",
                syntax_skeleton=True,
                command_variant_count=len(line_units)
            )
            chunk_id = f"{self.command_name}_synopsis_{len(chunks) + 1}"
            chunk = ManPageChunk(
                chunk_id=chunk_id,
                chunk_content=chunk_content,
                metadata=metadata
            )
            chunks.append(chunk)
        
        return chunks

    def chunk_description(self, section_name: str) -> list[ManPageChunk]:
        content = self.get_section_content(section_name)
        if content is None or not content.strip():
            print(f"No chunks found for {section_name} section")
            return []
        
        # split the content into overlapped chunks
        text_chunks = overlap_text(content)
        if not text_chunks:
            return []
        
        # form chunks from the text chunks
        chunks: list[ManPageChunk] = []
        for i, text_chunk in enumerate[str](text_chunks):
            metadata = DESCRIPTIONMetadataModel(
                command_name=self.command_name,
                section_category="DESCRIPTION",
                subject_name=section_name,
                command_category=get_command_category(self.command_name),
                source_file=self.man_page_path,
                utility="MEDIUM",
                overlap=(i > 0),
                fragmented=(len(text_chunks) > 1)
            )
            chunk_id = f"{self.command_name}_description_{section_name}_{i + 1}"
            chunk = ManPageChunk(
                chunk_id=chunk_id,
                chunk_content=text_chunk,
                metadata=metadata
            )
            chunks.append(chunk)

        return chunks

    def chunk_options(self, section_name: str) -> list[ManPageChunk]:
        content = self.get_section_content(section_name)
        if content is None or not content.strip():
            print(f"No chunks found for {section_name} section")
            return []
        
        # split content into option units and context units
        option_units: list[dict[str, str]] = []
        context_units: list[str] = []
        lines = content.splitlines()
        i = 0 # iterator for option units
        j = 0 # iterator for context units

        # retrieve and create option units from section
        while i < len(lines):
            current_line = lines[i].strip()
            # check if current set of lines is an option
            if starts_with_dash(current_line):
                flag_line = current_line
                i += 1 # go to next line to start option description
                description_lines: list[str] = []
                # collect description lines for current option flag
                while i < len(lines) and (
                    lines[i].strip() == "" or 
                    starts_with_indent(lines[i])
                ):
                    description_lines.append(lines[i])
                    i += 1
                
                # check if the option description contains suboptions (metadata)
                has_suboptions = any(
                    line.startswith(CONTENT_INDENT + CONTENT_INDENT) or len(line) - len(line.lstrip()) > len(CONTENT_INDENT)
                    for line in description_lines
                    if line.strip()
                )
                
                # create option unit
                option_unit = {
                    "type": "option",
                    "flag_line": flag_line,
                    "description_lines": fix_section_content_indent("\n".join(description_lines).strip()),
                    "has_suboptions": has_suboptions
                }
                option_units.append(option_unit)
                continue
            
            # go to next line since current line is not an option
            i += 1

        # retrieve and create context units from section
        while j < len(lines):
            current_line = lines[j].strip()
            # blank line, can skip
            if current_line == "":
                j += 1
                continue
            
            # check if option section and skip it
            next_line = lines[j + 1] if j + 1 < len(lines) else None
            next_is_blank_or_indent = (
                next_line is not None and (
                    next_line.strip() == "" or 
                    starts_with_indent(next_line)
                )
            )
            if (
                not starts_with_indent(lines[j]) 
                and starts_with_dash(current_line)
                and next_is_blank_or_indent
            ):
                j += 1 # go to start of option description
                while j < len(lines) and (
                    current_line == "" or 
                    starts_with_indent(lines[j])
                ):
                    j += 1 # go to next line
                continue
            
            # collect context paragraph lines
            if not starts_with_indent(lines[j]) and (
                not starts_with_dash(current_line)
                or (j + 1 >= len(lines) or not starts_with_indent(lines[j + 1]))
            ):
                context_units.append(current_line)
                j += 1 # keep iterating to collect context paragraph lines until blank line hits
                while j < len(lines) and (
                    current_line == "" or
                    starts_with_indent(lines[j])
                ):
                    if current_line != "":
                        context_units.append(current_line)
                    j += 1 # go to next context paragraph line
                continue

            # go to next line since current line is not a context paragraph
            j += 1

        chunks: list[ManPageChunk] = []
        
        # form chunks from the option units
        for option_unit in option_units:
            flag_line = option_unit["flag_line"]
            description_lines = option_unit["description_lines"]
            has_suboptions = option_unit["has_suboptions"]
            description_text = " ".join(
                line.strip() for line in description_lines.splitlines() if line.strip()
            )

            flag_name_tokens = count_tokens(flag_line)
            option_chunks = split_text_by_tokens(
                description_text,
                max_tokens=MAX_TOKEN_LIMIT - flag_name_tokens
            )
            for i, option_chunk in enumerate[str](option_chunks):
                if i == 0:
                    chunk_content = flag_line + " : " + option_chunk
                else:
                    chunk_content = flag_line + " (continued)" + " : " + option_chunk
                
                metadata = OPTIONSMetadataModel(
                    command_name=self.command_name,
                    section_category="OPTIONS",
                    subject_name=section_name,
                    command_category=get_command_category(self.command_name),
                    source_file=self.man_page_path,
                    utility="HIGH",
                    unit_type="option_flag_unit",
                    flag_name=flag_line,
                    has_suboptions=has_suboptions,
                    fragmented=(len(option_chunks) > 1)
                )
                chunk_id = f"{self.command_name}_options_flag_{section_name}_{i + 1}"
                chunk = ManPageChunk(
                    chunk_id=chunk_id,
                    chunk_content=chunk_content,
                    metadata=metadata
                )
                chunks.append(chunk)
            
        # form chunks from the context units
        combined_context = " ".join(context_units)
        context_chunks = split_text_by_tokens(combined_context)
        for i, context_chunk in enumerate[str](context_chunks):
            metadata = OPTIONSMetadataModel(
                command_name=self.command_name,
                section_category="OPTIONS",
                subject_name=section_name,
                command_category=get_command_category(self.command_name),
                source_file=self.man_page_path,
                utility="HIGH",
                unit_type="context_unit",
                fragmented=(len(context_chunks) > 1),
                has_suboptions=False
            )
            chunk_id = f"{self.command_name}_options_context_{section_name}_{i + 1}"
            chunk = ManPageChunk(
                chunk_id=chunk_id,
                chunk_content=context_chunk,
                metadata=metadata
            )
            chunks.append(chunk)
        
        return chunks

    def chunk_examples(self) -> list[ManPageChunk]:
        content = self.get_section_content("EXAMPLES")
        if content is None or not content.strip():
            print("No chunks found for EXAMPLES section")
            return []
        
        # split content into example units
        lines = content.splitlines()
        example_units: list[dict[str, str]] = []
        i = 0 # iterator for example units

        while i < len(lines):
            # skip blank lines between examples
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i >= len(lines):
                break

            # get example description lines
            description_lines: list[str] = []
            while i < len(lines) and (
                not lines[i].strip() or not lines[i].startswith(CONTENT_INDENT)
            ):
                if lines[i].strip():
                    description_lines.append(lines[i].strip())
                i += 1 # go to next line
            
            # get example command lines
            command_lines: list[str] = []
            while i < len(lines) and lines[i].startswith(CONTENT_INDENT):
                command_lines.append(lines[i][len(CONTENT_INDENT):].strip())
                i += 1 # go to next line
            
            # create example unit
            if description_lines or command_lines:
                example_units.append({
                    "type": "example",
                    "description_lines": description_lines,
                    "command_lines": command_lines,
                })

        # form chunks from the example units
        chunks: list[ManPageChunk] = []

        for example_unit in example_units:
            description_lines = " ".join(example_unit["description_lines"])
            command_lines = " ".join(example_unit["command_lines"])

            example_command_tokens = count_tokens(command_lines)
            example_chunks = split_text_by_tokens(
                description_lines,
                max_tokens=MAX_TOKEN_LIMIT - example_command_tokens
            )
            for i, example_chunk in enumerate[str](example_chunks):
                if i == 0:
                    chunk_content = example_chunk + " " + command_lines
                else:
                    chunk_content = "(continued) " + example_chunk + " " + command_lines
                
                metadata = EXAMPLESMetadataModel(
                    command_name=self.command_name,
                    section_category="EXAMPLES",
                    command_category=get_command_category(self.command_name),
                    source_file=self.man_page_path,
                    utility="HIGH",
                    example_command=command_lines,
                    fragmented=(len(example_chunks) > 1)
                )
                chunk_id = f"{self.command_name}_examples_{command_lines.replace(" ", "_")}_{i + 1}"
                chunk = ManPageChunk(
                    chunk_id=chunk_id,
                    chunk_content=chunk_content,
                    metadata=metadata
                )
                chunks.append(chunk)
        
        return chunks
    
    def chunk_expressions(self, section_name: str) -> list[ManPageChunk]:
        content = self.get_section_content(section_name)
        if content is None or not content.strip():
            print(f"No chunks found for {section_name} section")
            return []
        
        # split content into expression units and context units
        expression_units: list[dict[str, str]] = []
        context_units: list[str] = []
        lines = content.splitlines()
        i = 0 # iterator for expression units
        j = 0 # iterator for context units

        # retrieve and create expression units from section
        while i < len(lines):
            # skip the blank lines between expressions
            if not lines[i].strip():
                i += 1
                continue
            
            # check if current set of lines is an expression
            if (
                lines[i] == lines[i].lstrip()
                and i + 1 < len(lines)
                and starts_with_indent(lines[i + 1])
            ):
                expression_name = lines[i].strip()
                i += 1 # go to next line to start expression description
                
                # collect description lines for current expression
                description_lines: list[str] = []
                while i < len(lines) and (
                    lines[i].strip() == "" or 
                    starts_with_indent(lines[i])
                ):
                    description_lines.append(lines[i].strip())
                    i += 1
                
                # create expression unit
                expression_unit = {
                    "type": "expression",
                    "expression_name": expression_name,
                    "description_lines": fix_section_content_indent("\n".join(description_lines).strip()),
                }
                expression_units.append(expression_unit)
                continue
            
            # go to next line since current line is not an expression
            i += 1

        # retrieve and create context units from section
        while j < len(lines):
            # blank line, can skip
            if not lines[j].strip():
                j += 1
                continue
            
            # check if environment section and skip it
            next_line = lines[j + 1] if j + 1 < len(lines) else None
            next_is_env_description = (
                next_line is not None and (
                    starts_with_indent(next_line)
                )
            )
            if (
                not starts_with_indent(lines[j]) 
                and next_is_env_description
            ):
                j += 1 # go to start of environment description
                while j < len(lines) and (
                    lines[j].strip() == "" or 
                    starts_with_indent(lines[j])
                ):
                    j += 1 # go to next line
                continue
            
            # collect context paragraph lines
            if not starts_with_indent(lines[j]) and (
                (j + 1 >= len(lines) or not starts_with_indent(lines[j + 1]))
            ):
                context_units.append(lines[j].strip())
                j += 1 # keep iterating to collect context paragraph lines until blank line hits
                while j < len(lines) and (
                    lines[j].strip() == "" or
                    starts_with_indent(lines[j])
                ):
                    if lines[j].strip() != "":
                        context_units.append(lines[j].strip())
                    j += 1 # go to next context paragraph line
                continue

            # go to next line since current line is not a context paragraph
            j += 1

        chunks: list[ManPageChunk] = []

        # form chunks from the expression units
        for expression_unit in expression_units:
            expression_name = expression_unit["expression_name"]
            description_lines = expression_unit["description_lines"]
            description_text = " ".join(
                line.strip() for line in description_lines.splitlines() if line.strip()
            )

            expression_name_tokens = count_tokens(expression_name)
            expression_chunks = split_text_by_tokens(
                description_text,
                max_tokens=MAX_TOKEN_LIMIT - expression_name_tokens
            )
            for i, expression_chunk in enumerate[str](expression_chunks):
                if i == 0:
                    chunk_content = expression_name + ":" + expression_chunk
                else:
                    chunk_content = expression_name + " (continued)" + ":" + expression_chunk
                
                metadata = EXPRESSIONSMetadataModel(
                    command_name=self.command_name,
                    section_category="(REGULAR) EXPRESSIONS",
                    expression_header=section_name,
                    command_category=get_command_category(self.command_name),
                    source_file=self.man_page_path,
                    utility="HIGH",
                    unit_type="expression_unit",
                    expression_name=expression_name,
                    fragmented=(len(expression_chunks) > 1)
                )
                chunk_id = f"{self.command_name}_expression_{expression_name}_{i + 1}"
                chunk = ManPageChunk(
                    chunk_id=chunk_id,
                    chunk_content=chunk_content,
                    metadata=metadata
                )
                chunks.append(chunk)
        
        # form chunks from the context units
        combined_context = " ".join(context_units)
        context_chunks = split_text_by_tokens(combined_context)
        for i, context_chunk in enumerate[str](context_chunks):
            metadata = EXPRESSIONSMetadataModel(
                command_name=self.command_name,
                section_category="(REGULAR) EXPRESSIONS",
                expression_header=section_name,
                command_category=get_command_category(self.command_name),
                source_file=self.man_page_path,
                utility="HIGH",
                unit_type="context_unit",
                fragmented=(len(context_chunks) > 1)
            )
            chunk_id = f"{self.command_name}_expressions_{section_name}_context_{i + 1}"
            chunk = ManPageChunk(
                chunk_id=chunk_id,
                chunk_content=context_chunk,
                metadata=metadata
            )
            chunks.append(chunk)
        
        return chunks

    def chunk_environment(self, section_name: str) -> list[ManPageChunk]:
        content = self.get_section_content(section_name)
        if content is None or not content.strip():
            print(f"No chunks found for {section_name} section")
            return []

        # split content into environment units and context units
        environment_units: list[dict[str, str]] = []
        context_units: list[str] = []
        lines = content.splitlines()
        i = 0 # iterator for environment units
        j = 0 # iterator for context units

        # retrieve and create environment units from section
        while i < len(lines):
            # skip the blank lines between environment variables
            if not lines[i].strip():
                i += 1
                continue
            
            # check if current set of lines is an environment variable
            if (
                lines[i] == lines[i].lstrip()
                and i + 1 < len(lines)
                and starts_with_indent(lines[i + 1])
            ):
                variable_name = lines[i].strip()
                i += 1 # go to next line to start environment variable description
                
                # collect description lines for current environment variable
                description_lines: list[str] = []
                while i < len(lines) and (
                    lines[i].strip() == "" or 
                    starts_with_indent(lines[i])
                ):
                    description_lines.append(lines[i].strip())
                    i += 1
                
                # create environment unit
                environment_unit = {
                    "type": "environment_variable",
                    "variable_name": variable_name,
                    "description_lines": fix_section_content_indent("\n".join(description_lines).strip()),
                }
                environment_units.append(environment_unit)
                continue
            
            # go to next line since current line is not an option
            i += 1

        # retrieve and create context units from section
        while j < len(lines):
            # blank line, can skip
            if not lines[j].strip():
                j += 1
                continue
            
            # check if environment section and skip it
            next_line = lines[j + 1] if j + 1 < len(lines) else None
            next_is_env_description = (
                next_line is not None and (
                    starts_with_indent(next_line)
                )
            )
            if (
                not starts_with_indent(lines[j]) 
                and next_is_env_description
            ):
                j += 1 # go to start of environment description
                while j < len(lines) and (
                    lines[j].strip() == "" or 
                    starts_with_indent(lines[j])
                ):
                    j += 1 # go to next line
                continue
            
            # collect context paragraph lines
            if not starts_with_indent(lines[j]) and (
                (j + 1 >= len(lines) or not starts_with_indent(lines[j + 1]))
            ):
                context_units.append(lines[j].strip())
                j += 1 # keep iterating to collect context paragraph lines until blank line hits
                while j < len(lines) and (
                    lines[j].strip() == "" or
                    starts_with_indent(lines[j])
                ):
                    if lines[j].strip() != "":
                        context_units.append(lines[j].strip())
                    j += 1 # go to next context paragraph line
                continue

            # go to next line since current line is not a context paragraph
            j += 1
        
        chunks: list[ManPageChunk] = []

        # form chunks from the environment units
        for environment_unit in environment_units:
            variable_name = environment_unit["variable_name"]
            description_lines = environment_unit["description_lines"]
            description_text = " ".join(
                line.strip() for line in description_lines.splitlines() if line.strip()
            )

            variable_name_tokens = count_tokens(variable_name)
            environment_chunks = split_text_by_tokens(
                description_text,
                max_tokens=MAX_TOKEN_LIMIT - variable_name_tokens
            )
            for i, environment_chunk in enumerate[str](environment_chunks):
                if i == 0:
                    chunk_content = variable_name + ":" + environment_chunk
                else:
                    chunk_content = variable_name + " (continued)" + ":" + environment_chunk
                
                metadata = ENVIRONMENTMetadataModel(
                    command_name=self.command_name,
                    section_category="ENVIRONMENT (VARIABLES)",
                    command_category=get_command_category(self.command_name),
                    source_file=self.man_page_path,
                    utility="MEDIUM",
                    unit_type="environment_variable_unit",
                    variable_name=variable_name,
                    fragmented=(len(environment_chunks) > 1)
                )
                chunk_id = f"{self.command_name}_environment_variable_{variable_name}_{i + 1}"
                chunk = ManPageChunk(
                    chunk_id=chunk_id,
                    chunk_content=chunk_content,
                    metadata=metadata
                )
                chunks.append(chunk)

        # form chunks from the context units
        combined_context = " ".join(context_units)
        context_chunks = split_text_by_tokens(combined_context)
        for i, context_chunk in enumerate[str](context_chunks):
            metadata = ENVIRONMENTMetadataModel(
                command_name=self.command_name,
                section_category="ENVIRONMENT (VARIABLES)",
                command_category=get_command_category(self.command_name),
                source_file=self.man_page_path,
                utility="MEDIUM",
                unit_type="context_unit",
                fragmented=(len(context_chunks) > 1)
            )
            chunk_id = f"{self.command_name}_environment_variables_context_{i + 1}"
            chunk = ManPageChunk(
                chunk_id=chunk_id,
                chunk_content=context_chunk,
                metadata=metadata
            )
            chunks.append(chunk)
        
        return chunks

    def chunk_output(self, section_name: str) -> list[ManPageChunk]:
        content = self.get_section_content(section_name)
        if content is None or not content.strip():
            print(f"No chunks found for {section_name} section")
            return []
        
        # split content into output units and context units
        output_units: list[dict[str, str]] = []
        context_units: list[str] = []
        lines = content.splitlines()
        i = 0 # iterator for output units
        j = 0 # iterator for context units

        # retrieve and create output units from section
        while i < len(lines):
            current_line = lines[i].strip()
            # check if current set of lines is an output flag
            if starts_with_dash(current_line):
                flag_line = current_line
                i += 1 # go to next line to start output flag description
                description_lines: list[str] = []
                # collect description lines for current output flag
                while i < len(lines) and (
                    lines[i].strip() == "" or 
                    starts_with_indent(lines[i])
                ):
                    description_lines.append(lines[i])
                    i += 1
                
                # create output unit
                output_unit = {
                    "type": "output",
                    "flag_line": flag_line,
                    "description_lines": fix_section_content_indent("\n".join(description_lines).strip()),
                }
                output_units.append(output_unit)
                continue
            
            # go to next line since current line is not an option
            i += 1

        # retrieve and create context units from section
        while j < len(lines):
            current_line = lines[j].strip()
            # blank line, can skip
            if current_line == "":
                j += 1
                continue
            
            # check if option section and skip it
            next_line = lines[j + 1] if j + 1 < len(lines) else None
            next_is_blank_or_indent = (
                next_line is not None and (
                    next_line.strip() == "" or 
                    starts_with_indent(next_line)
                )
            )
            if (
                not starts_with_indent(lines[j]) 
                and starts_with_dash(current_line)
                and next_is_blank_or_indent
            ):
                j += 1 # go to start of option description
                while j < len(lines) and (
                    current_line == "" or 
                    starts_with_indent(lines[j])
                ):
                    j += 1 # go to next line
                continue
            
            # collect context paragraph lines
            if not starts_with_indent(lines[j]) and (
                not starts_with_dash(current_line)
                or (j + 1 >= len(lines) or not starts_with_indent(lines[j + 1]))
            ):
                context_units.append(current_line)
                j += 1 # keep iterating to collect context paragraph lines until blank line hits
                while j < len(lines) and (
                    current_line == "" or
                    starts_with_indent(lines[j])
                ):
                    if current_line != "":
                        context_units.append(current_line)
                    j += 1 # go to next context paragraph line
                continue

            # go to next line since current line is not a context paragraph
            j += 1

        chunks: list[ManPageChunk] = []
        
        # form chunks from the option units
        for output_unit in output_units:
            flag_line = output_unit["flag_line"]
            description_lines = output_unit["description_lines"]
            description_text = " ".join(
                line.strip() for line in description_lines.splitlines() if line.strip()
            )

            flag_name_tokens = count_tokens(flag_line)
            output_chunks = split_text_by_tokens(
                description_text,
                max_tokens=MAX_TOKEN_LIMIT - flag_name_tokens
            )
            for i, output_chunk in enumerate[str](output_chunks):
                if i == 0:
                    chunk_content = flag_line + ": " + output_chunk
                else:
                    chunk_content = flag_line + " (continued)" + ": " + output_chunk
                
                metadata = OUTPUTMetadataModel(
                    command_name=self.command_name,
                    section_category="OUTPUT (FORMAT)",
                    subject_name=section_name,
                    command_category=get_command_category(self.command_name),
                    source_file=self.man_page_path,
                    utility="HIGH",
                    unit_type="output_flag_unit",
                    flag_name=flag_line,
                    fragmented=(len(output_chunks) > 1)
                )
                chunk_id = f"{self.command_name}_output_flag_{section_name}_{i + 1}"
                chunk = ManPageChunk(
                    chunk_id=chunk_id,
                    chunk_content=chunk_content,
                    metadata=metadata
                )
                chunks.append(chunk)
            
        # form chunks from the context units
        combined_context = " ".join(context_units)
        context_chunks = split_text_by_tokens(combined_context)
        for i, context_chunk in enumerate[str](context_chunks):
            metadata = OUTPUTMetadataModel(
                command_name=self.command_name,
                section_category="OUTPUT (FORMAT)",
                subject_name=section_name,
                command_category=get_command_category(self.command_name),
                source_file=self.man_page_path,
                utility="HIGH",
                unit_type="context_unit",
                fragmented=(len(context_chunks) > 1)
            )
            chunk_id = f"{self.command_name}_output_context_{section_name}_{i + 1}"
            chunk = ManPageChunk(
                chunk_id=chunk_id,
                chunk_content=context_chunk,
                metadata=metadata
            )
            chunks.append(chunk)
        
        return chunks

if __name__ == "__main__":
    print("Splitting man page...")
    splitter = ManPageSplitter("data/curl.txt", "curl")

    expressions_sections: list[str] = []
    if "EXPRESSIONS" in TARGET_COMMAND_SECTIONS[splitter.command_name]:
        expressions_sections.append("EXPRESSIONS")
    elif "REGULAR EXPRESSIONS" in TARGET_COMMAND_SECTIONS[splitter.command_name]:
        expressions_sections.append("REGULAR EXPRESSIONS")
    for section in TARGET_COMMAND_SECTIONS[splitter.command_name]:
        if section in ADJACENT_SECTIONS["EXPRESSIONS"]:
            expressions_sections.append(section)

    for section in expressions_sections:
        content = splitter.get_section_content(section)
        if content:
            expressions_chunks = splitter.chunk_expressions(section)
            for chunk in expressions_chunks:
                print(chunk.chunk_id)
                print(chunk.chunk_content)
                print(chunk.metadata)
                print("-" * 100)
            print(len(expressions_chunks))
        else:
            print("no content found")