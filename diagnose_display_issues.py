"""
تشخيص مشاكل عرض الصفحات
"""
import requests
import time

def test_page_content():
    """اختبار محتوى الصفحات"""
    print("🔍 اختبار محتوى الصفحات...")
    
    base_url = "http://localhost:5000"
    
    # انتظار قليل للتأكد من تشغيل الخادم
    time.sleep(2)
    
    try:
        # اختبار الصفحة الرئيسية
        print("\n1. اختبار الصفحة الرئيسية...")
        response = requests.get(f"{base_url}/", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print(f"   ✅ الحالة: {response.status_code}")
            print(f"   📏 حجم المحتوى: {len(content):,} حرف")
            
            # فحص العناصر المهمة
            checks = [
                ('COFFLOW', 'اسم التطبيق'),
                ('bootstrap', 'مكتبة Bootstrap'),
                ('dir="rtl"', 'الاتجاه العربي'),
                ('lang="ar"', 'اللغة العربية'),
                ('viewport', 'إعدادات العرض'),
                ('manifest.json', 'ملف PWA'),
                ('service-worker', 'Service Worker')
            ]
            
            for check, description in checks:
                if check.lower() in content.lower():
                    print(f"   ✅ {description}: موجود")
                else:
                    print(f"   ⚠️ {description}: مفقود أو غير واضح")
            
            # فحص الأخطاء المحتملة
            if 'error' in content.lower() or 'exception' in content.lower():
                print(f"   ❌ يحتوي على أخطاء")
            else:
                print(f"   ✅ لا توجد أخطاء واضحة")
                
        else:
            print(f"   ❌ الحالة: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
    
    # اختبار صفحة تسجيل الدخول
    try:
        print("\n2. اختبار صفحة تسجيل الدخول...")
        response = requests.get(f"{base_url}/login", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print(f"   ✅ الحالة: {response.status_code}")
            print(f"   📏 حجم المحتوى: {len(content):,} حرف")
            
            # فحص عناصر تسجيل الدخول
            login_checks = [
                ('تسجيل الدخول', 'عنوان الصفحة'),
                ('phone', 'حقل الهاتف'),
                ('password', 'حقل كلمة المرور'),
                ('form', 'نموذج تسجيل الدخول'),
                ('btn', 'زر الإرسال')
            ]
            
            for check, description in login_checks:
                if check.lower() in content.lower():
                    print(f"   ✅ {description}: موجود")
                else:
                    print(f"   ⚠️ {description}: مفقود أو غير واضح")
                    
        else:
            print(f"   ❌ الحالة: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ خطأ: {e}")

def test_static_resources():
    """اختبار الموارد الثابتة"""
    print("\n🎨 اختبار الموارد الثابتة...")
    
    base_url = "http://localhost:5000"
    
    resources = [
        ('/static/manifest.json', 'ملف Manifest'),
        ('/static/sw.js', 'Service Worker'),
        ('/static/pwa.js', 'سكريبت PWA'),
        ('/static/icons/icon-192x192.png', 'أيقونة 192x192'),
        ('/static/icons/icon-512x512.png', 'أيقونة 512x512')
    ]
    
    for url, name in resources:
        try:
            response = requests.get(f"{base_url}{url}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name}: {response.status_code} ({len(response.content):,} bytes)")
            else:
                print(f"   ❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: خطأ - {e}")

def test_admin_dashboard():
    """اختبار لوحة تحكم المدير"""
    print("\n👨‍💼 اختبار لوحة تحكم المدير...")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        # تسجيل الدخول
        login_data = {
            'phone': '0544482434',
            'password': 'admin123'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code == 200:
            content = login_response.text
            print(f"   ✅ تسجيل الدخول نجح")
            print(f"   📏 حجم المحتوى: {len(content):,} حرف")
            
            # فحص محتوى لوحة التحكم
            dashboard_checks = [
                ('لوحة تحكم', 'عنوان لوحة التحكم'),
                ('إحصائيات', 'قسم الإحصائيات'),
                ('العملاء', 'قسم العملاء'),
                ('الكوبونات', 'قسم الكوبونات'),
                ('الإشعارات', 'قسم الإشعارات'),
                ('chart', 'الرسوم البيانية')
            ]
            
            for check, description in dashboard_checks:
                if check in content:
                    print(f"   ✅ {description}: موجود")
                else:
                    print(f"   ⚠️ {description}: مفقود أو غير واضح")
                    
        else:
            print(f"   ❌ فشل تسجيل الدخول: {login_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ خطأ: {e}")

def check_encoding_issues():
    """فحص مشاكل الترميز"""
    print("\n🔤 فحص مشاكل الترميز...")
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/login", timeout=5)
        
        if response.status_code == 200:
            # فحص ترميز الاستجابة
            encoding = response.encoding
            print(f"   📝 ترميز الاستجابة: {encoding}")
            
            # فحص Content-Type
            content_type = response.headers.get('Content-Type', '')
            print(f"   📄 نوع المحتوى: {content_type}")
            
            # فحص النصوص العربية
            content = response.text
            arabic_chars = ['ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر']
            arabic_found = any(char in content for char in arabic_chars)
            
            if arabic_found:
                print(f"   ✅ النصوص العربية تظهر بشكل صحيح")
            else:
                print(f"   ⚠️ قد تكون هناك مشكلة في عرض النصوص العربية")
                
            # فحص meta charset
            if 'charset=utf-8' in content.lower():
                print(f"   ✅ ترميز UTF-8 محدد في HTML")
            else:
                print(f"   ⚠️ ترميز UTF-8 قد يكون مفقود")
                
        else:
            print(f"   ❌ فشل في الحصول على الصفحة: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ خطأ: {e}")

def main():
    """الدالة الرئيسية"""
    print("🔍 تشخيص شامل لمشاكل عرض الصفحات")
    print("=" * 60)
    
    test_page_content()
    test_static_resources()
    test_admin_dashboard()
    check_encoding_issues()
    
    print("\n" + "=" * 60)
    print("📋 ملخص التشخيص:")
    print("   إذا كانت جميع الاختبارات تمر، فالمشكلة قد تكون:")
    print("   1. 🌐 مشكلة في المتصفح (cache أو إعدادات)")
    print("   2. 🎨 مشكلة في تحميل CSS أو JavaScript")
    print("   3. 📱 مشكلة في عرض الهاتف المحمول")
    print("   4. 🔤 مشكلة في ترميز النصوص")
    
    print("\n💡 حلول مقترحة:")
    print("   - اضغط Ctrl+Shift+R لإعادة تحميل كامل")
    print("   - افتح أدوات المطور (F12) وتحقق من الأخطاء")
    print("   - جرب متصفح مختلف")
    print("   - تحقق من إعدادات اللغة في المتصفح")

if __name__ == "__main__":
    main()
