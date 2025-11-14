"""
فحص شامل لمصدر البيانات والترابط بين الصفحات
"""
import sqlite3
import os
import requests
from datetime import datetime

def check_database_files():
    """فحص ملفات قاعدة البيانات"""
    print("🔍 فحص ملفات قاعدة البيانات...")
    
    db_files = [
        'cofflow.db',
        'instance/cofflow.db',
        'instance/database.db'
    ]
    
    active_db = None
    
    for db_file in db_files:
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            print(f"\n📁 {db_file}:")
            print(f"   الحجم: {size:,} بايت")
            
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # فحص الجداول
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [table[0] for table in cursor.fetchall()]
                print(f"   الجداول: {tables}")
                
                # فحص البيانات
                data_summary = {}
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        data_summary[table] = count
                    except:
                        data_summary[table] = "خطأ"
                
                print(f"   البيانات: {data_summary}")
                
                # تحديد قاعدة البيانات النشطة
                if data_summary.get('users', 0) > 1:  # أكثر من مستخدم واحد
                    active_db = db_file
                    print(f"   🎯 هذه قاعدة البيانات النشطة المحتملة")
                
                conn.close()
                
            except Exception as e:
                print(f"   ❌ خطأ: {e}")
        else:
            print(f"❌ {db_file}: غير موجود")
    
    return active_db

def check_app_database_connection():
    """فحص اتصال التطبيق بقاعدة البيانات"""
    print("\n🔗 فحص اتصال التطبيق بقاعدة البيانات...")
    
    try:
        # قراءة config.py
        with open('config.py', 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        print("📄 إعدادات قاعدة البيانات في config.py:")
        for line_num, line in enumerate(config_content.split('\n'), 1):
            if 'DATABASE_URI' in line or 'sqlite' in line.lower():
                print(f"   السطر {line_num}: {line.strip()}")
        
        # استخراج مسار قاعدة البيانات
        if 'sqlite:///cofflow.db' in config_content:
            expected_db = 'cofflow.db'
        elif 'sqlite:///instance/cofflow.db' in config_content:
            expected_db = 'instance/cofflow.db'
        else:
            expected_db = "غير محدد"
        
        print(f"📍 قاعدة البيانات المتوقعة: {expected_db}")
        
        return expected_db
        
    except Exception as e:
        print(f"❌ خطأ في قراءة الإعدادات: {e}")
        return None

def test_live_data_access():
    """اختبار الوصول للبيانات المباشرة"""
    print("\n🧪 اختبار الوصول للبيانات المباشرة...")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        # تسجيل الدخول كمدير
        login_data = {
            'phone': '0544482434',
            'password': 'admin123'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code == 200:
            print("✅ تم تسجيل الدخول بنجاح")
            
            # الوصول للوحة التحكم
            dashboard_response = session.get(f"{base_url}/admin/dashboard")
            
            if dashboard_response.status_code == 200:
                content = dashboard_response.text
                print("✅ تم الوصول للوحة التحكم")
                
                # البحث عن البيانات في HTML
                import re
                
                # البحث عن الأرقام
                numbers = re.findall(r'<h3[^>]*>(\d+)</h3>', content)
                print(f"📊 الأرقام الموجودة في الصفحة: {numbers}")
                
                # البحث عن النصوص المهمة
                important_checks = [
                    ('إجمالي العملاء', 'total_customers'),
                    ('إجمالي الموظفين', 'total_employees'),
                    ('الأكواد النشطة', 'active_coupons'),
                    ('الأكواد المستخدمة', 'used_coupons')
                ]
                
                for text, var in important_checks:
                    if text in content:
                        print(f"   ✅ '{text}': موجود في الصفحة")
                    else:
                        print(f"   ❌ '{text}': مفقود من الصفحة")
                
                # فحص وجود أخطاء
                if 'error' in content.lower() or 'traceback' in content.lower():
                    print("❌ توجد أخطاء في الصفحة")
                    
                    # استخراج الأخطاء
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'error' in line.lower() or 'traceback' in line.lower():
                            print(f"      خطأ في السطر {i}: {line.strip()[:100]}")
                            break
                else:
                    print("✅ لا توجد أخطاء واضحة")
                    
            else:
                print(f"❌ فشل الوصول للوحة التحكم: {dashboard_response.status_code}")
                
        else:
            print(f"❌ فشل تسجيل الدخول: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")

def check_app_py_data_flow():
    """فحص تدفق البيانات في app.py"""
    print("\n📋 فحص تدفق البيانات في app.py...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # البحث عن دالة admin_dashboard
        import re
        
        # استخراج دالة admin_dashboard
        dashboard_match = re.search(r'def admin_dashboard\(\):(.*?)(?=def|\Z)', app_content, re.DOTALL)
        
        if dashboard_match:
            dashboard_code = dashboard_match.group(1)
            print("📄 كود دالة admin_dashboard:")
            
            # فحص الاستعلامات
            queries = [
                'User.query.filter_by(role=\'customer\').count()',
                'User.query.filter_by(role=\'employee\').count()',
                'Coupon.query.filter_by(status=\'active\').count()',
                'Coupon.query.filter_by(status=\'used\').count()'
            ]
            
            for query in queries:
                if query in dashboard_code:
                    print(f"   ✅ {query}: موجود")
                else:
                    print(f"   ❌ {query}: مفقود")
            
            # فحص render_template
            if 'render_template' in dashboard_code:
                template_match = re.search(r'render_template\([^)]+\)', dashboard_code)
                if template_match:
                    print(f"   📄 استدعاء القالب: {template_match.group()}")
            
        else:
            print("❌ لم يتم العثور على دالة admin_dashboard")
            
    except Exception as e:
        print(f"❌ خطأ في فحص app.py: {e}")

def fix_database_connection():
    """إصلاح اتصال قاعدة البيانات"""
    print("\n🔧 إصلاح اتصال قاعدة البيانات...")
    
    # التحقق من وجود قاعدة البيانات الصحيحة
    if os.path.exists('cofflow.db'):
        conn = sqlite3.connect('cofflow.db')
        cursor = conn.cursor()
        
        # فحص البيانات
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'customer'")
        customers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'employee'")
        employees = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM coupons WHERE status = 'active'")
        active_coupons = cursor.fetchone()[0]
        
        print(f"📊 البيانات في cofflow.db:")
        print(f"   العملاء: {customers}")
        print(f"   الموظفون: {employees}")
        print(f"   الكوبونات النشطة: {active_coupons}")
        
        conn.close()
        
        if customers > 0:
            print("✅ قاعدة البيانات تحتوي على بيانات")
            
            # تحديث config.py للتأكد
            config_content = """import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cofflow-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cofflow.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = 86400 * 30  # 30 يوم
    
    # إعدادات رفع الملفات
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
"""
            
            with open('config.py', 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            print("✅ تم تحديث config.py")
            return True
        else:
            print("⚠️ قاعدة البيانات فارغة")
            return False
    else:
        print("❌ cofflow.db غير موجودة")
        return False

def create_test_route():
    """إنشاء مسار اختبار للبيانات"""
    print("\n🧪 إنشاء مسار اختبار للبيانات...")
    
    test_route = """
@app.route('/test-data')
def test_data():
    \"\"\"اختبار البيانات\"\"\"
    try:
        from models import User, Coupon, Transaction, Settings
        
        # جمع البيانات
        total_customers = User.query.filter_by(role='customer').count()
        total_employees = User.query.filter_by(role='employee').count()
        active_coupons = Coupon.query.filter_by(status='active').count()
        used_coupons = Coupon.query.filter_by(status='used').count()
        total_transactions = Transaction.query.count()
        
        # إنشاء تقرير
        report = {
            'database_status': 'متصل',
            'total_customers': total_customers,
            'total_employees': total_employees,
            'active_coupons': active_coupons,
            'used_coupons': used_coupons,
            'total_transactions': total_transactions,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({
            'database_status': 'خطأ',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })
"""
    
    try:
        # قراءة app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # إضافة المسار إذا لم يكن موجوداً
        if '@app.route(\'/test-data\')' not in app_content:
            # البحث عن مكان الإدراج (قبل if __name__ == '__main__')
            insertion_point = app_content.find("if __name__ == '__main__':")
            
            if insertion_point != -1:
                new_content = (
                    app_content[:insertion_point] + 
                    test_route + 
                    "\n" + 
                    app_content[insertion_point:]
                )
                
                with open('app.py', 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print("✅ تم إضافة مسار اختبار البيانات")
                print("🌐 يمكنك الوصول إليه عبر: /test-data")
                return True
            else:
                print("❌ لم يتم العثور على نقطة الإدراج")
                return False
        else:
            print("✅ مسار اختبار البيانات موجود بالفعل")
            return True
            
    except Exception as e:
        print(f"❌ خطأ في إضافة مسار الاختبار: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔍 فحص شامل لمصدر البيانات والترابط")
    print("=" * 60)
    
    # فحص ملفات قاعدة البيانات
    active_db = check_database_files()
    
    # فحص إعدادات التطبيق
    expected_db = check_app_database_connection()
    
    # فحص تدفق البيانات في app.py
    check_app_py_data_flow()
    
    # اختبار الوصول المباشر للبيانات
    test_live_data_access()
    
    # إصلاح الاتصال إذا لزم الأمر
    if fix_database_connection():
        print("\n✅ تم إصلاح اتصال قاعدة البيانات")
    
    # إضافة مسار اختبار
    if create_test_route():
        print("\n✅ تم إضافة مسار اختبار البيانات")
    
    print("\n" + "=" * 60)
    print("📋 ملخص التشخيص:")
    print(f"   قاعدة البيانات النشطة: {active_db or 'غير محددة'}")
    print(f"   قاعدة البيانات المتوقعة: {expected_db or 'غير محددة'}")
    
    if active_db == expected_db:
        print("✅ قاعدة البيانات متطابقة")
    else:
        print("⚠️ عدم تطابق في قاعدة البيانات")
    
    print("\n💡 خطوات التحقق:")
    print("1. أعد تشغيل الخادم: python app.py")
    print("2. اختبر البيانات: /test-data")
    print("3. تحقق من لوحة التحكم: /admin/dashboard")

if __name__ == "__main__":
    main()
