"""
سكريبت تحديث قاعدة البيانات لإضافة جداول وأعمدة الإشعارات
"""
import sqlite3
import os
from datetime import datetime

def update_database():
    db_path = 'instance/database.db'
    
    # التأكد من وجود مجلد instance
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # الاتصال بقاعدة البيانات
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔄 بدء تحديث قاعدة البيانات...")
        
        # 1. إضافة أعمدة جديدة لجدول users
        print("📝 تحديث جدول المستخدمين...")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN push_subscription TEXT")
            print("✅ تم إضافة عمود push_subscription")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("⚠️ عمود push_subscription موجود مسبقاً")
            else:
                print(f"❌ خطأ في إضافة push_subscription: {e}")
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN allow_notifications BOOLEAN DEFAULT 0")
            print("✅ تم إضافة عمود allow_notifications")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("⚠️ عمود allow_notifications موجود مسبقاً")
            else:
                print(f"❌ خطأ في إضافة allow_notifications: {e}")
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN last_notification_read DATETIME DEFAULT CURRENT_TIMESTAMP")
            print("✅ تم إضافة عمود last_notification_read")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("⚠️ عمود last_notification_read موجود مسبقاً")
            else:
                print(f"❌ خطأ في إضافة last_notification_read: {e}")
        
        # 2. إضافة أعمدة جديدة لجدول settings
        print("📝 تحديث جدول الإعدادات...")
        try:
            cursor.execute("ALTER TABLE settings ADD COLUMN push_public_key TEXT")
            print("✅ تم إضافة عمود push_public_key")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("⚠️ عمود push_public_key موجود مسبقاً")
            else:
                print(f"❌ خطأ في إضافة push_public_key: {e}")
        
        try:
            cursor.execute("ALTER TABLE settings ADD COLUMN push_private_key TEXT")
            print("✅ تم إضافة عمود push_private_key")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("⚠️ عمود push_private_key موجود مسبقاً")
            else:
                print(f"❌ خطأ في إضافة push_private_key: {e}")
        
        # 3. إنشاء جدول الإشعارات
        print("📝 إنشاء جدول الإشعارات...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(100) NOT NULL,
                body TEXT NOT NULL,
                type VARCHAR(50) NOT NULL,
                image_url VARCHAR(255),
                action_url VARCHAR(255),
                is_public BOOLEAN DEFAULT 1,
                created_by INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                scheduled_at DATETIME,
                expire_at DATETIME,
                icon VARCHAR(50) DEFAULT 'bell',
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        """)
        print("✅ تم إنشاء جدول notifications")
        
        # 4. إنشاء جدول العلاقة بين المستخدمين والإشعارات
        print("📝 إنشاء جدول العلاقات...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_notifications (
                user_id INTEGER NOT NULL,
                notification_id INTEGER NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                read_at DATETIME,
                is_sent BOOLEAN DEFAULT 0,
                sent_at DATETIME,
                PRIMARY KEY (user_id, notification_id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (notification_id) REFERENCES notifications (id)
            )
        """)
        print("✅ تم إنشاء جدول user_notifications")
        
        # 5. التأكد من وجود إعدادات افتراضية
        print("📝 التحقق من الإعدادات الافتراضية...")
        cursor.execute("SELECT COUNT(*) FROM settings")
        settings_count = cursor.fetchone()[0]
        
        if settings_count == 0:
            cursor.execute("""
                INSERT INTO settings (cups_required, primary_color, secondary_color, updated_at)
                VALUES (6, '#8B4513', '#D2691E', CURRENT_TIMESTAMP)
            """)
            print("✅ تم إنشاء إعدادات افتراضية")
        else:
            print("⚠️ الإعدادات موجودة مسبقاً")
        
        # حفظ التغييرات
        conn.commit()
        print("✅ تم حفظ جميع التغييرات بنجاح!")
        
        # عرض معلومات الجداول
        print("\n📊 معلومات قاعدة البيانات:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n🎉 تم تحديث قاعدة البيانات بنجاح!")
        
    except Exception as e:
        print(f"❌ خطأ في تحديث قاعدة البيانات: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_database()
