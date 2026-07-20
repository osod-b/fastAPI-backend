from pydantic import BaseModel

class Content(BaseModel):
    content_type: str
    credentials: str
    created: str

class ContentMod(Content):
    results:list

class CreateResponse(BaseModel):
    status_code: int
    id: str
    content: Content

class UpdateResponse(BaseModel):
    status_code: int
    id: int
    content: Content

class DeleteResponse(BaseModel):
    status_code: int
    id: int
    content: Content

class FilterResponse(BaseModel):
    status_code: int
    id: int | list[int]
    content: ContentMod 

