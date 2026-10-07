import sqlite3
import pymysql
from pymysql.cursors import DictCursor
import os
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global flag to track active backend
ACTIVE_DB_TYPE = "mysql"

def get_connection():
    """
    Attempts to connect to MySQL first.
    If MySQL connection fails or server is unreachable, falls back to SQLite.
    """
    global ACTIVE_DB_TYPE
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=DictCursor,
            connect_timeout=3,
            autocommit=True
        )
        ACTIVE_DB_TYPE = "mysql"
        return conn, "mysql"
    except Exception as e:
        logger.warning(f"MySQL connection not available ({e}). Falling back to SQLite at {Config.SQLITE_DB_PATH}")
        conn = sqlite3.connect(Config.SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        ACTIVE_DB_TYPE = "sqlite"
        return conn, "sqlite"

def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Executes a SQL query adjusting placeholders (%s for MySQL, ? for SQLite)
    and returns results as dictionaries.
    """
    conn, db_type = get_connection()
    try:
        # Convert parameter placeholders if needed
        if db_type == "sqlite":
            formatted_query = query.replace('%s', '?')
        else:
            formatted_query = query

        cursor = conn.cursor()
        if params:
            cursor.execute(formatted_query, params)
        else:
            cursor.execute(formatted_query)

        if commit or db_type == "sqlite":
            conn.commit()

        if fetchone:
            row = cursor.fetchone()
            if row is None:
                return None
            return dict(row)

        if fetchall:
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

        if hasattr(cursor, 'lastrowid'):
            return cursor.lastrowid
        return True
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass

def init_db():
    """
    Initializes database tables for patients, appointments, and doctors.
    """
    conn, db_type = get_connection()
    try:
        cursor = conn.cursor()
        
        if db_type == "mysql":
            # Ensure database exists
            cursor.execute("CREATE DATABASE IF NOT EXISTS hospital;")
            cursor.execute("USE hospital;")

            # MySQL schemas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INT NOT NULL,
                gender VARCHAR(15) NOT NULL,
                weight INT NOT NULL,
                contact VARCHAR(15) NOT NULL,
                symptoms TEXT NOT NULL,
                medicines TEXT NOT NULL,
                total_amount INT NOT NULL,
                payment_mode VARCHAR(20) NOT NULL DEFAULT 'Cash',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_name VARCHAR(100) NOT NULL,
                appoint_date DATE NOT NULL,
                appoint_time VARCHAR(20) NOT NULL,
                doctor VARCHAR(100) NOT NULL,
                contact VARCHAR(15),
                status VARCHAR(20) DEFAULT 'Scheduled',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # Safe column additions if table previously created with other names
            try:
                cursor.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS appoint_date DATE;")
                cursor.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS appoint_time VARCHAR(20);")
                cursor.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS notes TEXT;")
                cursor.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS contact VARCHAR(15);")
                cursor.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'Scheduled';")
            except:
                pass

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                specialization VARCHAR(100) NOT NULL,
                available_days VARCHAR(100) DEFAULT 'Mon-Sat',
                room_no VARCHAR(20) DEFAULT 'Room 101'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            conn.commit()
        else:
            # SQLite schemas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                weight INTEGER NOT NULL,
                contact TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                medicines TEXT NOT NULL,
                total_amount INTEGER NOT NULL,
                payment_mode TEXT NOT NULL DEFAULT 'Cash',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                appoint_date TEXT NOT NULL,
                appoint_time TEXT NOT NULL,
                doctor TEXT NOT NULL,
                contact TEXT,
                status TEXT DEFAULT 'Scheduled',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                available_days TEXT DEFAULT 'Mon-Sat',
                room_no TEXT DEFAULT 'Room 101'
            )
            """)
            conn.commit()

        # Seed default doctors if empty
        cursor.execute("SELECT COUNT(*) as count FROM doctors")
        res = cursor.fetchone()
        count = res['count'] if isinstance(res, dict) else res[0]
        if count == 0:
            default_doctors = [
                ("Dr. Rajesh Sharma", "General Physician", "Mon-Sat", "Cabin A-101"),
                ("Dr. Ananya Iyer", "Cardiologist", "Mon-Fri", "Cabin B-204"),
                ("Dr. Vikram Patil", "Pediatrician", "Tue-Sun", "Cabin A-105"),
                ("Dr. Priya Menon", "Dermatologist & Allergist", "Mon-Sat", "Cabin C-302"),
                ("Dr. Suresh Kumar", "Orthopedic Surgeon", "Mon-Fri", "Cabin D-401")
            ]
            for doc in default_doctors:
                if db_type == "sqlite":
                    cursor.execute("INSERT INTO doctors (name, specialization, available_days, room_no) VALUES (?, ?, ?, ?)", doc)
                else:
                    cursor.execute("INSERT INTO doctors (name, specialization, available_days, room_no) VALUES (%s, %s, %s, %s)", doc)
            conn.commit()

        logger.info(f"Database initialized successfully using [{db_type.upper()}] backend.")
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

if __name__ == "__main__":
    init_db()
