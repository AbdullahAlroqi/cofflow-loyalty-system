"""
إصلاح قاعدة البيانات لنظام الإشعارات
"""
import sqlite3
import os

def fix_notifications_database():
    print("🔧 إصلاح قاعدة البيانات لنظام الإشعارات...")
    
    db_path = 'cofflow.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # حذف الجداول الموجودة وإعادة إنشائها
        print("🗑️ حذف الجداول القديمة...")
        cursor.execute("DROP TABLE IF EXISTS user_notifications")
        cursor.execute("DROP TABLE IF EXISTS notifications")
        
        # إنشاء جدول الإشعارات مع التصحيحات
        print("📝 إنشاء جدول الإشعارات الجديد...")
        cursor.execute("""
        CREATE TABLE notifications (
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
        
        # إنشاء جدول ربط المستخدمين بالإشعارات
        print("📝 إنشاء جدول ربط المستخدمين بالإشعارات...")
        cursor.execute("""
        CREATE TABLE user_notifications (
            user_id INTEGER NOT NULL,
            notification_id INTEGER NOT NULL,
            read_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, notification_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (notification_id) REFERENCES notifications (id)
        )
        """)
        
        # الحصول على المدير
        cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
        admin = cursor.fetchone()
        
        if admin:
            admin_id = admin[0]
            
            # إنشاء إشعارات تجريبية
            print("📝 إنشاء إشعارات تجريبية...")
            
            sample_notifications = [
                ('🎉 مرحباً بكم في نظام الإشعارات!', 'تم تفعيل نظام الإشعارات بنجاح. ستصلكم الآن جميع العروض والتحديثات.', 'news', 'celebration'),
                ('☕ عرض خاص: كوب مجاني!', 'احصل على كوب قهوة مجاني عند شراء 5 أكواب. العرض ساري لمدة أسبوع.', 'offer', 'local_cafe'),
                ('🔔 تذكير: نقاط الولاء', 'لا تنسوا استخدام نقاط الولاء المتراكمة للحصول على مشروبات مجانية.', 'alert', 'loyalty'),
                ('🆕 قائمة جديدة متاحة الآن!', 'اكتشفوا مشروبات جديدة ولذيذة في قائمتنا المحدثة.', 'news', 'menu_book'),
                ('⏰ ساعات العمل الجديدة', 'تم تحديث ساعات العمل: من 6 صباحاً حتى 12 منتصف الليل.', 'alert', 'schedule')
            ]
            
            for title, body, type_val, icon in sample_notifications:
                cursor.execute("""
                INSERT INTO notifications (title, body, type, icon, creator_id, is_public)
                VALUES (?, ?, ?, ?, ?, 1)
                """, (title, body, type_val, icon, admin_id))
            
            print(f"   ✅ تم إنشاء {len(sample_notifications)} إشعارات تجريبية")
            
            # ربط الإشعارات بجميع العملاء
            print("📝 ربط الإشعارات بالعملاء...")
            
            cursor.execute("SELECT id FROM users WHERE role = 'customer'")
            customers = cursor.fetchall()
            
            cursor.execute("SELECT id FROM notifications")
            notifications = cursor.fetchall()
            
            for customer in customers:
                for notification in notifications:
                    cursor.execute("""
                    INSERT INTO user_notifications (user_id, notification_id)
                    VALUES (?, ?)
                    """, (customer[0], notification[0]))
            
            print(f"   ✅ تم ربط الإشعارات بـ {len(customers)} عميل")
        
        conn.commit()
        print("\n🎉 تم إصلاح قاعدة البيانات بنجاح!")
        
        # عرض الإحصائيات
        cursor.execute("SELECT COUNT(*) FROM notifications")
        notifications_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_notifications")
        user_notifications_count = cursor.fetchone()[0]
        
        print(f"\n📊 الإحصائيات النهائية:")
        print(f"   📢 الإشعارات: {notifications_count}")
        print(f"   👥 ربط المستخدمين: {user_notifications_count}")
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_notifications_database()
