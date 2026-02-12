import os
import uuid
from fastapi import UploadFile, HTTPException
from pathlib import Path
from PIL import Image
import io
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

UPLOAD_DIR = Path(__file__).parent / "static" / "photos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Supabase Storage Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_BUCKET = "member-photos"

supabase_client: Client = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print(f"Supabase storage client initialized with URL: {SUPABASE_URL}")
        
        # Verify bucket access
        try:
            buckets = supabase_client.storage.list_buckets()
            bucket_names = [b.name for b in buckets]
            if SUPABASE_BUCKET not in bucket_names:
                print(f"WARNING: Supabase bucket '{SUPABASE_BUCKET}' not found. Available buckets: {bucket_names}")
            else:
                print(f"Verified access to Supabase bucket: {SUPABASE_BUCKET}")
        except Exception as bucket_err:
            print(f"Could not verify Supabase buckets: {bucket_err}")
            
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
else:
    print("Supabase credentials missing. Falling back to local storage.")


async def save_upload_file(upload_file: UploadFile) -> str:
    """
    Save uploaded file and return the file path or URL
    """
    # Validate file extension
    file_ext = Path(upload_file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    contents = await upload_file.read()
    
    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Validate it's actually an image
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # --- PROD: Supabase Storage ---
    if supabase_client:
        try:
            # Upload to Supabase
            print(f"Attempting Supabase upload to bucket: {SUPABASE_BUCKET}")
            response = supabase_client.storage.from_(SUPABASE_BUCKET).upload(
                path=unique_filename,
                file=contents,
                file_options={"content-type": upload_file.content_type}
            )
            
            # The supabase-py client sometimes returns the path in the response
            # or might raise an exception if it fails.
            
            # Get Public URL
            public_url = supabase_client.storage.from_(SUPABASE_BUCKET).get_public_url(unique_filename)
            print(f"File uploaded to Supabase successfully: {public_url}")
            return public_url
        except Exception as e:
            print(f"Supabase upload failed: {e}")
            print(f"Falling back to local storage for: {unique_filename}")
            # Fallback to local if upload fails

    # --- DEV/FALLBACK: Local Storage ---
    file_path = UPLOAD_DIR / unique_filename
    with open(file_path, "wb") as f:
        f.write(contents)
    
    return f"static/photos/{unique_filename}"


def delete_file(photo_path: str):
    """Delete a file if it exists (handles both Local paths and Supabase URLs)"""
    if not photo_path:
        return
        
    # --- Case 1: Supabase URL ---
    if photo_path.startswith("http") and "supabase" in photo_path:
        if not supabase_client:
            print("Supabase client not initialized, cannot delete cloud file.")
            return
            
        try:
            # Extract filename from URL (it's the last part)
            filename = photo_path.split("/")[-1]
            supabase_client.storage.from_(SUPABASE_BUCKET).remove([filename])
            print(f"Successfully deleted photo from Supabase: {filename}")
        except Exception as e:
            print(f"Error deleting from Supabase: {e}")
        return

    # --- Case 2: Local Path ---
    # extract filename from path like "static/photos/filename.jpg"
    filename = os.path.basename(photo_path)
    full_path = UPLOAD_DIR / filename
    
    try:
        if full_path.exists():
            os.remove(full_path)
            print(f"Successfully deleted photo from disk: {full_path}")
    except Exception as e:
        print(f"Error deleting file {full_path}: {e}")
