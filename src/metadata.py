from pydantic import BaseModel
from typing import Optional, Literal

class NAMEMetadataModel(BaseModel):
    command_name: str
    section_category: Literal["NAME"] = "NAME"
    command_category: Literal["FILE_PROCESSING", "NETWORKING"]
    source_file: str
    utility: Literal["LOW", "MEDIUM", "HIGH"] = "LOW"

class SYNOPSISMetadataModel(BaseModel):
    command_name: str
    section_category: Literal["SYNOPSIS"] = "SYNOPSIS"
    command_category: Literal["FILE_PROCESSING", "NETWORKING"]
    source_file: str
    utility: Literal["LOW", "MEDIUM", "HIGH"] = "HIGH"
    syntax_skeleton: bool = True
    command_variant_count: int

class DESCRIPTIONMetadataModel(BaseModel):
    command_name: str
    section_category: Literal["DESCRIPTION"] = "DESCRIPTION"
    subject_name: str = "GENERAL DESCRIPTION"
    command_category: Literal["FILE_PROCESSING", "NETWORKING"]
    source_file: str
    utility: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"
    overlap: bool = False
    fragmented: bool = False

class OPTIONSMetadataModel(BaseModel):
    command_name: str
    section_category: Literal["OPTIONS"] = "OPTIONS"
    subject_name: str = "GENERAL OPTIONS"
    command_category: Literal["FILE_PROCESSING", "NETWORKING"]
    source_file: str
    utility: Literal["LOW", "MEDIUM", "HIGH"] = "HIGH"
    unit_type: Literal["option_flag_unit", "context_unit"]
    flag_name: Optional[str] = None
    has_suboptions: bool = False
    fragmented: bool = False

class EXPRESSIONSMetadataModel(BaseModel):
    command_name: str
    section_category: Literal["(REGULAR) EXPRESSIONS"] = "(REGULAR) EXPRESSIONS"
    expression_header: Optional[str] = "EXPRESSIONS"
    command_category: Literal["FILE_PROCESSING", "NETWORKING"]
    source_file: str
    utility: Literal["LOW", "MEDIUM", "HIGH"] = "HIGH"
    unit_type: Literal["expression_unit", "context_unit"]
    expression_name: Optional[str] = None
    fragmented: bool = False

class EXAMPLESMetadataModel(BaseModel):
    command_name: str
    section_category: Literal["EXAMPLES"] = "EXAMPLES"
    command_category: Literal["FILE_PROCESSING", "NETWORKING"]
    source_file: str
    utility: Literal["LOW", "MEDIUM", "HIGH"] = "HIGH"
    example_command: str
    fragmented: bool = False

class ENVIRONMENTMetadataModel(BaseModel):
    command_name: str
    section_category: Literal["ENVIRONMENT (VARIABLES)"] = "ENVIRONMENT (VARIABLES)"
    command_category: Literal["FILE_PROCESSING", "NETWORKING"]
    source_file: str
    utility: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"
    variable_name: Optional[str] = None
    unit_type: Literal["environment_variable_unit", "context_unit"]
    fragmented: bool = False

class OUTPUTMetadataModel(BaseModel):
    command_name: str
    section_category: Literal["OUTPUT (FORMAT)"] = "OUTPUT (FORMAT)"
    subject_name: str = "GENERAL OUTPUT"
    command_category: Literal["FILE_PROCESSING", "NETWORKING"]
    source_file: str
    utility: Literal["LOW", "MEDIUM", "HIGH"] = "HIGH"
    unit_type: Literal["output_flag_unit", "context_unit"]
    flag_name: Optional[str] = None
    fragmented: bool = False