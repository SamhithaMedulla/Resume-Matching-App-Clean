try:
    client = pymongo.MongoClient(MONGODB_URI)
    db = client["resume_screening"]
    resumes_collection = db["resumes"]
    jobs_collection = db["jobs"]
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")
    raise HTTPException(status_code=500, detail=f"Database connection error: {e}")



