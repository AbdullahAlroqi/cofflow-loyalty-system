"""
إصلاح قاعدة البيانات في مجلد instance
"""
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash
import random

def fix_instance_database():
    """إصلاح قاعدة البيانات في مجلد instance"""
    print("🔧 إصلاح قاعدة البيانات في مجلد instance...")
    
    db_path = 'instance/cofflow.db'
    
    if not os.path.exists(db_path):
        print("❌ قاعدة البيانات غير موجودة في instance")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # فحص هيكل جدول الكوبونات
        cursor.execute("PRAGMA table_info(coupons)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 أعمدة جدول الكوبونات: {columns}")
        
        # إضافة الأعمدة المفقودة
        if 'used_by' not in columns:
            cursor.execute("ALTER TABLE coupons ADD COLUMN used_by INTEGER")
            print("   ✅ تم إضافة عمود used_by")
        
        if 'employee_id' not in columns:
            cursor.execute("ALTER TABLE coupons ADD COLUMN employee_id INTEGER")
            print("   ✅ تم إضافة عمود employee_id")
        
        # فحص البيانات الحالية
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'customer'")
        customers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'employee'")
        employees = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM coupons")
        coupons = cursor.fetchone()[0]
        
        print(f"📊 البيانات الحالية:")
        print(f"   العملاء: {customers}")
        print(f"   الموظفون: {employees}")
        print(f"   الكوبونات: {coupons}")
        
        # إذا كانت البيانات قليلة، أضف المزيد
        if customers < 10:
            print("📝 إضافة بيانات تجريبية...")
            
            # إضافة موظفين
            employees_data = [
                ('أحمد محمد', '0501234567', 'ahmed@cofflow.com'),
                ('فاطمة علي', '0507654321', 'fatima@cofflow.com'),
                ('محمد سالم', '0509876543', 'mohammed@cofflow.com')
            ]
            
            for name, phone, email in employees_data:
                cursor.execute("SELECT COUNT(*) FROM users WHERE phone = ?", (phone,))
                if cursor.fetchone()[0] == 0:
                    password_hash = generate_password_hash('123456')
                    cursor.execute("""
                    INSERT INTO users (name, phone, email, password_hash, role, notifications_enabled)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (name, phone, email, password_hash, 'employee', 1))
            
            # إضافة عملاء
            customers_data = [
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
            
            for name, phone, email in customers_data:
                cursor.execute("SELECT COUNT(*) FROM users WHERE phone = ?", (phone,))
                if cursor.fetchone()[0] == 0:
                    password_hash = generate_password_hash('123456')
                    cups_count = random.randint(0, 8)
                    cursor.execute("""
                    INSERT INTO users (name, phone, email, password_hash, role, cups_count, notifications_enabled)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (name, phone, email, password_hash, 'customer', cups_count, 1))
            
            print("   ✅ تم إضافة المستخدمين")
        
        # إضافة كوبونات إذا لم تكن موجودة
        if coupons < 5:
            cursor.execute("SELECT id, cups_count FROM users WHERE role = 'customer' AND cups_count >= 6")
            eligible_customers = cursor.fetchall()
            
            coupon_counter = 1
            for customer_id, cups_count in eligible_customers:
                coupons_to_create = cups_count // 6
                
                for i in range(coupons_to_create):
                    coupon_code = f"CF{coupon_counter:04d}"
                    status = 'active' if random.choice([True, False]) else 'used'
                    
                    cursor.execute("""
                    INSERT INTO coupons (code, customer_id, status, created_at)
                    VALUES (?, ?, ?, ?)
                    """, (coupon_code, customer_id, status, datetime.now()))
                    
                    coupon_counter += 1
            
            print(f"   ✅ تم إضافة {coupon_counter - 1} كوبون")
        
        # إضافة معاملات
        cursor.execute("SELECT COUNT(*) FROM transactions")
        transactions_count = cursor.fetchone()[0]
        
        if transactions_count < 50:
            cursor.execute("SELECT id FROM users WHERE role = 'customer'")
            customer_ids = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT id FROM users WHERE role IN ('admin', 'employee')")
            employee_ids = [row[0] for row in cursor.fetchall()]
            
            if customer_ids and employee_ids:
                for _ in range(50):
                    customer_id = random.choice(customer_ids)
                    employee_id = random.choice(employee_ids)
                    transaction_type = random.choice(['add_cup', 'redeem_coupon', 'bonus_cup'])
                    cups_added = 1 if transaction_type != 'redeem_coupon' else 0
                    
                    created_at = datetime.now()
                    
                    cursor.execute("""
                    INSERT INTO transactions (customer_id, employee_id, transaction_type, cups_added, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """, (customer_id, employee_id, transaction_type, cups_added, created_at))
                
                print("   ✅ تم إضافة 50 معاملة")
        
        conn.commit()
        
        # فحص النتيجة النهائية
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'customer'")
        final_customers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'employee'")
        final_employees = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM coupons WHERE status = 'active'")
        active_coupons = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM coupons WHERE status = 'used'")
        used_coupons = cursor.fetchone()[0]
        
        print(f"\n📊 البيانات النهائية:")
        print(f"   العملاء: {final_customers}")
        print(f"   الموظفون: {final_employees}")
        print(f"   الكوبونات النشطة: {active_coupons}")
        print(f"   الكوبونات المستخدمة: {used_coupons}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if fix_instance_database():
        print("\n🎉 تم إصلاح قاعدة البيانات بنجاح!")
        print("🔄 أعد تشغيل الخادم لرؤية التغييرات")
    else:
        print("\n❌ فشل في إصلاح قاعدة البيانات")
