"""
سكريبت تحديث قاعدة البيانات الأصلية مع الحفاظ على البيانات الموجودة
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash

def update_existing_database():
    print("🔄 بدء تحديث قاعدة البيانات الأصلية...")
    
    # التحقق من وجود قاعدة البيانات الأصلية
    original_db = 'cofflow.db'
    instance_db = 'instance/cofflow.db'
    
    # إذا كانت قاعدة البيانات في مجلد instance، انقلها للمجلد الرئيسي
    if os.path.exists(instance_db) and not os.path.exists(original_db):
        import shutil
        shutil.copy2(instance_db, original_db)
        print("✅ تم نقل قاعدة البيانات من مجلد instance")
    
    if not os.path.exists(original_db):
        print("❌ قاعدة البيانات الأصلية غير موجودة!")
        return
    
    # الاتصال بقاعدة البيانات
    conn = sqlite3.connect(original_db)
    cursor = conn.cursor()
    
    try:
        print("📊 فحص الجداول الموجودة...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"الجداول الموجودة: {existing_tables}")
        
        # تحديث جدول المستخدمين
        if 'users' in existing_tables:
            print("📝 تحديث جدول المستخدمين...")
            
            # إضافة الأعمدة الجديدة إذا لم تكن موجودة
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'push_subscription' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN push_subscription TEXT")
                print("✅ تم إضافة عمود push_subscription")
            
            if 'allow_notifications' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN allow_notifications BOOLEAN DEFAULT 0")
                print("✅ تم إضافة عمود allow_notifications")
            
            if 'last_notification_read' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN last_notification_read DATETIME DEFAULT CURRENT_TIMESTAMP")
                print("✅ تم إضافة عمود last_notification_read")
        
        # تحديث جدول الإعدادات
        if 'settings' in existing_tables:
            print("📝 تحديث جدول الإعدادات...")
            
            cursor.execute("PRAGMA table_info(settings)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'push_public_key' not in columns:
                cursor.execute("ALTER TABLE settings ADD COLUMN push_public_key TEXT")
                print("✅ تم إضافة عمود push_public_key")
            
            if 'push_private_key' not in columns:
                cursor.execute("ALTER TABLE settings ADD COLUMN push_private_key TEXT")
                print("✅ تم إضافة عمود push_private_key")
        
        # إنشاء جدول الإشعارات إذا لم يكن موجوداً
        if 'notifications' not in existing_tables:
            print("📝 إنشاء جدول الإشعارات...")
            cursor.execute("""
                CREATE TABLE notifications (
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
        
        # إنشاء جدول العلاقة بين المستخدمين والإشعارات
        if 'user_notifications' not in existing_tables:
            print("📝 إنشاء جدول العلاقات...")
            cursor.execute("""
                CREATE TABLE user_notifications (
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
        
        # التأكد من وجود حساب مدير
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print("📝 إنشاء حساب مدير افتراضي...")
            admin_password = generate_password_hash('admin123')
            cursor.execute("""
                INSERT INTO users (name, phone, email, password_hash, role, created_at)
                VALUES ('المدير', 'admin', 'admin@cofflow.com', ?, 'admin', CURRENT_TIMESTAMP)
            """, (admin_password,))
            print("✅ تم إنشاء حساب المدير: admin / admin123")
        else:
            print(f"ℹ️ يوجد {admin_count} حساب مدير")
        
        # التأكد من وجود إعدادات
        if 'settings' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM settings")
            settings_count = cursor.fetchone()[0]
            
            if settings_count == 0:
                cursor.execute("""
                    INSERT INTO settings (cups_required, primary_color, secondary_color, updated_at)
                    VALUES (6, '#8B4513', '#D2691E', CURRENT_TIMESTAMP)
                """)
                print("✅ تم إنشاء إعدادات افتراضية")
            else:
                print(f"ℹ️ يوجد {settings_count} إعداد")
        
        # حفظ التغييرات
        conn.commit()
        
        # عرض إحصائيات البيانات
        print("\n📊 إحصائيات قاعدة البيانات:")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        print(f"  👥 المستخدمون: {users_count}")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'customer'")
        customers_count = cursor.fetchone()[0]
        print(f"  🛍️ العملاء: {customers_count}")
        
        if 'coupons' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM coupons")
            coupons_count = cursor.fetchone()[0]
            print(f"  🎫 الكوبونات: {coupons_count}")
        
        if 'transactions' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM transactions")
            transactions_count = cursor.fetchone()[0]
            print(f"  💳 المعاملات: {transactions_count}")
        
        print("\n🎉 تم تحديث قاعدة البيانات بنجاح مع الحفاظ على جميع البيانات!")
        
    except Exception as e:
        print(f"❌ خطأ في تحديث قاعدة البيانات: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_existing_database()
