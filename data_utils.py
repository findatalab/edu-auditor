from typing import List

from pypdf import PdfReader

import torch
import numpy as np
import torch.nn as nn

from transformers import AutoModel, AutoTokenizer

# Classes

class TextEmbedding:
    def __init__(self, model_name: str, device: str = "cpu"):
        self.device = device
        self.model = AutoModel.from_pretrained(model_name).to(device).eval()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    def embed(self, docs: List, max_length: int = 8192, batch_size: int = 3) -> np.ndarray:
        """
        Embeds list of documents to vector representations by yilding embedded batches

        Args
        ----
        docs: List
            Documents to be embedded
        
        Yields
        -------
        array: np.ndarray
            Numpy array of shape (B, E) representing normalized vector embeddings, where
            B - number of documents in a batch; E - dimension of model vectors 
        """
        NUM_DOCS = len(docs)
        for i_batch in range(1, NUM_DOCS//batch_size + 1):
            docs_tokens = self.tokenizer(docs[(i_batch-1)*batch_size:i_batch*batch_size if i_batch*batch_size <= NUM_DOCS else NUM_DOCS], return_tensors='pt',
                                         padding=True, truncation=True, max_length=max_length)

            docs_device_tokens = {k: v.to(device=self.device) for k, v in docs_tokens.items()}
            docs_embeddings = self.model(**docs_device_tokens)[0][:, 0]
            normalized_embeddings = nn.functional.normalize(docs_embeddings, p=2.0, dim=1).detach().cpu().numpy()
            yield normalized_embeddings
    

class PdfChunkReader():
    def __init__(self, pdf_path: str, chunk_length: int = 2500):
        self.pdf_path = pdf_path
        self.chunk_length = chunk_length
        self.pdf_chunks = None
    
    @property
    def pdf_lines(self):
        """
        Returns a generator of all pdf lines 
        """
        pdf_reader = PdfReader(self.pdf_path)
        for page in pdf_reader.pages:
            for line in page.extract_text().split("\n"):
                yield line

    def get_chunks(self):
        if self.pdf_chunks != None:
            return self.pdf_chunks
        
        pdf_chunks = []
        current_lines_list = []
        for line in self.pdf_lines:
            current_lines_list.append(line+"\n")
            if len("".join(current_lines_list)) >= self.chunk_length:
                pdf_chunks.append("".join(current_lines_list[:-1]))
                current_lines_list = [current_lines_list[-1]]
        # Check whether there are leftover lines
        if len(current_lines_list) != 0:
            pdf_chunks.append("".join(current_lines_list).rstrip("\n"))

        self.pdf_chunks = pdf_chunks
        return pdf_chunks


# Functions

def normalize_vectors(vectors_array: np.ndarray) -> np.ndarray:
    """
    Function that takes in numpy vectors as rows, normalizes and returns them back

    Args
    ----
    vectors_array: np.ndarray
        Numpy array of shape N x E where N is number of vectors and E is their dimension

    Returns
    -------
    normalized_vectors: np.ndarray
        Same vectors but normalized 
    """
    norms = np.apply_along_axis(np.linalg.norm, arr = vectors_array, axis = 1) # Shape N 
    normalized_vectors = vectors_array/norms[:, np.newaxis]
    return normalized_vectors

"--------------------------------------------------------------------------------"