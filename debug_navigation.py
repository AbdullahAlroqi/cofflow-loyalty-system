"""
سكريبت لتشخيص مشكلة التنقل
"""
from app import app
from models import db, User
from flask_login import current_user

def debug_navigation():
    print("🔍 تشخيص مشكلة التنقل...")
    
    with app.app_context():
        try:
            # فحص المستخدمين
            users = User.query.all()
            print(f"\n👥 المستخدمون في قاعدة البيانات ({len(users)}):")
            
            for user in users:
                print(f"   ID: {user.id}, الاسم: {user.name}, الهاتف: {user.phone}, الدور: {user.role}")
            
            # فحص المدير
            admin = User.query.filter_by(role='admin').first()
            if admin:
                print(f"\n👨‍💼 المدير: {admin.name} (ID: {admin.id})")
                
                # اختبار تحميل المستخدم
                loaded_user = db.session.get(User, admin.id)
                if loaded_user:
                    print(f"✅ يمكن تحميل المستخدم: {loaded_user.name}")
                    print(f"   is_authenticated: {loaded_user.is_authenticated}")
                    print(f"   is_active: {loaded_user.is_active}")
                    print(f"   is_anonymous: {loaded_user.is_anonymous}")
                else:
                    print("❌ لا يمكن تحميل المستخدم")
            
            # فحص مسارات لوحات التحكم
            print(f"\n🔍 فحص مسارات لوحات التحكم:")
            
            with app.test_client() as client:
                # محاولة الوصول للوحة تحكم المدير
                response = client.get('/admin/dashboard')
                print(f"   /admin/dashboard: {response.status_code}")
                
                response = client.get('/customer/dashboard')
                print(f"   /customer/dashboard: {response.status_code}")
                
                response = client.get('/employee/dashboard')
                print(f"   /employee/dashboard: {response.status_code}")
        
        except Exception as e:
            print(f"❌ خطأ: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_navigation()
