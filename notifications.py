"""
وحدة الإشعارات والتكامل مع Web Push API
"""
from pywebpush import webpush, WebPushException
import json
import base64
from py_vapid import Vapid
from datetime import datetime, timedelta
from urllib.parse import urlparse
from models import db, Notification, User, Settings, user_notifications
import logging
import os

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notifications")

class NotificationManager:
    """مدير الإشعارات ودفع الإشعارات"""

    @staticmethod
    def generate_vapid_keys():
        """توليد مفاتيح VAPID لاستخدامها في إشعارات الويب"""
        try:
            vapid = Vapid()
            vapid_key = vapid.generate_keys()
            private_key = vapid.private_key.decode('utf-8')
            public_key = vapid.public_key.decode('utf-8')
            
            # حفظ المفاتيح في الإعدادات
            settings = Settings.query.first()
            if not settings:
                settings = Settings()
                db.session.add(settings)
                
            settings.push_public_key = public_key
            settings.push_private_key = private_key
            db.session.commit()
            
            return {
                "public_key": public_key,
                "private_key": private_key
            }
        except Exception as e:
            logger.error(f"خطأ في توليد مفاتيح VAPID: {str(e)}")
            return None

    @staticmethod
    def get_vapid_keys():
        """الحصول على مفاتيح VAPID الحالية، أو توليد مفاتيح جديدة إذا لم تكن موجودة"""
        settings = Settings.query.first()
        
        if not settings or not settings.push_public_key or not settings.push_private_key:
            return NotificationManager.generate_vapid_keys()
        
        return {
            "public_key": settings.push_public_key,
            "private_key": settings.push_private_key
        }

    @staticmethod
    def save_subscription(user_id, subscription_json):
        """حفظ اشتراك الإشعارات للمستخدم"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            user.push_subscription = json.dumps(subscription_json)
            user.allow_notifications = True
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"خطأ في حفظ اشتراك الإشعارات: {str(e)}")
            return False

    @staticmethod
    def send_push_notification_to_user(user_id, notification_id):
        """إرسال إشعار دفع إلى مستخدم محدد"""
        try:
            user = User.query.get(user_id)
            notification = Notification.query.get(notification_id)
            
            if not user or not notification or not user.push_subscription or not user.allow_notifications:
                return False
            
            subscription_info = json.loads(user.push_subscription)
            vapid_keys = NotificationManager.get_vapid_keys()
            
            if not vapid_keys:
                return False
            
            data = notification.to_dict()
            
            # استخراج domain من اشتراك المستخدم
            endpoint = subscription_info.get('endpoint', '')
            domain = urlparse(endpoint).netloc
            
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(data),
                vapid_private_key=vapid_keys['private_key'],
                vapid_claims={
                    "sub": f"mailto:admin@cofflow.com",
                    "aud": f"https://{domain}" if domain else None,
                    "exp": int((datetime.now() + timedelta(hours=12)).timestamp())
                }
            )
            
            # تحديث حالة الإشعار
            stmt = db.text("""
                UPDATE user_notifications
                SET is_sent = TRUE, sent_at = :sent_at
                WHERE user_id = :user_id AND notification_id = :notification_id
            """)
            
            db.session.execute(stmt, {"user_id": user_id, "notification_id": notification_id, "sent_at": datetime.now()})
            db.session.commit()
            
            return True
        except WebPushException as e:
            logger.error(f"خطأ في إرسال الإشعار: {str(e)}")
            # إذا كان الخطأ هو أن الاشتراك غير صالح، قم بإلغاء اشتراك المستخدم
            if e.response and e.response.status_code in [404, 410]:
                logger.info(f"إلغاء اشتراك المستخدم {user_id} بسبب بطلان الاشتراك")
                user = User.query.get(user_id)
                if user:
                    user.push_subscription = None
                    user.allow_notifications = False
                    db.session.commit()
            return False
        except Exception as e:
            logger.error(f"خطأ في إرسال الإشعار: {str(e)}")
            return False

    @staticmethod
    def create_notification(title, body, type, created_by, recipients=None, is_public=True, **kwargs):
        """إنشاء إشعار جديد"""
        try:
            notification = Notification(
                title=title,
                body=body,
                type=type,
                is_public=is_public,
                created_by=created_by,
                image_url=kwargs.get('image_url'),
                action_url=kwargs.get('action_url'),
                icon=kwargs.get('icon', 'bell'),
                scheduled_at=kwargs.get('scheduled_at'),
                expire_at=kwargs.get('expire_at')
            )
            db.session.add(notification)
            db.session.flush()  # للحصول على معرف الإشعار
            
            # إضافة المستلمين
            if is_public:
                # إضافة جميع المستخدمين الذين سمحوا بالإشعارات
                users = User.query.filter_by(role='customer', allow_notifications=True).all()
                notification.recipients.extend(users)
            elif recipients and isinstance(recipients, list):
                # إضافة المستلمين المحددين
                users = User.query.filter(User.id.in_(recipients), User.allow_notifications==True).all()
                notification.recipients.extend(users)
            
            db.session.commit()
            
            # إرسال الإشعارات فوراً إذا لم تكن مجدولة
            if not notification.scheduled_at:
                for user in notification.recipients:
                    NotificationManager.send_push_notification_to_user(user.id, notification.id)
            
            return notification.id
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في إنشاء الإشعار: {str(e)}")
            return None

    @staticmethod
    def get_user_notifications(user_id, unread_only=False, page=1, per_page=10):
        """الحصول على إشعارات المستخدم"""
        try:
            user = User.query.get(user_id)
            if not user:
                return []
            
            # الاستعلام عن إشعارات المستخدم
            query = db.session.query(
                Notification, 
                db.literal(False).label('is_read')
            ).join(
                Notification.recipients
            ).filter(
                User.id == user_id
            )
            
            if unread_only:
                query = query.filter(db.text("user_notifications.is_read = FALSE"))
            
            query = query.order_by(Notification.created_at.desc())
            
            # التقسيم إلى صفحات
            offset = (page - 1) * per_page
            notifications = query.limit(per_page).offset(offset).all()
            
            result = []
            for notification, is_read in notifications:
                notif_dict = notification.to_dict()
                notif_dict['is_read'] = is_read
                result.append(notif_dict)
            
            return result
        except Exception as e:
            logger.error(f"خطأ في الحصول على إشعارات المستخدم: {str(e)}")
            return []

    @staticmethod
    def mark_notification_read(user_id, notification_id):
        """تعليم الإشعار كمقروء"""
        try:
            stmt = db.text("""
                UPDATE user_notifications
                SET is_read = TRUE, read_at = :read_at
                WHERE user_id = :user_id AND notification_id = :notification_id
            """)
            
            db.session.execute(stmt, {"user_id": user_id, "notification_id": notification_id, "read_at": datetime.now()})
            db.session.commit()
            
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في تعليم الإشعار كمقروء: {str(e)}")
            return False

    @staticmethod
    def send_scheduled_notifications():
        """إرسال الإشعارات المجدولة"""
        try:
            now = datetime.now()
            
            # الحصول على الإشعارات المجدولة التي حان وقتها
            scheduled_notifications = Notification.query.filter(
                Notification.scheduled_at <= now,
                Notification.scheduled_at.isnot(None)
            ).all()
            
            for notification in scheduled_notifications:
                for user in notification.recipients:
                    if user.allow_notifications and user.push_subscription:
                        NotificationManager.send_push_notification_to_user(user.id, notification.id)
                
                # تحديث الإشعار لإزالة الجدولة
                notification.scheduled_at = None
                db.session.commit()
                
            return len(scheduled_notifications)
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في إرسال الإشعارات المجدولة: {str(e)}")
            return 0

    @staticmethod
    def delete_notification(notification_id):
        """حذف إشعار"""
        try:
            notification = Notification.query.get(notification_id)
            if not notification:
                return False
            
            db.session.delete(notification)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في حذف الإشعار: {str(e)}")
            return False

    @staticmethod
    def get_unread_count(user_id):
        """الحصول على عدد الإشعارات غير المقروءة"""
        try:
            count = db.session.query(db.func.count()).select_from(
                db.table('user_notifications')
            ).filter(
                db.text("user_id = :user_id AND is_read = FALSE")
            ).params(user_id=user_id).scalar()
            
            return count or 0
        except Exception as e:
            logger.error(f"خطأ في الحصول على عدد الإشعارات غير المقروءة: {str(e)}")
            return 0
