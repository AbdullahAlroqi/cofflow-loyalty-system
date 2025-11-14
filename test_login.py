"""
سكريبت لاختبار تسجيل الدخول
"""
import requests
import json

def test_login():
    base_url = "http://localhost:5000"
    
    print("🧪 اختبار تسجيل الدخول...")
    
    # إنشاء جلسة
    session = requests.Session()
    
    try:
        # الحصول على صفحة تسجيل الدخول
        print("1. الحصول على صفحة تسجيل الدخول...")
        login_page = session.get(f"{base_url}/login")
        print(f"   حالة الاستجابة: {login_page.status_code}")
        
        if login_page.status_code == 200:
            print("   ✅ صفحة تسجيل الدخول متاحة")
        else:
            print("   ❌ مشكلة في الوصول لصفحة تسجيل الدخول")
            return
        
        # محاولة تسجيل الدخول
        print("\n2. محاولة تسجيل الدخول...")
        login_data = {
            'phone': '0544482434',  # رقم المدير من قاعدة البيانات
            'password': 'admin123'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"   حالة الاستجابة: {login_response.status_code}")
        
        if login_response.status_code == 302:  # إعادة توجيه
            redirect_url = login_response.headers.get('Location', '')
            print(f"   ✅ تم تسجيل الدخول بنجاح - إعادة توجيه إلى: {redirect_url}")
            
            # متابعة إعادة التوجيه
            if redirect_url:
                final_response = session.get(redirect_url)
                print(f"   الصفحة النهائية: {final_response.status_code}")
                if final_response.status_code == 200:
                    print("   ✅ تم الوصول للوحة التحكم بنجاح")
                else:
                    print("   ❌ مشكلة في الوصول للوحة التحكم")
        else:
            print("   ❌ فشل تسجيل الدخول")
            print(f"   محتوى الاستجابة: {login_response.text[:200]}...")
        
        # اختبار تسجيل دخول عميل
        print("\n3. اختبار تسجيل دخول عميل...")
        customer_data = {
            'phone': '0583270028',  # رقم عميل من قاعدة البيانات
            'password': 'password123'  # كلمة مرور افتراضية
        }
        
        # تسجيل خروج أولاً
        session.get(f"{base_url}/logout")
        
        customer_response = session.post(f"{base_url}/login", data=customer_data, allow_redirects=False)
        print(f"   حالة الاستجابة: {customer_response.status_code}")
        
        if customer_response.status_code == 302:
            redirect_url = customer_response.headers.get('Location', '')
            print(f"   ✅ تم تسجيل دخول العميل - إعادة توجيه إلى: {redirect_url}")
        else:
            print("   ⚠️ قد تحتاج كلمة مرور العميل لإعادة تعيين")
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")

if __name__ == "__main__":
    test_login()
