from typing import List, Dict, Any

from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field



class Title(BaseModel):
    title: str = Field(description="title")

    def to_dict(self) -> Dict[str, Any]:
        return {"title": self.title}


class Summary(BaseModel):
    summary: str = Field(description="summary")

    def to_dict(self) -> Dict[str, Any]:
        return {"summary": self.summary}
    

class Similarity(BaseModel):
    similarity: int = Field(description="similarity")
    
    def to_dict(self) -> Dict[int, Any]:
        return {"similarity": self.similarity}
    

class Speaker(BaseModel):
    speaker: str = Field(description="speaker")
    
    def to_dict(self) -> Dict[str, Any]:
        return {"speaker": self.speaker}
    

title_parser = PydanticOutputParser(pydantic_object=Title)
summary_parser = PydanticOutputParser(pydantic_object=Summary)
similarity_parser = PydanticOutputParser(pydantic_object=Similarity)
speaker_parser = PydanticOutputParser(pydantic_object=Speaker)



