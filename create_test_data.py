"""
سكريبت لإنشاء بيانات تجريبية للاختبار
قم بتشغيله مرة واحدة لإضافة موظفين وعملاء تجريبيين
"""

from app import app
from models import db, User, Coupon, Transaction, Settings
from datetime import datetime, timedelta

def create_test_data():
    with app.app_context():
        print("🚀 بدء إنشاء البيانات التجريبية...")
        
        # التحقق من وجود الإدارة
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                name='مدير النظام',
                phone='0500000000',
                email='admin@cofflow.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ تم إنشاء حساب الإدارة")
        
        # إنشاء موظفين
        employees_data = [
            {'name': 'أحمد محمد', 'phone': '0501111111', 'email': 'ahmed@cofflow.com'},
            {'name': 'فاطمة علي', 'phone': '0502222222', 'email': 'fatima@cofflow.com'},
        ]
        
        employees = []
        for emp_data in employees_data:
            emp = User.query.filter_by(phone=emp_data['phone']).first()
            if not emp:
                emp = User(
                    name=emp_data['name'],
                    phone=emp_data['phone'],
                    email=emp_data['email'],
                    role='employee'
                )
                emp.set_password('123456')
                db.session.add(emp)
                employees.append(emp)
                print(f"✅ تم إنشاء موظف: {emp_data['name']}")
            else:
                employees.append(emp)
        
        # إنشاء عملاء
        customers_data = [
            {'name': 'خالد السعيد', 'phone': '0551111111', 'email': 'khaled@email.com', 'cups': 3},
            {'name': 'سارة الأحمد', 'phone': '0552222222', 'email': 'sara@email.com', 'cups': 5},
            {'name': 'محمد العتيبي', 'phone': '0553333333', 'email': 'mohammed@email.com', 'cups': 2},
            {'name': 'نورة المطيري', 'phone': '0554444444', 'email': 'noura@email.com', 'cups': 6},
            {'name': 'عبدالله الدوسري', 'phone': '0555555555', 'email': 'abdullah@email.com', 'cups': 1},
        ]
        
        customers = []
        for cust_data in customers_data:
            cust = User.query.filter_by(phone=cust_data['phone']).first()
            if not cust:
                cust = User(
                    name=cust_data['name'],
                    phone=cust_data['phone'],
                    email=cust_data['email'],
                    role='customer',
                    cups_count=cust_data['cups']
                )
                cust.set_password('123456')
                db.session.add(cust)
                customers.append(cust)
                print(f"✅ تم إنشاء عميل: {cust_data['name']} ({cust_data['cups']} أكواب)")
            else:
                customers.append(cust)
        
        db.session.commit()
        
        # إنشاء بعض العمليات التجريبية
        if employees and customers:
            print("\n📊 إنشاء عمليات تجريبية...")
            for customer in customers[:3]:
                for i in range(customer.cups_count):
                    trans = Transaction(
                        customer_id=customer.id,
                        employee_id=employees[0].id,
                        transaction_type='add_cup',
                        description='إضافة كوب',
                        created_at=datetime.utcnow() - timedelta(days=10-i)
                    )
                    db.session.add(trans)
            
            # إنشاء كوبون لعميل واحد
            if customers and customers[3].cups_count >= 6:
                coupon = Coupon(
                    customer_id=customers[3].id,
                    code='TEST1234',
                    status='active'
                )
                db.session.add(coupon)
                customers[3].cups_count = 0
                print(f"✅ تم إنشاء كوبون تجريبي: TEST1234 للعميل {customers[3].name}")
            
            db.session.commit()
            print("✅ تم إنشاء العمليات التجريبية")
        
        # التأكد من وجود الإعدادات
        settings = Settings.query.first()
        if not settings:
            settings = Settings(cups_required=6)
            db.session.add(settings)
            db.session.commit()
            print("✅ تم إنشاء الإعدادات الافتراضية")
        
        print("\n" + "="*50)
        print("🎉 تم إنشاء جميع البيانات التجريبية بنجاح!")
        print("="*50)
        print("\n📝 بيانات تسجيل الدخول:")
        print("\n🔐 الإدارة:")
        print("   الجوال: 0500000000")
        print("   كلمة المرور: admin123")
        print("\n👔 الموظفين:")
        for emp_data in employees_data:
            print(f"   {emp_data['name']}: {emp_data['phone']} / 123456")
        print("\n👤 العملاء:")
        for cust_data in customers_data:
            print(f"   {cust_data['name']}: {cust_data['phone']} / 123456")
        print("\n" + "="*50)

if __name__ == '__main__':
    create_test_data()
