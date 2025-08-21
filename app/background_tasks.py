from datetime import datetime, timezone
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models import ReportStatus
from app.report_generator import generate_report

def generate_report_async(report_id: str):
    """Run report generation in a background thread for the given report_id"""
    print(f"🔄 Starting background report generation for {report_id}")
    
        
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Fetch the report record from DB
        report = session.query(ReportStatus).filter(ReportStatus.report_id == report_id).first()
        
        if report:
            try:
                print(f"📊 Generating actual report for {report_id}...")
                
                # creates the report file
                file_path = generate_report()
                
                # Mark report as complete and update fields
                report.status = "Complete"
                report.completed_at = datetime.now(timezone.utc)
                report.file_path = file_path
                
                session.commit()
                print(f"✅ Background report {report_id} completed! File: {file_path}")
                
            except Exception as e:
                # If report generation fails, mark as Error
                report.status = "Error"
                report.completed_at = datetime.now(timezone.utc)
                session.commit()
                print(f"❌ Background report {report_id} failed: {e}")
        
    except Exception as e:
        print(f"Database error in background task: {e}")
    finally:
        session.close() # close the DB session


