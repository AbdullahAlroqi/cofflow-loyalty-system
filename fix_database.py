"""
سكريبت إصلاح قاعدة البيانات بطريقة مبسطة
"""
import sqlite3
import os
from datetime import datetime

def fix_database():
    print("🔧 بدء إصلاح قاعدة البيانات...")
    
    # التأكد من وجود مجلد instance
    if not os.path.exists('instance'):
        os.makedirs('instance')
        print("✅ تم إنشاء مجلد instance")
    
    db_path = 'instance/database.db'
    
    # حذف قاعدة البيانات القديمة إن وجدت
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️ تم حذف قاعدة البيانات القديمة")
    
    # إنشاء قاعدة بيانات جديدة
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. إنشاء جدول المستخدمين
        print("📝 إنشاء جدول المستخدمين...")
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL,
                cups_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                push_subscription TEXT,
                allow_notifications BOOLEAN DEFAULT 0,
                last_notification_read DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ تم إنشاء جدول users")
        
        # 2. إنشاء جدول الكوبونات
        print("📝 إنشاء جدول الكوبونات...")
        cursor.execute("""
            CREATE TABLE coupons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                code VARCHAR(20) UNIQUE NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                used_at DATETIME,
                used_by INTEGER,
                FOREIGN KEY (customer_id) REFERENCES users (id),
                FOREIGN KEY (used_by) REFERENCES users (id)
            )
        """)
        print("✅ تم إنشاء جدول coupons")
        
        # 3. إنشاء جدول المعاملات
        print("📝 إنشاء جدول المعاملات...")
        cursor.execute("""
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                employee_id INTEGER NOT NULL,
                transaction_type VARCHAR(50) NOT NULL,
                description VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES users (id),
                FOREIGN KEY (employee_id) REFERENCES users (id)
            )
        """)
        print("✅ تم إنشاء جدول transactions")
        
        # 4. إنشاء جدول الإعدادات
        print("📝 إنشاء جدول الإعدادات...")
        cursor.execute("""
            CREATE TABLE settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cups_required INTEGER DEFAULT 6,
                logo_path VARCHAR(255),
                primary_color VARCHAR(7) DEFAULT '#8B4513',
                secondary_color VARCHAR(7) DEFAULT '#D2691E',
                push_public_key TEXT,
                push_private_key TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ تم إنشاء جدول settings")
        
        # 5. إنشاء جدول الإشعارات
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
        
        # 6. إنشاء جدول العلاقة بين المستخدمين والإشعارات
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
        
        # 7. إدراج البيانات الافتراضية
        print("📝 إدراج البيانات الافتراضية...")
        
        # إعدادات افتراضية
        cursor.execute("""
            INSERT INTO settings (cups_required, primary_color, secondary_color, updated_at)
            VALUES (6, '#8B4513', '#D2691E', CURRENT_TIMESTAMP)
        """)
        print("✅ تم إدراج الإعدادات الافتراضية")
        
        # مستخدم مدير افتراضي
        from werkzeug.security import generate_password_hash
        admin_password = generate_password_hash('admin123')
        
        cursor.execute("""
            INSERT INTO users (name, phone, email, password_hash, role, created_at)
            VALUES ('المدير', 'admin', 'admin@cofflow.com', ?, 'admin', CURRENT_TIMESTAMP)
        """, (admin_password,))
        print("✅ تم إنشاء حساب المدير")
        
        # حفظ التغييرات
        conn.commit()
        print("✅ تم حفظ جميع التغييرات")
        
        print("\n🎉 تم إصلاح قاعدة البيانات بنجاح!")
        print("📋 معلومات الدخول:")
        print("   المدير: admin / admin123")
        
    except Exception as e:
        print(f"❌ خطأ في إصلاح قاعدة البيانات: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()
