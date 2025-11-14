"""
إصلاح مشاكل حساب المدير ومسار الكوبونات
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash

def fix_admin_email():
    """إصلاح مشكلة البريد المكرر للمدير"""
    print("🔧 إصلاح مشكلة بريد المدير...")
    
    conn = sqlite3.connect('instance/cofflow.db')
    cursor = conn.cursor()
    
    try:
        # البحث عن حساب المدير الحالي
        cursor.execute("SELECT id, phone, email FROM users WHERE role = 'admin'")
        admins = cursor.fetchall()
        
        print(f"   وجدنا {len(admins)} حساب مدير:")
        for admin in admins:
            print(f"      ID: {admin[0]}, Phone: {admin[1]}, Email: {admin[2]}")
        
        # إذا كان هناك أكثر من مدير، نحتفظ بواحد فقط
        if len(admins) > 1:
            # نحتفظ بالمدير الأول فقط
            admin_id_to_keep = admins[0][0]
            
            # حذف بقية المدراء
            for admin in admins[1:]:
                cursor.execute("DELETE FROM users WHERE id = ?", (admin[0],))
            
            print(f"   ✅ تم الاحتفاظ بالمدير رقم {admin_id_to_keep} وحذف البقية")
        
        # التأكد من أن بيانات المدير الصحيحة
        if len(admins) > 0:
            cursor.execute("""
            UPDATE users 
            SET phone = '0544482434', 
                email = 'admin@cofflow.com',
                name = 'مدير النظام',
                password_hash = ? 
            WHERE role = 'admin'
            """, (generate_password_hash('admin123'),))
            
            print("   ✅ تم تحديث بيانات المدير")
            print("   👤 بيانات المدير الآن: 0544482434 / admin123")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def add_missing_routes():
    """إضافة المسارات المفقودة"""
    print("\n🔧 إضافة المسارات المفقودة...")
    
    # كود مسار الكوبونات
    coupons_route_code = """
@app.route('/admin/coupons')
@login_required
@admin_required
def admin_coupons():
    \"\"\"صفحة إدارة الكوبونات\"\"\"
    
    # استرجاع الكوبونات مع معلومات العملاء
    coupons = db.session.query(Coupon, User)\\
        .join(User, User.id == Coupon.customer_id)\\
        .order_by(Coupon.created_at.desc())\\
        .all()
    
    # تصنيف الكوبونات
    active_coupons = [coupon for coupon, user in coupons if coupon.status == 'active']
    used_coupons = [coupon for coupon, user in coupons if coupon.status == 'used']
    
    return render_template('admin/coupons.html', 
        coupons=coupons, 
        active_coupons=active_coupons,
        used_coupons=used_coupons,
        current_time=datetime.utcnow())
"""
    
    # قراءة ملف app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # البحث عن مكان مناسب لإضافة المسار (بعد admin_transactions)
    import re
    transactions_match = re.search(r'def admin_transactions\(\):.*?(?=@app\.route|def\s|$)', app_content, re.DOTALL)
    
    if transactions_match:
        # إضافة المسار بعد admin_transactions مباشرةً
        transactions_end = transactions_match.end()
        
        # التحقق من وجود المسار بالفعل
        if '@app.route(\'/admin/coupons\')' not in app_content:
            new_content = app_content[:transactions_end] + coupons_route_code + app_content[transactions_end:]
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("   ✅ تم إضافة مسار الكوبونات")
            return True
        else:
            print("   ✅ مسار الكوبونات موجود بالفعل")
            return True
    else:
        print("   ❌ لم يتم العثور على مكان مناسب لإضافة المسار")
        return False

def create_coupons_template():
    """إنشاء قالب الكوبونات"""
    print("\n📝 إنشاء قالب الكوبونات...")
    
    # إنشاء مجلد admin إذا لم يكن موجوداً
    os.makedirs('templates/admin', exist_ok=True)
    
    # محتوى قالب الكوبونات
    coupons_template = """{% extends "base.html" %}

{% block title %}إدارة الكوبونات - COFFLOW{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2><i class="fas fa-ticket-alt"></i> إدارة الكوبونات</h2>
        <a href="{{ url_for('admin_dashboard') }}" class="btn btn-outline-primary">
            <i class="fas fa-arrow-right"></i> العودة للوحة التحكم
        </a>
    </div>
    
    <div class="row mb-4">
        <div class="col-md-4">
            <div class="stat-card">
                <i class="fas fa-ticket-alt"></i>
                <h3>{{ active_coupons|length }}</h3>
                <p>الكوبونات النشطة</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="stat-card">
                <i class="fas fa-check-circle"></i>
                <h3>{{ used_coupons|length }}</h3>
                <p>الكوبونات المستخدمة</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="stat-card">
                <i class="fas fa-calendar"></i>
                <h3>{{ coupons|length }}</h3>
                <p>إجمالي الكوبونات</p>
            </div>
        </div>
    </div>
    
    <ul class="nav nav-tabs mb-4" id="couponsTab" role="tablist">
        <li class="nav-item">
            <a class="nav-link active" id="active-tab" data-bs-toggle="tab" href="#active" role="tab">
                <i class="fas fa-check-circle text-success"></i> الكوبونات النشطة
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link" id="used-tab" data-bs-toggle="tab" href="#used" role="tab">
                <i class="fas fa-times-circle text-secondary"></i> الكوبونات المستخدمة
            </a>
        </li>
    </ul>
    
    <div class="tab-content" id="couponsTabContent">
        <!-- الكوبونات النشطة -->
        <div class="tab-pane fade show active" id="active" role="tabpanel">
            {% if active_coupons %}
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>رمز الكوبون</th>
                            <th>العميل</th>
                            <th>تاريخ الإنشاء</th>
                            <th>العمليات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for coupon, user in coupons if coupon.status == 'active' %}
                        <tr>
                            <td>
                                <span class="badge bg-success">{{ coupon.code }}</span>
                            </td>
                            <td>{{ user.name }}</td>
                            <td>{{ coupon.created_at.strftime('%d/%m/%Y') }}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-danger">
                                    <i class="fas fa-times"></i> إلغاء
                                </button>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <div class="text-center text-muted my-5">
                <i class="fas fa-ticket-alt fa-4x mb-3"></i>
                <h5>لا توجد كوبونات نشطة</h5>
            </div>
            {% endif %}
        </div>
        
        <!-- الكوبونات المستخدمة -->
        <div class="tab-pane fade" id="used" role="tabpanel">
            {% if used_coupons %}
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>رمز الكوبون</th>
                            <th>العميل</th>
                            <th>تاريخ الإنشاء</th>
                            <th>تاريخ الاستخدام</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for coupon, user in coupons if coupon.status == 'used' %}
                        <tr>
                            <td>
                                <span class="badge bg-secondary">{{ coupon.code }}</span>
                            </td>
                            <td>{{ user.name }}</td>
                            <td>{{ coupon.created_at.strftime('%d/%m/%Y') }}</td>
                            <td>{{ coupon.used_at.strftime('%d/%m/%Y') if coupon.used_at else '-' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <div class="text-center text-muted my-5">
                <i class="fas fa-check-circle fa-4x mb-3"></i>
                <h5>لا توجد كوبونات مستخدمة</h5>
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
"""
    
    # كتابة القالب
    if os.path.exists('templates/admin/coupons.html'):
        print("   ✅ قالب الكوبونات موجود بالفعل")
    else:
        with open('templates/admin/coupons.html', 'w', encoding='utf-8') as f:
            f.write(coupons_template)
        print("   ✅ تم إنشاء قالب الكوبونات")
    
    return True

def main():
    """الدالة الرئيسية"""
    print("🔧 إصلاح مشاكل حساب المدير ومسار الكوبونات")
    print("=" * 50)
    
    # إصلاح بريد المدير
    admin_fixed = fix_admin_email()
    
    # إضافة مسار الكوبونات
    routes_fixed = add_missing_routes()
    
    # إنشاء قالب الكوبونات
    template_created = create_coupons_template()
    
    print("\n" + "=" * 50)
    print("📊 نتائج الإصلاح:")
    print(f"   حساب المدير: {'✅ تم إصلاحه' if admin_fixed else '❌ فشل الإصلاح'}")
    print(f"   مسار الكوبونات: {'✅ تم إضافته' if routes_fixed else '❌ فشل الإضافة'}")
    print(f"   قالب الكوبونات: {'✅ تم إنشاؤه' if template_created else '❌ فشل الإنشاء'}")
    
    if admin_fixed and routes_fixed and template_created:
        print("\n🎉 تم إصلاح جميع المشاكل!")
        print("💡 أعد تشغيل الخادم لرؤية التغييرات:")
        print("   1. أوقف الخادم (Ctrl+C)")
        print("   2. شغل: python app.py")
    else:
        print("\n⚠️ بعض الإصلاحات فشلت. تحقق من الأخطاء أعلاه.")

if __name__ == "__main__":
    main()
