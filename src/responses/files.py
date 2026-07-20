from pydantic import BaseModel

class Content(BaseModel):
    file_size: int
    file_name: str
    content_type: str

class FileImportResponse(BaseModel):
    status_code: int
    path: str
    content: Content

class FileExportResponse(BaseModel):
    status_code: int
    path: str
    content: Content