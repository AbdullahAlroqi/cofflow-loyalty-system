"""
فحص شامل لجميع مكونات النظام
"""
import os
import sqlite3
from datetime import datetime

def comprehensive_system_check():
    print("🔍 فحص شامل لنظام COFFLOW")
    print("=" * 50)
    
    # 1. فحص الملفات الأساسية
    print("\n📁 الملفات الأساسية:")
    essential_files = {
        'app.py': 'الملف الرئيسي للتطبيق',
        'models.py': 'نماذج قاعدة البيانات',
        'config.py': 'إعدادات التطبيق',
        'cofflow.db': 'قاعدة البيانات',
        'requirements.txt': 'متطلبات Python'
    }
    
    for file_path, description in essential_files.items():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} - {description} ({size:,} bytes)")
        else:
            print(f"   ❌ {file_path} - {description} (مفقود)")
    
    # 2. فحص ملفات القوالب
    print("\n📄 ملفات القوالب:")
    template_files = {
        'templates/base.html': 'القالب الأساسي',
        'templates/index.html': 'الصفحة الرئيسية',
        'templates/login.html': 'صفحة تسجيل الدخول',
        'templates/admin/dashboard.html': 'لوحة تحكم المدير',
        'templates/customer/dashboard.html': 'لوحة تحكم العميل',
        'templates/employee/dashboard.html': 'لوحة تحكم الموظف',
        'templates/admin/notifications.html': 'إدارة الإشعارات',
        'templates/customer/notifications.html': 'إشعارات العميل'
    }
    
    for file_path, description in template_files.items():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} - {description} ({size:,} bytes)")
        else:
            print(f"   ❌ {file_path} - {description} (مفقود)")
    
    # 3. فحص ملفات PWA
    print("\n📱 ملفات PWA:")
    pwa_files = {
        'static/manifest.json': 'ملف Manifest',
        'static/sw.js': 'Service Worker',
        'static/pwa.js': 'سكريبت PWA',
        'static/icons/icon-192x192.png': 'أيقونة 192x192',
        'static/icons/icon-512x512.png': 'أيقونة 512x512'
    }
    
    for file_path, description in pwa_files.items():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} - {description} ({size:,} bytes)")
        else:
            print(f"   ❌ {file_path} - {description} (مفقود)")
    
    # 4. فحص ملفات الإشعارات
    print("\n🔔 ملفات الإشعارات:")
    notification_files = {
        'api_notifications.py': 'واجهة برمجة تطبيقات الإشعارات',
        'notifications.py': 'مدير الإشعارات'
    }
    
    for file_path, description in notification_files.items():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} - {description} ({size:,} bytes)")
        else:
            print(f"   ❌ {file_path} - {description} (مفقود)")
    
    # 5. فحص قاعدة البيانات
    print("\n💾 قاعدة البيانات:")
    if os.path.exists('cofflow.db'):
        conn = sqlite3.connect('cofflow.db')
        cursor = conn.cursor()
        
        # فحص الجداول
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"   📊 عدد الجداول: {len(tables)}")
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   📋 {table[0]}: {count:,} سجل")
        
        # فحص المستخدمين
        cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
        user_roles = cursor.fetchall()
        
        print(f"\n   👥 المستخدمون حسب الدور:")
        for role, count in user_roles:
            print(f"      {role}: {count}")
        
        conn.close()
    else:
        print("   ❌ قاعدة البيانات غير موجودة")
    
    # 6. فحص سكريبتات الإدارة
    print("\n🛠️ سكريبتات الإدارة:")
    admin_scripts = {
        'system_manager.py': 'مدير النظام الشامل',
        'check_database.py': 'فحص قاعدة البيانات',
        'test_login.py': 'اختبار تسجيل الدخول',
        'enable_notifications.py': 'تفعيل الإشعارات'
    }
    
    for file_path, description in admin_scripts.items():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} - {description} ({size:,} bytes)")
        else:
            print(f"   ❌ {file_path} - {description} (مفقود)")
    
    # 7. تقييم عام للنظام
    print("\n" + "=" * 50)
    print("📊 تقييم عام للنظام:")
    
    # حساب النسبة المئوية للملفات الموجودة
    all_files = {**essential_files, **template_files, **pwa_files, **notification_files, **admin_scripts}
    existing_files = sum(1 for file_path in all_files.keys() if os.path.exists(file_path))
    total_files = len(all_files)
    completion_percentage = (existing_files / total_files) * 100
    
    print(f"📁 الملفات: {existing_files}/{total_files} ({completion_percentage:.1f}%)")
    
    if completion_percentage >= 90:
        print("🎉 النظام مكتمل وجاهز للاستخدام!")
    elif completion_percentage >= 75:
        print("⚠️ النظام شبه مكتمل - بعض الملفات مفقودة")
    else:
        print("❌ النظام غير مكتمل - ملفات مهمة مفقودة")
    
    # 8. توصيات
    print("\n💡 التوصيات:")
    
    if not os.path.exists('cofflow.db'):
        print("   🔧 قم بتشغيل fix_database.py لإنشاء قاعدة البيانات")
    
    if not os.path.exists('api_notifications.py'):
        print("   🔔 قم بتشغيل enable_notifications.py لتفعيل الإشعارات")
    
    if completion_percentage >= 90:
        print("   🚀 يمكنك تشغيل النظام بـ: python app.py")
        print("   🌐 ثم زيارة: http://localhost:5000")
        print("   👤 تسجيل الدخول: 0544482434 / admin123")
    
    print("\n" + "=" * 50)
    print(f"✅ انتهى الفحص الشامل - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    comprehensive_system_check()
