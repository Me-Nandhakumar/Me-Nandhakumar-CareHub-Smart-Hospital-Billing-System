import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'carehub-hospital-secret-key-2026-secure')
    
    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'nandhu@1112')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'hospital')
    
    # SQLite Fallback Path
    SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'carehub.db')
    
    # UPI Payment Configuration
    UPI_ID = os.environ.get('UPI_ID', 'nandhakumar.s.jnandhu-1@okhdfcbank')
    HOSPITAL_NAME = "CareHub Multispeciality Hospital"
    HOSPITAL_PHONE = "+91 98765 43210"
    HOSPITAL_ADDRESS = "104 Healthcare Avenue, Medical District"
