"""
سكريبت لإعادة تعيين كلمة مرور المدير
"""
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def reset_admin_password():
    print("🔐 إعادة تعيين كلمة مرور المدير...")
    
    conn = sqlite3.connect('cofflow.db')
    cursor = conn.cursor()
    
    try:
        # الحصول على المدير
        cursor.execute("SELECT id, name, phone FROM users WHERE role = 'admin'")
        admin = cursor.fetchone()
        
        if admin:
            print(f"👨‍💼 المدير: {admin[1]} ({admin[2]})")
            
            # إنشاء كلمة مرور جديدة
            new_password = 'admin123'
            new_hash = generate_password_hash(new_password)
            
            # تحديث كلمة المرور
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, admin[0]))
            conn.commit()
            
            print(f"✅ تم تحديث كلمة المرور إلى: {new_password}")
            
            # اختبار كلمة المرور الجديدة
            cursor.execute("SELECT password_hash FROM users WHERE id = ?", (admin[0],))
            updated_hash = cursor.fetchone()[0]
            
            if check_password_hash(updated_hash, new_password):
                print("✅ تم التحقق من كلمة المرور الجديدة بنجاح")
            else:
                print("❌ فشل في التحقق من كلمة المرور الجديدة")
        else:
            print("❌ لم يتم العثور على المدير")
    
    except Exception as e:
        print(f"❌ خطأ: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    reset_admin_password()
