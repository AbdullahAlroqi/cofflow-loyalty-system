from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
import string

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """نموذج المستخدم الأساسي - يشمل العملاء والموظفين والإدارة"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'employee', 'customer'
    cups_count = db.Column(db.Integer, default=0)  # للعملاء فقط
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # حقول الإشعارات
    push_subscription = db.Column(db.Text, nullable=True)  # بيانات اشتراك Push
    last_notification_read = db.Column(db.DateTime, nullable=True)
    allow_notifications = db.Column(db.Boolean, default=True)  # تطابق مع قاعدة البيانات
    notifications_enabled = db.Column(db.Boolean, default=True)
    
    # ملاحظة: العلاقات محددة في النماذج الأخرى لتجنب التضارب
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def add_cup(self, cups_required):
        """إضافة كوب للعميل"""
        self.cups_count += 1
        
        # إذا وصل للعدد المطلوب، أنشئ كود وأعد العداد
        if self.cups_count >= cups_required:
            coupon = Coupon(
                customer_id=self.id,
                code=self.generate_coupon_code(),
                status='active'
            )
            db.session.add(coupon)
            self.cups_count = 0
            return coupon
        return None
    
    @staticmethod
    def generate_coupon_code():
        """توليد كود فريد"""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))


class Coupon(db.Model):
    """نموذج الكوبونات"""
    __tablename__ = 'coupons'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, used, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime, nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    used_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # العلاقات
    customer = db.relationship('User', foreign_keys=[customer_id], backref=db.backref('customer_coupons', lazy='dynamic'))
    employee = db.relationship('User', foreign_keys=[employee_id], backref=db.backref('processed_coupons', lazy='dynamic'))
    used_by_user = db.relationship('User', foreign_keys=[used_by], backref=db.backref('used_coupons', lazy='dynamic'))
    
    def use_coupon(self, employee_id, used_by_id=None):
        """تفعيل الكوبون كمستخدم"""
        if self.status != 'active':
            return False
        
        self.status = 'used'
        self.used_at = datetime.utcnow()
        self.employee_id = employee_id
        if used_by_id:
            self.used_by = used_by_id
        return True

class Transaction(db.Model):
    """نموذج العمليات"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # 'add_cup', 'redeem_coupon', 'admin_edit'
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    customer = db.relationship('User', foreign_keys=[customer_id], backref=db.backref('customer_transactions', lazy='dynamic'))
    employee = db.relationship('User', foreign_keys=[employee_id], backref=db.backref('employee_transactions', lazy='dynamic'))


class Settings(db.Model):
    """نموذج الإعدادات"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    cups_required = db.Column(db.Integer, default=6)  # عدد الأكواب المطلوبة للحصول على كوب مجاني
    logo_path = db.Column(db.String(255), nullable=True)
    primary_color = db.Column(db.String(7), default='#8B4513')  # لون بني للقهوة
    secondary_color = db.Column(db.String(7), default='#D2691E')
    
    # إعدادات الإشعارات
    push_public_key = db.Column(db.Text, nullable=True)
    push_private_key = db.Column(db.Text, nullable=True)
    notifications_enabled = db.Column(db.Boolean, default=True)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# جدول ربط المستخدمين بالإشعارات (Many-to-Many)
user_notifications = db.Table('user_notifications',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('notification_id', db.Integer, db.ForeignKey('notifications.id'), primary_key=True),
    db.Column('read_at', db.DateTime, nullable=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class Notification(db.Model):
    """نموذج الإشعارات"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False, default='general')  # general, offer, alert, news
    image_url = db.Column(db.String(500), nullable=True)
    action_url = db.Column(db.String(500), nullable=True)
    is_public = db.Column(db.Boolean, default=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scheduled_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    icon = db.Column(db.String(100), default='bell')
    
    # العلاقات
    creator = db.relationship('User', backref='created_notifications', foreign_keys=[creator_id])
    recipients = db.relationship('User', secondary=user_notifications, backref='received_notifications')
    
    def __repr__(self):
        return f'<Notification {self.title}>'
    
    def to_dict(self):
        """تحويل الإشعار إلى قاموس"""
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'type': self.type,
            'image_url': self.image_url,
            'action_url': self.action_url,
            # مفاتيح مختصرة متوافقة مع الواجهة الأمامية
            'image': self.image_url,
            'action': self.action_url,
            'is_public': self.is_public,
            'creator_id': self.creator_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'icon': self.icon
        }
