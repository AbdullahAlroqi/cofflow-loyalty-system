"""
سكريبت لاختبار الإعدادات والتأكد من حفظها بشكل صحيح
"""

from app import app
from models import db, Settings

def test_settings():
    with app.app_context():
        settings = Settings.query.first()
        
        if not settings:
            print("❌ لا توجد إعدادات في قاعدة البيانات!")
            print("   جاري إنشاء إعدادات افتراضية...")
            settings = Settings()
            db.session.add(settings)
            db.session.commit()
            print("✅ تم إنشاء الإعدادات الافتراضية")
            settings = Settings.query.first()
        
        print("\n" + "="*50)
        print("📊 الإعدادات الحالية:")
        print("="*50)
        print(f"🎨 اللون الأساسي: {settings.primary_color}")
        print(f"🎨 اللون الثانوي: {settings.secondary_color}")
        print(f"☕ عدد الأكواب المطلوبة: {settings.cups_required}")
        print(f"🖼️  مسار الشعار: {settings.logo_path if settings.logo_path else 'لا يوجد'}")
        print(f"📅 آخر تحديث: {settings.updated_at}")
        print("="*50)
        
        # التحقق من مجلد الـ uploads
        import os
        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
        if os.path.exists(upload_folder):
            files = os.listdir(upload_folder)
            print(f"\n📁 ملفات في مجلد uploads: {len(files)}")
            for f in files:
                print(f"   - {f}")
        else:
            print(f"\n❌ مجلد uploads غير موجود: {upload_folder}")
            os.makedirs(upload_folder, exist_ok=True)
            print("✅ تم إنشاء مجلد uploads")
        
        print("\n" + "="*50)

if __name__ == '__main__':
    test_settings()
