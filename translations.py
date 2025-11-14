"""
ملف الترجمات للغات المختلفة
Arabic, English, Bengali (Bangladesh)
"""

TRANSLATIONS = {
    'ar': {
        # القائمة
        'dashboard': 'لوحة التحكم',
        'search_customer': 'البحث عن عميل',
        'verify_coupon': 'التحقق من كوبون',
        'logout': 'تسجيل الخروج',
        
        # صفحة Dashboard
        'employee_dashboard': 'لوحة تحكم الموظف',
        'welcome': 'مرحباً',
        'today_operations': 'عمليات اليوم',
        'operations': 'عملية',
        'quick_actions': 'إجراءات سريعة',
        
        # البحث
        'search': 'البحث عن عميل',
        'search_placeholder': 'ابحث بالاسم أو رقم الجوال',
        'search_button': 'بحث',
        'view': 'عرض',
        'no_results': 'لا توجد نتائج',
        'customer_name': 'اسم العميل',
        'phone': 'رقم الجوال',
        'cups_count': 'عدد الأكواب',
        'actions': 'إجراءات',
        
        # صفحة العميل
        'customer_info': 'معلومات العميل',
        'email': 'البريد الإلكتروني',
        'cups_progress': 'تقدم الأكواب',
        'add_cup': 'إضافة كوب جديد',
        'add_cup_confirm': 'هل تريد إضافة كوب لهذا العميل؟',
        'active_coupons': 'الأكواد النشطة',
        'redeem_free_cup': 'صرف الكوب المجاني',
        'redeem_confirm': 'هل تريد صرف هذا الكود للعميل؟',
        'created_at': 'تم الإنشاء',
        'back_to_search': 'العودة للبحث',
        
        # التحقق من الكوبون
        'verify_coupon_title': 'التحقق من كوبون',
        'enter_code': 'أدخل الكود',
        'code_placeholder': 'مثال: ABC123XY',
        'verify_button': 'التحقق',
        'code_valid': 'الكود صحيح! تم صرف الكوب المجاني بنجاح',
        'code_invalid': 'الكود غير موجود',
        'code_used': 'الكود مرفوض - مستخدم سابقاً',
        
        # رسائل
        'success': 'نجح',
        'error': 'خطأ',
        'cup_added': 'تم إضافة كوب!',
        'coupon_redeemed': 'تم صرف الكوب المجاني بنجاح!',
        'code': 'الكود',
    },
    
    'en': {
        # Menu
        'dashboard': 'Dashboard',
        'search_customer': 'Search Customer',
        'verify_coupon': 'Verify Coupon',
        'logout': 'Logout',
        
        # Dashboard Page
        'employee_dashboard': 'Employee Dashboard',
        'welcome': 'Welcome',
        'today_operations': "Today's Operations",
        'operations': 'operations',
        'quick_actions': 'Quick Actions',
        
        # Search
        'search': 'Search Customer',
        'search_placeholder': 'Search by name or phone',
        'search_button': 'Search',
        'view': 'View',
        'no_results': 'No results found',
        'customer_name': 'Customer Name',
        'phone': 'Phone Number',
        'cups_count': 'Cups Count',
        'actions': 'Actions',
        
        # Customer Page
        'customer_info': 'Customer Information',
        'email': 'Email',
        'cups_progress': 'Cups Progress',
        'add_cup': 'Add New Cup',
        'add_cup_confirm': 'Do you want to add a cup for this customer?',
        'active_coupons': 'Active Coupons',
        'redeem_free_cup': 'Redeem Free Cup',
        'redeem_confirm': 'Do you want to redeem this code?',
        'created_at': 'Created',
        'back_to_search': 'Back to Search',
        
        # Verify Coupon
        'verify_coupon_title': 'Verify Coupon',
        'enter_code': 'Enter Code',
        'code_placeholder': 'Example: ABC123XY',
        'verify_button': 'Verify',
        'code_valid': 'Code is valid! Free cup redeemed successfully',
        'code_invalid': 'Code not found',
        'code_used': 'Code rejected - Already used',
        
        # Messages
        'success': 'Success',
        'error': 'Error',
        'cup_added': 'Cup added!',
        'coupon_redeemed': 'Free cup redeemed successfully!',
        'code': 'Code',
    },
    
    'bn': {
        # মেনু
        'dashboard': 'ড্যাশবোর্ড',
        'search_customer': 'গ্রাহক খুঁজুন',
        'verify_coupon': 'কুপন যাচাই করুন',
        'logout': 'লগ আউট',
        
        # Dashboard Page
        'employee_dashboard': 'কর্মচারী ড্যাশবোর্ড',
        'welcome': 'স্বাগতম',
        'today_operations': 'আজকের কার্যক্রম',
        'operations': 'কার্যক্রম',
        'quick_actions': 'দ্রুত কার্যক্রম',
        
        # Search
        'search': 'গ্রাহক খুঁজুন',
        'search_placeholder': 'নাম বা ফোন নম্বর দিয়ে খুঁজুন',
        'search_button': 'খুঁজুন',
        'view': 'দেখুন',
        'no_results': 'কোন ফলাফল পাওয়া যায়নি',
        'customer_name': 'গ্রাহকের নাম',
        'phone': 'ফোন নম্বর',
        'cups_count': 'কাপের সংখ্যা',
        'actions': 'কার্যক্রম',
        
        # Customer Page
        'customer_info': 'গ্রাহক তথ্য',
        'email': 'ইমেইল',
        'cups_progress': 'কাপ অগ্রগতি',
        'add_cup': 'নতুন কাপ যোগ করুন',
        'add_cup_confirm': 'আপনি কি এই গ্রাহকের জন্য একটি কাপ যোগ করতে চান?',
        'active_coupons': 'সক্রিয় কুপন',
        'redeem_free_cup': 'বিনামূল্যে কাপ নিন',
        'redeem_confirm': 'আপনি কি এই কোডটি ব্যবহার করতে চান?',
        'created_at': 'তৈরি হয়েছে',
        'back_to_search': 'খোঁজে ফিরে যান',
        
        # Verify Coupon
        'verify_coupon_title': 'কুপন যাচাই করুন',
        'enter_code': 'কোড লিখুন',
        'code_placeholder': 'উদাহরণ: ABC123XY',
        'verify_button': 'যাচাই করুন',
        'code_valid': 'কোডটি সঠিক! বিনামূল্যে কাপ সফলভাবে প্রদান করা হয়েছে',
        'code_invalid': 'কোড পাওয়া যায়নি',
        'code_used': 'কোড প্রত্যাখ্যাত - ইতিমধ্যে ব্যবহৃত',
        
        # Messages
        'success': 'সফল',
        'error': 'ত্রুটি',
        'cup_added': 'কাপ যোগ করা হয়েছে!',
        'coupon_redeemed': 'বিনামূল্যে কাপ সফলভাবে প্রদান করা হয়েছে!',
        'code': 'কোড',
    }
}

def get_translation(lang, key, default=None):
    """الحصول على الترجمة لمفتاح معين"""
    if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][key]
    # إذا لم توجد الترجمة، استخدم العربية كافتراضي
    if default:
        return default
    return TRANSLATIONS.get('ar', {}).get(key, key)

def get_all_translations(lang):
    """الحصول على جميع الترجمات للغة معينة"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['ar'])
