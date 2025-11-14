"""
سكريبت لتفعيل نظام الإشعارات تدريجياً
"""
import os
import shutil

def enable_notifications():
    print("🔔 تفعيل نظام الإشعارات...")
    
    try:
        # 1. استعادة النماذج الكاملة
        print("📝 استعادة نماذج الإشعارات...")
        if os.path.exists('models_with_notifications.py'):
            shutil.copy2('models_with_notifications.py', 'models_full_backup.py')
            print("✅ تم حفظ نسخة احتياطية من النماذج الكاملة")
        
        # 2. تحديث app.py لإضافة مسارات الإشعارات
        print("🔧 تحديث app.py...")
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # إلغاء تعليق استيراد API الإشعارات
        content = content.replace('# from api_notifications import notifications_api', 'from api_notifications import notifications_api')
        content = content.replace('# app.register_blueprint(notifications_api)', 'app.register_blueprint(notifications_api)')
        
        # تحديث مسارات الإشعارات
        old_admin_notifications = '''@app.route('/admin/notifications')
@login_required
@role_required('admin')
def admin_notifications():
    """صفحة إدارة الإشعارات (مؤقتة)"""
    flash('نظام الإشعارات قيد التطوير - سيتم تفعيله قريباً', 'info')
    return redirect(url_for('admin_dashboard'))'''

        new_admin_notifications = '''@app.route('/admin/notifications')
@login_required
@role_required('admin')
def admin_notifications():
    """صفحة إدارة الإشعارات"""
    return render_template('admin/notifications.html')'''
        
        content = content.replace(old_admin_notifications, new_admin_notifications)
        
        old_customer_notifications = '''@app.route('/customer/notifications')
@login_required
def customer_notifications():
    """صفحة إشعارات العميل (مؤقتة)"""
    if current_user.role != 'customer':
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('login'))
    flash('نظام الإشعارات قيد التطوير - سيتم تفعيله قريباً', 'info')
    return redirect(url_for('customer_dashboard'))'''

        new_customer_notifications = '''@app.route('/customer/notifications')
@login_required
def customer_notifications():
    """صفحة إشعارات العميل"""
    if current_user.role != 'customer':
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('login'))
    return render_template('customer/notifications.html')'''
        
        content = content.replace(old_customer_notifications, new_customer_notifications)
        
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ تم تحديث app.py")
        
        # 3. التحقق من وجود ملفات الإشعارات
        required_files = [
            'api_notifications.py',
            'notifications.py',
            'templates/admin/notifications.html',
            'templates/customer/notifications.html'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            print("⚠️ ملفات مفقودة:")
            for file_path in missing_files:
                print(f"   - {file_path}")
        else:
            print("✅ جميع ملفات الإشعارات موجودة")
        
        print("\n🎉 تم تفعيل نظام الإشعارات!")
        print("📋 الخطوات التالية:")
        print("   1. أعد تشغيل الخادم")
        print("   2. قم بتحديث قاعدة البيانات إذا لزم الأمر")
        print("   3. اختبر صفحات الإشعارات")
        
    except Exception as e:
        print(f"❌ خطأ في تفعيل الإشعارات: {e}")

if __name__ == "__main__":
    enable_notifications()
