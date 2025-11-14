"""
سكريبت للتحقق من قاعدة البيانات التي يستخدمها التطبيق
"""
from app import app
from models import db, User
import os

def check_app_database():
    print("🔍 فحص قاعدة البيانات المستخدمة في التطبيق...")
    
    with app.app_context():
        try:
            # طباعة مسار قاعدة البيانات
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"📍 مسار قاعدة البيانات: {db_uri}")
            
            # التحقق من وجود الملف
            if 'sqlite:///' in db_uri:
                db_path = db_uri.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    print(f"✅ ملف قاعدة البيانات موجود: {db_path}")
                    print(f"   حجم الملف: {os.path.getsize(db_path)} بايت")
                else:
                    print(f"❌ ملف قاعدة البيانات غير موجود: {db_path}")
            
            # عدد المستخدمين
            user_count = User.query.count()
            print(f"👥 عدد المستخدمين في التطبيق: {user_count}")
            
            # البحث عن المدير
            admin = User.query.filter_by(role='admin').first()
            if admin:
                print(f"👨‍💼 المدير في التطبيق: {admin.name} ({admin.phone})")
                print(f"   ID: {admin.id}")
                
                # اختبار كلمة المرور
                if admin.check_password('admin123'):
                    print("✅ كلمة المرور صحيحة في التطبيق")
                else:
                    print("❌ كلمة المرور خاطئة في التطبيق")
                    
                    # إعادة تعيين كلمة المرور من خلال التطبيق
                    admin.set_password('admin123')
                    db.session.commit()
                    print("🔄 تم إعادة تعيين كلمة المرور من خلال التطبيق")
                    
                    # اختبار مرة أخرى
                    if admin.check_password('admin123'):
                        print("✅ كلمة المرور صحيحة الآن")
                    else:
                        print("❌ لا تزال كلمة المرور خاطئة")
            else:
                print("❌ لم يتم العثور على المدير في التطبيق")
        
        except Exception as e:
            print(f"❌ خطأ: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_app_database()
