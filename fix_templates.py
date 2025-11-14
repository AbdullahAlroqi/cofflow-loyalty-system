"""
إصلاح مشاكل القوالب والأنماط
"""
import os
import requests

def check_template_files():
    """فحص ملفات القوالب"""
    print("📄 فحص ملفات القوالب...")
    
    template_files = [
        'templates/base.html',
        'templates/index.html', 
        'templates/login.html',
        'templates/admin/dashboard.html',
        'templates/customer/dashboard.html',
        'templates/employee/dashboard.html',
        'templates/admin/notifications.html',
        'templates/customer/notifications.html'
    ]
    
    for template in template_files:
        if os.path.exists(template):
            size = os.path.getsize(template)
            print(f"   ✅ {template} ({size:,} bytes)")
        else:
            print(f"   ❌ {template} - مفقود")

def check_static_files():
    """فحص الملفات الثابتة"""
    print("\n🎨 فحص الملفات الثابتة...")
    
    static_files = [
        'static/manifest.json',
        'static/sw.js',
        'static/pwa.js',
        'static/icons/icon-192x192.png',
        'static/icons/icon-512x512.png'
    ]
    
    for static_file in static_files:
        if os.path.exists(static_file):
            size = os.path.getsize(static_file)
            print(f"   ✅ {static_file} ({size:,} bytes)")
        else:
            print(f"   ❌ {static_file} - مفقود")

def test_page_responses():
    """اختبار استجابات الصفحات"""
    print("\n🌐 اختبار استجابات الصفحات...")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # اختبار الصفحات العامة
    pages = [
        ('/', 'الصفحة الرئيسية'),
        ('/login', 'صفحة تسجيل الدخول'),
        ('/register', 'صفحة التسجيل'),
        ('/manifest.json', 'ملف Manifest'),
        ('/sw.js', 'Service Worker')
    ]
    
    for url, name in pages:
        try:
            response = session.get(f"{base_url}{url}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name}: {response.status_code}")
                
                # فحص المحتوى
                content = response.text
                if url == '/':
                    if 'COFFLOW' in content:
                        print(f"      ✅ يحتوي على اسم التطبيق")
                    else:
                        print(f"      ⚠️ لا يحتوي على اسم التطبيق")
                        
                elif url == '/login':
                    if 'تسجيل الدخول' in content:
                        print(f"      ✅ يحتوي على نموذج تسجيل الدخول")
                    else:
                        print(f"      ⚠️ لا يحتوي على نموذج تسجيل الدخول")
                        
            elif response.status_code == 302:
                print(f"   🔄 {name}: {response.status_code} (إعادة توجيه)")
            else:
                print(f"   ❌ {name}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {name}: خطأ - {e}")

def test_admin_login():
    """اختبار تسجيل دخول المدير"""
    print("\n🔐 اختبار تسجيل دخول المدير...")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        # تسجيل الدخول
        login_data = {
            'phone': '0544482434',
            'password': 'admin123'
        }
        
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        if response.status_code == 302:
            print("   ✅ تسجيل الدخول نجح")
            
            # اختبار الوصول للوحة تحكم المدير
            redirect_url = response.headers.get('Location', '')
            if redirect_url:
                full_url = f"{base_url}{redirect_url}" if redirect_url.startswith('/') else redirect_url
                
                dashboard_response = session.get(full_url)
                if dashboard_response.status_code == 200:
                    print("   ✅ الوصول للوحة تحكم المدير نجح")
                    
                    content = dashboard_response.text
                    if 'لوحة تحكم المدير' in content or 'إحصائيات' in content:
                        print("   ✅ محتوى لوحة التحكم صحيح")
                    else:
                        print("   ⚠️ محتوى لوحة التحكم قد يكون غير صحيح")
                        
                else:
                    print(f"   ❌ فشل الوصول للوحة التحكم: {dashboard_response.status_code}")
            else:
                print("   ⚠️ لا يوجد رابط إعادة توجيه")
                
        else:
            print(f"   ❌ فشل تسجيل الدخول: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ خطأ في اختبار تسجيل الدخول: {e}")

def check_css_and_styling():
    """فحص الأنماط والتصميم"""
    print("\n🎨 فحص الأنماط والتصميم...")
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/login", timeout=5)
        if response.status_code == 200:
            content = response.text
            
            # فحص وجود Bootstrap
            if 'bootstrap' in content.lower():
                print("   ✅ Bootstrap موجود")
            else:
                print("   ⚠️ Bootstrap قد يكون مفقود")
            
            # فحص وجود أنماط مخصصة
            if 'style' in content.lower():
                print("   ✅ أنماط CSS موجودة")
            else:
                print("   ⚠️ أنماط CSS قد تكون مفقودة")
            
            # فحص الاتجاه العربي
            if 'rtl' in content.lower() or 'dir="rtl"' in content:
                print("   ✅ دعم الاتجاه العربي موجود")
            else:
                print("   ⚠️ دعم الاتجاه العربي قد يكون مفقود")
                
        else:
            print(f"   ❌ فشل في الحصول على الصفحة: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ خطأ في فحص الأنماط: {e}")

def main():
    """الدالة الرئيسية"""
    print("🔍 فحص وتشخيص مشاكل عرض الصفحات")
    print("=" * 50)
    
    check_template_files()
    check_static_files()
    test_page_responses()
    test_admin_login()
    check_css_and_styling()
    
    print("\n" + "=" * 50)
    print("📋 ملخص التشخيص:")
    print("   إذا كانت جميع الاختبارات تمر بنجاح، فالمشكلة قد تكون:")
    print("   1. مشكلة في المتصفح (cache)")
    print("   2. مشكلة في الأنماط CSS")
    print("   3. مشكلة في JavaScript")
    print("   4. مشكلة في ترميز النصوص")
    
    print("\n💡 حلول مقترحة:")
    print("   - امسح cache المتصفح (Ctrl+F5)")
    print("   - جرب متصفح آخر")
    print("   - تحقق من وحدة تحكم المطور (F12)")

if __name__ == "__main__":
    main()
