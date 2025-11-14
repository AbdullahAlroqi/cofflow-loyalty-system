"""
إصلاح تناسق التصميم عبر جميع الصفحات
"""

def create_enhanced_login_template():
    """إنشاء قالب تسجيل دخول محسن"""
    
    login_template = """{% extends "base.html" %}

{% block title %}تسجيل الدخول - COFFLOW{% endblock %}

{% block extra_css %}
<style>
    .login-container {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        position: relative;
    }
    
    .login-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="coffee" patternUnits="userSpaceOnUse" width="20" height="20"><circle cx="10" cy="10" r="2" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23coffee)"/></svg>');
        opacity: 0.3;
    }
    
    .login-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        position: relative;
        z-index: 1;
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
        position: relative;
    }
    
    .login-header::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 0;
        height: 0;
        border-left: 15px solid transparent;
        border-right: 15px solid transparent;
        border-top: 10px solid var(--secondary-color);
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
    
    .login-body {
        padding: 40px 30px;
    }
    
    .form-control {
        border-radius: 15px;
        border: 2px solid #e9ecef;
        padding: 15px 20px;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: rgba(248, 249, 250, 0.8);
    }
    
    .form-control:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 0.2rem rgba(139, 69, 19, 0.25);
        background: white;
    }
    
    .btn-login {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        border: none;
        border-radius: 15px;
        padding: 15px 30px;
        font-size: 1.1rem;
        font-weight: 600;
        color: white;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .btn-login::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .btn-login:hover::before {
        left: 100%;
    }
    
    .btn-login:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(139, 69, 19, 0.3);
    }
    
    .register-link {
        color: var(--primary-color);
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .register-link:hover {
        color: var(--secondary-color);
        text-decoration: underline;
    }
    
    .form-label {
        font-weight: 600;
        color: var(--dark-brown);
        margin-bottom: 8px;
    }
    
    .input-group {
        position: relative;
        margin-bottom: 20px;
    }
    
    .input-icon {
        position: absolute;
        right: 15px;
        top: 50%;
        transform: translateY(-50%);
        color: var(--primary-color);
        z-index: 10;
    }
    
    .form-control.with-icon {
        padding-right: 50px;
    }
</style>
{% endblock %}

{% block content %}
<div class="login-container">
    <div class="login-card">
        <div class="login-header">
            <i class="fas fa-coffee coffee-icon"></i>
            <h2 class="mb-0">COFFLOW</h2>
            <p class="mb-0 mt-2">نظام إدارة الولاء</p>
        </div>
        
        <div class="login-body">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST" action="{{ url_for('login') }}">
                <div class="input-group">
                    <label for="phone" class="form-label">
                        <i class="fas fa-phone"></i> رقم الجوال
                    </label>
                    <input type="text" class="form-control with-icon" id="phone" name="phone" 
                           placeholder="05xxxxxxxx" required autofocus>
                    <i class="fas fa-phone input-icon"></i>
                </div>
                
                <div class="input-group">
                    <label for="password" class="form-label">
                        <i class="fas fa-lock"></i> كلمة المرور
                    </label>
                    <input type="password" class="form-control with-icon" id="password" name="password" 
                           placeholder="أدخل كلمة المرور" required>
                    <i class="fas fa-lock input-icon"></i>
                </div>
                
                <button type="submit" class="btn btn-login w-100 mb-4">
                    <i class="fas fa-sign-in-alt me-2"></i> تسجيل الدخول
                </button>
            </form>
            
            <div class="text-center">
                <p class="mb-2">ليس لديك حساب؟</p>
                <a href="{{ url_for('register') }}" class="register-link">
                    <i class="fas fa-user-plus me-1"></i> إنشاء حساب جديد
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    // تأثير التركيز على الحقول
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.querySelector('.input-icon').style.color = 'var(--secondary-color)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.querySelector('.input-icon').style.color = 'var(--primary-color)';
        });
    });
    
    // تأثير الضغط على زر تسجيل الدخول
    const loginBtn = document.querySelector('.btn-login');
    loginBtn.addEventListener('click', function(e) {
        this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> جاري تسجيل الدخول...';
    });
});
</script>
{% endblock %}
"""
    
    try:
        with open('templates/login.html', 'w', encoding='utf-8') as f:
            f.write(login_template)
        print("✅ تم تحديث قالب تسجيل الدخول")
        return True
    except Exception as e:
        print(f"❌ خطأ في تحديث قالب تسجيل الدخول: {e}")
        return False

def enhance_base_template():
    """تحسين القالب الأساسي"""
    
    # قراءة القالب الأساسي الحالي
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
        
        # إضافة blocks إضافية للتخصيص
        enhanced_blocks = """
    {% block extra_css %}{% endblock %}
    
    {% block extra_head %}{% endblock %}
</head>
<body>
    {% block navbar %}
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <i class="fas fa-coffee"></i> COFFLOW
            </a>
            
            {% if current_user.is_authenticated %}
            <div class="navbar-nav ms-auto">
                <div class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                        <i class="fas fa-user"></i> {{ current_user.name }}
                    </a>
                    <ul class="dropdown-menu">
                        {% if current_user.role == 'admin' %}
                            <li><a class="dropdown-item" href="{{ url_for('admin_dashboard') }}">
                                <i class="fas fa-tachometer-alt"></i> لوحة التحكم
                            </a></li>
                        {% elif current_user.role == 'employee' %}
                            <li><a class="dropdown-item" href="{{ url_for('employee_dashboard') }}">
                                <i class="fas fa-tachometer-alt"></i> لوحة التحكم
                            </a></li>
                        {% else %}
                            <li><a class="dropdown-item" href="{{ url_for('customer_dashboard') }}">
                                <i class="fas fa-tachometer-alt"></i> لوحة التحكم
                            </a></li>
                        {% endif %}
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="{{ url_for('logout') }}">
                            <i class="fas fa-sign-out-alt"></i> تسجيل الخروج
                        </a></li>
                    </ul>
                </div>
            </div>
            {% endif %}
        </div>
    </nav>
    {% endblock %}
    
    <main class="main-content">
        {% block content %}{% endblock %}
    </main>
    
    {% block footer %}
    <footer class="footer mt-auto py-3 bg-dark text-light">
        <div class="container text-center">
            <span>&copy; 2024 COFFLOW - نظام الولاء الذكي للمقاهي</span>
        </div>
    </footer>
    {% endblock %}
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>"""
        
        # البحث عن نهاية head وإضافة blocks
        if '{% block extra_css %}{% endblock %}' not in base_content:
            base_content = base_content.replace('</head>', '    {% block extra_css %}{% endblock %}\n    {% block extra_head %}{% endblock %}\n</head>')
        
        # إضافة block للـ JavaScript في النهاية
        if '{% block extra_js %}{% endblock %}' not in base_content:
            base_content = base_content.replace('</body>', '    {% block extra_js %}{% endblock %}\n</body>')
        
        with open('templates/base.html', 'w', encoding='utf-8') as f:
            f.write(base_content)
        
        print("✅ تم تحسين القالب الأساسي")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تحسين القالب الأساسي: {e}")
        return False

def create_consistent_admin_dashboard():
    """إنشاء لوحة تحكم المدير بتصميم متناسق"""
    
    admin_template = """{% extends "base.html" %}

{% block title %}لوحة تحكم الإدارة - COFFLOW{% endblock %}

{% block extra_css %}
<style>
    .dashboard-header {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 30px 0;
        margin-bottom: 30px;
        border-radius: 0 0 20px 20px;
    }
    
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
    
    .dashboard-card {
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(139, 69, 19, 0.1);
        margin-bottom: 30px;
    }
    
    .dashboard-card .card-header {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border-radius: 15px 15px 0 0;
        padding: 20px 25px;
        border: none;
    }
    
    .dashboard-card .card-body {
        padding: 25px;
    }
    
    .quick-action-btn {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        border: none;
        border-radius: 10px;
        color: white;
        padding: 12px 20px;
        margin: 5px;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-block;
    }
    
    .quick-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(139, 69, 19, 0.3);
        color: white;
    }
</style>
{% endblock %}

{% block content %}
<div class="dashboard-header">
    <div class="container">
        <div class="row align-items-center">
            <div class="col-md-8">
                <h1 class="mb-2">
                    <i class="fas fa-tachometer-alt"></i> لوحة تحكم الإدارة
                </h1>
                <p class="mb-0">مرحباً {{ current_user.name }}، إليك ملخص اليوم</p>
            </div>
            <div class="col-md-4 text-end">
                <div class="d-flex justify-content-end gap-2">
                    <a href="{{ url_for('admin_notifications') }}" class="btn btn-light">
                        <i class="fas fa-bell"></i> الإشعارات
                    </a>
                    <a href="{{ url_for('admin_settings') }}" class="btn btn-outline-light">
                        <i class="fas fa-cog"></i> الإعدادات
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="container">
    <!-- إحصائيات سريعة -->
    <div class="row g-4 mb-4">
        <div class="col-md-3">
            <div class="stat-card">
                <i class="fas fa-users"></i>
                <h3>{{ total_customers }}</h3>
                <p>إجمالي العملاء</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stat-card">
                <i class="fas fa-user-tie"></i>
                <h3>{{ total_employees }}</h3>
                <p>إجمالي الموظفين</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stat-card">
                <i class="fas fa-ticket-alt"></i>
                <h3>{{ active_coupons }}</h3>
                <p>الأكواد النشطة</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stat-card">
                <i class="fas fa-check-circle"></i>
                <h3>{{ used_coupons }}</h3>
                <p>الأكواد المستخدمة</p>
            </div>
        </div>
    </div>
    
    <!-- إجراءات سريعة -->
    <div class="row">
        <div class="col-md-6">
            <div class="dashboard-card">
                <div class="card-header">
                    <h5 class="mb-0">
                        <i class="fas fa-bolt"></i> إجراءات سريعة
                    </h5>
                </div>
                <div class="card-body">
                    <div class="d-grid gap-2">
                        <a href="{{ url_for('admin_customers') }}" class="quick-action-btn">
                            <i class="fas fa-users"></i> إدارة العملاء
                        </a>
                        <a href="{{ url_for('admin_employees') }}" class="quick-action-btn">
                            <i class="fas fa-user-tie"></i> إدارة الموظفين
                        </a>
                        <a href="{{ url_for('admin_coupons') }}" class="quick-action-btn">
                            <i class="fas fa-ticket-alt"></i> إدارة الكوبونات
                        </a>
                        <a href="{{ url_for('admin_notifications') }}" class="quick-action-btn">
                            <i class="fas fa-bell"></i> إدارة الإشعارات
                        </a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="dashboard-card">
                <div class="card-header">
                    <h5 class="mb-0">
                        <i class="fas fa-history"></i> المعاملات الأخيرة
                    </h5>
                </div>
                <div class="card-body">
                    {% if recent_transactions %}
                        <div class="list-group list-group-flush">
                            {% for transaction in recent_transactions[:5] %}
                            <div class="list-group-item border-0 px-0">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="mb-1">{{ transaction.customer.name }}</h6>
                                        <small class="text-muted">{{ transaction.transaction_type }}</small>
                                    </div>
                                    <small class="text-muted">{{ transaction.created_at.strftime('%d/%m %H:%M') }}</small>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        <div class="text-center mt-3">
                            <a href="{{ url_for('admin_transactions') }}" class="btn btn-outline-primary">
                                عرض جميع المعاملات
                            </a>
                        </div>
                    {% else %}
                        <div class="text-center text-muted">
                            <i class="fas fa-inbox fa-3x mb-3"></i>
                            <p>لا توجد معاملات حتى الآن</p>
                        </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
    
    try:
        with open('templates/admin/dashboard.html', 'w', encoding='utf-8') as f:
            f.write(admin_template)
        print("✅ تم تحديث لوحة تحكم المدير")
        return True
    except Exception as e:
        print(f"❌ خطأ في تحديث لوحة تحكم المدير: {e}")
        return False

def main():
    """تطبيق جميع الإصلاحات"""
    print("🎨 إصلاح تناسق التصميم عبر جميع الصفحات")
    print("=" * 50)
    
    results = []
    
    # تحسين القالب الأساسي
    results.append(("القالب الأساسي", enhance_base_template()))
    
    # تحديث قالب تسجيل الدخول
    results.append(("قالب تسجيل الدخول", create_enhanced_login_template()))
    
    # تحديث لوحة تحكم المدير
    results.append(("لوحة تحكم المدير", create_consistent_admin_dashboard()))
    
    print("\n📊 نتائج الإصلاح:")
    for name, success in results:
        status = "✅ نجح" if success else "❌ فشل"
        print(f"   {name}: {status}")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n🎯 النتيجة: {successful}/{total} إصلاحات نجحت")
    
    if successful == total:
        print("\n🎉 تم إصلاح جميع مشاكل التصميم!")
        print("💡 أعد تشغيل الخادم لرؤية التغييرات:")
        print("   python app.py")
    else:
        print("\n⚠️ بعض الإصلاحات فشلت. تحقق من الأخطاء أعلاه.")

if __name__ == "__main__":
    main()
