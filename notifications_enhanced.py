"""
مدير الإشعارات المحسن والمتقدم
"""
from pywebpush import webpush, WebPushException
import json
import base64
from py_vapid import Vapid
from datetime import datetime, timedelta
from models import db, Notification, User, Settings, user_notifications
import logging
import os
from urllib.parse import urlparse

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notifications_enhanced")

class EnhancedNotificationManager:
    """مدير الإشعارات المحسن مع مميزات متقدمة"""

    @staticmethod
    def generate_vapid_keys():
        """توليد مفاتيح VAPID جديدة"""
        try:
            vapid = Vapid()
            vapid.generate_key()
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
            
            logger.info("تم توليد مفاتيح VAPID جديدة")
            return {
                "public_key": public_key,
                "private_key": private_key
            }
        except Exception as e:
            logger.error(f"خطأ في توليد مفاتيح VAPID: {str(e)}")
            return None

    @staticmethod
    def get_vapid_keys():
        """الحصول على مفاتيح VAPID"""
        settings = Settings.query.first()
        
        if not settings or not settings.push_public_key or not settings.push_private_key:
            return EnhancedNotificationManager.generate_vapid_keys()
        
        return {
            "public_key": settings.push_public_key,
            "private_key": settings.push_private_key
        }

    @staticmethod
    def create_notification(title, body, notification_type='general', creator_id=None, 
                          recipients=None, image_url=None, action_url=None, 
                          scheduled_at=None, expires_at=None, icon='bell', send_immediately=True):
        """إنشاء إشعار جديد مع مميزات متقدمة"""
        try:
            # إنشاء الإشعار
            notification = Notification(
                title=title,
                body=body,
                type=notification_type,
                creator_id=creator_id,
                image_url=image_url,
                action_url=action_url,
                scheduled_at=scheduled_at,
                expires_at=expires_at,
                icon=icon,
                is_public=recipients is None
            )
            
            db.session.add(notification)
            db.session.flush()  # للحصول على ID
            
            # ربط المستلمين
            if recipients is None:
                # إشعار عام لجميع العملاء النشطين
                customers = User.query.filter(
                    User.role == 'customer',
                    User.notifications_enabled == True
                ).all()
                
                for customer in customers:
                    db.session.execute(
                        user_notifications.insert().values(
                            user_id=customer.id,
                            notification_id=notification.id
                        )
                    )
            else:
                # إشعار لمستلمين محددين
                for user_id in recipients:
                    user = User.query.get(user_id)
                    if user and user.notifications_enabled:
                        db.session.execute(
                            user_notifications.insert().values(
                                user_id=user_id,
                                notification_id=notification.id
                            )
                        )
            
            db.session.commit()
            
            # إرسال الإشعار فوراً إذا لم يكن مجدولاً
            if send_immediately and scheduled_at is None:
                EnhancedNotificationManager.send_notification_now(notification.id)
            
            logger.info(f"تم إنشاء إشعار جديد: {title} (ID: {notification.id})")
            return notification
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في إنشاء الإشعار: {e}")
            return None

    @staticmethod
    def send_notification_now(notification_id):
        """إرسال إشعار فوراً لجميع المستلمين"""
        try:
            notification = Notification.query.get(notification_id)
            if not notification:
                logger.error(f"الإشعار غير موجود: {notification_id}")
                return False
            
            # الحصول على المستلمين
            recipients = db.session.query(User)\
                .join(user_notifications)\
                .filter(user_notifications.c.notification_id == notification_id)\
                .filter(User.notifications_enabled == True)\
                .all()
            
            if not recipients:
                logger.warning(f"لا توجد مستلمين للإشعار: {notification_id}")
                return False
            
            # إعداد بيانات الإشعار
            notification_data = {
                'title': notification.title,
                'body': notification.body,
                'icon': f'/static/icons/{notification.icon}.png',
                'badge': '/static/icons/badge.png',
                'image': notification.image_url,
                'tag': f'notification-{notification.id}',
                'requireInteraction': notification.type in ['alert', 'offer'],
                'data': {
                    'id': notification.id,
                    'type': notification.type,
                    'url': notification.action_url or '/customer/notifications',
                    'timestamp': datetime.utcnow().isoformat()
                },
                'actions': []
            }
            
            # إضافة أزرار حسب نوع الإشعار
            if notification.type == 'offer':
                notification_data['actions'] = [
                    {'action': 'view_offer', 'title': '🎁 عرض العرض'},
                    {'action': 'dismiss', 'title': '❌ إغلاق'}
                ]
            elif notification.type == 'alert':
                notification_data['actions'] = [
                    {'action': 'acknowledge', 'title': '✅ فهمت'},
                    {'action': 'dismiss', 'title': '❌ إغلاق'}
                ]
            else:
                notification_data['actions'] = [
                    {'action': 'view', 'title': '👁️ عرض'},
                    {'action': 'dismiss', 'title': '❌ إغلاق'}
                ]
            
            success_count = 0
            failed_count = 0
            
            for user in recipients:
                if EnhancedNotificationManager.send_push_to_user(user.id, notification_data):
                    success_count += 1
                else:
                    failed_count += 1
            
            logger.info(f"إرسال الإشعار {notification_id}: نجح {success_count}, فشل {failed_count}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"خطأ في إرسال الإشعار: {e}")
            return False

    @staticmethod
    def send_push_to_user(user_id, notification_data):
        """إرسال إشعار Push لمستخدم محدد"""
        try:
            user = User.query.get(user_id)
            if not user or not user.push_subscription or not user.notifications_enabled:
                return False
            
            subscription_info = json.loads(user.push_subscription)
            vapid_keys = EnhancedNotificationManager.get_vapid_keys()
            
            if not vapid_keys:
                logger.error("مفاتيح VAPID غير متاحة")
                return False
            
            # إرسال الإشعار
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(notification_data),
                vapid_private_key=vapid_keys['private_key'],
                vapid_claims={
                    "sub": "mailto:admin@cofflow.com",
                    "exp": int((datetime.utcnow() + timedelta(hours=12)).timestamp())
                }
            )
            
            logger.info(f"تم إرسال إشعار للمستخدم {user.name} (ID: {user_id})")
            return True
            
        except WebPushException as ex:
            logger.error(f"خطأ WebPush للمستخدم {user_id}: {ex}")
            
            # إذا كان الاشتراك غير صالح، قم بإلغائه
            if ex.response and ex.response.status_code in [404, 410, 413]:
                user = User.query.get(user_id)
                if user:
                    user.push_subscription = None
                    db.session.commit()
                    logger.info(f"تم إلغاء اشتراك المستخدم {user_id} بسبب عدم صحة الاشتراك")
            
            return False
        except Exception as ex:
            logger.error(f"خطأ عام في إرسال الإشعار للمستخدم {user_id}: {ex}")
            return False

    @staticmethod
    def mark_as_read(user_id, notification_id):
        """تعليم إشعار كمقروء"""
        try:
            db.session.execute(
                user_notifications.update()
                .where(user_notifications.c.user_id == user_id)
                .where(user_notifications.c.notification_id == notification_id)
                .values(read_at=datetime.utcnow())
            )
            db.session.commit()
            logger.info(f"تم تعليم الإشعار {notification_id} كمقروء للمستخدم {user_id}")
            return True
        except Exception as e:
            logger.error(f"خطأ في تعليم الإشعار كمقروء: {e}")
            return False

    @staticmethod
    def mark_all_as_read(user_id):
        """تعليم جميع إشعارات المستخدم كمقروءة"""
        try:
            db.session.execute(
                user_notifications.update()
                .where(user_notifications.c.user_id == user_id)
                .where(user_notifications.c.read_at.is_(None))
                .values(read_at=datetime.utcnow())
            )
            db.session.commit()
            logger.info(f"تم تعليم جميع الإشعارات كمقروءة للمستخدم {user_id}")
            return True
        except Exception as e:
            logger.error(f"خطأ في تعليم جميع الإشعارات كمقروءة: {e}")
            return False

    @staticmethod
    def get_user_notifications(user_id, unread_only=False, limit=50):
        """الحصول على إشعارات المستخدم مع تفاصيل القراءة"""
        try:
            query = db.session.query(
                Notification,
                user_notifications.c.read_at,
                user_notifications.c.created_at.label('received_at')
            ).join(user_notifications)\
            .filter(user_notifications.c.user_id == user_id)
            
            if unread_only:
                query = query.filter(user_notifications.c.read_at.is_(None))
            
            # فلترة الإشعارات المنتهية الصلاحية
            query = query.filter(
                db.or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > datetime.utcnow()
                )
            )
            
            results = query.order_by(Notification.created_at.desc()).limit(limit).all()
            
            notifications = []
            for notification, read_at, received_at in results:
                notif_dict = notification.to_dict()
                notif_dict['is_read'] = read_at is not None
                notif_dict['read_at'] = read_at.isoformat() if read_at else None
                notif_dict['received_at'] = received_at.isoformat() if received_at else None
                notifications.append(notif_dict)
            
            return notifications
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على إشعارات المستخدم: {e}")
            return []

    @staticmethod
    def get_unread_count(user_id):
        """الحصول على عدد الإشعارات غير المقروءة"""
        try:
            count = db.session.query(user_notifications)\
                .filter(user_notifications.c.user_id == user_id)\
                .filter(user_notifications.c.read_at.is_(None))\
                .count()
            
            return count
        except Exception as e:
            logger.error(f"خطأ في الحصول على عدد الإشعارات غير المقروءة: {e}")
            return 0

    @staticmethod
    def get_notification_stats():
        """الحصول على إحصائيات شاملة للإشعارات"""
        try:
            # إحصائيات عامة
            total_notifications = Notification.query.count()
            public_notifications = Notification.query.filter_by(is_public=True).count()
            
            # إحصائيات حسب النوع
            type_stats = db.session.query(
                Notification.type,
                db.func.count(Notification.id)
            ).group_by(Notification.type).all()
            
            # إحصائيات القراءة
            total_sent = db.session.query(user_notifications).count()
            total_read = db.session.query(user_notifications)\
                .filter(user_notifications.c.read_at.isnot(None)).count()
            
            # إحصائيات المستخدمين
            active_users = User.query.filter_by(notifications_enabled=True).count()
            subscribed_users = User.query.filter(User.push_subscription.isnot(None)).count()
            
            # إحصائيات حديثة (آخر 7 أيام)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_notifications = Notification.query.filter(
                Notification.created_at >= week_ago
            ).count()
            
            return {
                'total_notifications': total_notifications,
                'public_notifications': public_notifications,
                'private_notifications': total_notifications - public_notifications,
                'type_stats': dict(type_stats),
                'total_sent': total_sent,
                'total_read': total_read,
                'unread': total_sent - total_read,
                'read_rate': round((total_read / total_sent * 100), 2) if total_sent > 0 else 0,
                'active_users': active_users,
                'subscribed_users': subscribed_users,
                'recent_notifications': recent_notifications
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإحصائيات: {e}")
            return {}

    @staticmethod
    def send_welcome_notification(user_id):
        """إرسال إشعار ترحيب للمستخدم الجديد"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            notification = EnhancedNotificationManager.create_notification(
                title=f"🎉 مرحباً {user.name}!",
                body="أهلاً بك في تطبيق COFFLOW! استمتع بتجميع النقاط والحصول على مشروبات مجانية.",
                notification_type='news',
                creator_id=1,  # المدير
                recipients=[user_id],
                icon='celebration',
                action_url='/customer/dashboard'
            )
            
            return notification is not None
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار الترحيب: {e}")
            return False

    @staticmethod
    def send_loyalty_notification(user_id, cups_count, cups_required):
        """إرسال إشعار نقاط الولاء"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            remaining = cups_required - cups_count
            
            if remaining == 0:
                # كوب مجاني جاهز
                title = "🎊 تهانينا! كوب مجاني جاهز!"
                body = "لقد جمعت العدد المطلوب من الأكواب. احصل على كوبك المجاني الآن!"
                notification_type = 'offer'
                icon = 'local_cafe'
            elif remaining == 1:
                # كوب واحد متبقي
                title = "☕ كوب واحد فقط للكوب المجاني!"
                body = f"أنت على بُعد كوب واحد فقط من الحصول على كوب مجاني. لديك {cups_count} من {cups_required} أكواب."
                notification_type = 'alert'
                icon = 'loyalty'
            else:
                # تحديث عادي
                title = f"☕ تم إضافة كوب جديد!"
                body = f"لديك الآن {cups_count} من {cups_required} أكواب. {remaining} أكواب متبقية للكوب المجاني."
                notification_type = 'general'
                icon = 'add_circle'
            
            notification = EnhancedNotificationManager.create_notification(
                title=title,
                body=body,
                notification_type=notification_type,
                creator_id=1,
                recipients=[user_id],
                icon=icon,
                action_url='/customer/dashboard'
            )
            
            return notification is not None
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار الولاء: {e}")
            return False

    @staticmethod
    def send_offer_notification(title, body, image_url=None, action_url=None, expires_at=None):
        """إرسال إشعار عرض خاص لجميع العملاء"""
        try:
            notification = EnhancedNotificationManager.create_notification(
                title=title,
                body=body,
                notification_type='offer',
                creator_id=1,
                recipients=None,  # جميع العملاء
                image_url=image_url,
                action_url=action_url,
                expires_at=expires_at,
                icon='local_offer'
            )
            
            return notification is not None
            
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار العرض: {e}")
            return False

    @staticmethod
    def cleanup_expired_notifications():
        """تنظيف الإشعارات المنتهية الصلاحية"""
        try:
            expired_notifications = Notification.query.filter(
                Notification.expires_at < datetime.utcnow()
            ).all()
            
            count = len(expired_notifications)
            
            for notification in expired_notifications:
                db.session.delete(notification)
            
            db.session.commit()
            
            logger.info(f"تم حذف {count} إشعار منتهي الصلاحية")
            return count
            
        except Exception as e:
            logger.error(f"خطأ في تنظيف الإشعارات المنتهية الصلاحية: {e}")
            return 0

    @staticmethod
    def save_user_subscription(user_id, subscription_data):
        """حفظ اشتراك الإشعارات للمستخدم"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            user.push_subscription = json.dumps(subscription_data)
            user.notifications_enabled = True
            db.session.commit()
            
            logger.info(f"تم حفظ اشتراك الإشعارات للمستخدم {user.name}")
            
            # إرسال إشعار ترحيب
            EnhancedNotificationManager.send_welcome_notification(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في حفظ اشتراك الإشعارات: {e}")
            return False
