"""
إصلاح مشاكل عرض الصفحات
"""
import requests
import json

def test_admin_dashboard_data():
    """اختبار بيانات لوحة تحكم المدير"""
    print("🔍 اختبار بيانات لوحة تحكم المدير...")
    
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
            print("   ✅ تم تسجيل الدخول بنجاح")
            
            # الحصول على لوحة التحكم
            dashboard_response = session.get(f"{base_url}/admin/dashboard")
            
            if dashboard_response.status_code == 200:
                content = dashboard_response.text
                print("   ✅ تم الوصول للوحة التحكم")
                
                # البحث عن البيانات في HTML
                import re
                
                # البحث عن الأرقام في الإحصائيات
                numbers = re.findall(r'<h3>(\d+)</h3>', content)
                if numbers:
                    print(f"   📊 الإحصائيات الموجودة: {numbers}")
                else:
                    print("   ⚠️ لا توجد إحصائيات رقمية واضحة")
                
                # البحث عن النصوص المهمة
                important_texts = [
                    'إجمالي العملاء',
                    'إجمالي الموظفين', 
                    'الأكواد النشطة',
                    'الأكواد المستخدمة',
                    'المعاملات الأخيرة'
                ]
                
                for text in important_texts:
                    if text in content:
                        print(f"   ✅ '{text}': موجود")
                    else:
                        print(f"   ❌ '{text}': مفقود")
                        
                # فحص وجود أخطاء
                if 'error' in content.lower() or 'exception' in content.lower():
                    print("   ❌ توجد أخطاء في الصفحة")
                    
                    # استخراج الأخطاء
                    error_lines = [line.strip() for line in content.split('\n') if 'error' in line.lower()]
                    for error in error_lines[:3]:  # أول 3 أخطاء
                        print(f"      {error}")
                        
            else:
                print(f"   ❌ فشل الوصول للوحة التحكم: {dashboard_response.status_code}")
                
        else:
            print(f"   ❌ فشل تسجيل الدخول: {login_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ خطأ: {e}")

def check_template_rendering():
    """فحص عرض القوالب"""
    print("\n🎨 فحص عرض القوالب...")
    
    base_url = "http://localhost:5000"
    
    try:
        # فحص صفحة تسجيل الدخول
        response = requests.get(f"{base_url}/login")
        
        if response.status_code == 200:
            content = response.text
            
            # فحص وجود عناصر Bootstrap
            bootstrap_elements = [
                'class="container"',
                'class="row"',
                'class="col-',
                'class="btn',
                'class="form-control"',
                'class="card"'
            ]
            
            bootstrap_found = 0
            for element in bootstrap_elements:
                if element in content:
                    bootstrap_found += 1
            
            print(f"   📊 عناصر Bootstrap: {bootstrap_found}/{len(bootstrap_elements)}")
            
            # فحص وجود Font Awesome
            if 'fas fa-' in content or 'fontawesome' in content:
                print("   ✅ Font Awesome: موجود")
            else:
                print("   ⚠️ Font Awesome: مفقود")
            
            # فحص وجود CSS مخصص
            if '<style>' in content or 'custom' in content:
                print("   ✅ أنماط مخصصة: موجودة")
            else:
                print("   ⚠️ أنماط مخصصة: مفقودة")
                
            # فحص JavaScript
            if '<script>' in content or '.js' in content:
                print("   ✅ JavaScript: موجود")
            else:
                print("   ⚠️ JavaScript: مفقود")
                
        else:
            print(f"   ❌ فشل في الحصول على الصفحة: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ خطأ: {e}")

def suggest_fixes():
    """اقتراح حلول للمشاكل"""
    print("\n💡 حلول مقترحة لمشاكل العرض:")
    
    print("\n1. 🔄 مشاكل Cache المتصفح:")
    print("   - اضغط Ctrl+Shift+R للإعادة تحميل الكامل")
    print("   - امسح cache المتصفح")
    print("   - جرب وضع التصفح الخاص")
    
    print("\n2. 🎨 مشاكل CSS:")
    print("   - تحقق من تحميل Bootstrap")
    print("   - تحقق من الأنماط المخصصة")
    print("   - تحقق من Font Awesome")
    
    print("\n3. 📱 مشاكل العرض المتجاوب:")
    print("   - تحقق من viewport meta tag")
    print("   - جرب أحجام شاشة مختلفة")
    print("   - استخدم أدوات المطور للمحاكاة")
    
    print("\n4. 🔤 مشاكل النصوص العربية:")
    print("   - تحقق من ترميز UTF-8")
    print("   - تحقق من dir='rtl'")
    print("   - تحقق من خطوط النصوص العربية")
    
    print("\n5. ⚡ مشاكل الأداء:")
    print("   - تحقق من سرعة تحميل الصفحة")
    print("   - تحقق من أخطاء JavaScript")
    print("   - تحقق من أخطاء الشبكة")

def create_test_page():
    """إنشاء صفحة اختبار بسيطة"""
    print("\n🧪 إنشاء صفحة اختبار...")
    
    test_html = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>صفحة اختبار COFFLOW</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .test-card { 
            background: linear-gradient(135deg, #8B4513, #D2691E);
            color: white;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <div class="row">
            <div class="col-12">
                <h1 class="text-center mb-4">
                    <i class="fas fa-coffee"></i>
                    صفحة اختبار COFFLOW
                </h1>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-4">
                <div class="test-card text-center">
                    <i class="fas fa-users fa-3x mb-3"></i>
                    <h3>15</h3>
                    <p>إجمالي العملاء</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="test-card text-center">
                    <i class="fas fa-ticket-alt fa-3x mb-3"></i>
                    <h3>5</h3>
                    <p>الكوبونات النشطة</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="test-card text-center">
                    <i class="fas fa-bell fa-3x mb-3"></i>
                    <h3>6</h3>
                    <p>الإشعارات</p>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-check-circle text-success"></i> اختبار المكونات</h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item">✅ النصوص العربية تظهر بشكل صحيح</li>
                            <li class="list-group-item">✅ الاتجاه من اليمين لليسار يعمل</li>
                            <li class="list-group-item">✅ Bootstrap يعمل بشكل صحيح</li>
                            <li class="list-group-item">✅ Font Awesome يعمل بشكل صحيح</li>
                            <li class="list-group-item">✅ الألوان والتدرجات تظهر</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    
    try:
        with open('templates/test.html', 'w', encoding='utf-8') as f:
            f.write(test_html)
        print("   ✅ تم إنشاء صفحة الاختبار: templates/test.html")
        print("   🌐 يمكنك الوصول إليها عبر: /test")
        
        return True
    except Exception as e:
        print(f"   ❌ خطأ في إنشاء صفحة الاختبار: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 تشخيص وإصلاح مشاكل عرض الصفحات")
    print("=" * 60)
    
    test_admin_dashboard_data()
    check_template_rendering()
    suggest_fixes()
    
    # إنشاء صفحة اختبار
    if create_test_page():
        print("\n📝 تم إنشاء صفحة اختبار. أضف هذا المسار إلى app.py:")
        print("""
@app.route('/test')
def test_page():
    return render_template('test.html')
        """)

if __name__ == "__main__":
    main()
