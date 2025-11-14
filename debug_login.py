"""
سكريبت لتشخيص مشكلة تسجيل الدخول
"""
from models import db, User
from werkzeug.security import check_password_hash
from app import app

def debug_login():
    print("🔍 تشخيص مشكلة تسجيل الدخول...")
    
    with app.app_context():
        try:
            # البحث عن المدير
            phone = '0544482434'
            password = 'admin123'
            
            print(f"🔍 البحث عن المستخدم: {phone}")
            user = User.query.filter_by(phone=phone).first()
            
            if user:
                print(f"✅ تم العثور على المستخدم: {user.name} ({user.role})")
                print(f"   ID: {user.id}")
                print(f"   الهاتف: {user.phone}")
                print(f"   الدور: {user.role}")
                
                # اختبار كلمة المرور
                if user.check_password(password):
                    print(f"✅ كلمة المرور صحيحة")
                    
                    # اختبار Flask-Login
                    print(f"🔍 اختبار Flask-Login...")
                    print(f"   is_authenticated: {user.is_authenticated}")
                    print(f"   is_active: {user.is_active}")
                    print(f"   is_anonymous: {user.is_anonymous}")
                    print(f"   get_id(): {user.get_id()}")
                    
                else:
                    print(f"❌ كلمة المرور خاطئة")
                    
                    # اختبار مباشر
                    if check_password_hash(user.password_hash, password):
                        print("✅ كلمة المرور صحيحة (اختبار مباشر)")
                    else:
                        print("❌ كلمة المرور خاطئة (اختبار مباشر)")
            else:
                print(f"❌ لم يتم العثور على المستخدم")
                
                # عرض جميع المستخدمين
                print("\n👥 جميع المستخدمين:")
                users = User.query.all()
                for u in users:
                    print(f"   {u.id}: {u.name} ({u.phone}) - {u.role}")
        
        except Exception as e:
            print(f"❌ خطأ: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_login()
