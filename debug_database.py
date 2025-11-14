"""
تشخيص مشكلة قاعدة البيانات
"""
import sqlite3
import os

def debug_database():
    print("🔍 تشخيص قاعدة البيانات...")
    
    # فحص جميع ملفات قاعدة البيانات
    db_files = ['cofflow.db', 'instance/cofflow.db', 'instance/database.db']
    
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"\n📁 ملف قاعدة البيانات: {db_file}")
            print(f"   الحجم: {os.path.getsize(db_file)} بايت")
            
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # فحص جدول المستخدمين
                cursor.execute("PRAGMA table_info(users)")
                columns = cursor.fetchall()
                
                print(f"   أعمدة جدول المستخدمين:")
                for col in columns:
                    print(f"      {col[1]} ({col[2]})")
                
                # عدد المستخدمين
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                print(f"   عدد المستخدمين: {user_count}")
                
                conn.close()
                
            except Exception as e:
                print(f"   ❌ خطأ في قراءة قاعدة البيانات: {e}")
        else:
            print(f"❌ ملف غير موجود: {db_file}")

def fix_database_schema():
    """إصلاح مخطط قاعدة البيانات"""
    print("\n🔧 إصلاح مخطط قاعدة البيانات...")
    
    db_path = 'cofflow.db'
    
    if not os.path.exists(db_path):
        print("❌ ملف قاعدة البيانات الرئيسي غير موجود")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # إنشاء جدول مستخدمين جديد مع جميع الأعمدة
        print("📝 إنشاء جدول مستخدمين محدث...")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL,
            cups_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            push_subscription TEXT,
            last_notification_read DATETIME,
            allow_notifications BOOLEAN DEFAULT 1,
            notifications_enabled BOOLEAN DEFAULT 1
        )
        """)
        
        # نسخ البيانات من الجدول القديم
        print("📋 نسخ البيانات من الجدول القديم...")
        
        cursor.execute("""
        INSERT INTO users_new (id, name, phone, email, password_hash, role, cups_count, created_at)
        SELECT id, name, phone, email, password_hash, role, cups_count, created_at
        FROM users
        """)
        
        # حذف الجدول القديم وإعادة تسمية الجديد
        print("🔄 استبدال الجدول القديم...")
        
        cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        
        conn.commit()
        print("✅ تم إصلاح مخطط قاعدة البيانات بنجاح")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إصلاح المخطط: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    debug_database()
    
    print("\n" + "="*50)
    response = input("هل تريد إصلاح مخطط قاعدة البيانات؟ (y/n): ")
    
    if response.lower() == 'y':
        if fix_database_schema():
            print("\n🎉 تم الإصلاح بنجاح!")
            debug_database()  # فحص مرة أخرى
        else:
            print("\n❌ فشل في الإصلاح")
