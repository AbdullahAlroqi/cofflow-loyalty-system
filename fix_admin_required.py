"""
إضافة دالة admin_required المفقودة
"""

def add_admin_required_decorator():
    """إضافة دالة admin_required المفقودة"""
    print("🔧 إضافة دالة admin_required...")
    
    # كود الدالة
    admin_required_code = """
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if current_user.role != 'admin':
            flash('هذه الصفحة للمدراء فقط', 'danger')
            if current_user.role == 'employee':
                return redirect(url_for('employee_dashboard'))
            else:
                return redirect(url_for('customer_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

"""
    
    try:
        # قراءة ملف app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # البحث عن مكان مناسب للإضافة (بعد admin_or_employee_required)
        import re
        
        admin_or_employee_match = re.search(r'def admin_or_employee_required\(f\):.*?return decorated_function\s*\n', app_content, re.DOTALL)
        
        if admin_or_employee_match:
            # مكان الإضافة
            insert_position = admin_or_employee_match.end()
            
            # إضافة الدالة الجديدة
            new_content = app_content[:insert_position] + admin_required_code + app_content[insert_position:]
            
            # كتابة الملف المعدل
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ تم إضافة دالة admin_required بنجاح")
            return True
            
        else:
            print("❌ لم يتم العثور على مكان مناسب للإضافة")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def fix_admin_coupons_function():
    """تصحيح دالة admin_coupons"""
    print("\n🔧 تصحيح دالة admin_coupons...")
    
    try:
        # قراءة ملف app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # البحث عن دالة admin_coupons
        import re
        admin_coupons_match = re.search(r'@app\.route\(\'/admin/coupons\'\).*?@admin_required.*?def admin_coupons\(\):.*?return render_template', app_content, re.DOTALL)
        
        if admin_coupons_match:
            # تحديث الدالة لتستخدم role_required بدلاً من admin_required
            updated_function = admin_coupons_match.group().replace('@admin_required', '@login_required\n@role_required(\'admin\')')
            
            # تحديث الملف
            new_content = app_content.replace(admin_coupons_match.group(), updated_function)
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ تم تصحيح دالة admin_coupons بنجاح")
            return True
            
        else:
            print("❌ لم يتم العثور على دالة admin_coupons")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 إصلاح مشكلة admin_required")
    print("=" * 50)
    
    # خيار 1: إضافة دالة admin_required
    decorator_added = add_admin_required_decorator()
    
    if not decorator_added:
        # خيار 2: إذا فشلت إضافة الدالة، نصحح استخدام admin_required
        function_fixed = fix_admin_coupons_function()
    else:
        function_fixed = True
    
    print("\n" + "=" * 50)
    if decorator_added or function_fixed:
        print("🎉 تم إصلاح المشكلة!")
        print("💡 أعد تشغيل الخادم لرؤية التغييرات:")
        print("   python app.py")
    else:
        print("❌ فشل الإصلاح. تحقق من الأخطاء أعلاه.")

if __name__ == "__main__":
    main()
