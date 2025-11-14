"""
إصلاح مشكلة حذف الموظف
"""

def fix_employee_deletion():
    """إصلاح مشكلة حذف الموظف"""
    print("🔧 إصلاح مشكلة حذف الموظف...")
    
    # قراءة ملف app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # البحث عن دالة حذف الموظف
    import re
    old_function = re.search(r'@app\.route\(\'/admin/employee/delete/.*?@role_required.*?def admin_delete_employee.*?return redirect\(url_for\(\'admin_employees\'\)\)', app_content, re.DOTALL)
    
    if old_function:
        # الدالة المحسنة
        new_function = """@app.route('/admin/employee/delete/<int:id>', methods=['POST'])
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
        updated_content = app_content.replace(old_function.group(), new_function)
        
        # حفظ التغييرات
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ تم إصلاح دالة حذف الموظف")
        return True
    else:
        print("⚠️ لم يتم العثور على دالة حذف الموظف")
        return False

if __name__ == "__main__":
    fix_employee_deletion()
