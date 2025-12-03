"""
Embedding CRUD Operations

This module provides database operations for Embedding entities including:
- Creating new embedding records
- Retrieving all embeddings
- Calculating cosine similarity between vectors
"""

from __future__ import annotations

from typing import List, Optional, Sequence

import numpy as np
from sqlmodel import Session, select

from app.models.embedding import Embedding


def add_new_emb(embedding: Embedding, session: Session) -> int | None:
    """
    Create a new embedding record in the database.
    
    Args:
        embedding: Embedding object containing face embedding vector
        session: Database session
        
    Returns:
        Embedding ID (primary key) of the created record, or None if creation fails
    """
    emb = Embedding.model_validate(embedding)
    session.add(emb)
    session.commit()
    session.refresh(emb)

    if not emb:
        return None
    return emb.embedding_id


def get_all(session: Session) -> Optional[List[Embedding]]:
    """
    Retrieve all embedding records from the database.
    
    Args:
        session: Database session
        
    Returns:
        List of all Embedding objects, or None if no embeddings found
    """
    statement = select(Embedding)
    embeddings = session.exec(statement).all()
    if not embeddings:
        return None
    return embeddings


def cosine_similarity(vec1: Sequence[float], vec2: Sequence[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Formula: (A · B) / (||A|| * ||B||)
    Returns a value between -1 and 1, where 1 indicates identical vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity score as a float (0.0 if either vector is zero)
    """
    v1 = np.array(vec1, dtype=float)
    v2 = np.array(vec2, dtype=float)

    # Avoid division by zero
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    if norm_v1 == 0.0 or norm_v2 == 0.0:
        return 0.0

    similarity = np.dot(v1, v2) / (norm_v1 * norm_v2)
    return float(similarity)