"""
سكريبت لتحديث قائمة التنقل في base.html وإضافة روابط الإشعارات
"""

def update_base_navigation():
    # قراءة ملف base.html
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # التحقق من وجود رابط الإشعارات مسبقاً
    if 'admin_notifications' in content:
        print("✅ رابط الإشعارات موجود مسبقاً في base.html")
        return
    
    # إضافة رابط الإشعارات للمدير (بعد رابط العملاء)
    admin_notifications_link = '''                            <li class="nav-item">
                                <a class="nav-link" href="{{ url_for('admin_notifications') }}">
                                    <i class="fas fa-bell"></i> الإشعارات
                                </a>
                            </li>'''
    
    # البحث عن مكان إضافة الرابط (بعد رابط العملاء)
    customers_link_pattern = '''                            <li class="nav-item">
                                <a class="nav-link" href="{{ url_for('admin_customers') }}">
                                    <i class="fas fa-user-friends"></i> العملاء
                                </a>
                            </li>'''
    
    if customers_link_pattern in content:
        content = content.replace(customers_link_pattern, customers_link_pattern + '\n' + admin_notifications_link)
        print("✅ تم إضافة رابط الإشعارات للمدير")
    
    # إضافة رابط الإشعارات للعميل
    customer_notifications_link = '''                            <li class="nav-item">
                                <a class="nav-link" href="{{ url_for('customer_notifications') }}">
                                    <i class="fas fa-bell"></i> الإشعارات
                                </a>
                            </li>'''
    
    # البحث عن مكان إضافة الرابط للعميل (بعد سجل المشتريات)
    history_link_pattern = '''                            <li class="nav-item">
                                <a class="nav-link" href="{{ url_for('customer_history') }}">
                                    <i class="fas fa-history"></i> سجل المشتريات
                                </a>
                            </li>'''
    
    if history_link_pattern in content:
        content = content.replace(history_link_pattern, history_link_pattern + '\n' + customer_notifications_link)
        print("✅ تم إضافة رابط الإشعارات للعميل")
    
    # إضافة سكريبت تحديث عداد الإشعارات
    notification_counter_script = '''
<script>
    // تحديث عداد الإشعارات غير المقروءة
    function updateNotificationCounter() {
        // فقط للمستخدمين المسجلين
        {% if current_user.is_authenticated and current_user.role == 'customer' %}
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
</script>'''
    
    # إضافة السكريبت قبل نهاية body
    if '</body>' in content:
        content = content.replace('</body>', notification_counter_script + '\n</body>')
        print("✅ تم إضافة سكريبت عداد الإشعارات")
    
    # كتابة الملف المحدث
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ تم تحديث ملف base.html بنجاح!")

if __name__ == "__main__":
    update_base_navigation()
