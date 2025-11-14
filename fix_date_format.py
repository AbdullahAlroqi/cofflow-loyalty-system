"""
إصلاح مشكلة تنسيق التواريخ في القوالب
"""
import os
import re

def fix_templates():
    """إصلاح قوالب Jinja2 لتجنب أخطاء التاريخ"""
    print("🔧 إصلاح مشكلة تنسيق التواريخ في القوالب...")
    
    # قائمة الملفات التي تحتاج للإصلاح
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
            
            # البحث عن أنماط التاريخ غير الآمنة واستبدالها
            # النمط 1: قيمة.strftime() مباشرة بدون تحقق
            unsafe_pattern1 = r'(\{\{\s*[a-zA-Z0-9._]+\s*\}})\.strftime\('
            if re.search(unsafe_pattern1, content):
                content = re.sub(unsafe_pattern1, r'\1 and \1.strftime(', content)
                fixes_count += 1
            
            # النمط 2: استخدام .strftime بدون تحقق مسبق
            unsafe_pattern2 = r'(\{\{\s*[a-zA-Z0-9._]+)\.strftime\(([^}]+)\}\}'
            if re.search(unsafe_pattern2, content):
                content = re.sub(unsafe_pattern2, r'\1.strftime(\2 if \1 else "-" }}}', content)
                fixes_count += 1
            
            # النمط 3: تصحيح المشاكل الشائعة
            replacements = [
                # coupon.used_at.strftime
                (r'(\{\{\s*coupon\.used_at)\.strftime\(([^}]+)\}\}', r'\1.strftime(\2 if coupon.used_at else "-" }}}'),
                
                # transaction.created_at.strftime
                (r'(\{\{\s*transaction\.created_at)\.strftime\(([^}]+)\}\}', r'\1.strftime(\2 if transaction.created_at else "-" }}}'),
                
                # customer.created_at.strftime
                (r'(\{\{\s*customer\.created_at)\.strftime\(([^}]+)\}\}', r'\1.strftime(\2 if customer.created_at else "-" }}}'),
                
                # settings.updated_at.strftime - إذا لم يكن محتوياً على تحقق بالفعل
                (r'(\{\{\s*settings\.updated_at)\.strftime\(([^}]+)\}\}', r'\1.strftime(\2 if settings.updated_at else "-" }}}')
            ]
            
            for pattern, replacement in replacements:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    fixes_count += 1
            
            # إصلاح خاص لملف coupons.html - هنا المشكلة المحددة
            if template_file == 'templates/admin/coupons.html':
                # تحقق من وجود تحقق مسبق من coupon.used_at
                if 'coupon.used_at.strftime' in content and 'if coupon.used_at else' not in content:
                    content = content.replace(
                        '{{ coupon.used_at.strftime(\'%d/%m/%Y\') }}',
                        '{{ coupon.used_at.strftime(\'%d/%m/%Y\') if coupon.used_at else \'-\' }}'
                    )
                    fixes_count += 1
            
            # حفظ التغييرات
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ تم إصلاح ملف: {template_file}")
        
        except Exception as e:
            print(f"❌ خطأ في إصلاح ملف {template_file}: {str(e)}")
    
    # إصلاح خاص للقوالب الأكثر احتمالية لوجود المشكلة
    fix_specific_templates()
    
    print(f"\n✨ تم إجراء {fixes_count} إصلاحات لمشكلة تنسيق التواريخ")
    return fixes_count > 0

def fix_specific_templates():
    """إصلاح خاص للقوالب الأكثر احتمالية لوجود المشكلة"""
    try:
        # إصلاح خاص لقالب admin/coupons.html
        coupons_template = 'templates/admin/coupons.html'
        if os.path.exists(coupons_template):
            with open(coupons_template, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # إصلاح محدد لمشكلة coupon.used_at
            if '{{ coupon.used_at.strftime(\'%d/%m/%Y\') }}' in content:
                content = content.replace(
                    '{{ coupon.used_at.strftime(\'%d/%m/%Y\') }}',
                    '{{ coupon.used_at.strftime(\'%d/%m/%Y\') if coupon.used_at else \'-\' }}'
                )
                
                with open(coupons_template, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ تم إصلاح خاص لـ {coupons_template}")
            
            # إضافة تحقق إضافي لـ coupon.used_at
            problem_line = '<td>{{ coupon.used_at.strftime(\'%d/%m/%Y\') if coupon.used_at else \'-\' }}</td>'
            if problem_line in content:
                # هذا السطر صحيح بالفعل، لا يحتاج إلى إصلاح
                print(f"✓ السطر المشكل تم إصلاحه بالفعل")
    
    except Exception as e:
        print(f"❌ خطأ في الإصلاح الخاص: {str(e)}")

if __name__ == "__main__":
    fix_templates()
