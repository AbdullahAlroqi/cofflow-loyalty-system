"""
اختبار شامل لنظام الإشعارات المطور
"""
import requests
import json
import time
from datetime import datetime, timedelta

class NotificationSystemTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_logged_in = False
        self.customer_logged_in = False
    
    def login_as_admin(self):
        """تسجيل الدخول كمدير"""
        print("🔐 تسجيل الدخول كمدير...")
        
        login_data = {
            'phone': '0544482434',
            'password': 'admin123'
        }
        
        response = self.session.post(f"{self.base_url}/login", data=login_data)
        
        if response.status_code == 302:
            print("✅ تم تسجيل الدخول كمدير بنجاح")
            self.admin_logged_in = True
            return True
        else:
            print(f"❌ فشل تسجيل الدخول كمدير: {response.status_code}")
            return False
    
    def test_vapid_keys(self):
        """اختبار مفاتيح VAPID"""
        print("\n🔑 اختبار مفاتيح VAPID...")
        
        if not self.admin_logged_in:
            print("❌ يجب تسجيل الدخول كمدير أولاً")
            return False
        
        # الحصول على المفاتيح الحالية
        response = self.session.get(f"{self.base_url}/api/notifications/vapid-keys")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ تم الحصول على مفاتيح VAPID")
                print(f"   المفتاح العام: {data['public_key'][:50]}...")
                return True
            else:
                print(f"❌ فشل في الحصول على مفاتيح VAPID: {data.get('message')}")
                return False
        else:
            print(f"❌ خطأ في طلب مفاتيح VAPID: {response.status_code}")
            return False
    
    def test_create_notification(self):
        """اختبار إنشاء إشعار"""
        print("\n📢 اختبار إنشاء إشعار...")
        
        if not self.admin_logged_in:
            print("❌ يجب تسجيل الدخول كمدير أولاً")
            return False
        
        notification_data = {
            'title': '🧪 إشعار اختبار النظام',
            'body': 'هذا إشعار تجريبي لاختبار النظام المطور. تم إنشاؤه في ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': 'general',
            'icon': 'science',
            'send_immediately': True
        }
        
        response = self.session.post(
            f"{self.base_url}/api/notifications/create",
            json=notification_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ تم إنشاء الإشعار بنجاح")
                print(f"   ID: {data['notification']['id']}")
                print(f"   العنوان: {data['notification']['title']}")
                return data['notification']['id']
            else:
                print(f"❌ فشل في إنشاء الإشعار: {data.get('message')}")
                return None
        else:
            print(f"❌ خطأ في إنشاء الإشعار: {response.status_code}")
            print(f"   الاستجابة: {response.text}")
            return None
    
    def test_offer_notification(self):
        """اختبار إشعار العرض"""
        print("\n🎁 اختبار إشعار العرض...")
        
        if not self.admin_logged_in:
            print("❌ يجب تسجيل الدخول كمدير أولاً")
            return False
        
        offer_data = {
            'title': '🎉 عرض خاص: خصم 50%!',
            'body': 'احصل على خصم 50% على جميع المشروبات الساخنة. العرض ساري حتى نهاية الأسبوع!',
            'action_url': '/customer/dashboard',
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        response = self.session.post(
            f"{self.base_url}/api/notifications/send-offer",
            json=offer_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ تم إرسال إشعار العرض بنجاح")
                return True
            else:
                print(f"❌ فشل في إرسال إشعار العرض: {data.get('message')}")
                return False
        else:
            print(f"❌ خطأ في إرسال إشعار العرض: {response.status_code}")
            return False
    
    def test_notification_stats(self):
        """اختبار إحصائيات الإشعارات"""
        print("\n📊 اختبار إحصائيات الإشعارات...")
        
        if not self.admin_logged_in:
            print("❌ يجب تسجيل الدخول كمدير أولاً")
            return False
        
        response = self.session.get(f"{self.base_url}/api/notifications/stats")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data['stats']
                print("✅ تم الحصول على الإحصائيات بنجاح")
                print(f"   إجمالي الإشعارات: {stats.get('total_notifications', 0)}")
                print(f"   الإشعارات العامة: {stats.get('public_notifications', 0)}")
                print(f"   إجمالي المرسل: {stats.get('total_sent', 0)}")
                print(f"   إجمالي المقروء: {stats.get('total_read', 0)}")
                print(f"   معدل القراءة: {stats.get('read_rate', 0):.1f}%")
                print(f"   المستخدمون النشطون: {stats.get('active_users', 0)}")
                print(f"   المشتركون: {stats.get('subscribed_users', 0)}")
                return True
            else:
                print(f"❌ فشل في الحصول على الإحصائيات: {data.get('message')}")
                return False
        else:
            print(f"❌ خطأ في طلب الإحصائيات: {response.status_code}")
            return False
    
    def test_admin_notifications_page(self):
        """اختبار صفحة إدارة الإشعارات"""
        print("\n📄 اختبار صفحة إدارة الإشعارات...")
        
        if not self.admin_logged_in:
            print("❌ يجب تسجيل الدخول كمدير أولاً")
            return False
        
        response = self.session.get(f"{self.base_url}/admin/notifications")
        
        if response.status_code == 200:
            print("✅ تم الوصول لصفحة إدارة الإشعارات بنجاح")
            
            # فحص محتوى الصفحة
            content = response.text
            if 'إدارة الإشعارات' in content:
                print("   ✅ العنوان موجود")
            if 'إنشاء إشعار جديد' in content:
                print("   ✅ زر إنشاء إشعار موجود")
            if 'الإحصائيات' in content:
                print("   ✅ قسم الإحصائيات موجود")
            
            return True
        else:
            print(f"❌ فشل في الوصول لصفحة إدارة الإشعارات: {response.status_code}")
            return False
    
    def login_as_customer(self):
        """تسجيل الدخول كعميل"""
        print("\n🛍️ تسجيل الدخول كعميل...")
        
        # تسجيل خروج المدير أولاً
        self.session.get(f"{self.base_url}/logout")
        
        login_data = {
            'phone': '0583270028',  # ريهام
            'password': '123456'
        }
        
        response = self.session.post(f"{self.base_url}/login", data=login_data)
        
        if response.status_code == 302:
            print("✅ تم تسجيل الدخول كعميل بنجاح")
            self.customer_logged_in = True
            self.admin_logged_in = False
            return True
        else:
            print(f"❌ فشل تسجيل الدخول كعميل: {response.status_code}")
            return False
    
    def test_customer_notifications_page(self):
        """اختبار صفحة إشعارات العميل"""
        print("\n📱 اختبار صفحة إشعارات العميل...")
        
        if not self.customer_logged_in:
            print("❌ يجب تسجيل الدخول كعميل أولاً")
            return False
        
        response = self.session.get(f"{self.base_url}/customer/notifications")
        
        if response.status_code == 200:
            print("✅ تم الوصول لصفحة إشعارات العميل بنجاح")
            
            # فحص محتوى الصفحة
            content = response.text
            if 'الإشعارات' in content:
                print("   ✅ العنوان موجود")
            if 'تعليم الكل كمقروء' in content:
                print("   ✅ زر تعليم الكل موجود")
            
            return True
        else:
            print(f"❌ فشل في الوصول لصفحة إشعارات العميل: {response.status_code}")
            return False
    
    def test_user_notifications_api(self):
        """اختبار API إشعارات المستخدم"""
        print("\n🔔 اختبار API إشعارات المستخدم...")
        
        if not self.customer_logged_in:
            print("❌ يجب تسجيل الدخول كعميل أولاً")
            return False
        
        response = self.session.get(f"{self.base_url}/api/notifications/user")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                notifications = data.get('notifications', [])
                unread_count = data.get('unread_count', 0)
                
                print(f"✅ تم الحصول على إشعارات المستخدم")
                print(f"   عدد الإشعارات: {len(notifications)}")
                print(f"   غير المقروءة: {unread_count}")
                
                if notifications:
                    print(f"   آخر إشعار: {notifications[0].get('title', 'بدون عنوان')}")
                
                return True
            else:
                print(f"❌ فشل في الحصول على إشعارات المستخدم: {data.get('message')}")
                return False
        else:
            print(f"❌ خطأ في طلب إشعارات المستخدم: {response.status_code}")
            return False
    
    def test_cleanup_notifications(self):
        """اختبار تنظيف الإشعارات"""
        print("\n🧹 اختبار تنظيف الإشعارات...")
        
        # العودة لتسجيل دخول المدير
        if not self.login_as_admin():
            return False
        
        response = self.session.post(f"{self.base_url}/api/notifications/cleanup")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                deleted_count = data.get('deleted_count', 0)
                print(f"✅ تم تنظيف الإشعارات بنجاح")
                print(f"   عدد الإشعارات المحذوفة: {deleted_count}")
                return True
            else:
                print(f"❌ فشل في تنظيف الإشعارات: {data.get('message')}")
                return False
        else:
            print(f"❌ خطأ في تنظيف الإشعارات: {response.status_code}")
            return False
    
    def run_comprehensive_test(self):
        """تشغيل اختبار شامل لنظام الإشعارات"""
        print("🚀 بدء الاختبار الشامل لنظام الإشعارات المطور")
        print("=" * 60)
        
        results = {}
        
        # اختبارات المدير
        results['admin_login'] = self.login_as_admin()
        
        if results['admin_login']:
            results['vapid_keys'] = self.test_vapid_keys()
            results['create_notification'] = self.test_create_notification()
            results['offer_notification'] = self.test_offer_notification()
            results['notification_stats'] = self.test_notification_stats()
            results['admin_page'] = self.test_admin_notifications_page()
        
        # اختبارات العميل
        results['customer_login'] = self.login_as_customer()
        
        if results['customer_login']:
            results['customer_page'] = self.test_customer_notifications_page()
            results['user_notifications_api'] = self.test_user_notifications_api()
        
        # اختبارات التنظيف
        results['cleanup'] = self.test_cleanup_notifications()
        
        # تقرير النتائج
        print("\n" + "=" * 60)
        print("📊 تقرير نتائج الاختبار:")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ نجح" if result else "❌ فشل"
            print(f"   {test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n📈 النتيجة النهائية: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 جميع الاختبارات نجحت! نظام الإشعارات يعمل بشكل مثالي!")
        elif passed >= total * 0.8:
            print("⚠️ معظم الاختبارات نجحت. هناك بعض المشاكل الطفيفة.")
        else:
            print("❌ فشلت عدة اختبارات. يحتاج النظام لمراجعة.")
        
        return results

def main():
    """تشغيل اختبار النظام"""
    print("🔔 مختبر نظام الإشعارات المتقدم")
    print("تأكد من تشغيل الخادم على http://localhost:5000")
    
    input("اضغط Enter للمتابعة...")
    
    tester = NotificationSystemTester()
    results = tester.run_comprehensive_test()
    
    return results

if __name__ == "__main__":
    main()
