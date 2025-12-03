"""
Face recognition service built on top of InsightFace.

This module is responsible for:
- Initializing the InsightFace `FaceAnalysis` pipeline.
- Extracting face embeddings from images.
- Comparing embeddings and resolving persons from the database.
"""

import cv2
import numpy as np
from insightface.app import FaceAnalysis

from app.cruds.person_crud import get_person_by_embedding_id


model_name = "buffalo_l"


class InsightFaceEmbedder:
    """
    Thin wrapper around InsightFace `FaceAnalysis` providing helpers
    to extract embeddings and perform matching.
    """

    def __init__(self):
        self.app = FaceAnalysis(name=model_name, providers=['CPUExecutionProvider'])
        ctx_id = 1
        self.app.prepare(ctx_id=ctx_id, det_size=(640, 640))

    def get_face_embedding_image(self, image_path: str) -> np.ndarray:
        """
        Load an image from disk and compute a face embedding.

        Raises:
            ValueError: If the image cannot be read or no faces are detected.
        """
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        faces = self.app.get(img)
        
        if len(faces) < 1:
            raise ValueError("No faces detected in the image")
        if len(faces) > 1:
            print("Warning: Multiple faces detected. Using first detected face")
        return faces[0].embedding.astype(np.float32)
    

    def recoginze_face_image(self, image_path: str, embedding: np.ndarray):
        """
        Convenience helper: compute an embedding for `image_path`
        and compare it with a reference `embedding`.
        """
        emb1 = self.get_face_embedding_image(image_path)
        res = self.compare_faces(emb1, embedding)
        print(res)
        return res
    
    def find_match(self, face, embeddings, session, threshold: float = 0.65):
        """
        Find the best matching person for a detected face.

        Args:
            face: A single `FaceAnalysis` result.
            embeddings: Iterable of embedding rows from the database.
            session: Database session used to load person data.
            threshold: Cosine similarity threshold for a positive match.

        Returns:
            A list containing a single result dict with bounding box and
            match information.
        """
        results = [] 

        emb = face.embedding 
        best_score = 0.0 
        best_person = None 
        emb_id = 0
        for e in embeddings: 
            ref_emb = np.frombuffer(e.vector, dtype=np.float32)
            similarity, is_match = cosine_similarity(emb, ref_emb) 
            if similarity > best_score: 
                best_score = similarity 
                emb_id = e.embedding_id
                bbox = face.bbox.astype(int).tolist()
        
        matched = best_score > threshold
         

        if matched:
            best_person = get_person_by_embedding_id(emb_id, session) 
            result = { "bbox": bbox,
            "matched": matched,
            "person_id" : best_person.person_id,
            "first_name": best_person.first_name,
            "last_name" : best_person.last_name,
            "score": float(best_score) }
        else:
            result = { "bbox": bbox,
            "matched": False,
            "name" : "Unkown",
            "score": float(best_score) }
            
        results.append(result) 

        return results
    
def calculate_embeddings_avg(embs: list[np.ndarray]) -> np.ndarray:
    if not embs:
        raise ValueError("The list of embeddings is empty.")
    normalized_embs = [e / (np.linalg.norm(e) + 1e-8) for e in embs]
    avg_emb = np.mean(np.vstack(normalized_embs), axis=0)
    avg_emb = avg_emb / (np.linalg.norm(avg_emb) + 1e-8)

    return avg_emb


def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray, threshold: float = 0.65 ):
    denom = (np.linalg.norm(emb1) * np.linalg.norm(emb2)) + 1e-8
    similarity = float(np.dot(emb1, emb2) / denom)
    return similarity, similarity > threshold