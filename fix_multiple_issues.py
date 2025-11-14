"""
إصلاح المشاكل المتعددة:
1. مشكلة حذف الموظف
2. صفحة إرسال الإشعارات لا ترسل الإشعارات
3. استعادة تصميم صفحة تسجيل الدخول القديمة
"""
import os
import sqlite3

def fix_employee_deletion():
    """إصلاح مشكلة حذف الموظف"""
    print("🔧 إصلاح مشكلة حذف الموظف...")
    
    # قراءة ملف app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # تحديث دالة حذف الموظف لمعالجة العلاقات أولاً
    old_delete_function = """@app.route('/admin/employee/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_employee(id):
    """حذف موظف"""
    employee = User.query.get_or_404(id)
    if employee.role != 'employee':
        flash('لا يمكن حذف هذا المستخدم', 'danger')
        return redirect(url_for('admin_employees'))
    
    db.session.delete(employee)
    db.session.commit()
    flash('تم حذف الموظف بنجاح', 'success')
    return redirect(url_for('admin_employees'))"""
    
    new_delete_function = """@app.route('/admin/employee/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_employee(id):
    """حذف موظف"""
    employee = User.query.get_or_404(id)
    if employee.role != 'employee':
        flash('لا يمكن حذف هذا المستخدم', 'danger')
        return redirect(url_for('admin_employees'))
    
    try:
        # حذف جميع المعاملات المرتبطة بالموظف أو نقلها للمدير
        admin_user = User.query.filter_by(role='admin').first()
        if admin_user:
            # معالجة معاملات الموظف
            transactions = Transaction.query.filter_by(employee_id=id).all()
            for transaction in transactions:
                transaction.employee_id = admin_user.id
            
            # معالجة الكوبونات التي تم التحقق منها بواسطة الموظف
            coupons = Coupon.query.filter_by(employee_id=id).all()
            for coupon in coupons:
                coupon.employee_id = admin_user.id
                
            # معالجة علاقات أخرى قبل الحذف
            db.session.commit()
        
        # الآن يمكن حذف الموظف بأمان
        db.session.delete(employee)
        db.session.commit()
        
        flash('تم حذف الموظف بنجاح', 'success')
        return redirect(url_for('admin_employees'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف الموظف: {str(e)}', 'danger')
        return redirect(url_for('admin_employees'))"""
    
    # استبدال الدالة القديمة بالجديدة
    updated_content = app_content.replace(old_delete_function, new_delete_function)
    
    # حفظ التغييرات
    if updated_content != app_content:
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("✅ تم إصلاح دالة حذف الموظف")
        return True
    else:
        print("⚠️ لم يتم العثور على دالة حذف الموظف")
        return False

def fix_notifications_sending():
    """إصلاح مشكلة عدم إرسال الإشعارات"""
    print("\n🔧 إصلاح مشكلة إرسال الإشعارات...")
    
    # قراءة ملف api_notifications.py
    try:
        with open('api_notifications.py', 'r', encoding='utf-8') as f:
            notifications_content = f.read()
        
        # البحث عن دالة إرسال الإشعارات وإصلاحها
        old_send_function = """@notifications_api.route('/api/notifications/send', methods=['POST'])
@login_required
def send_notification():
    """إرسال إشعار جديد"""
    data = request.json
    
    if not data or 'title' not in data or 'body' not in data:
        return jsonify({'success': False, 'message': 'بيانات غير كاملة'}), 400
    
    title = data.get('title')
    body = data.get('body')
    icon = data.get('icon', '')
    url = data.get('url', '')
    recipients = data.get('recipients', [])
    
    if not recipients:
        # إذا لم يتم تحديد مستقبلين، أرسل لجميع المستخدمين
        users = User.query.filter_by(notifications_enabled=True).all()
        recipients = [user.id for user in users]
    
    # إنشاء الإشعار
    notification_manager.create_notification(
        title=title,
        body=body,
        icon=icon,
        url=url,
        sender_id=current_user.id,
        recipients=recipients
    )
    
    return jsonify({'success': True, 'message': 'تم إرسال الإشعار بنجاح'})"""
        
        new_send_function = """@notifications_api.route('/api/notifications/send', methods=['POST'])
@login_required
def send_notification():
    """إرسال إشعار جديد"""
    data = request.json
    
    if not data or 'title' not in data or 'body' not in data:
        return jsonify({'success': False, 'message': 'بيانات غير كاملة'}), 400
    
    title = data.get('title')
    body = data.get('body')
    icon = data.get('icon', '')
    url = data.get('url', '')
    recipients = data.get('recipients', [])
    
    if not recipients:
        # إذا لم يتم تحديد مستقبلين، أرسل لجميع المستخدمين
        users = User.query.filter_by(notifications_enabled=True).all()
        recipients = [user.id for user in users]
    
    try:
        # إنشاء وإرسال الإشعار
        notification = notification_manager.create_notification(
            title=title,
            body=body,
            icon=icon,
            url=url,
            sender_id=current_user.id,
            recipients=recipients
        )
        
        # التأكد من إرسال الإشعار فوراً
        success = notification_manager.send_push_notification(
            title=title,
            body=body,
            icon=icon,
            url=url,
            user_ids=recipients
        )
        
        if success:
            return jsonify({'success': True, 'message': 'تم إرسال الإشعار بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'تم حفظ الإشعار ولكن لم يتم الإرسال'})
    
    except Exception as e:
        app.logger.error(f"خطأ في إرسال الإشعار: {str(e)}")
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500"""
        
        # استبدال الدالة القديمة بالجديدة
        updated_content = notifications_content.replace(old_send_function, new_send_function)
        
        # حفظ التغييرات
        if updated_content != notifications_content:
            with open('api_notifications.py', 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print("✅ تم إصلاح دالة إرسال الإشعارات")
            return True
        else:
            # البحث عن النمط بطريقة أكثر مرونة
            import re
            pattern = r'@notifications_api\.route\(\'/api/notifications/send\'.*?jsonify\(\{\'success\': True.*?\}\)'
            matches = re.search(pattern, notifications_content, re.DOTALL)
            
            if matches:
                updated_content = notifications_content.replace(matches.group(0), new_send_function)
                with open('api_notifications.py', 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print("✅ تم إصلاح دالة إرسال الإشعارات (بنمط مرن)")
                return True
            else:
                print("⚠️ لم يتم العثور على دالة إرسال الإشعارات")
                return False
    
    except Exception as e:
        print(f"❌ خطأ في قراءة أو تحديث ملف api_notifications.py: {str(e)}")
        return False

def restore_old_login_template():
    """استعادة تصميم صفحة تسجيل الدخول القديمة"""
    print("\n🔧 استعادة تصميم صفحة تسجيل الدخول القديمة...")
    
    # استرجاع قالب تسجيل الدخول القديم
    old_login_template = """{% extends "base.html" %}

{% block title %}تسجيل الدخول - COFFLOW{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-5">
        <div class="card shadow-lg">
            <div class="card-header text-center">
                <h3 class="mb-0">
                    <i class="fas fa-sign-in-alt"></i> تسجيل الدخول
                </h3>
            </div>
            <div class="card-body p-4">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }}">
                                {{ message }}
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}

                <form method="POST" action="{{ url_for('login') }}">
                    <div class="mb-3">
                        <label for="phone" class="form-label">
                            <i class="fas fa-phone"></i> رقم الجوال
                        </label>
                        <input type="text" class="form-control form-control-lg" id="phone" name="phone" 
                               placeholder="05xxxxxxxx" required autofocus>
                    </div>
                    
                    <div class="mb-4">
                        <label for="password" class="form-label">
                            <i class="fas fa-lock"></i> كلمة المرور
                        </label>
                        <input type="password" class="form-control form-control-lg" id="password" name="password" 
                               placeholder="أدخل كلمة المرور" required>
                    </div>
                    
                    <button type="submit" class="btn btn-primary btn-lg w-100 mb-3">
                        <i class="fas fa-sign-in-alt"></i> دخول
                    </button>
                </form>
                
                <hr>
                
                <div class="text-center">
                    <p class="mb-0">ليس لديك حساب؟</p>
                    <a href="{{ url_for('register') }}" class="btn btn-outline-secondary mt-2">
                        <i class="fas fa-user-plus"></i> إنشاء حساب جديد
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
    
    # حفظ القالب القديم
    try:
        with open('templates/login.html', 'w', encoding='utf-8') as f:
            f.write(old_login_template)
        print("✅ تم استعادة تصميم صفحة تسجيل الدخول القديمة")
        return True
    except Exception as e:
        print(f"❌ خطأ في استعادة تصميم صفحة تسجيل الدخول: {str(e)}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 إصلاح المشاكل المتعددة")
    print("=" * 50)
    
    results = []
    
    # 1. إصلاح مشكلة حذف الموظف
    results.append(("إصلاح مشكلة حذف الموظف", fix_employee_deletion()))
    
    # 2. إصلاح مشكلة إرسال الإشعارات
    results.append(("إصلاح مشكلة إرسال الإشعارات", fix_notifications_sending()))
    
    # 3. استعادة تصميم صفحة تسجيل الدخول القديمة
    results.append(("استعادة تصميم صفحة تسجيل الدخول", restore_old_login_template()))
    
    print("\n" + "=" * 50)
    print("📊 نتائج الإصلاح:")
    
    for name, success in results:
        status = "✅ نجح" if success else "❌ فشل"
        print(f"   {name}: {status}")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n🎯 النتيجة: {successful}/{total} إصلاحات نجحت")
    
    if successful == total:
        print("\n🎉 تم إصلاح جميع المشاكل!")
        print("💡 أعد تشغيل الخادم لرؤية التغييرات:")
        print("   1. أوقف الخادم (Ctrl+C)")
        print("   2. شغل: python app.py")
    else:
        print("\n⚠️ بعض الإصلاحات فشلت. تحقق من الأخطاء أعلاه.")

if __name__ == "__main__":
    main()
