"""
إصلاح جدول المستخدمين لإضافة أعمدة الإشعارات
"""
import sqlite3
import os

def fix_users_table():
    print("🔧 إصلاح جدول المستخدمين...")
    
    db_path = 'cofflow.db'
    if not os.path.exists(db_path):
        print("❌ ملف قاعدة البيانات غير موجود")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # فحص الأعمدة الموجودة
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 الأعمدة الموجودة: {columns}")
        
        # إضافة الأعمدة المفقودة
        columns_to_add = [
            ('push_subscription', 'TEXT'),
            ('last_notification_read', 'DATETIME'),
            ('notifications_enabled', 'BOOLEAN DEFAULT 1')
        ]
        
        for column_name, column_type in columns_to_add:
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
                    print(f"   ✅ تم إضافة عمود {column_name}")
                except Exception as e:
                    print(f"   ❌ خطأ في إضافة عمود {column_name}: {e}")
            else:
                print(f"   ✅ عمود {column_name} موجود بالفعل")
        
        # تحديث القيم الافتراضية للمستخدمين الموجودين
        cursor.execute("UPDATE users SET notifications_enabled = 1 WHERE notifications_enabled IS NULL")
        
        conn.commit()
        print("✅ تم إصلاح جدول المستخدمين بنجاح")
        
        # فحص النتيجة
        cursor.execute("PRAGMA table_info(users)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 الأعمدة بعد الإصلاح: {new_columns}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إصلاح الجدول: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def test_user_query():
    """اختبار استعلام المستخدم"""
    print("\n🧪 اختبار استعلام المستخدم...")
    
    conn = sqlite3.connect('cofflow.db')
    cursor = conn.cursor()
    
    try:
        # اختبار استعلام المستخدم
        cursor.execute("""
        SELECT id, name, phone, role, push_subscription, 
               last_notification_read, notifications_enabled
        FROM users 
        WHERE id = 4
        """)
        
        user = cursor.fetchone()
        if user:
            print("✅ تم العثور على المستخدم:")
            print(f"   ID: {user[0]}")
            print(f"   الاسم: {user[1]}")
            print(f"   الهاتف: {user[2]}")
            print(f"   الدور: {user[3]}")
            print(f"   اشتراك الإشعارات: {user[4]}")
            print(f"   آخر قراءة: {user[5]}")
            print(f"   الإشعارات مفعلة: {user[6]}")
            return True
        else:
            print("❌ لم يتم العثور على المستخدم")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاستعلام: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔔 إصلاح قاعدة البيانات لنظام الإشعارات")
    print("=" * 50)
    
    if fix_users_table():
        test_user_query()
        print("\n🎉 تم الإصلاح بنجاح! يمكن إعادة تشغيل الخادم الآن.")
    else:
        print("\n❌ فشل في الإصلاح")
