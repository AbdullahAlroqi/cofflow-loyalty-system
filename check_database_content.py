"""
فحص محتوى قاعدة البيانات
"""
import sqlite3
import os

def check_database_content():
    """فحص محتوى قاعدة البيانات"""
    print("🔍 فحص محتوى قاعدة البيانات...")
    
    # فحص جميع ملفات قاعدة البيانات المحتملة
    db_files = [
        'cofflow.db',
        'instance/cofflow.db', 
        'instance/database.db'
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"\n📁 قاعدة البيانات: {db_file}")
            print(f"   الحجم: {os.path.getsize(db_file):,} بايت")
            
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # فحص الجداول
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print(f"   الجداول: {[table[0] for table in tables]}")
                
                # فحص عدد السجلات في كل جدول
                for table in tables:
                    table_name = table[0]
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        print(f"   📊 {table_name}: {count} سجل")
                        
                        # عرض بعض البيانات للجداول المهمة
                        if table_name == 'users' and count > 0:
                            cursor.execute("SELECT id, name, role FROM users LIMIT 5")
                            users = cursor.fetchall()
                            print("      👥 المستخدمون:")
                            for user in users:
                                print(f"         {user[0]}: {user[1]} ({user[2]})")
                                
                        elif table_name == 'coupons' and count > 0:
                            cursor.execute("SELECT id, code, status FROM coupons LIMIT 5")
                            coupons = cursor.fetchall()
                            print("      🎫 الكوبونات:")
                            for coupon in coupons:
                                print(f"         {coupon[0]}: {coupon[1]} ({coupon[2]})")
                                
                    except Exception as e:
                        print(f"   ❌ خطأ في جدول {table_name}: {e}")
                
                conn.close()
                
            except Exception as e:
                print(f"   ❌ خطأ في قراءة قاعدة البيانات: {e}")
        else:
            print(f"❌ {db_file}: غير موجود")

def check_app_database_config():
    """فحص إعدادات قاعدة البيانات في التطبيق"""
    print("\n⚙️ فحص إعدادات قاعدة البيانات في التطبيق...")
    
    try:
        # قراءة ملف config.py
        with open('config.py', 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        print("📄 محتوى config.py:")
        for line_num, line in enumerate(config_content.split('\n'), 1):
            if 'DATABASE_URI' in line or 'sqlite' in line.lower():
                print(f"   {line_num}: {line.strip()}")
        
        # فحص app.py للتأكد من استخدام الإعدادات
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        if 'from config import Config' in app_content:
            print("✅ التطبيق يستخدم إعدادات config.py")
        else:
            print("⚠️ التطبيق قد لا يستخدم إعدادات config.py")
            
    except Exception as e:
        print(f"❌ خطأ في فحص الإعدادات: {e}")

def fix_database_path():
    """إصلاح مسار قاعدة البيانات"""
    print("\n🔧 إصلاح مسار قاعدة البيانات...")
    
    # التحقق من وجود قاعدة البيانات الصحيحة
    if os.path.exists('cofflow.db'):
        size = os.path.getsize('cofflow.db')
        print(f"✅ cofflow.db موجودة ({size:,} بايت)")
        
        # فحص محتواها
        conn = sqlite3.connect('cofflow.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            print(f"✅ قاعدة البيانات تحتوي على {user_count} مستخدم")
            
            # تحديث config.py للتأكد من المسار الصحيح
            config_content = """import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cofflow-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cofflow.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = 86400 * 30  # 30 يوم
    
    # إعدادات رفع الملفات
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
"""
            
            with open('config.py', 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            print("✅ تم تحديث config.py")
            
        else:
            print("⚠️ قاعدة البيانات فارغة")
            
        conn.close()
        
    else:
        print("❌ cofflow.db غير موجودة")

if __name__ == "__main__":
    check_database_content()
    check_app_database_config()
    fix_database_path()
