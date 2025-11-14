"""
إنشاء قاعدة بيانات جديدة مع عينات شاملة
"""
import os
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import random

def delete_old_databases():
    """حذف قواعد البيانات القديمة"""
    print("🗑️ حذف قواعد البيانات القديمة...")
    
    db_files = ['cofflow.db', 'instance/cofflow.db', 'instance/database.db']
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"   ✅ تم حذف {db_file}")
            except Exception as e:
                print(f"   ❌ خطأ في حذف {db_file}: {e}")
        else:
            print(f"   ℹ️ {db_file} غير موجود")

def create_fresh_database():
    """إنشاء قاعدة بيانات جديدة"""
    print("\n📝 إنشاء قاعدة بيانات جديدة...")
    
    conn = sqlite3.connect('cofflow.db')
    cursor = conn.cursor()
    
    try:
        # إنشاء جدول المستخدمين
        print("👥 إنشاء جدول المستخدمين...")
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
            last_notification_read DATETIME,
            allow_notifications BOOLEAN DEFAULT 1,
            notifications_enabled BOOLEAN DEFAULT 1
        )
        """)
        
        # إنشاء جدول الإعدادات
        print("⚙️ إنشاء جدول الإعدادات...")
        cursor.execute("""
        CREATE TABLE settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cups_required INTEGER DEFAULT 6,
            logo_path VARCHAR(255),
            primary_color VARCHAR(7) DEFAULT '#8B4513',
            secondary_color VARCHAR(7) DEFAULT '#D2691E',
            push_public_key TEXT,
            push_private_key TEXT,
            notifications_enabled BOOLEAN DEFAULT 1,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # إنشاء جدول الكوبونات
        print("🎫 إنشاء جدول الكوبونات...")
        cursor.execute("""
        CREATE TABLE coupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code VARCHAR(20) UNIQUE NOT NULL,
            customer_id INTEGER NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            used_at DATETIME,
            employee_id INTEGER,
            FOREIGN KEY (customer_id) REFERENCES users (id),
            FOREIGN KEY (employee_id) REFERENCES users (id)
        )
        """)
        
        # إنشاء جدول المعاملات
        print("💳 إنشاء جدول المعاملات...")
        cursor.execute("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            transaction_type VARCHAR(50) NOT NULL,
            cups_added INTEGER DEFAULT 1,
            coupon_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES users (id),
            FOREIGN KEY (employee_id) REFERENCES users (id),
            FOREIGN KEY (coupon_id) REFERENCES coupons (id)
        )
        """)
        
        # إنشاء جدول الإشعارات
        print("🔔 إنشاء جدول الإشعارات...")
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
        print("🔗 إنشاء جدول ربط الإشعارات...")
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
        
        conn.commit()
        print("✅ تم إنشاء جميع الجداول بنجاح")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def insert_sample_data():
    """إدراج بيانات العينات"""
    print("\n📊 إدراج بيانات العينات...")
    
    conn = sqlite3.connect('cofflow.db')
    cursor = conn.cursor()
    
    try:
        # إدراج الإعدادات الافتراضية
        print("⚙️ إدراج الإعدادات الافتراضية...")
        cursor.execute("""
        INSERT INTO settings (cups_required, primary_color, secondary_color, notifications_enabled)
        VALUES (6, '#8B4513', '#D2691E', 1)
        """)
        
        # إدراج المستخدمين
        print("👥 إدراج المستخدمين...")
        
        # المدير
        admin_password = generate_password_hash('admin123')
        cursor.execute("""
        INSERT INTO users (name, phone, email, password_hash, role, notifications_enabled)
        VALUES (?, ?, ?, ?, ?, ?)
        """, ('مدير النظام', '0544482434', 'admin@cofflow.com', admin_password, 'admin', 1))
        
        # الموظفين
        employees = [
            ('أحمد محمد', '0501234567', 'ahmed@cofflow.com'),
            ('فاطمة علي', '0507654321', 'fatima@cofflow.com'),
            ('محمد سالم', '0509876543', 'mohammed@cofflow.com')
        ]
        
        for name, phone, email in employees:
            password_hash = generate_password_hash('123456')
            cursor.execute("""
            INSERT INTO users (name, phone, email, password_hash, role, notifications_enabled)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (name, phone, email, password_hash, 'employee', 1))
        
        # العملاء
        customers = [
            ('ريهام أحمد', '0583270028', 'reham@example.com'),
            ('عادل العتيبي', '0500207042', 'adel@example.com'),
            ('خالد محمد', '0568553992', 'khalid@example.com'),
            ('آلاء الروقي', '0505299738', 'alaa@example.com'),
            ('الجوهرة العتيبي', '0569063432', 'jawhara@example.com'),
            ('أماني العتيبي', '0591932158', 'amani@example.com'),
            ('رنيم الروقي', '0554339327', 'raneem@example.com'),
            ('بدرية العتيبي', '0595070748', 'badriya@example.com'),
            ('رند الأنصاري', '0561631034', 'rand@example.com'),
            ('شهد السهلي', '0561248067', 'shahad@example.com'),
            ('سامي أحمد', '0545703321', 'sami@example.com'),
            ('نورا محمد', '0556789012', 'nora@example.com'),
            ('عبدالله سعد', '0567890123', 'abdullah@example.com'),
            ('مريم علي', '0578901234', 'mariam@example.com'),
            ('يوسف خالد', '0589012345', 'youssef@example.com')
        ]
        
        for name, phone, email in customers:
            password_hash = generate_password_hash('123456')
            cups_count = random.randint(0, 8)  # عدد عشوائي من الأكواب
            cursor.execute("""
            INSERT INTO users (name, phone, email, password_hash, role, cups_count, notifications_enabled)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, phone, email, password_hash, 'customer', cups_count, 1))
        
        print(f"   ✅ تم إدراج {len(customers)} عميل")
        
        # إنشاء كوبونات للعملاء الذين لديهم 6 أكواب أو أكثر
        print("🎫 إنشاء الكوبونات...")
        
        cursor.execute("SELECT id, cups_count FROM users WHERE role = 'customer' AND cups_count >= 6")
        eligible_customers = cursor.fetchall()
        
        coupon_counter = 1
        for customer_id, cups_count in eligible_customers:
            # إنشاء كوبون لكل 6 أكواب
            coupons_to_create = cups_count // 6
            
            for i in range(coupons_to_create):
                coupon_code = f"CF{coupon_counter:04d}"
                status = 'active' if random.choice([True, False]) else 'used'
                
                cursor.execute("""
                INSERT INTO coupons (code, customer_id, status, created_at)
                VALUES (?, ?, ?, ?)
                """, (coupon_code, customer_id, status, datetime.now() - timedelta(days=random.randint(1, 30))))
                
                coupon_counter += 1
        
        print(f"   ✅ تم إنشاء {coupon_counter - 1} كوبون")
        
        # إنشاء معاملات
        print("💳 إنشاء المعاملات...")
        
        cursor.execute("SELECT id FROM users WHERE role = 'customer'")
        customer_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id FROM users WHERE role IN ('admin', 'employee')")
        employee_ids = [row[0] for row in cursor.fetchall()]
        
        transaction_counter = 0
        for _ in range(100):  # إنشاء 100 معاملة
            customer_id = random.choice(customer_ids)
            employee_id = random.choice(employee_ids)
            transaction_type = random.choice(['add_cup', 'redeem_coupon', 'bonus_cup'])
            cups_added = 1 if transaction_type != 'redeem_coupon' else 0
            
            created_at = datetime.now() - timedelta(days=random.randint(1, 90))
            
            cursor.execute("""
            INSERT INTO transactions (customer_id, employee_id, transaction_type, cups_added, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (customer_id, employee_id, transaction_type, cups_added, created_at))
            
            transaction_counter += 1
        
        print(f"   ✅ تم إنشاء {transaction_counter} معاملة")
        
        # إنشاء إشعارات
        print("🔔 إنشاء الإشعارات...")
        
        notifications = [
            {
                'title': '🎉 مرحباً بكم في COFFLOW!',
                'body': 'أهلاً وسهلاً بكم في تطبيق COFFLOW لإدارة نقاط الولاء. استمتعوا بتجميع النقاط والحصول على مشروبات مجانية!',
                'type': 'news',
                'icon': 'celebration'
            },
            {
                'title': '☕ عرض خاص: خصم 25%',
                'body': 'احصلوا على خصم 25% على جميع المشروبات الساخنة طوال هذا الأسبوع. لا تفوتوا الفرصة!',
                'type': 'offer',
                'icon': 'local_offer',
                'expires_at': datetime.now() + timedelta(days=7)
            },
            {
                'title': '🆕 قائمة جديدة متاحة الآن',
                'body': 'اكتشفوا مشروبات جديدة ولذيذة في قائمتنا المحدثة. قهوة مختصة وعصائر طبيعية طازجة.',
                'type': 'news',
                'icon': 'menu_book'
            },
            {
                'title': '⏰ ساعات العمل الجديدة',
                'body': 'تم تحديث ساعات العمل: من الساعة 6:00 صباحاً حتى 12:00 منتصف الليل يومياً.',
                'type': 'alert',
                'icon': 'schedule'
            },
            {
                'title': '🎁 برنامج الولاء المحسن',
                'body': 'تم تحسين برنامج الولاء! الآن يمكنكم الحصول على كوب مجاني كل 5 أكواب بدلاً من 6.',
                'type': 'news',
                'icon': 'loyalty'
            },
            {
                'title': '🌟 تقييمكم يهمنا',
                'body': 'شاركونا تجربتكم وقيموا خدماتنا. رأيكم يساعدنا على التحسين المستمر.',
                'type': 'general',
                'icon': 'star'
            }
        ]
        
        for notif in notifications:
            created_at = datetime.now() - timedelta(days=random.randint(1, 15))
            expires_at = notif.get('expires_at')
            
            cursor.execute("""
            INSERT INTO notifications (title, body, type, icon, creator_id, is_public, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (notif['title'], notif['body'], notif['type'], notif['icon'], 1, 1, created_at, expires_at))
        
        # ربط الإشعارات بالعملاء
        cursor.execute("SELECT id FROM notifications")
        notification_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id FROM users WHERE role = 'customer'")
        customer_ids = [row[0] for row in cursor.fetchall()]
        
        for notification_id in notification_ids:
            for customer_id in customer_ids:
                # بعض الإشعارات مقروءة وبعضها غير مقروء
                read_at = None
                if random.choice([True, False, False]):  # 33% مقروءة
                    read_at = datetime.now() - timedelta(days=random.randint(1, 10))
                
                cursor.execute("""
                INSERT INTO user_notifications (user_id, notification_id, read_at)
                VALUES (?, ?, ?)
                """, (customer_id, notification_id, read_at))
        
        print(f"   ✅ تم إنشاء {len(notifications)} إشعار")
        
        conn.commit()
        print("✅ تم إدراج جميع البيانات بنجاح")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إدراج البيانات: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def show_database_stats():
    """عرض إحصائيات قاعدة البيانات"""
    print("\n📊 إحصائيات قاعدة البيانات الجديدة:")
    
    conn = sqlite3.connect('cofflow.db')
    cursor = conn.cursor()
    
    try:
        # إحصائيات المستخدمين
        cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
        user_stats = cursor.fetchall()
        
        print("👥 المستخدمون:")
        for role, count in user_stats:
            print(f"   {role}: {count}")
        
        # إحصائيات الكوبونات
        cursor.execute("SELECT status, COUNT(*) FROM coupons GROUP BY status")
        coupon_stats = cursor.fetchall()
        
        print("🎫 الكوبونات:")
        for status, count in coupon_stats:
            print(f"   {status}: {count}")
        
        # إحصائيات المعاملات
        cursor.execute("SELECT transaction_type, COUNT(*) FROM transactions GROUP BY transaction_type")
        transaction_stats = cursor.fetchall()
        
        print("💳 المعاملات:")
        for t_type, count in transaction_stats:
            print(f"   {t_type}: {count}")
        
        # إحصائيات الإشعارات
        cursor.execute("SELECT COUNT(*) FROM notifications")
        notification_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_notifications WHERE read_at IS NOT NULL")
        read_notifications = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_notifications")
        total_notifications = cursor.fetchone()[0]
        
        print("🔔 الإشعارات:")
        print(f"   إجمالي الإشعارات: {notification_count}")
        print(f"   إجمالي المرسل: {total_notifications}")
        print(f"   المقروءة: {read_notifications}")
        print(f"   غير المقروءة: {total_notifications - read_notifications}")
        
    except Exception as e:
        print(f"❌ خطأ في عرض الإحصائيات: {e}")
    finally:
        conn.close()

def main():
    """الدالة الرئيسية"""
    print("🚀 إنشاء قاعدة بيانات COFFLOW جديدة مع عينات شاملة")
    print("=" * 60)
    
    # حذف قواعد البيانات القديمة
    delete_old_databases()
    
    # إنشاء قاعدة بيانات جديدة
    if create_fresh_database():
        # إدراج بيانات العينات
        if insert_sample_data():
            # عرض الإحصائيات
            show_database_stats()
            
            print("\n🎉 تم إنشاء قاعدة البيانات الجديدة بنجاح!")
            print("📋 معلومات الدخول:")
            print("   👨‍💼 المدير: 0544482434 / admin123")
            print("   👷 الموظف: 0501234567 / 123456")
            print("   🛍️ العميل: 0583270028 / 123456")
            print("\n🌐 يمكنك الآن تشغيل الخادم: python app.py")
        else:
            print("❌ فشل في إدراج البيانات")
    else:
        print("❌ فشل في إنشاء قاعدة البيانات")

if __name__ == "__main__":
    main()
