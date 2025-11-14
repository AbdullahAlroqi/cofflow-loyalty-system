"""
سكريبت لدمج ملفات الإشعارات في ملف واحد كامل
"""

def create_complete_notifications_file():
    # قراءة الملف الأساسي
    with open('templates/admin/notifications.html', 'r', encoding='utf-8') as f:
        base_content = f.read()
    
    # قراءة المودالز
    with open('templates/admin/notifications_modals.html', 'r', encoding='utf-8') as f:
        modals_content = f.read()
    
    # قراءة الجافاسكريبت الجزء الأول
    with open('templates/admin/notifications_js.html', 'r', encoding='utf-8') as f:
        js_content1 = f.read()
    
    # قراءة الجافاسكريبت الجزء الثاني
    with open('templates/admin/notifications_js_part2.html', 'r', encoding='utf-8') as f:
        js_content2 = f.read()
    
    # دمج المحتوى
    complete_content = base_content.rstrip()
    
    # إضافة المودالز قبل نهاية div.container
    complete_content += "\n    " + modals_content
    
    # إضافة نهاية div.container
    complete_content += "\n</div>\n"
    
    # إضافة نهاية block content
    complete_content += "{% endblock %}\n\n"
    
    # إضافة الجافاسكريبت
    complete_content += js_content1 + "\n"
    complete_content += js_content2
    
    # كتابة الملف الكامل
    with open('templates/admin/notifications_complete.html', 'w', encoding='utf-8') as f:
        f.write(complete_content)
    
    print("✅ تم إنشاء ملف الإشعارات الكامل بنجاح!")
    print("📁 الملف: templates/admin/notifications_complete.html")

if __name__ == "__main__":
    create_complete_notifications_file()
