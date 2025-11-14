"""
سكريبت لاختبار كلمات المرور
"""
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

def test_passwords():
    print("🔐 اختبار كلمات المرور...")
    
    conn = sqlite3.connect('cofflow.db')
    cursor = conn.cursor()
    
    try:
        # الحصول على المدير
        cursor.execute("SELECT id, name, phone, password_hash FROM users WHERE role = 'admin'")
        admin = cursor.fetchone()
        
        if admin:
            print(f"👨‍💼 المدير: {admin[1]} ({admin[2]})")
            
            # اختبار كلمات مرور مختلفة
            test_passwords = ['admin123', 'admin', '123456', 'password']
            
            for pwd in test_passwords:
                if check_password_hash(admin[3], pwd):
                    print(f"   ✅ كلمة المرور الصحيحة: {pwd}")
                    break
            else:
                print("   ❌ لم يتم العثور على كلمة المرور الصحيحة")
                
                # إعادة تعيين كلمة المرور
                new_hash = generate_password_hash('admin123')
                cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, admin[0]))
                conn.commit()
                print("   ✅ تم إعادة تعيين كلمة المرور إلى: admin123")
        
        # اختبار العملاء
        print("\n👥 العملاء:")
        cursor.execute("SELECT id, name, phone, password_hash FROM users WHERE role = 'customer' LIMIT 3")
        customers = cursor.fetchall()
        
        for customer in customers:
            print(f"   العميل: {customer[1]} ({customer[2]})")
            
            # اختبار كلمات مرور شائعة
            common_passwords = ['123456', 'password', 'password123', customer[2]]  # رقم الهاتف ككلمة مرور
            
            password_found = False
            for pwd in common_passwords:
                if check_password_hash(customer[3], pwd):
                    print(f"     ✅ كلمة المرور: {pwd}")
                    password_found = True
                    break
            
            if not password_found:
                # إعادة تعيين كلمة مرور العميل
                new_hash = generate_password_hash('123456')
                cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, customer[0]))
                print(f"     🔄 تم إعادة تعيين كلمة المرور إلى: 123456")
        
        conn.commit()
        print("\n✅ انتهى اختبار كلمات المرور")
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_passwords()
