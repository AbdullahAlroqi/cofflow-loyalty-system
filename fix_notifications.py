"""
إصلاح مشكلة إرسال الإشعارات
"""

def fix_notifications_sending():
    """إصلاح مشكلة عدم إرسال الإشعارات"""
    print("\n🔧 إصلاح مشكلة إرسال الإشعارات...")
    
    # قراءة ملف api_notifications.py
    try:
        with open('api_notifications.py', 'r', encoding='utf-8') as f:
            notifications_content = f.read()
        
        # البحث عن دالة إرسال الإشعارات
        import re
        send_function = re.search(r'@notifications_api\.route\(\'/api/notifications/send\'.*?def send_notification.*?return jsonify.*?\)', notifications_content, re.DOTALL)
        
        if send_function:
            # الدالة المحسنة
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
            updated_content = notifications_content.replace(send_function.group(), new_send_function)
            
            # حفظ التغييرات
            with open('api_notifications.py', 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("✅ تم إصلاح دالة إرسال الإشعارات")
            return True
        else:
            print("⚠️ لم يتم العثور على دالة إرسال الإشعارات")
            
            # طريقة بديلة - إضافة الدالة في نهاية الملف
            add_send_function = """

@notifications_api.route('/api/notifications/send', methods=['POST'])
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
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500
"""
            # التحقق من عدم وجود الدالة قبل إضافتها
            if "def send_notification():" not in notifications_content:
                with open('api_notifications.py', 'a', encoding='utf-8') as f:
                    f.write(add_send_function)
                print("✅ تم إضافة دالة إرسال الإشعارات")
                return True
            else:
                print("⚠️ يبدو أن دالة إرسال الإشعارات موجودة لكن بتنسيق مختلف")
                return False
    
    except Exception as e:
        print(f"❌ خطأ في قراءة أو تحديث ملف api_notifications.py: {str(e)}")
        return False

if __name__ == "__main__":
    fix_notifications_sending()
