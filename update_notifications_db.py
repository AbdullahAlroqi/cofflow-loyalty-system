"""
سكريبت تحديث قاعدة البيانات لدعم نظام الإشعارات المتقدم
"""
import sqlite3
import os
from datetime import datetime

def update_database_for_notifications():
    print("🔔 تحديث قاعدة البيانات لدعم الإشعارات...")
    
    db_path = 'cofflow.db'
    if not os.path.exists(db_path):
        print("❌ ملف قاعدة البيانات غير موجود")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. إضافة حقول الإشعارات لجدول المستخدمين
        print("📝 إضافة حقول الإشعارات لجدول المستخدمين...")
        
        # التحقق من وجود الأعمدة أولاً
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'push_subscription' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN push_subscription TEXT")
            print("   ✅ تم إضافة عمود push_subscription")
        
        if 'last_notification_read' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN last_notification_read DATETIME")
            print("   ✅ تم إضافة عمود last_notification_read")
        
        if 'notifications_enabled' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN notifications_enabled BOOLEAN DEFAULT 1")
            print("   ✅ تم إضافة عمود notifications_enabled")
        
        # 2. إضافة حقول الإشعارات لجدول الإعدادات
        print("📝 إضافة حقول الإشعارات لجدول الإعدادات...")
        
        cursor.execute("PRAGMA table_info(settings)")
        settings_columns = [column[1] for column in cursor.fetchall()]
        
        if 'push_public_key' not in settings_columns:
            cursor.execute("ALTER TABLE settings ADD COLUMN push_public_key TEXT")
            print("   ✅ تم إضافة عمود push_public_key")
        
        if 'push_private_key' not in settings_columns:
            cursor.execute("ALTER TABLE settings ADD COLUMN push_private_key TEXT")
            print("   ✅ تم إضافة عمود push_private_key")
        
        if 'notifications_enabled' not in settings_columns:
            cursor.execute("ALTER TABLE settings ADD COLUMN notifications_enabled BOOLEAN DEFAULT 1")
            print("   ✅ تم إضافة عمود notifications_enabled للإعدادات")
        
        # 3. إنشاء جدول الإشعارات
        print("📝 إنشاء جدول الإشعارات...")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            body TEXT NOT NULL,
            type VARCHAR(50) NOT NULL DEFAULT 'general',
            image_url VARCHAR(500),
            action_url VARCHAR(500),
            is_public BOOLEAN DEFAULT 1,
            creator_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            scheduled_at DATETIME,
            expires_at DATETIME,
            icon VARCHAR(100) DEFAULT 'bell',
            FOREIGN KEY (creator_id) REFERENCES users (id)
        )
        """)
        print("   ✅ تم إنشاء جدول notifications")
        
        # 4. إنشاء جدول ربط المستخدمين بالإشعارات
        print("📝 إنشاء جدول ربط المستخدمين بالإشعارات...")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_notifications (
            user_id INTEGER NOT NULL,
            notification_id INTEGER NOT NULL,
            read_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, notification_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (notification_id) REFERENCES notifications (id)
        )
        """)
        print("   ✅ تم إنشاء جدول user_notifications")
        
        # 5. إنشاء إشعارات تجريبية
        print("📝 إنشاء إشعارات تجريبية...")
        
        # الحصول على المدير
        cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
        admin = cursor.fetchone()
        
        if admin:
            admin_id = admin[0]
            
            # إشعارات تجريبية
            sample_notifications = [
                {
                    'title': '🎉 مرحباً بكم في نظام الإشعارات!',
                    'body': 'تم تفعيل نظام الإشعارات بنجاح. ستصلكم الآن جميع العروض والتحديثات.',
                    'type': 'news',
                    'icon': 'celebration'
                },
                {
                    'title': '☕ عرض خاص: كوب مجاني!',
                    'body': 'احصل على كوب قهوة مجاني عند شراء 5 أكواب. العرض ساري لمدة أسبوع.',
                    'type': 'offer',
                    'icon': 'local_cafe'
                },
                {
                    'title': '🔔 تذكير: نقاط الولاء',
                    'body': 'لا تنسوا استخدام نقاط الولاء المتراكمة للحصول على مشروبات مجانية.',
                    'type': 'alert',
                    'icon': 'loyalty'
                }
            ]
            
            for notification in sample_notifications:
                cursor.execute("""
                INSERT INTO notifications (title, body, type, icon, creator_id, is_public)
                VALUES (?, ?, ?, ?, ?, 1)
                """, (
                    notification['title'],
                    notification['body'],
                    notification['type'],
                    notification['icon'],
                    admin_id
                ))
            
            print(f"   ✅ تم إنشاء {len(sample_notifications)} إشعارات تجريبية")
        
        # 6. ربط الإشعارات بجميع العملاء
        print("📝 ربط الإشعارات بالعملاء...")
        
        cursor.execute("SELECT id FROM users WHERE role = 'customer'")
        customers = cursor.fetchall()
        
        cursor.execute("SELECT id FROM notifications")
        notifications = cursor.fetchall()
        
        for customer in customers:
            for notification in notifications:
                cursor.execute("""
                INSERT OR IGNORE INTO user_notifications (user_id, notification_id)
                VALUES (?, ?)
                """, (customer[0], notification[0]))
        
        print(f"   ✅ تم ربط الإشعارات بـ {len(customers)} عميل")
        
        # 7. تحديث إعدادات النظام
        print("📝 تحديث إعدادات النظام...")
        
        cursor.execute("UPDATE settings SET notifications_enabled = 1")
        
        conn.commit()
        print("\n🎉 تم تحديث قاعدة البيانات بنجاح!")
        
        # عرض الإحصائيات
        cursor.execute("SELECT COUNT(*) FROM notifications")
        notifications_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_notifications")
        user_notifications_count = cursor.fetchone()[0]
        
        print(f"\n📊 الإحصائيات:")
        print(f"   📢 الإشعارات: {notifications_count}")
        print(f"   👥 ربط المستخدمين: {user_notifications_count}")
        
    except Exception as e:
        print(f"❌ خطأ في تحديث قاعدة البيانات: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_database_for_notifications()
