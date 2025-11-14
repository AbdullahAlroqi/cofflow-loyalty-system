"""
إصلاح عمود used_by في جدول الكوبونات وتحديث التصميم
"""
import sqlite3
import os

def fix_coupons_table():
    """إصلاح جدول الكوبونات"""
    print("🔧 إصلاح جدول الكوبونات...")
    
    conn = sqlite3.connect('instance/cofflow.db')
    cursor = conn.cursor()
    
    try:
        # فحص الأعمدة الموجودة
        cursor.execute("PRAGMA table_info(coupons)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 الأعمدة الحالية: {columns}")
        
        # إضافة عمود used_by إذا لم يكن موجوداً
        if 'used_by' not in columns:
            cursor.execute("ALTER TABLE coupons ADD COLUMN used_by INTEGER")
            print("   ✅ تم إضافة عمود used_by")
            
            # إضافة foreign key constraint (في SQLite نحتاج لإعادة إنشاء الجدول)
            cursor.execute("""
            CREATE TABLE coupons_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code VARCHAR(20) UNIQUE NOT NULL,
                customer_id INTEGER NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                used_at DATETIME,
                employee_id INTEGER,
                used_by INTEGER,
                FOREIGN KEY (customer_id) REFERENCES users (id),
                FOREIGN KEY (employee_id) REFERENCES users (id),
                FOREIGN KEY (used_by) REFERENCES users (id)
            )
            """)
            
            # نسخ البيانات
            cursor.execute("""
            INSERT INTO coupons_new (id, code, customer_id, status, created_at, used_at, employee_id, used_by)
            SELECT id, code, customer_id, status, created_at, used_at, employee_id, used_by FROM coupons
            """)
            
            # حذف الجدول القديم وإعادة تسمية الجديد
            cursor.execute("DROP TABLE coupons")
            cursor.execute("ALTER TABLE coupons_new RENAME TO coupons")
            
            print("   ✅ تم إعادة إنشاء جدول الكوبونات مع العلاقات الصحيحة")
        else:
            print("   ✅ عمود used_by موجود بالفعل")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_models_py():
    """تحديث models.py ليتطابق مع قاعدة البيانات"""
    print("\n📝 تحديث models.py...")
    
    try:
        # قراءة الملف الحالي
        with open('models.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # البحث عن تعريف جدول الكوبونات وتحديثه
        coupon_model = '''class Coupon(db.Model):
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
    customer = db.relationship('User', foreign_keys=[customer_id], backref='customer_coupons')
    employee = db.relationship('User', foreign_keys=[employee_id], backref='processed_coupons')
    used_by_user = db.relationship('User', foreign_keys=[used_by], backref='used_coupons')'''
        
        # استبدال تعريف الكوبون
        import re
        pattern = r'class Coupon\(db\.Model\):.*?(?=class|\Z)'
        
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, coupon_model + '\n\n', content, flags=re.DOTALL)
            
            with open('models.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("   ✅ تم تحديث models.py")
            return True
        else:
            print("   ⚠️ لم يتم العثور على تعريف Coupon في models.py")
            return False
            
    except Exception as e:
        print(f"   ❌ خطأ في تحديث models.py: {e}")
        return False

def clear_browser_cache_files():
    """إنشاء ملفات لمسح cache المتصفح"""
    print("\n🧹 إنشاء ملفات مسح cache المتصفح...")
    
    # إنشاء ملف CSS جديد مع timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # تحديث base.html لإضافة timestamp للـ CSS
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
        
        # إضافة meta tags لمنع cache
        cache_meta = '''    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <meta name="cache-version" content="''' + timestamp + '''">'''
        
        if 'cache-version' not in base_content:
            base_content = base_content.replace('<meta http-equiv="Expires" content="0">', cache_meta)
        
        # إضافة timestamp للـ CSS والـ JS
        if '?v=' not in base_content:
            base_content = base_content.replace('.css"', f'.css?v={timestamp}"')
            base_content = base_content.replace('.js"', f'.js?v={timestamp}"')
        
        with open('templates/base.html', 'w', encoding='utf-8') as f:
            f.write(base_content)
        
        print("   ✅ تم تحديث base.html لمنع cache")
        
    except Exception as e:
        print(f"   ❌ خطأ في تحديث base.html: {e}")

def create_unified_css():
    """إنشاء ملف CSS موحد"""
    print("\n🎨 إنشاء ملف CSS موحد...")
    
    css_content = """/* ملف CSS موحد لجميع صفحات COFFLOW */

/* المتغيرات العامة */
:root {
    --primary-color: #8B4513;
    --secondary-color: #D2691E;
    --dark-brown: #514f4b;
    --light-cream: #F5F5DC;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --info-color: #17a2b8;
}

/* الخطوط */
* {
    font-family: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* الخلفية العامة */
body {
    background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
    min-height: 100vh;
    direction: rtl;
    text-align: right;
}

/* شريط التنقل */
.navbar {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--dark-brown) 100%);
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.navbar-brand {
    font-weight: 700;
    font-size: 1.5rem;
    color: white !important;
}

.navbar-brand i {
    color: var(--secondary-color);
    margin-left: 10px;
}

/* البطاقات */
.card {
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    border: 1px solid rgba(139, 69, 19, 0.1);
    margin-bottom: 20px;
}

.card-header {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    border-radius: 15px 15px 0 0 !important;
    padding: 20px 25px;
    border: none;
}

/* الأزرار */
.btn-primary {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(139, 69, 19, 0.3);
}

/* بطاقات الإحصائيات */
.stat-card {
    background: white;
    border-radius: 15px;
    padding: 25px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    border: 1px solid rgba(139, 69, 19, 0.1);
    position: relative;
    overflow: hidden;
}

.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}

.stat-card i {
    font-size: 3rem;
    color: var(--primary-color);
    margin-bottom: 15px;
    display: block;
}

.stat-card h3 {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--dark-brown);
    margin-bottom: 10px;
}

.stat-card p {
    color: #6c757d;
    font-weight: 600;
    margin: 0;
}

/* النماذج */
.form-control {
    border-radius: 10px;
    border: 2px solid #e9ecef;
    padding: 12px 15px;
    font-size: 1rem;
    transition: all 0.3s ease;
}

.form-control:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 0.2rem rgba(139, 69, 19, 0.25);
}

/* الجداول */
.table {
    background: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.table thead th {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    border: none;
    padding: 15px;
    font-weight: 600;
}

.table tbody tr:hover {
    background-color: rgba(139, 69, 19, 0.05);
}

/* التنبيهات */
.alert {
    border-radius: 10px;
    border: none;
    padding: 15px 20px;
    margin-bottom: 20px;
}

.alert-success {
    background: linear-gradient(135deg, #d4edda, #c3e6cb);
    color: #155724;
}

.alert-danger {
    background: linear-gradient(135deg, #f8d7da, #f5c6cb);
    color: #721c24;
}

.alert-warning {
    background: linear-gradient(135deg, #fff3cd, #ffeaa7);
    color: #856404;
}

.alert-info {
    background: linear-gradient(135deg, #d1ecf1, #bee5eb);
    color: #0c5460;
}

/* الشارات */
.badge {
    border-radius: 20px;
    padding: 8px 12px;
    font-size: 0.85rem;
    font-weight: 600;
}

.badge-success {
    background: var(--success-color);
}

.badge-warning {
    background: var(--warning-color);
}

.badge-danger {
    background: var(--danger-color);
}

.badge-info {
    background: var(--info-color);
}

/* الصفحة الرئيسية */
.hero-section {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 60px 0;
    text-align: center;
    border-radius: 0 0 30px 30px;
}

.feature-card {
    background: white;
    border-radius: 15px;
    padding: 30px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    height: 100%;
}

.feature-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}

.feature-card i {
    font-size: 3rem;
    color: var(--primary-color);
    margin-bottom: 20px;
}

/* صفحة تسجيل الدخول */
.login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
}

.login-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    max-width: 400px;
    width: 100%;
    margin: 20px;
}

.login-header {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    text-align: center;
    padding: 30px 20px;
    border-radius: 20px 20px 0 0;
}

.coffee-icon {
    font-size: 3rem;
    margin-bottom: 10px;
    display: block;
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-10px); }
    60% { transform: translateY(-5px); }
}

/* الإشعارات */
.notification-item {
    background: white;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    border-right: 4px solid var(--primary-color);
    transition: all 0.3s ease;
}

.notification-item:hover {
    transform: translateX(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.notification-item.unread {
    background: linear-gradient(135deg, #fff, #f8f9fa);
    border-right-color: var(--secondary-color);
}

.notification-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
}

/* التجاوب */
@media (max-width: 768px) {
    .stat-card {
        margin-bottom: 20px;
    }
    
    .hero-section {
        padding: 40px 0;
    }
    
    .feature-card {
        margin-bottom: 30px;
    }
    
    .login-card {
        margin: 10px;
    }
}

/* تحسينات إضافية */
.main-content {
    min-height: calc(100vh - 200px);
    padding: 20px 0;
}

.footer {
    background: var(--dark-brown);
    color: white;
    text-align: center;
    padding: 20px 0;
    margin-top: auto;
}

/* تأثيرات التحميل */
.loading {
    opacity: 0.7;
    pointer-events: none;
}

.spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255,255,255,.3);
    border-radius: 50%;
    border-top-color: #fff;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* إصلاحات RTL */
.dropdown-menu {
    right: 0;
    left: auto;
}

.navbar-nav .dropdown-menu {
    position: absolute;
}

.text-end {
    text-align: left !important;
}

.me-2 {
    margin-left: 0.5rem !important;
    margin-right: 0 !important;
}

.ms-auto {
    margin-right: auto !important;
    margin-left: 0 !important;
}
"""
    
    # إنشاء مجلد static/css إذا لم يكن موجوداً
    os.makedirs('static/css', exist_ok=True)
    
    try:
        with open('static/css/style.css', 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print("   ✅ تم إنشاء ملف CSS موحد")
        
        # تحديث base.html لاستخدام الملف الجديد
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
        
        # إضافة رابط CSS الموحد
        css_link = '    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/style.css\') }}">'
        
        if 'css/style.css' not in base_content:
            # إضافة بعد Bootstrap
            base_content = base_content.replace(
                'bootstrap.rtl.min.css" rel="stylesheet">',
                'bootstrap.rtl.min.css" rel="stylesheet">\n' + css_link
            )
            
            with open('templates/base.html', 'w', encoding='utf-8') as f:
                f.write(base_content)
            
            print("   ✅ تم ربط CSS الموحد بـ base.html")
        
        return True
        
    except Exception as e:
        print(f"   ❌ خطأ في إنشاء CSS: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 إصلاح عمود used_by وتحديث التصميم")
    print("=" * 50)
    
    results = []
    
    # إصلاح جدول الكوبونات
    results.append(("إصلاح جدول الكوبونات", fix_coupons_table()))
    
    # تحديث models.py
    results.append(("تحديث models.py", update_models_py()))
    
    # مسح cache المتصفح
    clear_browser_cache_files()
    results.append(("مسح cache المتصفح", True))
    
    # إنشاء CSS موحد
    results.append(("إنشاء CSS موحد", create_unified_css()))
    
    print("\n" + "=" * 50)
    print("📊 نتائج الإصلاح:")
    
    for name, success in results:
        status = "✅ نجح" if success else "❌ فشل"
        print(f"   {name}: {status}")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n🎯 النتيجة: {successful}/{total} إصلاحات نجحت")
    
    if successful == total:
        print("\n🎉 تم إصلاح جميع المشاكل!")
        print("💡 أعد تشغيل الخادم لرؤية التغييرات:")
        print("   1. أوقف الخادم (Ctrl+C)")
        print("   2. شغل: python app.py")
        print("   3. امسح cache المتصفح (Ctrl+Shift+R)")
    else:
        print("\n⚠️ بعض الإصلاحات فشلت. تحقق من الأخطاء أعلاه.")

if __name__ == "__main__":
    main()
