"""
سكريبت للتحقق من قاعدة البيانات وحل مشاكل تسجيل الدخول
"""
import sqlite3
from werkzeug.security import check_password_hash

def check_database():
    print("🔍 فحص قاعدة البيانات...")
    
    conn = sqlite3.connect('cofflow.db')
    cursor = conn.cursor()
    
    try:
        # فحص المستخدمين
        print("\n👥 المستخدمون في قاعدة البيانات:")
        cursor.execute("SELECT id, name, phone, role FROM users")
        users = cursor.fetchall()
        
        for user in users:
            print(f"  ID: {user[0]}, الاسم: {user[1]}, الهاتف: {user[2]}, الدور: {user[3]}")
        
        # فحص حساب المدير
        print("\n👨‍💼 فحص حساب المدير:")
        cursor.execute("SELECT id, name, phone, password_hash FROM users WHERE role = 'admin'")
        admin = cursor.fetchone()
        
        if admin:
            print(f"  ✅ حساب المدير موجود: {admin[1]} ({admin[2]})")
            
            # اختبار كلمة المرور
            password_hash = admin[3]
            test_password = 'admin123'
            
            if check_password_hash(password_hash, test_password):
                print(f"  ✅ كلمة المرور صحيحة: {test_password}")
            else:
                print(f"  ❌ كلمة المرور خاطئة")
                
                # إعادة تعيين كلمة المرور
                from werkzeug.security import generate_password_hash
                new_hash = generate_password_hash('admin123')
                cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, admin[0]))
                conn.commit()
                print(f"  ✅ تم إعادة تعيين كلمة المرور إلى: admin123")
        else:
            print("  ❌ حساب المدير غير موجود!")
            
            # إنشاء حساب مدير جديد
            from werkzeug.security import generate_password_hash
            admin_password = generate_password_hash('admin123')
            cursor.execute("""
                INSERT INTO users (name, phone, email, password_hash, role, created_at)
                VALUES ('المدير', 'admin', 'admin@cofflow.com', ?, 'admin', datetime('now'))
            """, (admin_password,))
            conn.commit()
            print("  ✅ تم إنشاء حساب مدير جديد: admin / admin123")
        
        # فحص الجداول
        print("\n📊 الجداول الموجودة:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  {table[0]}: {count} سجل")
        
        print("\n✅ انتهى فحص قاعدة البيانات")
        
    except Exception as e:
        print(f"❌ خطأ في فحص قاعدة البيانات: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database()
