"""
فحص تناسق القوالب والتأكد من استخدام base.html
"""
import os
import glob

def check_template_inheritance():
    """فحص وراثة القوالب"""
    print("📄 فحص وراثة القوالب...")
    
    # البحث عن جميع ملفات HTML
    template_files = []
    for root, dirs, files in os.walk('templates'):
        for file in files:
            if file.endswith('.html'):
                template_files.append(os.path.join(root, file))
    
    print(f"📋 تم العثور على {len(template_files)} قالب:")
    
    inheritance_issues = []
    
    for template_file in template_files:
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # تخطي base.html نفسه
            if 'base.html' in template_file:
                print(f"   📄 {template_file}: القالب الأساسي")
                continue
            
            # فحص الوراثة
            if '{% extends "base.html" %}' in content:
                print(f"   ✅ {template_file}: يستخدم base.html")
            elif '{% extends' in content:
                # يستخدم قالب آخر
                import re
                extends_match = re.search(r'{%\s*extends\s*["\']([^"\']+)["\']', content)
                if extends_match:
                    parent_template = extends_match.group(1)
                    print(f"   ⚠️ {template_file}: يستخدم {parent_template}")
                    inheritance_issues.append((template_file, parent_template))
            else:
                print(f"   ❌ {template_file}: لا يستخدم وراثة")
                inheritance_issues.append((template_file, "لا يوجد"))
                
        except Exception as e:
            print(f"   ❌ {template_file}: خطأ في القراءة - {e}")
    
    return inheritance_issues

def fix_template_inheritance():
    """إصلاح وراثة القوالب"""
    print("\n🔧 إصلاح وراثة القوالب...")
    
    # قائمة القوالب التي يجب أن تستخدم base.html
    templates_to_fix = [
        'templates/index.html',
        'templates/login.html',
        'templates/register.html',
        'templates/admin/dashboard.html',
        'templates/admin/customers.html',
        'templates/admin/employees.html',
        'templates/admin/coupons.html',
        'templates/admin/notifications.html',
        'templates/admin/settings.html',
        'templates/employee/dashboard.html',
        'templates/customer/dashboard.html',
        'templates/customer/notifications.html'
    ]
    
    fixed_count = 0
    
    for template_file in templates_to_fix:
        if os.path.exists(template_file):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # التحقق من الوراثة
                if '{% extends "base.html" %}' not in content:
                    # إضافة الوراثة في البداية
                    if not content.startswith('{% extends'):
                        content = '{% extends "base.html" %}\n\n' + content
                        
                        with open(template_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"   ✅ تم إصلاح {template_file}")
                        fixed_count += 1
                    else:
                        print(f"   ⚠️ {template_file}: يستخدم قالب آخر")
                else:
                    print(f"   ✅ {template_file}: صحيح بالفعل")
                    
            except Exception as e:
                print(f"   ❌ خطأ في إصلاح {template_file}: {e}")
        else:
            print(f"   ❌ {template_file}: غير موجود")
    
    return fixed_count

def ensure_base_template_blocks():
    """التأكد من وجود blocks في القالب الأساسي"""
    print("\n🏗️ فحص blocks في القالب الأساسي...")
    
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
        
        required_blocks = [
            'title',
            'extra_css',
            'content',
            'extra_js'
        ]
        
        missing_blocks = []
        
        for block in required_blocks:
            if f'{{% block {block} %}}' in base_content:
                print(f"   ✅ block {block}: موجود")
            else:
                print(f"   ❌ block {block}: مفقود")
                missing_blocks.append(block)
        
        if missing_blocks:
            print(f"\n🔧 إضافة blocks مفقودة...")
            
            # إضافة blocks مفقودة
            if 'extra_css' in missing_blocks:
                base_content = base_content.replace('</head>', '    {% block extra_css %}{% endblock %}\n</head>')
            
            if 'extra_js' in missing_blocks:
                base_content = base_content.replace('</body>', '    {% block extra_js %}{% endblock %}\n</body>')
            
            with open('templates/base.html', 'w', encoding='utf-8') as f:
                f.write(base_content)
            
            print(f"   ✅ تم إضافة {len(missing_blocks)} blocks")
        
        return len(missing_blocks) == 0
        
    except Exception as e:
        print(f"   ❌ خطأ في فحص القالب الأساسي: {e}")
        return False

def create_missing_templates():
    """إنشاء القوالب المفقودة"""
    print("\n📝 إنشاء القوالب المفقودة...")
    
    # قالب التسجيل
    if not os.path.exists('templates/register.html'):
        register_template = """{% extends "base.html" %}

{% block title %}إنشاء حساب جديد - COFFLOW{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card shadow">
                <div class="card-header text-center">
                    <h3><i class="fas fa-user-plus"></i> إنشاء حساب جديد</h3>
                </div>
                <div class="card-body">
                    <form method="POST">
                        <div class="mb-3">
                            <label for="name" class="form-label">الاسم الكامل</label>
                            <input type="text" class="form-control" id="name" name="name" required>
                        </div>
                        <div class="mb-3">
                            <label for="phone" class="form-label">رقم الجوال</label>
                            <input type="text" class="form-control" id="phone" name="phone" placeholder="05xxxxxxxx" required>
                        </div>
                        <div class="mb-3">
                            <label for="email" class="form-label">البريد الإلكتروني (اختياري)</label>
                            <input type="email" class="form-control" id="email" name="email">
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">كلمة المرور</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="fas fa-user-plus"></i> إنشاء الحساب
                        </button>
                    </form>
                    <hr>
                    <div class="text-center">
                        <a href="{{ url_for('login') }}" class="btn btn-outline-secondary">
                            <i class="fas fa-sign-in-alt"></i> لديك حساب؟ سجل الدخول
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
        
        with open('templates/register.html', 'w', encoding='utf-8') as f:
            f.write(register_template)
        print("   ✅ تم إنشاء templates/register.html")
    
    # قالب إعدادات المدير
    if not os.path.exists('templates/admin/settings.html'):
        os.makedirs('templates/admin', exist_ok=True)
        
        settings_template = """{% extends "base.html" %}

{% block title %}الإعدادات - COFFLOW{% endblock %}

{% block content %}
<div class="container mt-4">
    <h2><i class="fas fa-cog"></i> إعدادات النظام</h2>
    
    <div class="row mt-4">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h5><i class="fas fa-palette"></i> إعدادات المظهر</h5>
                </div>
                <div class="card-body">
                    <form method="POST">
                        <div class="mb-3">
                            <label for="primary_color" class="form-label">اللون الأساسي</label>
                            <input type="color" class="form-control" id="primary_color" name="primary_color" 
                                   value="{{ settings.primary_color if settings else '#8B4513' }}">
                        </div>
                        <div class="mb-3">
                            <label for="secondary_color" class="form-label">اللون الثانوي</label>
                            <input type="color" class="form-control" id="secondary_color" name="secondary_color" 
                                   value="{{ settings.secondary_color if settings else '#D2691E' }}">
                        </div>
                        <div class="mb-3">
                            <label for="cups_required" class="form-label">عدد الأكواب المطلوبة للكوب المجاني</label>
                            <input type="number" class="form-control" id="cups_required" name="cups_required" 
                                   value="{{ settings.cups_required if settings else 6 }}" min="1" max="20">
                        </div>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i> حفظ الإعدادات
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
        
        with open('templates/admin/settings.html', 'w', encoding='utf-8') as f:
            f.write(settings_template)
        print("   ✅ تم إنشاء templates/admin/settings.html")

def main():
    """الدالة الرئيسية"""
    print("🔍 فحص تناسق القوالب وإصلاح المشاكل")
    print("=" * 50)
    
    # فحص وراثة القوالب
    inheritance_issues = check_template_inheritance()
    
    # إصلاح وراثة القوالب
    fixed_count = fix_template_inheritance()
    
    # فحص blocks في القالب الأساسي
    base_ok = ensure_base_template_blocks()
    
    # إنشاء القوالب المفقودة
    create_missing_templates()
    
    print("\n" + "=" * 50)
    print("📊 ملخص الإصلاحات:")
    print(f"   مشاكل الوراثة: {len(inheritance_issues)}")
    print(f"   القوالب المُصلحة: {fixed_count}")
    print(f"   القالب الأساسي: {'✅ صحيح' if base_ok else '⚠️ يحتاج إصلاح'}")
    
    if len(inheritance_issues) == 0 and base_ok:
        print("\n🎉 جميع القوالب تستخدم base.html بشكل صحيح!")
    else:
        print("\n⚠️ تم إصلاح معظم المشاكل. أعد تشغيل الخادم لرؤية التغييرات.")

if __name__ == "__main__":
    main()
