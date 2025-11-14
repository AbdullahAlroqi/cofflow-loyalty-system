# تعليمات تحديث نظام PWA والإشعارات

## 1. تعديل ملف app.py لإضافة مسارات الإشعارات

أضف الكود التالي إلى ملف `app.py` بعد استيراد المكتبات:

```python
# استيراد وحدة الإشعارات API
from api_notifications import notifications_api
```

وفي نفس الملف `app.py`، أضف التسجيل للـ Blueprint:

```python
# تسجيل مسارات API الإشعارات
app.register_blueprint(notifications_api)
```

ثم أضف مسار لصفحة إدارة الإشعارات في قسم مسارات المدير:

```python
@app.route('/admin/notifications')
@login_required
@admin_required
def admin_notifications():
    """صفحة إدارة الإشعارات"""
    return render_template('admin/notifications.html')
```

أضف أيضًا مسار لصفحة إشعارات العميل:

```python
@app.route('/customer/notifications')
@login_required
def customer_notifications():
    """صفحة إشعارات العميل"""
    return render_template('customer/notifications.html')
```

## 2. تحديث قائمة التنقل في base.html

أضف الرابط لصفحة الإشعارات في base.html في قائمة التنقل للمدير:

```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('admin_notifications') }}">
        <i class="fas fa-bell"></i> الإشعارات
    </a>
</li>
```

أضف الرابط لصفحة الإشعارات في قائمة العميل:

```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('customer_notifications') }}">
        <i class="fas fa-bell"></i> الإشعارات
    </a>
</li>
```

## 3. تحديث واجهات المستخدم مع عداد الإشعارات

أضف الكود التالي إلى ملف base.html في قسم JavaScript الإضافي:

```html
<script>
    // تحديث عداد الإشعارات غير المقروءة
    function updateNotificationCounter() {
        // فقط للمستخدمين المسجلين
        {% if current_user.is_authenticated %}
            fetch('/api/notifications/unread-count')
                .then(response => response.json())
                .then(data => {
                    const count = data.count || 0;
                    const notificationLinks = document.querySelectorAll('.nav-link[href*="notifications"]');
                    
                    notificationLinks.forEach(link => {
                        // إزالة العداد القديم إن وجد
                        const existingBadge = link.querySelector('.notification-badge');
                        if (existingBadge) {
                            existingBadge.remove();
                        }
                        
                        // إضافة العداد الجديد إذا كان هناك إشعارات غير مقروءة
                        if (count > 0) {
                            const badge = document.createElement('span');
                            badge.className = 'badge bg-danger rounded-pill notification-badge';
                            badge.textContent = count;
                            badge.style.marginRight = '5px';
                            badge.style.fontSize = '0.7rem';
                            link.appendChild(badge);
                        }
                    });
                })
                .catch(error => {
                    console.error('خطأ في تحديث عداد الإشعارات:', error);
                });
        {% endif %}
    }
    
    // تحديث العداد عند تحميل الصفحة
    document.addEventListener('DOMContentLoaded', function() {
        updateNotificationCounter();
        
        // تحديث العداد كل دقيقة
        setInterval(updateNotificationCounter, 60000);
    });
</script>
```

## 4. تأكد من إنشاء المجلدات المطلوبة

تأكد من إنشاء المجلدات التالية للصور والملفات الخاصة بالإشعارات:

```bash
static/uploads/notifications
```

## 5. تطبيق تعديلات صفحة الإشعارات

استخدم التعليمات الموجودة في ملف `INSTRUCCIONES_NOTIFICACIONES.md` لإكمال تعديل صفحة إدارة الإشعارات.

## 6. تشغيل Service Worker Scheduler

أضف الكود التالي في نهاية ملف app.py لضمان إرسال الإشعارات المجدولة:

```python
@app.before_first_request
def initialize_app():
    """تهيئة التطبيق"""
    # إنشاء مجلد الرفع إذا لم يكن موجوداً
    os.makedirs(os.path.join(app.static_folder, 'uploads', 'notifications'), exist_ok=True)
    
    # إنشاء مفاتيح VAPID إذا لم تكن موجودة
    from notifications import NotificationManager
    NotificationManager.get_vapid_keys()
    
    # بدء جدولة إرسال الإشعارات المجدولة
    def send_scheduled_notifications():
        with app.app_context():
            while True:
                NotificationManager.send_scheduled_notifications()
                time.sleep(60)  # التحقق كل دقيقة
    
    import threading
    import time
    scheduler_thread = threading.Thread(target=send_scheduled_notifications)
    scheduler_thread.daemon = True
    scheduler_thread.start()
```

**ملاحظة**: لا تنسى إضافة import للمكتبات المطلوبة:

```python
import threading
import time
```

## 7. تعديل رابط Service Worker في صفحة base.html

تأكد من أن رابط Service Worker في صفحة base.html صحيح:

```html
<script>
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('✅ Service Worker registered:', registration.scope);
                })
                .catch(error => {
                    console.error('❌ Service Worker registration failed:', error);
                });
        });
    }
</script>
```

## بعد تطبيق جميع التغييرات:

1. أعد تشغيل الخادم
2. تأكد من عمل نظام PWA بشكل صحيح
3. جرب إرسال إشعارات من صفحة المدير
4. تأكد من استلام العميل للإشعارات

هذا يكمل تكامل نظام الإشعارات مع دعم PWA الكامل في نظام COFFLOW.
