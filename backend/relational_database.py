import os
import sys
from typing import List, Optional

sys.path.extend(["..\\"])

import faiss
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from data_utils import TextEmbedding, normalize_vectors

# Global variables
DEVICE = "cpu"

# Creating connection to database
DB_PASSWORD = os.getenv("DB_PASSWORD")
engine = create_engine(f"postgresql://postgres:{DB_PASSWORD}@localhost/prototypedocumentreviewsystem")

index = faiss.read_index("C:\\main\\GitHub\\documentReviewSystem\\project_data\\initial_vector_db.index")

text_embedding = TextEmbedding(model_name='Snowflake/snowflake-arctic-embed-l-v2.0')
model = text_embedding.model
tokenizer = text_embedding.tokenizer

class Base(DeclarativeBase):
    pass

class Chunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    chunk: Mapped[str] 

    def __repr__(self) -> str:
        return f"Chunk(id={self.id!r}, content={self.chunk!r})"

Base.metadata.create_all(engine)

# API class
app = FastAPI()

class SimilarityRequest(BaseModel):
    text: str

class SimilarityResponse(BaseModel):
    chunks: str

@app.post("/similar_chunks", response_model = SimilarityResponse)
def similarity_search(request: SimilarityRequest):
    model_request = [request.text]
    print(f"Model request: ")
    tokens = tokenizer(model_request, return_tensors='pt',
                          padding=True, truncation=True, max_length=8000)
    device_tokens = {k: v.to(device=DEVICE) for k, v in tokens.items()}
    docs_embeddings = model(**device_tokens)[0][:, 0].detach().cpu().numpy()
    D, I = index.search(normalize_vectors(docs_embeddings), 5)
    id_list = I.flatten().tolist()
    stmt = select(Chunk).where(Chunk.id.in_(id_list))
    with Session(engine) as session:
        chunk_results = session.scalars(stmt).all()
    return SimilarityResponse(chunks = "\n".join([chunk.chunk for chunk in chunk_results]))



if __name__ == "__main__":
    uvicorn.run(app, port=8001)
'--------------------------------------------------------------------------------'





