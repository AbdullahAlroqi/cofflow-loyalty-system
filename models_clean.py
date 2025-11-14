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
    
    # العلاقات
    coupons = db.relationship('Coupon', backref='customer', lazy=True, foreign_keys='Coupon.customer_id')
    transactions = db.relationship('Transaction', backref='customer', lazy=True, foreign_keys='Transaction.customer_id')
    
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
    """نموذج الكوبونات (الأكواد المجانية)"""
    __tablename__ = 'coupons'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='active')  # 'active', 'used', 'expired'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime, nullable=True)
    used_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # الموظف الذي استخدم الكود
    
    def use_coupon(self, employee_id):
        """استخدام الكوبون"""
        if self.status == 'active':
            self.status = 'used'
            self.used_at = datetime.utcnow()
            self.used_by = employee_id
            return True
        return False


class Transaction(db.Model):
    """نموذج العمليات"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # 'add_cup', 'redeem_coupon', 'admin_edit'
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('User', foreign_keys=[employee_id])


class Settings(db.Model):
    """نموذج الإعدادات"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    cups_required = db.Column(db.Integer, default=6)  # عدد الأكواب المطلوبة للحصول على كوب مجاني
    logo_path = db.Column(db.String(255), nullable=True)
    primary_color = db.Column(db.String(7), default='#8B4513')  # لون بني للقهوة
    secondary_color = db.Column(db.String(7), default='#D2691E')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
