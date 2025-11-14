"""
سكريبت لإعادة تعيين الألوان إلى اللون البني الافتراضي (لون القهوة)
"""

from app import app
from models import db, Settings

def reset_colors():
    with app.app_context():
        settings = Settings.query.first()
        
        if not settings:
            print("❌ لا توجد إعدادات!")
            settings = Settings()
            db.session.add(settings)
        
        # إعادة تعيين الألوان إلى البني الافتراضي
        settings.primary_color = '#514f4b'      # بني غامق (SaddleBrown)
        settings.secondary_color = '#514f4b'    # برتقالي بني (Chocolate)
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("🎨 تم إعادة تعيين الألوان إلى اللون البني الافتراضي")
        print("="*50)
        print(f"✅ اللون الأساسي: {settings.primary_color} (بني غامق)")
        print(f"✅ اللون الثانوي: {settings.secondary_color} (برتقالي بني)")
        print("="*50)
        print("\n💡 الآن أعد تحميل الموقع بـ Ctrl+F5 لرؤية التغيير")
        print("\n" + "="*50)

if __name__ == '__main__':
    reset_colors()
