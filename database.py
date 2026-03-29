import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class Database:
    def __init__(self, db_name: str = "attendance.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Create and return a database connection"""
        return sqlite3.connect(self.db_name, check_same_thread=False)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'teacher')),
                name TEXT NOT NULL,
                student_id TEXT UNIQUE,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                date DATE NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Present', 'Absent', 'Late')),
                subject TEXT NOT NULL,
                marked_by TEXT NOT NULL,
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES users(student_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, username: str, password: str, role: str, name: str, 
                   student_id: str = None, email: str = None) -> bool:
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            hashed_password = self.hash_password(password)
            
            cursor.execute("""
                INSERT INTO users (username, password, role, name, student_id, email)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, hashed_password, role, name, student_id, email))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed_password = self.hash_password(password)
        
        cursor.execute("""
            SELECT id, username, role, name, student_id, email
            FROM users
            WHERE username = ? AND password = ?
        """, (username, hashed_password))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'role': result[2],
                'name': result[3],
                'student_id': result[4],
                'email': result[5]
            }
        return None
    
    def get_all_students(self) -> List[Dict]:
        """Get all students"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, name, student_id, email
            FROM users
            WHERE role = 'student'
            ORDER BY name
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'username': row[1],
                'name': row[2],
                'student_id': row[3],
                'email': row[4]
            }
            for row in results
        ]
    
    def get_student_by_id(self, student_id: str) -> Optional[Dict]:
        """Get student by student_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, name, student_id, email
            FROM users
            WHERE student_id = ? AND role = 'student'
        """, (student_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'name': result[2],
                'student_id': result[3],
                'email': result[4]
            }
        return None
    
    # ==================== ATTENDANCE OPERATIONS ====================
    
    def mark_attendance(self, student_id: str, date: str, status: str, 
                       subject: str, marked_by: str, remarks: str = None) -> bool:
        """Mark attendance for a student"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if attendance already exists for this date and subject
            cursor.execute("""
                SELECT id FROM attendance
                WHERE student_id = ? AND date = ? AND subject = ?
            """, (student_id, date, subject))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing attendance
                cursor.execute("""
                    UPDATE attendance
                    SET status = ?, marked_by = ?, remarks = ?
                    WHERE id = ?
                """, (status, marked_by, remarks, existing[0]))
            else:
                # Insert new attendance
                cursor.execute("""
                    INSERT INTO attendance (student_id, date, status, subject, marked_by, remarks)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (student_id, date, status, subject, marked_by, remarks))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking attendance: {e}")
            return False
    
    def get_student_attendance(self, student_id: str, 
                              start_date: str = None, 
                              end_date: str = None) -> List[Dict]:
        """Get attendance records for a specific student"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT a.id, a.student_id, a.date, a.status, a.subject, 
                   a.marked_by, a.remarks, u.name
            FROM attendance a
            JOIN users u ON a.student_id = u.student_id
            WHERE a.student_id = ?
        """
        params = [student_id]
        
        if start_date:
            query += " AND a.date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND a.date <= ?"
            params.append(end_date)
        
        query += " ORDER BY a.date DESC, a.subject"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'student_id': row[1],
                'date': row[2],
                'status': row[3],
                'subject': row[4],
                'marked_by': row[5],
                'remarks': row[6],
                'student_name': row[7]
            }
            for row in results
        ]
    
    def get_all_attendance(self, start_date: str = None, 
                          end_date: str = None,
                          subject: str = None) -> List[Dict]:
        """Get all attendance records (for teachers)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT a.id, a.student_id, a.date, a.status, a.subject, 
                   a.marked_by, a.remarks, u.name
            FROM attendance a
            JOIN users u ON a.student_id = u.student_id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND a.date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND a.date <= ?"
            params.append(end_date)
        
        if subject:
            query += " AND a.subject = ?"
            params.append(subject)
        
        query += " ORDER BY a.date DESC, u.name"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'student_id': row[1],
                'date': row[2],
                'status': row[3],
                'subject': row[4],
                'marked_by': row[5],
                'remarks': row[6],
                'student_name': row[7]
            }
            for row in results
        ]
    
    def get_attendance_statistics(self, student_id: str) -> Dict:
        """Get attendance statistics for a student"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present,
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent,
                SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) as late
            FROM attendance
            WHERE student_id = ?
        """, (student_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        total = result[0] or 0
        present = result[1] or 0
        absent = result[2] or 0
        late = result[3] or 0
        
        attendance_percentage = (present / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'percentage': round(attendance_percentage, 2)
        }
    
    def get_subject_wise_statistics(self, student_id: str) -> List[Dict]:
        """Get subject-wise attendance statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                subject,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present,
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent,
                SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) as late
            FROM attendance
            WHERE student_id = ?
            GROUP BY subject
            ORDER BY subject
        """, (student_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        stats = []
        for row in results:
            total = row[1] or 0
            present = row[2] or 0
            percentage = (present / total * 100) if total > 0 else 0
            
            stats.append({
                'subject': row[0],
                'total': total,
                'present': present,
                'absent': row[3] or 0,
                'late': row[4] or 0,
                'percentage': round(percentage, 2)
            })
        
        return stats
    
    def get_all_subjects(self) -> List[str]:
        """Get list of all subjects"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT subject
            FROM attendance
            ORDER BY subject
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in results]
    
    def delete_attendance(self, attendance_id: int) -> bool:
        """Delete an attendance record"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM attendance WHERE id = ?", (attendance_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting attendance: {e}")
            return False
