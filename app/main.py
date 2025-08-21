from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import uuid
import os
import threading

from app.database import get_db, create_tables
from app.models import ReportStatus

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize db tables when app starts
    create_tables()
    print("✅ Database tables ready!")
    yield
    # On shutdown 
    print("🔄 Shutting down...")

# FastAPI app config with lifespan hooks
app = FastAPI(
    title="Store Monitoring API",
    description="API for generating store uptime/downtime reports",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint for checking if API is running"""
    return {
        "message": "Store Monitoring API is running!",
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc)
    }

@app.post("/trigger_report")
async def trigger_report(db: Session = Depends(get_db)):
    """
    Start report generation in background
    Returns: report_id 
    """
    try:
        report_id = str(uuid.uuid4())    # Generate unique ID 
  
        # Insert initial report status in DB
        report_status = ReportStatus(
            report_id=report_id,
            status="Running",
            created_at=datetime.now(timezone.utc)
        )
        db.add(report_status)
        db.commit()
        
        # Import here to avoid circular dependency
        from app.background_tasks import generate_report_async
        
        # Run report generation in a background thread
        thread = threading.Thread(target=generate_report_async, args=(report_id,))
        thread.daemon = True
        thread.start()
        
        print(f"📊 Report {report_id} generation started in background...")
        
        # Return immediately without waiting for the report
        return {
            "report_id": report_id,
            "status": "Running",
            "message": "Report generation started"
        }
        
    except Exception as e:
        print(f"Error triggering report: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger report generation")


@app.get("/get_report")
async def get_report(report_id: str, db: Session = Depends(get_db)):
    """
    Get report status or download it if completed
    """
    try:
        report = db.query(ReportStatus).filter(ReportStatus.report_id == report_id).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        if report.status == "Running":
            return {
                "report_id": report_id,
                "status": "Running",
                "message": "Report generation in progress..."
            }
        
        elif report.status == "Complete":
            if report.file_path and os.path.exists(report.file_path):
                from fastapi.responses import FileResponse
                # Send CSV file for download
                return FileResponse(
                    path=report.file_path,
                    filename=f"store_report_{report_id}.csv",
                    media_type="text/csv"
                )
            else:
                return {
                    "report_id": report_id,
                    "status": "Error", 
                    "message": "Report completed but file not found"
                }
        
        else:
            return {
                "report_id": report_id,
                "status": "Error",
                "message": "Report generation failed"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get report status")


@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}









