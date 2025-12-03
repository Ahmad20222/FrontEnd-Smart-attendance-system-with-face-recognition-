"""
Attendance Router Module

This module handles all attendance-related API endpoints including:
- Face enrollment (camera, browser, images)
- Face recognition and attendance taking
- Attendance records retrieval
"""

# Standard library imports
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Annotated, List, Optional

# Third-party imports
import cv2
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from starlette.requests import ClientDisconnect

# Local application imports
from app.config.dbsetup import SessionDep
from app.cruds.attendance_crud import add_attendance, get_attendances
from app.cruds.embedding_crud import add_new_emb, get_all
from app.cruds.person_crud import create_person, get_person_by_embedding_id
from app.cruds.status_crud import get_status_id, add_new_status
from app.models.administrator import Administrator
from app.models.attendance import AttendanceCreate, AttendanceDTO
from app.models.embedding import Embedding
from app.models.person import PersonCreate
from app.services.auth import get_current_admin
from app.services.face_service import (
    InsightFaceEmbedder,
    calculate_embeddings_avg,
    cosine_similarity,
)

# Router configuration
router = APIRouter(prefix="/attendance", tags=["attendance"])
logger = logging.getLogger(__name__)

# Global embedder instance (initialized in main.py lifespan)
embedder: Optional[InsightFaceEmbedder] = None

# Dependency for authenticated admin users
current_admin_dep = Annotated[Administrator, Depends(get_current_admin)]

# Track persons who already took attendance today (prevents duplicate attendance)
seen_today = set()


# Request/Response Models
class EnrollReq(BaseModel):
    """Request model for face enrollment"""
    first_name: str
    last_name: str


class RecognizeReq(BaseModel):
    """Request model for face recognition"""
    image_path: str


class RecognizeResp(BaseModel):
    """Response model for face recognition"""
    matched: bool
    person_id: Optional[int] = None
    person_name: Optional[str] = None
    score: float

@router.get("/records", response_model=List[AttendanceDTO])
def fetch_all_attendances(
    session: SessionDep, 
    current_user: current_admin_dep
) -> List[AttendanceDTO]:
    """
    Retrieve all attendance records.
    
    Args:
        session: Database session dependency
        current_user: Authenticated administrator
        
    Returns:
        List of attendance records
        
    Raises:
        HTTPException: If no attendance records found
    """
    attendances = get_attendances(session)
    if not attendances:
        return []
    return attendances


@router.post("/enroll")
def enroll_face(
    req: EnrollReq, 
    session: SessionDep, 
    current_user: current_admin_dep
):
    """
    Enroll a person's face from a single image path.
    
    Note: This endpoint appears incomplete as EnrollReq doesn't have image_path.
    Consider using enroll_browser_camera or enroll_camera instead.
    
    Args:
        req: Enrollment request with first_name and last_name
        session: Database session dependency
        current_user: Authenticated administrator
        
    Returns:
        Enrollment confirmation with embedding ID
        
    Raises:
        HTTPException: If embedding fails or person creation fails
    """
    global embedder
    
    if embedder is None:
        raise HTTPException(status_code=503, detail="Vision pipeline not ready")
    
    # Note: This function needs image_path which is not in EnrollReq model
    # This endpoint may need to be refactored or removed
    raise HTTPException(
        status_code=501, 
        detail="This endpoint is not fully implemented. Use enroll_camera or enroll_browser_camera instead."
    )

@router.post("/recognize_user", response_model=RecognizeResp)
def recognize_user(
    req: RecognizeReq, 
    session: SessionDep, 
    current_user: current_admin_dep
) -> RecognizeResp:
    """
    Recognize a person from an image path by comparing face embeddings.
    
    Args:
        req: Recognition request with image_path
        session: Database session dependency
        current_user: Authenticated administrator
        
    Returns:
        Recognition result with match status, person info, and similarity score
    """
    global embedder
    
    if embedder is None:
        raise HTTPException(status_code=503, detail="Vision pipeline not ready")
    
    # Extract face embedding from image
    try:
        emb = embedder.get_face_embedding_image(req.image_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unable to embed face: {str(e)}")
    
    if emb is None:
        raise HTTPException(status_code=400, detail="Unable to embed face")
    
    # Get all embeddings from database
    embeddings = get_all(session)
    if not embeddings:
        return RecognizeResp(matched=False, score=-1.0)
    
    # Find best matching embedding
    matched_emb = None
    best_score = 0.0
    for e in embeddings:
        ref_emb = np.frombuffer(e.vector, dtype=np.float32)
        similarity, _ = cosine_similarity(emb, ref_emb)
        
        if similarity > best_score:
            best_score = similarity
            matched_emb = e.embedding_id
    
    # Check if match exceeds threshold
    is_match = best_score > 0.65
    
    if is_match and matched_emb:
        person = get_person_by_embedding_id(matched_emb, session)
        if person:
            return RecognizeResp(
                matched=True,
                person_id=person.person_id,
                person_name=f"{person.first_name} {person.last_name}",
                score=float(best_score)
            )
    
    return RecognizeResp(matched=False, score=float(best_score))


@router.post("/enroll_images")
def enroll_faces(
    req: EnrollReq, 
    session: SessionDep, 
    current_user: current_admin_dep
):
    """
    Enroll a person using multiple image paths.
    
    Note: This endpoint appears incomplete as EnrollReq model doesn't include
    image_path or email fields. Consider using enroll_browser_camera or enroll_camera instead.
    
    Args:
        req: Enrollment request (currently missing required fields)
        session: Database session dependency
        current_user: Authenticated administrator
        
    Returns:
        Enrollment confirmation
        
    Raises:
        HTTPException: If embedding fails or person creation fails
    """
    global embedder
    
    if embedder is None:
        raise HTTPException(status_code=503, detail="Vision pipeline not ready")
    
    # Note: This function references fields that don't exist in EnrollReq
    # This endpoint may need to be refactored or removed
    raise HTTPException(
        status_code=501,
        detail="This endpoint requires fields not present in EnrollReq model. Use enroll_camera or enroll_browser_camera instead."
    )


@router.post("/enroll_camera")
def enroll_camera(
    req: EnrollReq, 
    session: SessionDep, 
    current_user: current_admin_dep
):
    """
    Enroll a person using system camera (opens camera window, captures 10 images).
    
    This endpoint launches a subprocess that opens a camera window and captures
    10 images, then processes them to create an average face embedding.
    
    Args:
        req: Enrollment request with first_name and last_name
        session: Database session dependency
        current_user: Authenticated administrator
        
    Returns:
        Success message confirming enrollment
        
    Raises:
        HTTPException: If vision pipeline not ready, capture fails, or no faces detected
    """
    global embedder
    logger.info(f"=== ENROLL_CAMERA START === Enrolling: {req.first_name} {req.last_name}")
    
    # Check embedder initialization
    if embedder is None:
        logger.error("Vision pipeline not ready - embedder is None")
        raise HTTPException(status_code=503, detail="Vision pipeline not ready")
    logger.info("Embedder is ready")

    # Setup output directory
    out_dir = Path(os.getcwd()) / "enroll_images"
    logger.info(f"Output directory: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory created/exists: {out_dir.exists()}")

    # Prepare subprocess command
    cmd = [sys.executable, "-m", "app.services.enrollment_service", str(out_dir), "0", "15000"]
    logger.info(f"Launching subprocess with command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        logger.info(f"Subprocess completed with return code: {result.returncode}")
        
        if result.stdout:
            logger.info(f"Subprocess stdout: {result.stdout}")
        if result.stderr:
            logger.warning(f"Subprocess stderr: {result.stderr}")
            
        # Check return code
        if result.returncode != 0:
            error_detail = result.stderr if result.stderr else f"Subprocess exited with code {result.returncode}"
            logger.error(f"Subprocess failed: {error_detail}")
            raise HTTPException(
                status_code=500, 
                detail=f"Image capture failed (exit code {result.returncode}): {error_detail}"
            )
    except subprocess.TimeoutExpired:
        logger.error("Subprocess timed out after 20 seconds")
        raise HTTPException(status_code=500, detail="Image capture timed out after 20 seconds")
    except Exception as e:
        logger.error(f"Exception launching subprocess: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to launch capture helper: {e}")

    # Check for captured images
    image_paths = sorted(out_dir.glob("*.png"))
    logger.info(f"Found {len(image_paths)} image(s) after capture")
    
    if not image_paths:
        logger.error("No images found in output directory after capture")
        # List files in directory for debugging
        all_files = list(out_dir.glob("*"))
        logger.error(f"Files in directory: {[str(f) for f in all_files]}")
        raise HTTPException(status_code=500, detail="No images found after capture")

    # Process images to extract embeddings
    logger.info(f"Processing {len(image_paths)} image(s) to extract embeddings")
    embs = []
    
    for idx, p in enumerate(image_paths, 1):
        logger.info(f"Processing image {idx}/{len(image_paths)}: {p.name}")
        try:
            emb = embedder.get_face_embedding_image(str(p))
            if emb is not None:
                embs.append(emb)
                logger.info(f"Successfully extracted embedding from {p.name}")
            else:
                logger.warning(f"No embedding extracted from {p.name} (returned None)")
        except ValueError as e:
            logger.warning(f"ValueError processing {p.name}: {str(e)}")
            continue
        except Exception as e:
            logger.error(f"Exception processing {p.name}: {type(e).__name__}: {str(e)}", exc_info=True)
            continue

    logger.info(f"Successfully extracted {len(embs)} embedding(s) from {len(image_paths)} image(s)")
    
    # Check if we have any valid embeddings
    if not embs:
        logger.error(f"No valid embeddings could be computed from {len(image_paths)} captured images")
        logger.error("Possible reasons: 1) No face visible in images, 2) Face too far/close, 3) Poor lighting, 4) Face not facing camera")
        raise HTTPException(
            status_code=400, 
            detail="No face detected in captured images. Please ensure you are facing the camera clearly with good lighting and try again."
        )

    # Calculate average embedding
    logger.info("Calculating average embedding")
    try:
        avg_emb = calculate_embeddings_avg(embs)
        logger.info(f"Average embedding calculated successfully, shape: {avg_emb.shape}")
    except Exception as e:
        logger.error(f"Error calculating average embedding: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to calculate average embedding: {str(e)}"
        )

    # Convert to bytes
    avg = avg_emb.astype(np.float32).tobytes()
    logger.info(f"Embedding converted to bytes, size: {len(avg)} bytes")

    # Save embedding to database
    logger.info("Saving embedding to database")
    try:
        created_emb = add_new_emb(Embedding(vector=avg), session)
        logger.info(f"Embedding saved with ID: {created_emb}")
    except Exception as e:
        logger.error(f"Error saving embedding: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save embedding: {str(e)}")

    # Create person record
    logger.info(f"Creating person record: {req.first_name} {req.last_name}")
    try:
        person = create_person(
            PersonCreate(first_name=req.first_name, last_name=req.last_name, embedding_id=created_emb),
            session
        )
        if person is None:
            logger.error("Failed to create person - create_person returned None")
            raise HTTPException(status_code=500, detail="Failed to create person")
        logger.info(f"Person created successfully with ID: {person.person_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exception creating person: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create person: {str(e)}")

    # Clean up images
    logger.info("Cleaning up captured images")
    deleted_count = 0
    for p in image_paths:
        try:
            p.unlink()
            deleted_count += 1
        except Exception as e:
            logger.warning(f"Failed to delete {p.name}: {str(e)}")
    logger.info(f"Deleted {deleted_count}/{len(image_paths)} image(s)")

    logger.info(f"=== ENROLL_CAMERA SUCCESS === Enrolled: {req.first_name} {req.last_name}")
    return {
        "message": "Embeddings created successfully",
    }


@router.post("/enroll_browser_camera")
async def enroll_browser_camera(
    request: Request, 
    session: SessionDep, 
    current_user: current_admin_dep
):
    """
    Enroll a person using images captured from browser camera.
    
    Receives form data with first_name, last_name, and multiple image files.
    Processes images to extract face embeddings, calculates average, and creates
    person record in database.
    
    Args:
        request: FastAPI request object containing form data and image files
        session: Database session dependency
        current_user: Authenticated administrator
        
    Returns:
        Success message with enrolled person details
        
    Raises:
        HTTPException: If vision pipeline not ready, no images provided, 
                      no faces detected, or database errors
    """
    global embedder
    logger.info("=== ENROLL_BROWSER_CAMERA START ===")
    
    # Check embedder initialization
    if embedder is None:
        logger.error("Vision pipeline not ready - embedder is None")
        raise HTTPException(status_code=503, detail="Vision pipeline not ready")
    logger.info("Embedder is ready")
    
    try:
        try:
            form_data = await request.form()
        except ClientDisconnect:
            logger.warning("Client disconnected while uploading form data - request may have been cancelled or duplicated")
            raise HTTPException(status_code=499, detail="Client disconnected - request cancelled")
        
        first_name = form_data.get("first_name", "").strip()
        last_name = form_data.get("last_name", "").strip()
        
        if not first_name or not last_name:
            raise HTTPException(status_code=400, detail="first_name and last_name are required")
        
        logger.info(f"Enrolling: {first_name} {last_name}")
        
        # Get uploaded images
        image_files = []
        for key in form_data.keys():
            if key.startswith("image") or key == "images":
                files = form_data.getlist(key)
                image_files.extend(files)
        
        if not image_files:
            raise HTTPException(status_code=400, detail="No images provided")
        
        logger.info(f"Received {len(image_files)} image(s)")
        
        # Save images temporarily and extract embeddings
        out_dir = Path(os.getcwd()) / "enroll_images"
        out_dir.mkdir(parents=True, exist_ok=True)
        
        embs = []
        temp_files = []
        
        for idx, uploaded_file in enumerate(image_files):
            try:
                # Read image data
                image_data = await uploaded_file.read()
                if not image_data:
                    logger.warning(f"Empty image data for file {idx + 1}")
                    continue
                
                # Decode image
                nparr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is None:
                    logger.warning(f"Failed to decode image {idx + 1}")
                    continue
                
                # Save temporarily for debugging
                temp_path = out_dir / f"temp_browser_{idx + 1}.png"
                cv2.imwrite(str(temp_path), frame)
                temp_files.append(temp_path)
                
                # Extract embedding
                logger.info(f"Processing image {idx + 1}/{len(image_files)}")
                try:
                    emb = embedder.get_face_embedding_image(str(temp_path))
                    if emb is not None:
                        embs.append(emb)
                        logger.info(f"Successfully extracted embedding from image {idx + 1}")
                    else:
                        logger.warning(f"No embedding extracted from image {idx + 1} (returned None)")
                except ValueError as e:
                    logger.warning(f"ValueError processing image {idx + 1}: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"Exception processing image {idx + 1}: {type(e).__name__}: {str(e)}", exc_info=True)
                    continue
                    
            except Exception as e:
                logger.error(f"Error processing uploaded file {idx + 1}: {type(e).__name__}: {str(e)}", exc_info=True)
                continue
        
        # Clean up temp files
        for temp_file in temp_files:
            try:
                temp_file.unlink()
            except:
                pass
        
        logger.info(f"Successfully extracted {len(embs)} embedding(s) from {len(image_files)} image(s)")
        
        # Check if we have any valid embeddings
        if not embs:
            logger.error(f"No valid embeddings could be computed from {len(image_files)} uploaded images")
            raise HTTPException(
                status_code=400,
                detail="No face detected in uploaded images. Please ensure you are facing the camera clearly with good lighting."
            )
        
        # Calculate average embedding
        logger.info("Calculating average embedding")
        try:
            avg_emb = calculate_embeddings_avg(embs)
            logger.info(f"Average embedding calculated successfully, shape: {avg_emb.shape}")
        except Exception as e:
            logger.error(f"Error calculating average embedding: {type(e).__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to calculate average embedding: {str(e)}"
            )
        
        # Convert to bytes
        avg = avg_emb.astype(np.float32).tobytes()
        logger.info(f"Embedding converted to bytes, size: {len(avg)} bytes")
        
        # Save embedding to database
        logger.info("Saving embedding to database")
        try:
            created_emb = add_new_emb(Embedding(vector=avg), session)
            logger.info(f"Embedding saved with ID: {created_emb}")
        except Exception as e:
            logger.error(f"Error saving embedding: {type(e).__name__}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to save embedding: {str(e)}")
        
        # Create person record
        logger.info(f"Creating person record: {first_name} {last_name}")
        try:
            person = create_person(
                PersonCreate(first_name=first_name, last_name=last_name, embedding_id=created_emb),
                session
            )
            if person is None:
                logger.error("Failed to create person - create_person returned None")
                raise HTTPException(status_code=500, detail="Failed to create person")
            logger.info(f"Person created successfully with ID: {person.person_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Exception creating person: {type(e).__name__}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to create person: {str(e)}")
        
        logger.info(f"=== ENROLL_BROWSER_CAMERA SUCCESS === Enrolled: {first_name} {last_name}")
        return {
            "message": "Enrolled successfully",
            "person_id": person.person_id,
            "first_name": first_name,
            "last_name": last_name,
        }
        
    except HTTPException:
        raise
    except ClientDisconnect:
        logger.warning("Client disconnected during enrollment process")
        # Return 499 (Client Closed Request) - client cancelled
        raise HTTPException(status_code=499, detail="Client disconnected - enrollment cancelled")
    except Exception as e:
        logger.error(f"Unexpected error in enroll_browser_camera: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/take_attendance")
async def take_attendance(
    request: Request, 
    session: SessionDep, 
    current_user: current_admin_dep
):
    """
    Take attendance by recognizing a face from an uploaded image.
    
    Receives image data, extracts face embedding, matches against database,
    and records attendance if match found and person hasn't been marked today.
    
    Args:
        request: FastAPI request object containing image data in body
        session: Database session dependency
        current_user: Authenticated administrator
        
    Returns:
        Dictionary with attendance record or recognition results
    """
    global embedder
    if embedder is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vision pipeline not ready",
        )
   
    try:
        raw_bytes: bytes = await request.body()
        if not raw_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty frame",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to read request body",
        )

    nparr = np.frombuffer(raw_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image data",
        )
    
    embeddings = get_all(session)
    if not embeddings:
        return {"faces": [], "attendance": {}, "message": "No embeddings found in db"}

    faces = embedder.app.get(frame)

    if len(faces) < 1:
        return {"faces": [], "attendance": {}, "message": "No face detected"}
    
    if len(faces) > 1:
        logger.warning("Multiple faces detected. Using first detected face")

    results = embedder.find_match(face=faces[0], embeddings=embeddings, session=session, threshold=0.65)
    
    if not results or len(results) == 0:
        return {"faces": [], "attendance": {}, "message": "Recognition failed"}

    if not results[0]["matched"]:
        return {"faces": results, "attendance": {}, "message": "Face not recognized"}
    
    person_id = results[0]["person_id"]
    
    if person_id not in seen_today:
        status_id = get_status_id("Present", session)
        if not status_id:
            new_status = add_new_status("Present", session)
            if new_status:
                status_id = new_status.status_id
            else:
                logger.error("Failed to create Present status")
                return {"faces": results, "attendance": {}, "error": "Status not available"}
        
        if not status_id:
            logger.error("Failed to get or create Present status")
            return {"faces": results, "attendance": {}, "error": "Status not available"}
        
        created = add_attendance(
            AttendanceCreate(person_id=person_id, status_id=status_id),
            session,
        )
        
        if created:
            seen_today.add(person_id)
            return {"faces": results, "attendance": created, "message": "Attendance recorded"}
        else:
            logger.error("Failed to record attendance")
            return {"faces": results, "attendance": {}, "error": "Failed to record attendance"}

    return {"faces": results, "attendance": {}, "message": "Already taken attendance today"}
