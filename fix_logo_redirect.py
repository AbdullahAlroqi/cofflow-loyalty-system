"""
إصلاح مشكلة توجيه اللوجو للوحة التحكم المناسبة
"""

def fix_logo_redirect():
    """إصلاح توجيه اللوجو إلى لوحة التحكم المناسبة"""
    print("🔧 إصلاح توجيه اللوجو إلى لوحة التحكم المناسبة...")
    
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
        
        # البحث عن الـ logo link
        if '<a class="navbar-brand" href="{{ url_for(\'index\') }}">' in base_content:
            # استبدال الرابط بدالة توجيه ديناميكية
            new_content = base_content.replace(
                '<a class="navbar-brand" href="{{ url_for(\'index\') }}">',
                """<a class="navbar-brand" href="{% if current_user.is_authenticated %}
                    {% if current_user.role == 'admin' %}{{ url_for('admin_dashboard') }}
                    {% elif current_user.role == 'employee' %}{{ url_for('employee_dashboard') }}
                    {% else %}{{ url_for('customer_dashboard') }}
                    {% endif %}
                {% else %}
                    {{ url_for('index') }}
                {% endif %}">"""
            )
            
            with open('templates/base.html', 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ تم تحديث رابط اللوجو ليوجه إلى لوحة التحكم المناسبة")
        else:
            print("⚠️ لم يتم العثور على رابط اللوجو في base.html")
    except Exception as e:
        print(f"❌ خطأ في تحديث رابط اللوجو: {str(e)}")
    
    # إضافة تحقق من تسجيل الدخول في مسار الصفحة الرئيسية
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # البحث عن دالة index
        if '@app.route(\'/\')' in app_content and 'def index():' in app_content:
            # تحديث الدالة لتوجيه المستخدم المسجل للوحة التحكم المناسبة
            old_index = """@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')"""
            
            new_index = """@app.route('/')
def index():
    """الصفحة الرئيسية"""
    if current_user.is_authenticated:
        # توجيه المستخدم للوحة التحكم المناسبة
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'employee':
            return redirect(url_for('employee_dashboard'))
        else:
            return redirect(url_for('customer_dashboard'))
    return render_template('index.html')"""
            
            # استبدال الدالة القديمة بالجديدة
            new_app_content = app_content.replace(old_index, new_index)
            
            if new_app_content != app_content:
                with open('app.py', 'w', encoding='utf-8') as f:
                    f.write(new_app_content)
                print("✅ تم تحديث دالة index لتوجيه المستخدم للوحة التحكم المناسبة")
            else:
                print("⚠️ لم يتم العثور على دالة index في app.py")
        else:
            print("⚠️ لم يتم العثور على دالة index في app.py")
    except Exception as e:
        print(f"❌ خطأ في تحديث دالة index: {str(e)}")
    
    # تحديث دالة login لتوجيه المستخدم بعد تسجيل الدخول
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # البحث عن دالة login
        if 'def login():' in app_content:
            # البحث عن توجيه بعد تسجيل الدخول الناجح
            redirect_index = "return redirect(url_for('index'))"
            if redirect_index in app_content:
                # تحديث التوجيه ليكون للوحة التحكم المناسبة
                updated_login = app_content.replace(
                    redirect_index,
                    """# توجيه للوحة التحكم المناسبة بعد تسجيل الدخول
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif current_user.role == 'employee':
                return redirect(url_for('employee_dashboard'))
            else:
                return redirect(url_for('customer_dashboard'))"""
                )
                
                with open('app.py', 'w', encoding='utf-8') as f:
                    f.write(updated_login)
                print("✅ تم تحديث دالة login لتوجيه المستخدم للوحة التحكم المناسبة")
            else:
                print("⚠️ لم يتم العثور على توجيه بعد تسجيل الدخول في دالة login")
        else:
            print("⚠️ لم يتم العثور على دالة login في app.py")
    except Exception as e:
        print(f"❌ خطأ في تحديث دالة login: {str(e)}")
    
    print("\n🎉 تم إصلاح توجيه اللوجو ومسارات التوجيه بعد تسجيل الدخول بنجاح")
    return True

if __name__ == "__main__":
    fix_logo_redirect()
