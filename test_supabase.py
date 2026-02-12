import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_BUCKET = "member-photos"

def test_supabase():
    print("--- Supabase Connectivity Test ---")
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("ERROR: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in environment.")
        return

    try:
        print(f"Connecting to: {SUPABASE_URL}")
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        print("Fetching buckets...")
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        print(f"Available buckets: {bucket_names}")
        
        if SUPABASE_BUCKET in bucket_names:
            print(f"SUCCESS: Bucket '{SUPABASE_BUCKET}' found and accessible.")
        else:
            print(f"WARNING: Bucket '{SUPABASE_BUCKET}' not found.")
            print(f"Please ensure you have created a PUBLIC bucket named '{SUPABASE_BUCKET}' in your Supabase project.")
            
    except Exception as e:
        print(f"ERROR: Supabase connection failed: {e}")

if __name__ == "__main__":
    test_supabase()
