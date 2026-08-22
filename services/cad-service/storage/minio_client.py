class MinioClient:
    """
    Mock MinIO client for demo purposes.
    In a real system, this would upload to an S3-compatible bucket and return signed URLs.
    """
    def __init__(self, endpoint: str = "localhost:9000"):
        self.endpoint = endpoint
        
    def upload_file(self, bucket: str, object_name: str, file_path: str) -> str:
        # Pretend we uploaded it
        pass
        
    def get_presigned_url(self, bucket: str, object_name: str) -> str:
        # For the local demo, we're serving straight from the FastAPI static mount
        return f"/api/v1/cad/download/{object_name}"
