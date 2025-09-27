import fitz  # PyMuPDF
from PIL import Image
import torch

from transformers.utils.import_utils import is_flash_attn_2_available
from colpali_engine.models import ColQwen2, ColQwen2Processor

import numpy as np
from typing import List, Optional, Tuple
import io

class PDFColPaliEmbedder:
    """
    A class to read PDF files and generate embeddings for each page using ColPali.
    ColPali is a vision-language model designed for document retrieval.
    """
    
    def __init__(self, model_name: str = "vidore/colqwen2-v1.0"):
        """
        Initialize the PDFColPaliEmbedder with ColPali model.
        
        Args:
            model_name (str): HuggingFace model name for ColPali
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Load ColPali model and processor
        self.processor = ColQwen2Processor.from_pretrained(model_name)
        self.model = ColQwen2.from_pretrained(
                        model_name,
                        torch_dtype=torch.float32,
                        device_map=self.device,  # or "mps" if on Apple Silicon
                        attn_implementation="flash_attention_2" if is_flash_attn_2_available() else None,
                    ).eval()
        
        self.pdf_path = None
        self.page_images = []
        self.embeddings = []
    
    def load_pdf(self, pdf_path: str) -> None:
        """
        Load a PDF file and convert pages to images.
        
        Args:
            pdf_path (str): Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.page_images = []
        
        try:
            doc = fitz.open(pdf_path)
            print(f"Loaded PDF with {len(doc)} pages")
            
            # Convert each page to image
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Render page as image (300 DPI for good quality)
                mat = fitz.Matrix(300/72, 300/72)  # 300 DPI scaling
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data)).convert("RGB")
                
                self.page_images.append(image)
                print(f"Converted page {page_num + 1} to image")
            
            doc.close()
            
        except Exception as e:
            raise Exception(f"Error loading PDF: {str(e)}")
    
    def generate_embeddings(self, batch_size: int = 1) -> np.ndarray:
        """
        Generate ColPali embeddings for all PDF page images.
        
        Args:
            batch_size (int): Number of images to process at once
            
        Returns:
            np.ndarray: Array of embeddings with shape (num_pages, embedding_dim)
        """
        if not self.page_images:
            raise ValueError("No PDF loaded. Call load_pdf() first.")
        
        self.embeddings = []
        
        print(f"Generating embeddings for {len(self.page_images)} pages...")
        
        # Process images in batches
        for i in range(0, len(self.page_images), batch_size):
            batch_images = self.page_images[i:i + batch_size]
            
            with torch.no_grad():
                inputs = self.processor.process_images(batch_images)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                batch_embeddings = self.model(**inputs)
                batch_embeddings = batch_embeddings.cpu().numpy()
                self.embeddings.extend(batch_embeddings)
            
            print(f"Processed pages {i+1}-{min(i+batch_size, len(self.page_images))}")
        
        self.embeddings = np.array(self.embeddings)
        print(f"Generated embeddings with shape: {self.embeddings.shape}")
        
        return self.embeddings
    
    def get_embedding(self, page_num: int) -> Optional[np.ndarray]:
        """
        Get the embedding for a specific page.
        
        Args:
            page_num (int): Page number (0-indexed)
            
        Returns:
            np.ndarray: The page embedding, or None if invalid page number
        """
        if len(self.embeddings) > 0 and 0 <= page_num < len(self.embeddings):
            return self.embeddings[page_num]
        return None

# Example usage
if __name__ == "__main__":
    # Initialize the embedder
    embedder = PDFColPaliEmbedder()
    
    # Load a PDF file
    pdf_path = "example.pdf"  # Replace with your PDF path
    embedder.load_pdf(pdf_path)
    
    # Generate embeddings for all pages
    embeddings = embedder.generate_embeddings(batch_size=2)

    page_0_embedding = embedder.get_embedding(0)

    print(page_0_embedding)