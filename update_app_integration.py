"""
سكريبت لتحديث ملف app.py وإضافة التكامل مع نظام الإشعارات
"""

def update_app_py():
    # قراءة ملف app.py الحالي
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # التحقق من وجود التكامل مسبقاً
    if 'api_notifications' in content:
        print("✅ التكامل موجود مسبقاً في app.py")
        return
    
    # إضافة استيراد API الإشعارات
    import_line = "from api_notifications import notifications_api\n"
    
    # البحث عن مكان إضافة الاستيراد (بعد الاستيرادات الأخرى)
    lines = content.split('\n')
    insert_index = -1
    
    for i, line in enumerate(lines):
        if line.startswith('from functools import wraps'):
            insert_index = i + 1
            break
    
    if insert_index != -1:
        lines.insert(insert_index, import_line.strip())
    
    # إضافة تسجيل Blueprint
    blueprint_line = "app.register_blueprint(notifications_api)"
    
    # البحث عن مكان إضافة Blueprint (بعد إعداد قاعدة البيانات)
    for i, line in enumerate(lines):
        if 'db.init_app(app)' in line:
            lines.insert(i + 1, '')
            lines.insert(i + 2, '# تسجيل مسارات API الإشعارات')
            lines.insert(i + 3, blueprint_line)
            break
    
    # إضافة مسارات الإشعارات
    routes_to_add = [
        "",
        "@app.route('/admin/notifications')",
        "@login_required",
        "@role_required('admin')",
        "def admin_notifications():",
        '    """صفحة إدارة الإشعارات"""',
        "    return render_template('admin/notifications.html')",
        "",
        "@app.route('/customer/notifications')",
        "@login_required",
        "def customer_notifications():",
        '    """صفحة إشعارات العميل"""',
        "    return render_template('customer/notifications.html')"
    ]
    
    # البحث عن مكان إضافة المسارات (قبل نهاية الملف)
    for i, line in enumerate(lines):
        if 'if __name__ == \'__main__\':' in line:
            # إضافة المسارات قبل هذا السطر
            for route_line in reversed(routes_to_add):
                lines.insert(i, route_line)
            break
    
    # كتابة الملف المحدث
    updated_content = '\n'.join(lines)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✅ تم تحديث ملف app.py بنجاح!")
    print("📝 تم إضافة:")
    print("   - استيراد API الإشعارات")
    print("   - تسجيل Blueprint")
    print("   - مسارات صفحات الإشعارات")

if __name__ == "__main__":
    update_app_py()
