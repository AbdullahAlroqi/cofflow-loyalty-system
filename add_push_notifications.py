"""
إصلاح مشكلة إرسال الإشعارات كإشعارات Push وإضافة سكريبت تسجيل الاشتراك
"""

def fix_push_notifications():
    """إصلاح مشكلة إرسال الإشعارات Push"""
    print("🔧 إصلاح مشكلة إرسال الإشعارات Push...")
    
    # 1. أولاً: إضافة سكريبت خاص بتسجيل اشتراك الإشعارات في جميع الصفحات
    push_notifications_js = """
// تسجيل اشتراك الإشعارات
document.addEventListener('DOMContentLoaded', function() {
    // التحقق من دعم الإشعارات
    if (!('Notification' in window)) {
        console.log('❌ هذا المتصفح لا يدعم إشعارات الويب');
        return;
    }

    // طلب إذن الإشعارات بعد تفاعل المستخدم
    const requestNotificationPermission = async () => {
        if (Notification.permission !== 'granted') {
            try {
                const permission = await Notification.requestPermission();
                if (permission === 'granted') {
                    console.log('✅ تم منح إذن الإشعارات');
                    registerPushSubscription();
                } else {
                    console.log('❌ تم رفض إذن الإشعارات');
                }
            } catch (error) {
                console.error('❌ خطأ في طلب إذن الإشعارات:', error);
            }
        } else {
            // الإذن ممنوح بالفعل، تسجيل الاشتراك
            registerPushSubscription();
        }
    };

    // تسجيل اشتراك الإشعارات
    async function registerPushSubscription() {
        try {
            if ('serviceWorker' in navigator && 'PushManager' in window) {
                const registration = await navigator.serviceWorker.ready;
                
                // الحصول على مفاتيح VAPID العامة من الخادم
                const response = await fetch('/api/notifications/vapid-public-key');
                const data = await response.json();
                
                if (!data.publicKey) {
                    console.error('❌ لم يتم استلام مفتاح VAPID العام');
                    return;
                }
                
                // تحويل المفتاح العام من Base64 إلى ArrayBuffer
                const publicKeyBase64 = data.publicKey;
                const publicKey = urlBase64ToUint8Array(publicKeyBase64);
                
                // إلغاء أي اشتراكات سابقة
                const existingSubscription = await registration.pushManager.getSubscription();
                if (existingSubscription) {
                    await existingSubscription.unsubscribe();
                }
                
                // إنشاء اشتراك جديد
                const subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: publicKey
                });
                
                // إرسال الاشتراك إلى الخادم
                await fetch('/api/notifications/subscribe', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ subscription: JSON.stringify(subscription) })
                });
                
                console.log('✅ تم تسجيل اشتراك الإشعارات بنجاح');
            }
        } catch (error) {
            console.error('❌ خطأ في تسجيل اشتراك الإشعارات:', error);
        }
    }
    
    // تحويل Base64 URL Safe إلى Uint8Array
    function urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');
        
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        
        return outputArray;
    }
    
    // زر طلب الإشعارات
    const notificationBtn = document.getElementById('enable-notifications-btn');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', requestNotificationPermission);
    }
    
    // إذا كان المستخدم مسجل الدخول وسبق منح الإذن، تسجيل الاشتراك تلقائياً
    if (document.body.classList.contains('user-authenticated') && Notification.permission === 'granted') {
        registerPushSubscription();
    }
});
"""
    
    # حفظ السكريبت في ملف جديد
    try:
        with open('static/notifications.js', 'w', encoding='utf-8') as f:
            f.write(push_notifications_js)
        print("✅ تم إنشاء ملف notifications.js")
    except Exception as e:
        print(f"❌ خطأ في إنشاء ملف notifications.js: {str(e)}")
    
    # 2. إضافة رابط للسكريبت في القالب الأساسي
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
        
        # البحث عن مكان قبل نهاية الـ body
        if '<!-- PWA Script -->' in base_content:
            # إضافة سكريبت الإشعارات بعد سكريبت PWA
            new_content = base_content.replace(
                '<!-- PWA Script -->',
                '<!-- Notifications Script -->\n    <script src="{{ url_for(\'static\', filename=\'notifications.js\') }}"></script>\n    \n    <!-- PWA Script -->'
            )
            
            # إضافة كلاس للجسم إذا كان المستخدم مسجل الدخول
            if '<body>' in new_content:
                new_content = new_content.replace(
                    '<body>',
                    "{% if current_user.is_authenticated %}<body class=\"user-authenticated\">{% else %}<body>{% endif %}"
                )
            
            # إضافة زر تفعيل الإشعارات
            if 'pwa-install-container' in new_content:
                notification_button = """
    <!-- زر تفعيل الإشعارات -->
    <div class="notification-container" id="notification-container" style="display: none;">
        <button class="btn btn-info notification-button" id="enable-notifications-btn">
            <i class="fas fa-bell"></i> تفعيل الإشعارات
        </button>
    </div>
"""
                new_content = new_content.replace(
                    '</div>\n\n    <script>',
                    '</div>\n    ' + notification_button + '\n    <script>'
                )
                
                # إضافة تنسيق زر الإشعارات
                style_section = """
        .notification-container {
            position: fixed;
            bottom: 80px;
            left: 20px;
            z-index: 999;
        }
        
        .notification-button {
            border-radius: 25px;
            padding: 10px 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        
        .notification-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 15px rgba(0,0,0,0.3);
        }
        
        @media (max-width: 768px) {
            .notification-container {
                bottom: 70px;
                left: 10px;
                right: 10px;
                text-align: center;
            }
        }
"""
                new_content = new_content.replace('</style>', style_section + '</style>')
                
                # إضافة سكريبت لإظهار زر الإشعارات
                show_notification_button = """
            // إظهار زر تفعيل الإشعارات
            setTimeout(function() {
                if ('Notification' in window && Notification.permission !== 'granted' && Notification.permission !== 'denied') {
                    document.getElementById('notification-container').style.display = 'block';
                }
            }, 3000);
"""
                new_content = new_content.replace('}, 1500);', '}, 1500);' + show_notification_button)
            
            with open('templates/base.html', 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ تم تحديث base.html مع إضافة سكريبت الإشعارات وزر التفعيل")
        else:
            print("⚠️ لم يتم العثور على موقع لإضافة سكريبت الإشعارات في base.html")
    except Exception as e:
        print(f"❌ خطأ في تحديث base.html: {str(e)}")
    
    # 3. إضافة نقطة نهاية API للحصول على مفتاح VAPID العام
    try:
        with open('api_notifications.py', 'r', encoding='utf-8') as f:
            api_content = f.read()
        
        # إضافة نقطة نهاية جديدة للحصول على مفتاح VAPID العام
        if '/api/notifications/vapid-public-key' not in api_content:
            vapid_endpoint = """
@notifications_api.route('/api/notifications/vapid-public-key', methods=['GET'])
def get_vapid_public_key():
    """الحصول على مفتاح VAPID العام"""
    try:
        vapid_keys = EnhancedNotificationManager.get_vapid_keys()
        if vapid_keys and 'public_key' in vapid_keys:
            return jsonify({'publicKey': vapid_keys['public_key']})
        else:
            return jsonify({'error': 'مفتاح VAPID العام غير متوفر'}), 500
    except Exception as e:
        current_app.logger.error(f"خطأ في الحصول على مفتاح VAPID العام: {str(e)}")
        return jsonify({'error': str(e)}), 500
"""
            # إضافة في نهاية الملف
            new_content = api_content + vapid_endpoint
            
            with open('api_notifications.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ تم إضافة نقطة نهاية API للحصول على مفتاح VAPID العام")
        else:
            print("✅ نقطة نهاية مفتاح VAPID العام موجودة بالفعل")
    except Exception as e:
        print(f"❌ خطأ في تحديث api_notifications.py: {str(e)}")
    
    print("\n🎉 تم إصلاح مشكلة إرسال الإشعارات Push بنجاح")
    return True

def fix_logo_redirect():
    """إصلاح توجيه اللوجو إلى لوحة التحكم المناسبة"""
    print("\n🔧 إصلاح توجيه اللوجو إلى لوحة التحكم المناسبة...")
    
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
        
        # البحث عن توجيه بعد تسجيل الدخول
        if 'return redirect(url_for(\'index\'))  # توجيه للصفحة الرئيسية بعد تسجيل الدخول' in app_content:
            # تحديث التوجيه ليكون للوحة التحكم المناسبة
            updated_login = app_content.replace(
                'return redirect(url_for(\'index\'))  # توجيه للصفحة الرئيسية بعد تسجيل الدخول',
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
            print("⚠️ لم يتم العثور على توجيه بعد تسجيل الدخول في app.py")
    except Exception as e:
        print(f"❌ خطأ في تحديث دالة login: {str(e)}")
    
    print("\n🎉 تم إصلاح توجيه اللوجو ومسارات التوجيه بعد تسجيل الدخول بنجاح")
    return True

def main():
    """الدالة الرئيسية"""
    print("🔧 إصلاح مشاكل متعددة")
    print("=" * 50)
    
    # 1. إصلاح إرسال الإشعارات Push
    push_fixed = fix_push_notifications()
    
    # 2. إصلاح توجيه اللوجو
    logo_fixed = fix_logo_redirect()
    
    print("\n" + "=" * 50)
    print("📊 نتائج الإصلاح:")
    print(f"   إرسال الإشعارات Push: {'✅ تم الإصلاح' if push_fixed else '❌ فشل الإصلاح'}")
    print(f"   توجيه اللوجو للوحة التحكم: {'✅ تم الإصلاح' if logo_fixed else '❌ فشل الإصلاح'}")
    
    if push_fixed and logo_fixed:
        print("\n🎉 تم إصلاح جميع المشاكل!")
        print("💡 أعد تشغيل الخادم لرؤية التغييرات:")
        print("   1. أوقف الخادم (Ctrl+C)")
        print("   2. شغل: python app.py")
    else:
        print("\n⚠️ بعض الإصلاحات فشلت. تحقق من الأخطاء أعلاه.")

if __name__ == "__main__":
    main()
