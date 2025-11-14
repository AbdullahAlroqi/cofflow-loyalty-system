"""
إصلاح مشكلة بناء الجملة في قوالب Jinja2
"""
import os
import re

def fix_jinja_syntax():
    """إصلاح أخطاء بناء الجملة في قوالب Jinja2"""
    print("🔧 إصلاح مشكلة بناء الجملة في قوالب Jinja2...")
    
    # قائمة الملفات التي تم تعديلها وقد تحتاج للإصلاح
    template_files = [
        'templates/admin/coupons.html',
        'templates/admin/customer_details.html',
        'templates/customer/dashboard.html',
        'templates/admin/transactions.html'
    ]
    
    fixes_count = 0
    
    for template_file in template_files:
        if not os.path.exists(template_file):
            print(f"⚠️ ملف القالب غير موجود: {template_file}")
            continue
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # البحث عن الأنماط التي تم تصحيحها بشكل غير صحيح
            # المشكلة المحتملة: {{ var.strftime(...) if var else "-" }}} (يوجد قوس } زائد)
            bad_pattern1 = r'(\{\{\s*[a-zA-Z0-9._]+\.strftime\([^}]+)\s+if\s+[a-zA-Z0-9._]+\s+else\s+["\'][^"\']+["\']\s*\}\}\}'
            if re.search(bad_pattern1, content):
                content = re.sub(bad_pattern1, r'\1 if \2 else \3 }}', content)
                print(f"  ✓ تم إصلاح أنماط القوس الزائد")
                fixes_count += 1
            
            # مشكلة محتملة أخرى: عدم وضع القوس الثاني بشكل صحيح
            bad_pattern2 = r'(\{\{\s*[a-zA-Z0-9._]+)\.strftime\(([^}]+) if'
            if re.search(bad_pattern2, content):
                content = re.sub(bad_pattern2, r'\1.strftime(\2) if', content)
                print(f"  ✓ تم إصلاح موضع القوس")
                fixes_count += 1
            
            # إصلاح صيغ التاريخ بشكل كامل - استبدال كل الصيغ المشكوك فيها بصيغة صحيحة
            replacements = [
                # إصلاح المشكلة المحددة: استبدال الصيغ غير الصحيحة
                (r'\{\{\s*([a-zA-Z0-9._]+)\.strftime\(([^)]+)\)(\s+if\s+[^}]+else[^}]+)\}\}\}', r'{{ \1.strftime(\2)\3 }}'),
                # إصلاح مشكلة أخرى: وضع if في الموضع الصحيح
                (r'\{\{\s*([a-zA-Z0-9._]+)\.strftime\(([^)]+)\s+if\s+([^}]+)else([^}]+)\}\}', r'{{ \1.strftime(\2) if \3 else \4 }}'),
                # تبسيط الأمر: استبدال كل التعبيرات المعقدة بصيغة {% if %} بدلاً من التعبير الشرطي
                (r'\{\{\s*([a-zA-Z0-9._]+)\.strftime\(([^)]+)\)\s+if\s+([a-zA-Z0-9._]+)\s+else\s+["\']([^"\']+)["\']\s*\}\}', 
                 r'{% if \3 %}{{ \1.strftime(\2) }}{% else %}\4{% endif %}')
            ]
            
            modified = False
            for pattern, replacement in replacements:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    print(f"  ✓ تم إصلاح تعبير شرطي")
                    modified = True
                    fixes_count += 1
            
            # إصلاح يدوي لبعض الأنماط المعروفة بمشاكلها
            if 'coupon.used_at.strftime(' in content:
                # استبدال كل تعبيرات coupon.used_at.strftime بالصيغة الآمنة باستخدام {% if %}
                content = re.sub(
                    r'\{\{\s*coupon\.used_at\.strftime\(["\']([^"\']+)["\']\)(\s*if\s*coupon\.used_at\s*else\s*["\']([^"\']+)["\']\s*)\}\}',
                    r'{% if coupon.used_at %}{{ coupon.used_at.strftime("\1") }}{% else %}\3{% endif %}',
                    content
                )
                print(f"  ✓ تم إصلاح تعبير coupon.used_at")
                modified = True
                fixes_count += 1
            
            # في حالة تعذر الإصلاح الآلي، نقوم بإصلاح يدوي
            problem_strings = [
                # في coupons.html
                ('{{ coupon.used_at.strftime(\'%d/%m/%Y\') if coupon.used_at else \'-\' }}', 
                 '{% if coupon.used_at %}{{ coupon.used_at.strftime(\'%d/%m/%Y\') }}{% else %}-{% endif %}'),
                
                # في customer_details.html
                ('{{ coupon.used_at.strftime(\'%Y-%m-%d %H:%M\') if coupon.used_at else \'-\' }}',
                 '{% if coupon.used_at %}{{ coupon.used_at.strftime(\'%Y-%m-%d %H:%M\') }}{% else %}-{% endif %}'),
                
                # في customer/dashboard.html
                ('{{ coupon.used_at.strftime(\'%Y-%m-%d %H:%M\') }}',
                 '{% if coupon.used_at %}{{ coupon.used_at.strftime(\'%Y-%m-%d %H:%M\') }}{% else %}-{% endif %}')
            ]
            
            for old_str, new_str in problem_strings:
                if old_str in content:
                    content = content.replace(old_str, new_str)
                    print(f"  ✓ تم إصلاح نمط معروف")
                    modified = True
                    fixes_count += 1
            
            # حفظ التغييرات إذا تم إجراء أي تعديلات
            if modified:
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ تم حفظ الإصلاحات في {template_file}")
            else:
                print(f"⚠️ لم يتم العثور على مشاكل بناء جملة في {template_file}")
            
        except Exception as e:
            print(f"❌ خطأ في إصلاح ملف {template_file}: {str(e)}")
    
    # إصلاح يدوي مباشر للملفات المعروف أنها مشكلة
    fix_admin_coupons_html()
    
    print(f"\n✨ تم إجراء {fixes_count} إصلاحات لمشكلة بناء الجملة")
    return fixes_count > 0

def fix_admin_coupons_html():
    """إصلاح يدوي لملف coupons.html"""
    coupons_file = 'templates/admin/coupons.html'
    if not os.path.exists(coupons_file):
        return
    
    try:
        with open(coupons_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # البحث عن السطر الذي يحتوي على المشكلة
        line_with_issue = '<td>{{ coupon.used_at.strftime(\'%d/%m/%Y\') if coupon.used_at else \'-\' }}</td>'
        corrected_line = '<td>{% if coupon.used_at %}{{ coupon.used_at.strftime(\'%d/%m/%Y\') }}{% else %}-{% endif %}</td>'
        
        if line_with_issue in content:
            content = content.replace(line_with_issue, corrected_line)
            
            with open(coupons_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ تم إصلاح مباشر لملف {coupons_file}")
    except Exception as e:
        print(f"❌ خطأ في الإصلاح اليدوي: {str(e)}")

def fix_dashboard_html():
    """إصلاح يدوي لملف customer/dashboard.html"""
    dashboard_file = 'templates/customer/dashboard.html'
    if not os.path.exists(dashboard_file):
        return
    
    try:
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # البحث عن السطر الذي يحتوي على المشكلة
        line_with_issue = '{{ coupon.used_at.strftime(\'%Y-%m-%d %H:%M\') }}'
        corrected_line = '{% if coupon.used_at %}{{ coupon.used_at.strftime(\'%Y-%m-%d %H:%M\') }}{% else %}-{% endif %}'
        
        if line_with_issue in content:
            content = content.replace(line_with_issue, corrected_line)
            
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ تم إصلاح مباشر لملف {dashboard_file}")
    except Exception as e:
        print(f"❌ خطأ في الإصلاح اليدوي: {str(e)}")

if __name__ == "__main__":
    fix_jinja_syntax()
    fix_dashboard_html()
