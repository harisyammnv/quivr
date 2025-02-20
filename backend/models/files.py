import os
import tempfile
from typing import Any, Optional
from uuid import UUID

from fastapi import UploadFile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from logger import get_logger
from models.settings import CommonsDep, common_dependencies
from pydantic import BaseModel
from utils.file import compute_sha1_from_file

logger = get_logger(__name__)

class File(BaseModel):
    id: Optional[UUID] = None
    file: Optional[UploadFile]
    file_name: Optional[str] = ""
    file_size: Optional[int] = ""
    file_sha1: Optional[str] = ""
    vectors_ids: Optional[int]=[]
    file_extension: Optional[str] = ""
    content: Optional[Any]= None
    chunk_size: int = 500
    chunk_overlap: int= 0
    documents: Optional[Any]= None
    _commons: Optional[CommonsDep] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        if self.file:
            self.file_name = self.file.filename
            self.file_size = self.file.file._file.tell() 
            self.file_extension = os.path.splitext(self.file.filename)[-1].lower()
      
    async def compute_file_sha1(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=self.file.filename) as tmp_file:
            await self.file.seek(0)
            self.content = await self.file.read()
            tmp_file.write(self.content)
            tmp_file.flush()
            self.file_sha1 = compute_sha1_from_file(tmp_file.name)

        os.remove(tmp_file.name)

    def compute_documents(self, loader_class):
        logger.info(f"Computing documents from file {self.file_name}")
        
        documents = []
        with tempfile.NamedTemporaryFile(delete=False, suffix=self.file.filename) as tmp_file:
            tmp_file.write(self.content)
            tmp_file.flush()
            loader = loader_class(tmp_file.name)
            documents = loader.load()
            
            print("documents", documents)


        os.remove(tmp_file.name)
    
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )

        self.documents = text_splitter.split_documents(documents)

        print(self.documents)

    def set_file_vectors_ids(self):
        commons = common_dependencies() 
        response = (
            commons["supabase"].table("vectors")
            .select("id")
            .filter("metadata->>file_sha1", "eq", self.file_sha1)
            .execute()
        )
        self.vectors_ids = response.data
        return
    
    def file_already_exists(self, brain_id):
        commons = common_dependencies() 

        self.set_file_vectors_ids()

        print("file_sha1", self.file_sha1)
        print("vectors_ids", self.vectors_ids)
        print("len(vectors_ids)", len(self.vectors_ids))

        if len(self.vectors_ids) == 0:
            return False
        
        for vector in self.vectors_ids:
            response = (
                commons["supabase"].table("brains_vectors")
                .select("brain_id, vector_id")
                .filter("brain_id", "eq", brain_id)
                .filter("vector_id", "eq", vector['id'])
                .execute()
            )
            print("response.data", response.data)
            if len(response.data) == 0:
                return False
                
        return True
    
    def file_is_empty(self):
        return self.file.file._file.tell()  < 1
    