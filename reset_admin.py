"""
سكريبت لإنشاء أو إعادة تعيين حساب الإدارة
"""

from app import app
from models import db, User, Settings

def reset_admin():
    with app.app_context():
        print("=" * 50)
        print("🔧 إصلاح حساب الإدارة")
        print("=" * 50)
        
        # البحث عن حساب الإدارة الموجود
        admin = User.query.filter_by(phone='0500000000').first()
        
        if admin:
            print(f"\n✅ تم العثور على حساب: {admin.name}")
            print(f"   الدور: {admin.role}")
            
            # إعادة تعيين كلمة المرور
            admin.set_password('admin123')
            admin.role = 'admin'  # تأكيد الدور
            db.session.commit()
            print("✅ تم إعادة تعيين كلمة المرور إلى: admin123")
        else:
            print("\n❌ لم يتم العثور على حساب الإدارة")
            print("📝 جاري إنشاء حساب جديد...")
            
            # إنشاء حساب جديد
            admin = User(
                name='مدير النظام',
                phone='0500000000',
                email='admin@cofflow.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ تم إنشاء حساب الإدارة بنجاح!")
        
        # التأكد من الإعدادات
        settings = Settings.query.first()
        if not settings:
            settings = Settings()
            db.session.add(settings)
            db.session.commit()
            print("✅ تم إنشاء الإعدادات الافتراضية")
        
        print("\n" + "=" * 50)
        print("🎉 تم الإصلاح بنجاح!")
        print("=" * 50)
        print("\n📝 بيانات تسجيل الدخول:")
        print("   رقم الجوال: 0500000000")
        print("   كلمة المرور: admin123")
        print("\n" + "=" * 50)

if __name__ == '__main__':
    reset_admin()
