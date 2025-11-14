"""
تشخيص مشكلة لوحة تحكم المدير
"""
from app import app
from models import db, User, Coupon, Transaction, Settings

def debug_admin_dashboard():
    """تشخيص بيانات لوحة تحكم المدير"""
    print("🔍 تشخيص بيانات لوحة تحكم المدير...")
    
    with app.app_context():
        try:
            # فحص الإعدادات
            settings = Settings.query.first()
            print(f"⚙️ الإعدادات: {'موجودة' if settings else 'مفقودة'}")
            
            # فحص العملاء
            total_customers = User.query.filter_by(role='customer').count()
            print(f"👥 إجمالي العملاء: {total_customers}")
            
            # فحص الموظفين
            total_employees = User.query.filter_by(role='employee').count()
            print(f"👷 إجمالي الموظفين: {total_employees}")
            
            # فحص الكوبونات
            active_coupons = Coupon.query.filter_by(status='active').count()
            used_coupons = Coupon.query.filter_by(status='used').count()
            print(f"🎫 الكوبونات النشطة: {active_coupons}")
            print(f"🎫 الكوبونات المستخدمة: {used_coupons}")
            
            # فحص المعاملات
            total_transactions = Transaction.query.count()
            recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(10).all()
            print(f"💳 إجمالي المعاملات: {total_transactions}")
            print(f"💳 المعاملات الأخيرة: {len(recent_transactions)}")
            
            # طباعة بعض المعاملات الأخيرة
            if recent_transactions:
                print("📋 آخر 3 معاملات:")
                for i, transaction in enumerate(recent_transactions[:3]):
                    customer = User.query.get(transaction.customer_id)
                    employee = User.query.get(transaction.employee_id)
                    print(f"   {i+1}. {customer.name if customer else 'غير معروف'} - {transaction.transaction_type} - {transaction.created_at}")
            
            return {
                'settings': settings,
                'total_customers': total_customers,
                'total_employees': total_employees,
                'active_coupons': active_coupons,
                'used_coupons': used_coupons,
                'recent_transactions': recent_transactions
            }
            
        except Exception as e:
            print(f"❌ خطأ: {e}")
            import traceback
            traceback.print_exc()
            return None

def test_template_rendering():
    """اختبار عرض القالب"""
    print("\n🎨 اختبار عرض قالب لوحة التحكم...")
    
    with app.app_context():
        try:
            from flask import render_template_string
            
            # قالب مبسط للاختبار
            test_template = """
            <h1>لوحة تحكم المدير</h1>
            <div>إجمالي العملاء: {{ total_customers }}</div>
            <div>إجمالي الموظفين: {{ total_employees }}</div>
            <div>الكوبونات النشطة: {{ active_coupons }}</div>
            <div>الكوبونات المستخدمة: {{ used_coupons }}</div>
            """
            
            # الحصول على البيانات
            data = debug_admin_dashboard()
            
            if data:
                # عرض القالب
                rendered = render_template_string(test_template, **data)
                print("✅ تم عرض القالب بنجاح:")
                print(rendered)
                
                return True
            else:
                print("❌ فشل في الحصول على البيانات")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في عرض القالب: {e}")
            return False

if __name__ == "__main__":
    debug_admin_dashboard()
    test_template_rendering()
