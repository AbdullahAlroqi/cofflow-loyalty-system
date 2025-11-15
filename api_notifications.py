"""
API وحدة إشعارات نظام COFFLOW

يقوم هذا الملف بإضافة نقاط API الضرورية للتعامل مع الإشعارات:
- إنشاء إشعارات جديدة
- قراءة الإشعارات
- حذف الإشعارات
- إحصائيات الإشعارات
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Notification, User
from notifications_enhanced import EnhancedNotificationManager
from notifications import NotificationManager
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from functools import wraps

notifications_api = Blueprint('notifications_api', __name__)

# وظيفة للتحقق من صلاحيات المدير
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'غير مصرح بالوصول'}), 403
        return f(*args, **kwargs)
    return decorated_function

# إضافة مسارات API لوحة التحكم
@notifications_api.route('/api/admin/notifications', methods=['GET'])
@login_required
@admin_required
def get_notifications():
    """الحصول على قائمة الإشعارات"""
    page = int(request.args.get('page', 1))
    filter_type = request.args.get('filter', 'all')
    per_page = 10
    
    # بناء الاستعلام
    query = Notification.query
    
    # تطبيق الفلتر إذا كان محدداً
    if filter_type != 'all':
        query = query.filter_by(type=filter_type)
    
    # ترتيب حسب تاريخ الإنشاء
    query = query.order_by(Notification.created_at.desc())
    
    # التقسيم إلى صفحات
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # تحويل البيانات للرد
    notifications = []
    for notification in paginated.items:
        # الحصول على عدد المستلمين
        recipient_count = len(notification.recipients)
        
        # إضافة الإشعار للقائمة
        notifications.append({
            'id': notification.id,
            'title': notification.title,
            'body': notification.body,
            'type': notification.type,
            'icon': notification.icon,
            'image_url': notification.image_url,
            'action_url': notification.action_url,
            'is_public': notification.is_public,
            'created_at': notification.created_at.isoformat(),
            'scheduled_at': notification.scheduled_at.isoformat() if notification.scheduled_at else None,
            'expire_at': notification.expire_at.isoformat() if notification.expire_at else None,
            'recipient_count': recipient_count
        })
    
    return jsonify({
        'notifications': notifications,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
        'total_pages': paginated.pages,
        'has_next': paginated.has_next,
        'has_prev': paginated.has_prev
    })

@notifications_api.route('/api/admin/notifications/create', methods=['POST'])
@login_required
@admin_required
def create_notification():
    """إنشاء إشعار جديد"""
    try:
        # قراءة البيانات من النموذج
        title = request.form.get('title')
        body = request.form.get('body')
        notification_type = request.form.get('type')
        icon = request.form.get('icon', 'bell')
        is_public = request.form.get('is_public', 'true') == 'true'

        # التحقق من الحقول الإلزامية
        if not all([title, body, notification_type]):
            return jsonify({'success': False, 'message': 'جميع الحقول المطلوبة غير مكتملة'}), 400

        # معالجة الصورة إذا تم تحميلها
        image_url = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename:
                filename = secure_filename(image.filename)
                timestamp = int(datetime.now().timestamp())
                filename = f"notification_{timestamp}_{filename}"

                # إنشاء مجلد إذا لم يكن موجوداً
                upload_folder = os.path.join(current_app.static_folder, 'uploads', 'notifications')
                os.makedirs(upload_folder, exist_ok=True)

                # حفظ الصورة
                image_path = os.path.join(upload_folder, filename)
                image.save(image_path)

                # تعيين رابط الصورة للاستعمال في الواجهة
                image_url = f"/static/uploads/notifications/{filename}"

        # رابط الإجراء (اختياري)
        action_url = request.form.get('action_url') or None

        # المستلمون
        recipients = None
        if not is_public:
            recipients_json = request.form.get('recipients')
            if recipients_json:
                try:
                    recipients = [int(r) for r in json.loads(recipients_json)]
                except Exception:
                    return jsonify({'success': False, 'message': 'تنسيق قائمة العملاء غير صحيح'}), 400

        # وقت الجدولة (اختياري)
        scheduled_at = None
        scheduled_raw = request.form.get('scheduled_at')
        if scheduled_raw:
            try:
                # قيمة datetime-local تأتي بدون منطقة زمنية، ويتم تفسيرها كما هي على الخادم
                scheduled_at = datetime.fromisoformat(scheduled_raw)
            except ValueError:
                return jsonify({'success': False, 'message': 'تنسيق تاريخ الجدولة غير صحيح'}), 400

        # تاريخ انتهاء الصلاحية (اختياري)
        expires_at = None
        expires_raw = request.form.get('expire_at')
        if expires_raw:
            try:
                expires_at = datetime.fromisoformat(expires_raw)
            except ValueError:
                return jsonify({'success': False, 'message': 'تنسيق تاريخ الانتهاء غير صحيح'}), 400

        # إذا كان الإشعار غير مجدول، أرسله فوراً
        send_immediately = scheduled_at is None

        # إنشاء الإشعار عبر المدير المحسن
        notification = EnhancedNotificationManager.create_notification(
            title=title,
            body=body,
            notification_type=notification_type or 'general',
            creator_id=current_user.id,
            recipients=recipients,
            image_url=image_url,
            action_url=action_url,
            scheduled_at=scheduled_at,
            expires_at=expires_at,
            icon=icon,
            send_immediately=send_immediately
        )
        
        if notification:
            return jsonify({
                'success': True, 
                'message': 'تم إنشاء الإشعار بنجاح',
                'notification': notification.to_dict()
            })
        else:
            return jsonify({'success': False, 'message': 'فشل في إنشاء الإشعار'}), 500
            
    except Exception as e:
        current_app.logger.error(f"خطأ في إنشاء الإشعار: {str(e)}")
        return jsonify({'success': False, 'message': f'حدث خطأ في الخادم: {str(e)}'}), 500

@notifications_api.route('/api/admin/notifications/<int:notification_id>', methods=['GET'])
@login_required
@admin_required
def get_notification(notification_id):
    """الحصول على تفاصيل إشعار معين"""
    try:
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return jsonify({'error': 'الإشعار غير موجود'}), 404
            
        # حساب الإحصائيات
        total_recipients = len(notification.recipients)
        read_count = db.session.query(db.func.count()).select_from(db.table('user_notifications')).filter(
            db.text("notification_id = :notification_id AND is_read = TRUE")
        ).params(notification_id=notification_id).scalar() or 0
        
        sent_count = db.session.query(db.func.count()).select_from(db.table('user_notifications')).filter(
            db.text("notification_id = :notification_id AND is_sent = TRUE")
        ).params(notification_id=notification_id).scalar() or 0
        
        # تحويل البيانات للرد
        notification_data = {
            'id': notification.id,
            'title': notification.title,
            'body': notification.body,
            'type': notification.type,
            'icon': notification.icon,
            'image_url': notification.image_url,
            'action_url': notification.action_url,
            'is_public': notification.is_public,
            'created_at': notification.created_at.isoformat(),
            'scheduled_at': notification.scheduled_at.isoformat() if notification.scheduled_at else None,
            'expire_at': notification.expire_at.isoformat() if notification.expire_at else None,
            'stats': {
                'total_recipients': total_recipients,
                'read_count': read_count,
                'sent_count': sent_count
            }
        }
        
        return jsonify({'notification': notification_data})
        
    except Exception as e:
        current_app.logger.error(f"خطأ في الحصول على تفاصيل الإشعار: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notifications_api.route('/api/admin/notifications/<int:notification_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_notification(notification_id):
    """حذف إشعار محدد"""
    try:
        if NotificationManager.delete_notification(notification_id):
            return jsonify({'success': True, 'message': 'تم حذف الإشعار بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'فشل حذف الإشعار'}), 404
    except Exception as e:
        current_app.logger.error(f"خطأ في حذف الإشعار: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@notifications_api.route('/api/admin/notifications/stats', methods=['GET'])
@login_required
@admin_required
def get_notification_stats():
    """الحصول على إحصائيات الإشعارات"""
    try:
        # إجمالي الإشعارات
        total_count = Notification.query.count()
        
        # عدد الإشعارات المقروءة
        read_count = db.session.query(db.func.count(db.distinct(db.text('notification_id')))).select_from(
            db.table('user_notifications')
        ).filter(db.text("is_read = TRUE")).scalar() or 0
        
        # عدد كل نوع من الإشعارات
        promotion_count = Notification.query.filter_by(type='promotion').count()
        alert_count = Notification.query.filter_by(type='alert').count()
        news_count = Notification.query.filter_by(type='news').count()
        
        return jsonify({
            'stats': {
                'total': total_count,
                'read': read_count,
                'promotion': promotion_count,
                'alert': alert_count,
                'news': news_count
            }
        })
    except Exception as e:
        current_app.logger.error(f"خطأ في الحصول على إحصائيات الإشعارات: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notifications_api.route('/api/admin/customers', methods=['GET'])
@login_required
@admin_required
def get_customers():
    """الحصول على قائمة العملاء للاختيار"""
    try:
        # التحقق مما إذا كان المطلوب هو قائمة مبسطة أم لا
        simple = request.args.get('simple', 'false').lower() == 'true'
        
        # الحصول على العملاء
        customers = User.query.filter_by(role='customer').all()
        
        # تحويل البيانات للرد
        customers_data = []
        for customer in customers:
            if simple:
                customers_data.append({
                    'id': customer.id,
                    'name': customer.name,
                    'phone': customer.phone
                })
            else:
                # عرض بيانات أكثر تفصيلاً للعملاء
                customers_data.append({
                    'id': customer.id,
                    'name': customer.name,
                    'phone': customer.phone,
                    'email': customer.email,
                    'cups_count': customer.cups_count,
                    'allow_notifications': customer.allow_notifications,
                    'created_at': customer.created_at.isoformat()
                })
        
        return jsonify({'customers': customers_data})
    except Exception as e:
        current_app.logger.error(f"خطأ في الحصول على قائمة العملاء: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ------- نقاط واجهة API العميل -------

@notifications_api.route('/api/notifications', methods=['GET'])
@login_required
def get_user_notifications():
    """الحصول على قائمة الإشعارات للمستخدم الحالي"""
    try:
        page = int(request.args.get('page', 1))
        filter_type = request.args.get('filter', 'all')
        unread_param = request.args.get('unread', 'false').lower() == 'true'

        # إذا كان الفلتر "unread"، اعتبره unread_only أيضاً
        unread_only = unread_param or (filter_type == 'unread')

        per_page = 10

        # جلب الإشعارات باستخدام المدير المحسن (يعيد قائمة قواميس)
        # نستخدم limit أكبر قليلاً لتغطية الصفحات الأولى
        max_items = per_page * page
        notifications = EnhancedNotificationManager.get_user_notifications(
            user_id=current_user.id,
            unread_only=unread_only,
            limit=max_items
        )

        # تطبيق الفلتر حسب النوع إذا لزم الأمر
        if filter_type not in ['all', 'unread']:
            notifications = [n for n in notifications if n.get('type') == filter_type]

        total_items = len(notifications)
        total_pages = (total_items + per_page - 1) // per_page or 1
        start_idx = max(0, (page - 1) * per_page)
        end_idx = min(start_idx + per_page, total_items)

        return jsonify({
            'notifications': notifications[start_idx:end_idx],
            'total': total_items,
            'pages': total_pages,
            'current_page': page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        })
        
    except Exception as e:
        current_app.logger.error(f"خطأ في الحصول على إشعارات المستخدم: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notifications_api.route('/api/notifications/mark-read', methods=['POST'])
@login_required
def mark_notification_read():
    """تعليم الإشعار كمقروء"""
    try:
        data = request.json
        notification_id = data.get('notification_id')
        
        if not notification_id:
            return jsonify({'success': False, 'message': 'معرف الإشعار مطلوب'}), 400
            
        # تعليم الإشعار كمقروء باستخدام المدير المحسن
        if EnhancedNotificationManager.mark_as_read(current_user.id, notification_id):
            return jsonify({'success': True, 'message': 'تم تعليم الإشعار كمقروء'})
        else:
            return jsonify({'success': False, 'message': 'فشل تعليم الإشعار كمقروء'}), 400
            
    except Exception as e:
        current_app.logger.error(f"خطأ في تعليم الإشعار كمقروء: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@notifications_api.route('/api/notifications/unread-count', methods=['GET'])
@login_required
def get_unread_count():
    """الحصول على عدد الإشعارات غير المقروءة"""
    try:
        count = EnhancedNotificationManager.get_unread_count(current_user.id)
        return jsonify({'count': count})
    except Exception as e:
        current_app.logger.error(f"خطأ في الحصول على عدد الإشعارات غير المقروءة: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notifications_api.route('/api/notifications/subscribe', methods=['POST'])
@login_required
def subscribe_to_notifications():
    """الاشتراك في الإشعارات"""
    try:
        data = request.json
        subscription = data.get('subscription')
        
        if not subscription:
            return jsonify({'success': False, 'message': 'بيانات الاشتراك مطلوبة'}), 400
            
        # حفظ اشتراك الإشعارات باستخدام المدير المحسن
        if EnhancedNotificationManager.save_user_subscription(current_user.id, subscription):
            return jsonify({'success': True, 'message': 'تم الاشتراك في الإشعارات بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'فشل الاشتراك في الإشعارات'}), 400
            
    except Exception as e:
        current_app.logger.error(f"خطأ في الاشتراك في الإشعارات: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@notifications_api.route('/api/notifications/vapid-public-key', methods=['GET'])
@login_required
def get_vapid_public_key():
    """الحصول على المفتاح العام للإشعارات"""
    try:
        keys = NotificationManager.get_vapid_keys()
        if keys:
            return jsonify({'publicKey': keys['public_key']})
        else:
            return jsonify({'error': 'لم يتم العثور على المفاتيح'}), 404
    except Exception as e:
        current_app.logger.error(f"خطأ في الحصول على المفتاح العام للإشعارات: {str(e)}")
        return jsonify({'error': str(e)}), 500

# دوال معالجة رد الإشعارات

@notifications_api.route('/api/notifications/confirm-delivery', methods=['POST'])
def confirm_notification_delivery():
    """تأكيد استلام الإشعار"""
    try:
        data = request.json
        notification_id = data.get('notification_id')
        
        # هنا يمكن تسجيل استلام الإشعار في قاعدة البيانات
        # هذه الدالة تستدعى من Service Worker عند عرض الإشعار
        
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f"خطأ في تأكيد استلام الإشعار: {str(e)}")
        return jsonify({'success': False}), 500

@notifications_api.route('/api/notifications/dismissed', methods=['POST'])
def notification_dismissed():
    """الإبلاغ عن رفض الإشعار"""
    try:
        data = request.json
        notification_id = data.get('notification_id')
        
        # هنا يمكن تسجيل رفض الإشعار في قاعدة البيانات
        # هذه الدالة تستدعى من Service Worker عند إغلاق الإشعار
        
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f"خطأ في الإبلاغ عن رفض الإشعار: {str(e)}")
        return jsonify({'success': False}), 500

# ==================== مسارات API محسنة ====================

@notifications_api.route('/api/notifications/stats', methods=['GET'])
@login_required
@admin_required
def get_enhanced_notification_stats():
    """الحصول على إحصائيات شاملة للإشعارات"""
    try:
        stats = EnhancedNotificationManager.get_notification_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        current_app.logger.error(f"خطأ في الحصول على الإحصائيات: {str(e)}")
        return jsonify({'success': False, 'message': 'فشل في الحصول على الإحصائيات'}), 500

@notifications_api.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """تعليم جميع إشعارات المستخدم كمقروءة"""
    try:
        success = EnhancedNotificationManager.mark_all_as_read(current_user.id)
        if success:
            return jsonify({'success': True, 'message': 'تم تعليم جميع الإشعارات كمقروءة'})
        else:
            return jsonify({'success': False, 'message': 'فشل في تعليم الإشعارات'}), 500
    except Exception as e:
        current_app.logger.error(f"خطأ في تعليم جميع الإشعارات: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ في الخادم'}), 500

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
        notification = EnhancedNotificationManager.create_notification(
            title=title,
            body=body,
            icon=icon,
            url=url,
            sender_id=current_user.id,
            recipients=recipients
        )
        
        # التأكد من إرسال الإشعار فوراً
        success = EnhancedNotificationManager.send_push_notification(
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
        current_app.logger.error(f"خطأ في إرسال الإشعار: {str(e)}")
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@notifications_api.route('/api/notifications/send-offer', methods=['POST'])
@login_required
@admin_required
def send_offer_notification():
    """إرسال إشعار عرض خاص لجميع العملاء"""
    try:
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('body'):
            return jsonify({'success': False, 'message': 'العنوان والمحتوى مطلوبان'}), 400
        
        # معالجة تاريخ الانتهاء
        expires_at = None
        if data.get('expires_at'):
            try:
                expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'success': False, 'message': 'تنسيق تاريخ الانتهاء غير صحيح'}), 400
        
        success = EnhancedNotificationManager.send_offer_notification(
            title=data['title'],
            body=data['body'],
            image_url=data.get('image_url'),
            action_url=data.get('action_url'),
            expires_at=expires_at
        )
        
        if success:
            return jsonify({'success': True, 'message': 'تم إرسال إشعار العرض بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'فشل في إرسال إشعار العرض'}), 500
            
    except Exception as e:
        current_app.logger.error(f"خطأ في إرسال إشعار العرض: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ في الخادم'}), 500

@notifications_api.route('/api/notifications/cleanup', methods=['POST'])
@login_required
@admin_required
def cleanup_expired_notifications():
    """تنظيف الإشعارات المنتهية الصلاحية"""
    try:
        count = EnhancedNotificationManager.cleanup_expired_notifications()
        return jsonify({
            'success': True, 
            'message': f'تم حذف {count} إشعار منتهي الصلاحية',
            'deleted_count': count
        })
    except Exception as e:
        current_app.logger.error(f"خطأ في تنظيف الإشعارات: {str(e)}")
        return jsonify({'success': False, 'message': 'فشل في تنظيف الإشعارات'}), 500

@notifications_api.route('/api/notifications/test', methods=['POST'])
@login_required
@admin_required
def send_test_notification():
    """إرسال إشعار تجريبي للمدير"""
    try:
        notification = EnhancedNotificationManager.create_notification(
            title="🧪 إشعار تجريبي",
            body="هذا إشعار تجريبي للتأكد من عمل النظام بشكل صحيح.",
            notification_type='general',
            creator_id=current_user.id,
            recipients=[current_user.id],
            icon='science'
        )
        
        if notification:
            return jsonify({'success': True, 'message': 'تم إرسال الإشعار التجريبي بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'فشل في إرسال الإشعار التجريبي'}), 500
            
    except Exception as e:
        current_app.logger.error(f"خطأ في إرسال الإشعار التجريبي: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ في الخادم'}), 500

@notifications_api.route('/api/notifications/vapid-keys', methods=['GET'])
@login_required
@admin_required
def get_vapid_keys():
    """الحصول على مفاتيح VAPID"""
    try:
        keys = EnhancedNotificationManager.get_vapid_keys()
        if keys:
            return jsonify({
                'success': True, 
                'public_key': keys['public_key']
            })
        else:
            return jsonify({'success': False, 'message': 'فشل في الحصول على مفاتيح VAPID'}), 500
    except Exception as e:
        current_app.logger.error(f"خطأ في الحصول على مفاتيح VAPID: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ في الخادم'}), 500

@notifications_api.route('/api/notifications/regenerate-keys', methods=['POST'])
@login_required
@admin_required
def regenerate_vapid_keys():
    """إعادة توليد مفاتيح VAPID"""
    try:
        keys = EnhancedNotificationManager.generate_vapid_keys()
        if keys:
            return jsonify({
                'success': True, 
                'message': 'تم إعادة توليد مفاتيح VAPID بنجاح',
                'public_key': keys['public_key']
            })
        else:
            return jsonify({'success': False, 'message': 'فشل في إعادة توليد مفاتيح VAPID'}), 500
    except Exception as e:
        current_app.logger.error(f"خطأ في إعادة توليد مفاتيح VAPID: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ في الخادم'}), 500
