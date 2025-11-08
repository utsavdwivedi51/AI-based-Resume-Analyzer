import streamlit as st
from typing import Optional, Dict
from database import Database

class AuthManager:
    def __init__(self, db: Database):
        self.db = db
        
        # Initialize session state
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'user' not in st.session_state:
            st.session_state.user = None
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate user and create session"""
        user = self.db.authenticate_user(username, password)
        
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            return True
        return False
    
    def logout(self):
        """Clear session and logout user"""
        st.session_state.logged_in = False
        st.session_state.user = None
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return st.session_state.logged_in
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current logged in user"""
        return st.session_state.user if self.is_logged_in() else None
    
    def is_student(self) -> bool:
        """Check if current user is a student"""
        user = self.get_current_user()
        return user and user['role'] == 'student'
    
    def is_teacher(self) -> bool:
        """Check if current user is a teacher"""
        user = self.get_current_user()
        return user and user['role'] == 'teacher'
    
    def require_login(self):
        """Decorator-like function to require login"""
        if not self.is_logged_in():
            st.warning("⚠️ Please login to access this page")
            st.stop()
    
    def require_teacher(self):
        """Require teacher role"""
        self.require_login()
        if not self.is_teacher():
            st.error("🚫 Access Denied: Teacher privileges required")
            st.stop()
    
    def require_student(self):
        """Require student role"""
        self.require_login()
        if not self.is_student():
            st.error("🚫 Access Denied: Student privileges required")
            st.stop()
    
    def render_login_page(self):
        """Render login page UI"""
        st.markdown("""
        <h1 style='text-align: center;'>🎓 Attendance ERP System</h1>
        <p style='text-align: center;'>Please login to continue</p>
        <hr>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### 🔐 Login")
            
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("🚀 Login", use_container_width=True):
                    if not username or not password:
                        st.error("❌ Please enter both username and password")
                    else:
                        if self.login(username, password):
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
            
            with col_btn2:
                if st.button("ℹ️ Demo Credentials", use_container_width=True):
                    st.info("""
                    **Student Login:**
                    - Username: `student1` / Password: `student123`
                    - Username: `student2` / Password: `student123`
                    
                    **Teacher Login:**
                    - Username: `teacher1` / Password: `teacher123`
                    """)
    
    def render_sidebar_user_info(self):
        """Render user info in sidebar"""
        if self.is_logged_in():
            user = self.get_current_user()
            
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 👤 User Info")
            st.sidebar.markdown(f"**Name:** {user['name']}")
            st.sidebar.markdown(f"**Role:** {user['role'].title()}")
            
            if user['role'] == 'student':
                st.sidebar.markdown(f"**Student ID:** {user['student_id']}")
            
            st.sidebar.markdown("---")
            
            if st.sidebar.button("🚪 Logout", use_container_width=True):
                self.logout()
                st.rerun()
