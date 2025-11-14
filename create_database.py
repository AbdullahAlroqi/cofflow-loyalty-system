"""
سكريبت إنشاء قاعدة البيانات الكاملة من الصفر
"""
from app import app
from models import db, User, Settings
import os

def create_database():
    print("🔄 بدء إنشاء قاعدة البيانات...")
    
    # التأكد من وجود مجلد instance
    if not os.path.exists('instance'):
        os.makedirs('instance')
        print("✅ تم إنشاء مجلد instance")
    
    # إنشاء السياق للتطبيق
    with app.app_context():
        try:
            # حذف قاعدة البيانات القديمة إن وجدت
            db_path = 'instance/database.db'
            if os.path.exists(db_path):
                os.remove(db_path)
                print("🗑️ تم حذف قاعدة البيانات القديمة")
            
            # إنشاء جميع الجداول
            db.create_all()
            print("✅ تم إنشاء جميع الجداول")
            
            # إنشاء إعدادات افتراضية
            if not Settings.query.first():
                default_settings = Settings(
                    cups_required=6,
                    primary_color='#8B4513',
                    secondary_color='#D2691E'
                )
                db.session.add(default_settings)
                print("✅ تم إنشاء الإعدادات الافتراضية")
            
            # إنشاء مستخدم مدير افتراضي
            admin = User.query.filter_by(phone='admin').first()
            if not admin:
                admin = User(
                    name='المدير',
                    phone='admin',
                    email='admin@cofflow.com',
                    role='admin'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                print("✅ تم إنشاء حساب المدير (admin / admin123)")
            
            # حفظ التغييرات
            db.session.commit()
            print("✅ تم حفظ جميع البيانات")
            
            print("\n🎉 تم إنشاء قاعدة البيانات بنجاح!")
            print("📋 معلومات الدخول:")
            print("   المدير: admin / admin123")
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_database()
