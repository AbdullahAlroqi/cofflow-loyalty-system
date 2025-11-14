"""
سكريبت لإصلاح ملف models.py ليتوافق مع قاعدة البيانات الموجودة
"""

def fix_models():
    print("🔧 إصلاح ملف models.py...")
    
    # قراءة الملف الحالي
    with open('models.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إنشاء نسخة مبسطة من User بدون الحقول الجديدة مؤقتاً
    new_user_model = '''class User(UserMixin, db.Model):
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
    
    # الحقول الجديدة للإشعارات (اختيارية)
    # push_subscription = db.Column(db.Text, nullable=True)
    # allow_notifications = db.Column(db.Boolean, default=False)
    # last_notification_read = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    coupons = db.relationship('Coupon', backref='customer', lazy=True, foreign_keys='Coupon.customer_id')
    transactions = db.relationship('Transaction', backref='customer', lazy=True, foreign_keys='Transaction.customer_id')
    # notifications_received = db.relationship('Notification', secondary='user_notifications', back_populates='recipients')
    
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
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))'''

    # إنشاء نسخة مبسطة من Settings
    new_settings_model = '''class Settings(db.Model):
    """نموذج الإعدادات"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    cups_required = db.Column(db.Integer, default=6)  # عدد الأكواب المطلوبة للحصول على كوب مجاني
    logo_path = db.Column(db.String(255), nullable=True)
    primary_color = db.Column(db.String(7), default='#8B4513')  # لون بني للقهوة
    secondary_color = db.Column(db.String(7), default='#D2691E')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # الحقول الجديدة للإشعارات (اختيارية)
    # push_public_key = db.Column(db.Text, nullable=True)
    # push_private_key = db.Column(db.Text, nullable=True)'''

    # البحث عن نموذج User واستبداله
    import re
    
    # البحث عن بداية ونهاية نموذج User
    user_pattern = r'class User\(UserMixin, db\.Model\):.*?(?=class \w+\(|$)'
    settings_pattern = r'class Settings\(db\.Model\):.*?(?=class \w+\(|$)'
    
    # استبدال نموذج User
    content = re.sub(user_pattern, new_user_model, content, flags=re.DOTALL)
    
    # استبدال نموذج Settings
    content = re.sub(settings_pattern, new_settings_model, content, flags=re.DOTALL)
    
    # كتابة الملف المحدث
    with open('models.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ تم إصلاح ملف models.py")

if __name__ == "__main__":
    fix_models()
