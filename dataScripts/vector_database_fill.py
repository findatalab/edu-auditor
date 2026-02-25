import os
import sys
from typing import List, Callable

sys.path.extend(["..\\", "..\\backend\\"])

import pypdf
import faiss

from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from tqdm import tqdm

from data_utils import TextEmbedding, PdfChunkReader
from relational_database import Chunk

# Creating connection to database
DB_PASSWORD = os.getenv("DB_PASSWORD")
engine = create_engine(f"postgresql://postgres:{DB_PASSWORD}@localhost/prototypedocumentreviewsystem")

class FaissLoader:
    def __init__(self, embedding_class: TextEmbedding):
        self.embedding_class = embedding_class

    def load_and_save_database(self, folder_path: str, save_to: str, engine) -> None:
        """
        Loads all documents from folder path that contains only pdf docs
        chunks them and embeds into vector database (embedding vectors are normalized)
        and saves it to save_to path. It also adds chunks to database with specified function
        db_chunk_add
        """
        index = faiss.IndexFlatIP(self.embedding_class.model.embeddings.word_embeddings.weight.shape[1])
        pdf_filenames = os.listdir(folder_path)
        SESSION = Session(engine)
        CURRENT_TOTAL_VECTORS = 0
        for pdf_filename in tqdm(pdf_filenames, desc="Going through filenames..."):
            chunks = PdfChunkReader(folder_path + "\\" + pdf_filename).get_chunks()
            print(f"Length of chunks: {len(chunks)}")
            print(f"Number of vectors in database: {index.ntotal}")
            embedded_chunks_yielding = self.embedding_class.embed(chunks)
            previous_total = 0
            for chunk_batch in embedded_chunks_yielding:    
                index.add(chunk_batch)
                next_total = index.ntotal - CURRENT_TOTAL_VECTORS
                slice_chunks = chunks[previous_total:next_total]
                clean_slice_chunks = [chunk.replace('\x00', '') for chunk in slice_chunks]
                chunk_ids = list(range(previous_total + CURRENT_TOTAL_VECTORS, next_total + CURRENT_TOTAL_VECTORS))
                db_chunks = [Chunk(id=id, chunk=chunk) for id, chunk in zip(chunk_ids, clean_slice_chunks)]
                SESSION.add_all(db_chunks)
                SESSION.commit()
                previous_total = next_total
            CURRENT_TOTAL_VECTORS = previous_total + CURRENT_TOTAL_VECTORS
        SESSION.close()
        faiss.write_index(index, save_to)
        return None

if __name__ == "__main__":
    embedding_class = TextEmbedding(model_name='Snowflake/snowflake-arctic-embed-l-v2.0', device="cpu")
    faiss_loader = FaissLoader(embedding_class=embedding_class)
    faiss_loader.load_and_save_database(folder_path= "C:\\main\\GitHub\\documentReviewSystem\\knowledge_data",
                                        save_to= "C:\\main\\GitHub\\documentReviewSystem\\project_data\\vector_db.index",
                                        engine= engine)
