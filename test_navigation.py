"""
اختبار التنقل والوصول للصفحات
"""
import requests
import time

def test_navigation():
    base_url = "http://localhost:5000"
    
    print("🧪 اختبار التنقل...")
    
    # إنشاء جلسة
    session = requests.Session()
    
    try:
        # 1. اختبار الصفحة الرئيسية
        print("\n1. اختبار الصفحة الرئيسية...")
        response = session.get(f"{base_url}/", allow_redirects=False)
        print(f"   الحالة: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"   إعادة توجيه إلى: {redirect_url}")
        
        # 2. اختبار صفحة تسجيل الدخول مباشرة
        print("\n2. اختبار صفحة تسجيل الدخول...")
        response = session.get(f"{base_url}/login", allow_redirects=False)
        print(f"   الحالة: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ صفحة تسجيل الدخول متاحة")
            
            # محاولة تسجيل الدخول
            print("\n3. محاولة تسجيل الدخول...")
            login_data = {
                'phone': '0544482434',
                'password': 'admin123'
            }
            
            response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
            print(f"   حالة تسجيل الدخول: {response.status_code}")
            
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                print(f"   إعادة توجيه بعد تسجيل الدخول: {redirect_url}")
                
                # متابعة إعادة التوجيه
                if redirect_url:
                    if redirect_url.startswith('/'):
                        redirect_url = base_url + redirect_url
                    
                    print(f"\n4. متابعة إعادة التوجيه إلى: {redirect_url}")
                    response = session.get(redirect_url, allow_redirects=False)
                    print(f"   حالة الصفحة النهائية: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("   ✅ تم الوصول للوحة التحكم بنجاح")
                    elif response.status_code == 302:
                        next_redirect = response.headers.get('Location', '')
                        print(f"   ⚠️ إعادة توجيه أخرى إلى: {next_redirect}")
                    else:
                        print(f"   ❌ خطأ في الوصول للوحة التحكم: {response.status_code}")
            else:
                print("   ❌ فشل تسجيل الدخول")
        else:
            print(f"   ❌ مشكلة في صفحة تسجيل الدخول: {response.status_code}")
        
        # 5. اختبار الوصول المباشر للوحة تحكم المدير
        print("\n5. اختبار الوصول المباشر للوحة تحكم المدير...")
        response = session.get(f"{base_url}/admin/dashboard", allow_redirects=False)
        print(f"   الحالة: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ الوصول مباشر للوحة تحكم المدير")
        elif response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"   إعادة توجيه إلى: {redirect_url}")
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")

if __name__ == "__main__":
    test_navigation()
