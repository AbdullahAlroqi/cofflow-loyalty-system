"""
سكريبت لتعيين اللون المخصص #514f4b للموقع
"""

from app import app
from models import db, Settings

def set_custom_color():
    with app.app_context():
        settings = Settings.query.first()
        
        if not settings:
            print("❌ لا توجد إعدادات!")
            settings = Settings()
            db.session.add(settings)
        
        # تعيين اللون المخصص
        settings.primary_color = '#514f4b'      # رمادي غامق/بني رمادي
        settings.secondary_color = '#514f4b'    # نفس اللون للتناسق
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("🎨 تم تعيين اللون المخصص للموقع")
        print("="*50)
        print(f"✅ اللون الأساسي: {settings.primary_color}")
        print(f"✅ اللون الثانوي: {settings.secondary_color}")
        print("="*50)
        print("\n💡 الآن أعد تحميل الموقع بـ Ctrl+F5 لرؤية التغيير")
        print("\n" + "="*50)

if __name__ == '__main__':
    set_custom_color()
