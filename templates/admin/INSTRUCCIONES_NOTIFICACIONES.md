# تعليمات تحديث ملف إشعارات المدير

لإكمال ملف نظام الإشعارات، يجب اتباع الخطوات التالية:

## الخطوة 1: إضافة النوافذ المنبثقة (Modals)

أضف الكود التالي قبل نهاية الـ `div.container` (بعد آخر div.col-md-8):

```html
<!-- نافذة حوار تفاصيل الإشعار -->
<div class="modal fade" id="notificationDetailModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">تفاصيل الإشعار</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body" id="notification-detail-content">
                <!-- سيتم ملؤها من JavaScript -->
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                <button type="button" class="btn btn-danger" id="delete-notification-btn">
                    <i class="fas fa-trash"></i> حذف الإشعار
                </button>
            </div>
        </div>
    </div>
</div>

<!-- نافذة حوار التأكيد -->
<div class="modal fade" id="confirmationModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered modal-sm">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">تأكيد</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p id="confirmation-message">هل أنت متأكد من أنك تريد حذف هذا الإشعار؟</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                <button type="button" class="btn btn-danger" id="confirm-action-btn">حذف</button>
            </div>
        </div>
    </div>
</div>
```

## الخطوة 2: إضافة سكريبت جافاسكريبت

أضف هذا الكود في نهاية الملف (بعد {% endblock %} الخاص بـ content):

```html
{% block extra_js %}
<script>
    // متغيرات عامة
    let currentPage = 1;
    let totalPages = 1;
    let currentFilter = 'all';
    let detailModal;
    let confirmModal;
    let selectedNotificationId = null;
    let customersData = [];
    
    // عند تحميل الصفحة
    document.addEventListener('DOMContentLoaded', function() {
        // تهيئة modals
        detailModal = new bootstrap.Modal(document.getElementById('notificationDetailModal'));
        confirmModal = new bootstrap.Modal(document.getElementById('confirmationModal'));
        
        // تحميل الإشعارات
        loadNotifications(1);
        
        // تحميل العملاء للاختيار
        loadCustomers();
        
        // مستمع نموذج الإشعار الجديد
        document.getElementById('new-notification-form').addEventListener('submit', function(e) {
            e.preventDefault();
            createNotification();
        });
        
        // مستمع زر التحديث
        document.getElementById('refresh-notifications').addEventListener('click', function() {
            loadNotifications(1);
        });
        
        // مستمعات الفلاتر
        document.querySelectorAll('.filter-option').forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                currentFilter = this.getAttribute('data-filter');
                loadNotifications(1);
            });
        });
        
        // مستمع لمعاينة الصورة
        document.getElementById('notification-image').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('image-preview');
                    preview.src = e.target.result;
                    document.getElementById('image-preview-container').classList.remove('d-none');
                };
                reader.readAsDataURL(file);
            } else {
                document.getElementById('image-preview-container').classList.add('d-none');
            }
        });
        
        // مستمعات خيارات الإرسال
        document.getElementById('scope-specific').addEventListener('change', function() {
            if (this.checked) {
                document.getElementById('customers-selector-container').classList.remove('d-none');
            }
        });
        
        document.getElementById('scope-all').addEventListener('change', function() {
            if (this.checked) {
                document.getElementById('customers-selector-container').classList.add('d-none');
            }
        });
        
        // مستمعات توقيت الإرسال
        document.getElementById('schedule-later').addEventListener('change', function() {
            if (this.checked) {
                document.getElementById('schedule-datetime-container').classList.remove('d-none');
            }
        });
        
        document.getElementById('schedule-now').addEventListener('change', function() {
            if (this.checked) {
                document.getElementById('schedule-datetime-container').classList.add('d-none');
            }
        });
        
        // مستمع زر حذف الإشعار
        document.getElementById('delete-notification-btn').addEventListener('click', function() {
            if (selectedNotificationId) {
                showConfirmation('هل أنت متأكد من أنك تريد حذف هذا الإشعار؟', function() {
                    deleteNotification(selectedNotificationId);
                });
            }
        });
    });
    
    // تحميل الإشعارات
    function loadNotifications(page) {
        currentPage = page;
        
        // إظهار مؤشر التحميل
        document.getElementById('loading-indicator').classList.remove('d-none');
        document.getElementById('no-notifications').classList.add('d-none');
        
        // تحديث عدادات الإحصائيات
        updateStatistics();
        
        // طلب الإشعارات من الخادم
        fetch(`/api/admin/notifications?page=${page}&filter=${currentFilter}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading-indicator').classList.add('d-none');
                
                const notificationsList = document.getElementById('notifications-list');
                // إزالة الإشعارات السابقة (باستثناء مؤشر التحميل)
                Array.from(notificationsList.children).forEach(child => {
                    if (child.id !== 'loading-indicator') {
                        child.remove();
                    }
                });
                
                if (data.notifications && data.notifications.length > 0) {
                    // إضافة الإشعارات إلى القائمة
                    data.notifications.forEach(notification => {
                        const notificationElement = createNotificationElement(notification);
                        notificationsList.appendChild(notificationElement);
                    });
                    
                    // تحديث الترقيم
                    updatePagination(data.current_page, data.total_pages);
                } else {
                    document.getElementById('no-notifications').classList.remove('d-none');
                    document.getElementById('pagination').innerHTML = '';
                }
            })
            .catch(error => {
                console.error('خطأ في تحميل الإشعارات:', error);
                document.getElementById('loading-indicator').classList.add('d-none');
                document.getElementById('no-notifications').classList.remove('d-none');
            });
    }
    
    // إنشاء عنصر الإشعار
    function createNotificationElement(notification) {
        const listItem = document.createElement('a');
        listItem.className = 'list-group-item list-group-item-action';
        listItem.setAttribute('data-id', notification.id);
        
        // تحديد الأيقونة بناءً على النوع
        let icon = 'bell';
        if (notification.icon) {
            icon = notification.icon;
        } else if (notification.type === 'promotion') {
            icon = 'tag';
        } else if (notification.type === 'alert') {
            icon = 'exclamation-circle';
        } else if (notification.type === 'news') {
            icon = 'newspaper';
        }
        
        // تحديد نص النوع
        let typeText = 'إشعار';
        let typeBadgeClass = 'bg-secondary';
        
        if (notification.type === 'promotion') {
            typeText = 'عرض';
            typeBadgeClass = 'bg-success';
        } else if (notification.type === 'alert') {
            typeText = 'تنبيه';
            typeBadgeClass = 'bg-danger';
        } else if (notification.type === 'news') {
            typeText = 'أخبار';
            typeBadgeClass = 'bg-info';
        }
        
        // صياغة التاريخ
        const createdAt = new Date(notification.created_at);
        const formattedDate = createdAt.toLocaleString('ar-SA', { 
            day: 'numeric', 
            month: 'short', 
            year: 'numeric',
            hour: 'numeric',
            minute: 'numeric'
        });
        
        // المحتوى الداخلي
        listItem.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="me-3">
                    <span class="notification-icon notification-icon-${notification.type}">
                        <i class="fas fa-${icon}"></i>
                    </span>
                </div>
                <div class="flex-grow-1 ms-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="mb-1 notification-title">${notification.title}</h6>
                        <span class="badge ${typeBadgeClass}">${typeText}</span>
                    </div>
                    <p class="mb-1 text-muted small notification-date">
                        <i class="far fa-clock"></i> ${formattedDate}
                    </p>
                    <p class="mb-1 notification-content text-truncate">${notification.body}</p>
                    <div class="notification-status">
                        <small class="text-muted">
                            ${notification.scheduled_at ? `<i class="far fa-calendar-alt"></i> مجدول: ${new Date(notification.scheduled_at).toLocaleString('ar-SA')}` : ''}
                            ${notification.recipients && notification.recipients.length ? `<i class="fas fa-users"></i> ${notification.recipients.length} مستلم` : ''}
                        </small>
                    </div>
                </div>
            </div>
        `;
        
        // مستمع النقر لعرض التفاصيل
        listItem.addEventListener('click', function() {
            showNotificationDetails(notification.id);
        });
        
        return listItem;
    }
</script>
{% endblock %}
```

## الخطوة 3: إضافة وظائف جافاسكريبت إضافية

بعد السكريبت السابق مباشرة، أضف هذه الوظائف:

```html
<script>
    // تحديث الترقيم
    function updatePagination(currentPage, totalPages) {
        const pagination = document.getElementById('pagination');
        pagination.innerHTML = '';
        
        // إذا كان هناك صفحة واحدة فقط، لا داعي للترقيم
        if (totalPages <= 1) {
            return;
        }
        
        // زر الصفحة السابقة
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `<a class="page-link" href="#"><i class="fas fa-chevron-right"></i></a>`;
        prevLi.addEventListener('click', function(e) {
            e.preventDefault();
            if (currentPage > 1) {
                loadNotifications(currentPage - 1);
            }
        });
        pagination.appendChild(prevLi);
        
        // أرقام الصفحات
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, startPage + 4);
        
        for (let i = startPage; i <= endPage; i++) {
            const pageLi = document.createElement('li');
            pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`;
            pageLi.innerHTML = `<a class="page-link" href="#">${i}</a>`;
            pageLi.addEventListener('click', function(e) {
                e.preventDefault();
                loadNotifications(i);
            });
            pagination.appendChild(pageLi);
        }
        
        // زر الصفحة التالية
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = `<a class="page-link" href="#"><i class="fas fa-chevron-left"></i></a>`;
        nextLi.addEventListener('click', function(e) {
            e.preventDefault();
            if (currentPage < totalPages) {
                loadNotifications(currentPage + 1);
            }
        });
        pagination.appendChild(nextLi);
    }
    
    // تحميل العملاء للاختيار
    function loadCustomers() {
        fetch('/api/admin/customers?simple=true')
            .then(response => response.json())
            .then(data => {
                if (data.customers && data.customers.length > 0) {
                    customersData = data.customers;
                    
                    const selectElement = document.getElementById('customers-selector');
                    data.customers.forEach(customer => {
                        const option = document.createElement('option');
                        option.value = customer.id;
                        option.textContent = `${customer.name} - ${customer.phone}`;
                        selectElement.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('خطأ في تحميل العملاء:', error);
            });
    }
    
    // إنشاء إشعار جديد
    function createNotification() {
        const form = document.getElementById('new-notification-form');
        
        // التحقق من النموذج
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        // إعداد البيانات
        const formData = new FormData();
        formData.append('title', document.getElementById('notification-title').value);
        formData.append('body', document.getElementById('notification-body').value);
        formData.append('type', document.getElementById('notification-type').value);
        formData.append('icon', document.getElementById('notification-icon').value);
        
        // الصورة (إذا تم تحميلها)
        const imageFile = document.getElementById('notification-image').files[0];
        if (imageFile) {
            formData.append('image', imageFile);
        }
        
        // رابط العمل
        const actionUrl = document.getElementById('notification-action').value;
        if (actionUrl) {
            formData.append('action_url', actionUrl);
        }
        
        // المستلمون
        const scope = document.querySelector('input[name="notification-scope"]:checked').value;
        formData.append('is_public', scope === 'all' ? 'true' : 'false');
        
        if (scope === 'specific') {
            const selectedCustomers = Array.from(document.getElementById('customers-selector').selectedOptions).map(option => option.value);
            if (selectedCustomers.length === 0) {
                alert('الرجاء اختيار عميل واحد على الأقل');
                return;
            }
            formData.append('recipients', JSON.stringify(selectedCustomers));
        }
        
        // التوقيت
        const schedule = document.querySelector('input[name="notification-schedule"]:checked').value;
        if (schedule === 'later') {
            const scheduledDateTime = document.getElementById('schedule-datetime').value;
            if (!scheduledDateTime) {
                alert('الرجاء تحديد وقت الإرسال');
                return;
            }
            formData.append('scheduled_at', scheduledDateTime);
        }
        
        // تاريخ الانتهاء
        const expiryDate = document.getElementById('notification-expiry').value;
        if (expiryDate) {
            formData.append('expire_at', expiryDate);
        }
        
        // إرسال البيانات إلى الخادم
        fetch('/api/admin/notifications/create', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // إعادة تحميل الإشعارات
                loadNotifications(1);
                
                // إعادة تعيين النموذج
                form.reset();
                document.getElementById('image-preview-container').classList.add('d-none');
                document.getElementById('customers-selector-container').classList.add('d-none');
                document.getElementById('schedule-datetime-container').classList.add('d-none');
                
                // إظهار رسالة نجاح
                alert('تم إنشاء الإشعار بنجاح');
            } else {
                alert('حدث خطأ أثناء إنشاء الإشعار: ' + (data.message || 'خطأ غير معروف'));
            }
        })
        .catch(error => {
            console.error('خطأ في إنشاء الإشعار:', error);
            alert('حدث خطأ أثناء إنشاء الإشعار');
        });
    }
    
    // عرض تفاصيل الإشعار
    function showNotificationDetails(notificationId) {
        selectedNotificationId = notificationId;
        
        fetch(`/api/admin/notifications/${notificationId}`)
            .then(response => response.json())
            .then(data => {
                if (data.notification) {
                    const notification = data.notification;
                    
                    // تحديد نوع الإشعار
                    let typeText = 'إشعار';
                    let typeClass = 'secondary';
                    
                    if (notification.type === 'promotion') {
                        typeText = 'عرض';
                        typeClass = 'success';
                    } else if (notification.type === 'alert') {
                        typeText = 'تنبيه';
                        typeClass = 'danger';
                    } else if (notification.type === 'news') {
                        typeText = 'أخبار';
                        typeClass = 'info';
                    }
                    
                    // تنسيق التواريخ
                    const createdAt = new Date(notification.created_at).toLocaleString('ar-SA');
                    const scheduledAt = notification.scheduled_at ? new Date(notification.scheduled_at).toLocaleString('ar-SA') : 'غير مجدول';
                    const expireAt = notification.expire_at ? new Date(notification.expire_at).toLocaleString('ar-SA') : 'غير محدد';
                    
                    // إعداد HTML التفاصيل
                    const detailContent = document.getElementById('notification-detail-content');
                    detailContent.innerHTML = `
                        <div class="text-center mb-3">
                            <span class="notification-icon notification-icon-${notification.type} mx-auto">
                                <i class="fas fa-${notification.icon || 'bell'}"></i>
                            </span>
                            <h4 class="mt-2">${notification.title}</h4>
                            <span class="badge bg-${typeClass} mb-2">${typeText}</span>
                            <p class="text-muted small">
                                <i class="far fa-calendar-alt"></i> تم الإنشاء: ${createdAt}
                            </p>
                        </div>
                        
                        <div class="notification-details">
                            <div class="mb-3">
                                <label class="form-label fw-bold">المحتوى:</label>
                                <p>${notification.body}</p>
                            </div>
                            
                            ${notification.image_url ? `
                            <div class="mb-3">
                                <label class="form-label fw-bold">الصورة:</label>
                                <div>
                                    <img src="${notification.image_url}" class="img-fluid rounded" style="max-height: 200px">
                                </div>
                            </div>
                            ` : ''}
                            
                            ${notification.action_url ? `
                            <div class="mb-3">
                                <label class="form-label fw-bold">رابط العمل:</label>
                                <p><a href="${notification.action_url}" target="_blank">${notification.action_url}</a></p>
                            </div>
                            ` : ''}
                            
                            <div class="mb-3">
                                <label class="form-label fw-bold">حالة الجدولة:</label>
                                <p>${notification.scheduled_at ? '<span class="badge bg-warning">مجدول</span> ' + scheduledAt : '<span class="badge bg-success">تم الإرسال</span>'}</p>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label fw-bold">تاريخ انتهاء الصلاحية:</label>
                                <p>${expireAt}</p>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label fw-bold">نوع الإرسال:</label>
                                <p>${notification.is_public ? '<span class="badge bg-info">عام - لجميع العملاء</span>' : '<span class="badge bg-primary">خاص - لعملاء محددين</span>'}</p>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label fw-bold">إحصائيات:</label>
                                <div class="row">
                                    <div class="col">
                                        <div class="border rounded p-2 text-center">
                                            <h5>${notification.stats.total_recipients || 0}</h5>
                                            <small class="text-muted">إجمالي المستلمين</small>
                                        </div>
                                    </div>
                                    <div class="col">
                                        <div class="border rounded p-2 text-center">
                                            <h5>${notification.stats.read_count || 0}</h5>
                                            <small class="text-muted">قراءات</small>
                                        </div>
                                    </div>
                                    <div class="col">
                                        <div class="border rounded p-2 text-center">
                                            <h5>${notification.stats.sent_count || 0}</h5>
                                            <small class="text-muted">إرسال</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    detailModal.show();
                } else {
                    alert('تعذر العثور على الإشعار');
                }
            })
            .catch(error => {
                console.error('خطأ في جلب تفاصيل الإشعار:', error);
                alert('حدث خطأ أثناء تحميل تفاصيل الإشعار');
            });
    }
    
    // حذف إشعار
    function deleteNotification(notificationId) {
        fetch(`/api/admin/notifications/${notificationId}/delete`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                detailModal.hide();
                loadNotifications(currentPage);
            } else {
                alert('حدث خطأ أثناء حذف الإشعار: ' + (data.message || 'خطأ غير معروف'));
            }
        })
        .catch(error => {
            console.error('خطأ في حذف الإشعار:', error);
            alert('حدث خطأ أثناء حذف الإشعار');
        });
    }
    
    // تحديث الإحصائيات
    function updateStatistics() {
        fetch('/api/admin/notifications/stats')
            .then(response => response.json())
            .then(data => {
                if (data.stats) {
                    document.getElementById('stats-total').textContent = data.stats.total || 0;
                    document.getElementById('stats-read').textContent = data.stats.read || 0;
                    document.getElementById('stats-promotion').textContent = data.stats.promotion || 0;
                    document.getElementById('stats-alert').textContent = data.stats.alert || 0;
                }
            })
            .catch(error => {
                console.error('خطأ في تحميل الإحصائيات:', error);
            });
    }
    
    // عرض نافذة التأكيد
    function showConfirmation(message, callback) {
        document.getElementById('confirmation-message').textContent = message;
        
        // إزالة المستمعات السابقة
        const confirmButton = document.getElementById('confirm-action-btn');
        const newConfirmButton = confirmButton.cloneNode(true);
        confirmButton.parentNode.replaceChild(newConfirmButton, confirmButton);
        
        // إضافة مستمع جديد
        newConfirmButton.addEventListener('click', function() {
            confirmModal.hide();
            callback();
        });
        
        confirmModal.show();
    }
</script>
```

## ملاحظات هامة:
- أضف الكود أعلاه في أماكنه المحددة في الملف `notifications.html` الموجود.
- يجب أن تقع النوافذ المنبثقة داخل عنصر div.container الموجود في المحتوى.
- يجب أن يكون السكريبت مباشرة بعد انتهاء `{% endblock %}` الخاص بـ content.
- تأكد من عدم تكرار أي من العناصر.

## إنشاء API النظام

بعد تحديث الملفات، تحتاج إلى إنشاء نقاط الـ API التالية:

1. `/api/admin/notifications` - للحصول على قائمة الإشعارات
2. `/api/admin/notifications/create` - لإنشاء إشعار جديد
3. `/api/admin/notifications/{id}` - للحصول على تفاصيل إشعار معين
4. `/api/admin/notifications/{id}/delete` - لحذف إشعار
5. `/api/admin/notifications/stats` - للحصول على الإحصائيات
6. `/api/admin/customers?simple=true` - للحصول على قائمة العملاء مبسطة

هذه الأجزاء موجودة في الملفات:
- `notifications_modals.html` (النوافذ المنبثقة)
- `notifications_js.html` و `notifications_js_part2.html` (الجافاسكريبت)

يمكنك نسخ هذه الأكواد في ملف notifications.html الأصلي في الأماكن المناسبة.
