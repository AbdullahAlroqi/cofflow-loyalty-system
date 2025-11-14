import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cofflow-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'cofflow.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = 86400 * 30  # 30 يوم
    
    # إعدادات رفع الملفات
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
