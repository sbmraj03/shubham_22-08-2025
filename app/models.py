from sqlalchemy import Column, String, DateTime, Integer, Time
from sqlalchemy.ext.declarative import declarative_base

# Base class for all the models
Base = declarative_base()

class StoreStatus(Base):
    """
    Table to store the status of each store at a given timestamp.
    status = 'active' or 'inactive'
    """
    __tablename__ = "store_status"
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # unique id for each row
    store_id = Column(String, nullable=False, index=True)  # store identifier
    status = Column(String, nullable=False)  # whether store is active/inactive
    timestamp_utc = Column(DateTime, nullable=False, index=True)  # time of status update in UTC


class BusinessHours(Base):
    """
    Table to store local business hours of each store.
    Each row represents a day's opening and closing time.
    """
    __tablename__ = "business_hours"
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # unique id for each row
    store_id = Column(String, nullable=False, index=True)  # store identifier
    day_of_week = Column(Integer, nullable=False)  # 0 = Monday, ..., 6 = Sunday
    start_time_local = Column(Time, nullable=False)  # opening time (local time)
    end_time_local = Column(Time, nullable=False)  # closing time (local time)


class StoreTimezone(Base):
    """
    Table to store timezone info of each store.
    This helps in converting UTC timestamps to store's local time.
    """
    __tablename__ = "store_timezone"
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # unique id for each row
    store_id = Column(String, nullable=False, unique=True, index=True)  # store identifier
    timezone_str = Column(String, nullable=False)  # timezone string (eg -> "America/Chicago")


class ReportStatus(Base):
    """
    Table to track report generation jobs.
    Stores the current status and file path if the report is ready.
    """
    __tablename__ = "report_status"
    
    report_id = Column(String, primary_key=True)  # unique report identifier (UUID)
    status = Column(String, nullable=False)  # Running / Complete / Error
    created_at = Column(DateTime, nullable=False)  # when report job started
    completed_at = Column(DateTime, nullable=True)  # when report finished
    file_path = Column(String, nullable=True)  # path to generated report file
