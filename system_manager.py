"""
مدير النظام الشامل - COFFLOW System Manager
"""
import os
import subprocess
import sqlite3
from datetime import datetime

class SystemManager:
    def __init__(self):
        self.base_path = os.getcwd()
        self.db_path = 'cofflow.db'
    
    def show_menu(self):
        """عرض قائمة الإدارة"""
        print("\n" + "="*50)
        print("🚀 COFFLOW System Manager")
        print("="*50)
        print("1. 📊 عرض حالة النظام")
        print("2. 🔐 إدارة المستخدمين")
        print("3. 💾 إدارة قاعدة البيانات")
        print("4. 🔔 تفعيل/تعطيل الإشعارات")
        print("5. 🌐 إدارة الخادم")
        print("6. 📱 إدارة PWA")
        print("7. 🧪 اختبار النظام")
        print("8. 📋 تقارير النظام")
        print("0. ❌ خروج")
        print("="*50)
    
    def get_system_status(self):
        """عرض حالة النظام"""
        print("\n📊 حالة النظام:")
        
        # فحص الملفات الأساسية
        essential_files = [
            'app.py', 'models.py', 'config.py', 'cofflow.db',
            'templates/base.html', 'static/manifest.json', 'static/sw.js'
        ]
        
        print("\n📁 الملفات الأساسية:")
        for file_path in essential_files:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"   ✅ {file_path} ({size} bytes)")
            else:
                print(f"   ❌ {file_path} - مفقود")
        
        # فحص قاعدة البيانات
        if os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            print("\n💾 قاعدة البيانات:")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   📋 {table[0]}: {count} سجل")
            
            conn.close()
        else:
            print("\n❌ قاعدة البيانات غير موجودة")
    
    def manage_users(self):
        """إدارة المستخدمين"""
        print("\n👥 إدارة المستخدمين:")
        print("1. عرض جميع المستخدمين")
        print("2. إضافة مستخدم جديد")
        print("3. إعادة تعيين كلمة مرور")
        print("4. تغيير دور مستخدم")
        
        choice = input("اختر (1-4): ").strip()
        
        if choice == "1":
            self.show_all_users()
        elif choice == "2":
            self.add_new_user()
        elif choice == "3":
            self.reset_password()
        elif choice == "4":
            self.change_user_role()
    
    def show_all_users(self):
        """عرض جميع المستخدمين"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, phone, role, created_at FROM users ORDER BY role, name")
        users = cursor.fetchall()
        
        print(f"\n👥 المستخدمون ({len(users)}):")
        print("-" * 80)
        print(f"{'ID':<4} {'الاسم':<20} {'الهاتف':<15} {'الدور':<10} {'تاريخ الإنشاء':<20}")
        print("-" * 80)
        
        for user in users:
            print(f"{user[0]:<4} {user[1]:<20} {user[2]:<15} {user[3]:<10} {user[4]:<20}")
        
        conn.close()
    
    def manage_database(self):
        """إدارة قاعدة البيانات"""
        print("\n💾 إدارة قاعدة البيانات:")
        print("1. نسخ احتياطي")
        print("2. استعادة من نسخة احتياطية")
        print("3. تنظيف البيانات")
        print("4. إحصائيات مفصلة")
        
        choice = input("اختر (1-4): ").strip()
        
        if choice == "1":
            self.backup_database()
        elif choice == "4":
            self.detailed_stats()
    
    def backup_database(self):
        """إنشاء نسخة احتياطية"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"cofflow_backup_{timestamp}.db"
        
        try:
            import shutil
            shutil.copy2(self.db_path, backup_name)
            print(f"✅ تم إنشاء نسخة احتياطية: {backup_name}")
        except Exception as e:
            print(f"❌ خطأ في النسخ الاحتياطي: {e}")
    
    def detailed_stats(self):
        """إحصائيات مفصلة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print("\n📊 إحصائيات مفصلة:")
        
        # إحصائيات المستخدمين
        cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
        user_stats = cursor.fetchall()
        
        print("\n👥 المستخدمون:")
        for role, count in user_stats:
            print(f"   {role}: {count}")
        
        # إحصائيات الكوبونات
        cursor.execute("SELECT status, COUNT(*) FROM coupons GROUP BY status")
        coupon_stats = cursor.fetchall()
        
        print("\n🎫 الكوبونات:")
        for status, count in coupon_stats:
            print(f"   {status}: {count}")
        
        # إحصائيات المعاملات
        cursor.execute("SELECT transaction_type, COUNT(*) FROM transactions GROUP BY transaction_type")
        transaction_stats = cursor.fetchall()
        
        print("\n💳 المعاملات:")
        for t_type, count in transaction_stats:
            print(f"   {t_type}: {count}")
        
        conn.close()
    
    def manage_server(self):
        """إدارة الخادم"""
        print("\n🌐 إدارة الخادم:")
        print("1. تشغيل الخادم")
        print("2. إيقاف الخادم")
        print("3. إعادة تشغيل الخادم")
        print("4. فحص حالة الخادم")
        
        choice = input("اختر (1-4): ").strip()
        
        if choice == "1":
            self.start_server()
        elif choice == "4":
            self.check_server_status()
    
    def start_server(self):
        """تشغيل الخادم"""
        print("🚀 تشغيل خادم COFFLOW...")
        try:
            subprocess.Popen(['python', 'app.py'])
            print("✅ تم تشغيل الخادم")
            print("🌐 الرابط: http://localhost:5000")
        except Exception as e:
            print(f"❌ خطأ في تشغيل الخادم: {e}")
    
    def test_system(self):
        """اختبار النظام"""
        print("\n🧪 اختبار النظام:")
        print("1. اختبار تسجيل الدخول")
        print("2. اختبار قاعدة البيانات")
        print("3. اختبار PWA")
        print("4. اختبار شامل")
        
        choice = input("اختر (1-4): ").strip()
        
        if choice == "1":
            os.system('python test_login.py')
        elif choice == "2":
            os.system('python check_database.py')
        elif choice == "4":
            self.comprehensive_test()
    
    def comprehensive_test(self):
        """اختبار شامل"""
        print("\n🔍 اختبار شامل للنظام...")
        
        tests = [
            ("قاعدة البيانات", "python check_database.py"),
            ("تسجيل الدخول", "python test_login.py"),
            ("كلمات المرور", "python test_password.py")
        ]
        
        for test_name, command in tests:
            print(f"\n🧪 اختبار {test_name}...")
            try:
                result = os.system(command)
                if result == 0:
                    print(f"✅ {test_name}: نجح")
                else:
                    print(f"❌ {test_name}: فشل")
            except Exception as e:
                print(f"❌ خطأ في اختبار {test_name}: {e}")
    
    def run(self):
        """تشغيل مدير النظام"""
        while True:
            self.show_menu()
            choice = input("\nاختر خيار (0-8): ").strip()
            
            if choice == "0":
                print("👋 وداعاً!")
                break
            elif choice == "1":
                self.get_system_status()
            elif choice == "2":
                self.manage_users()
            elif choice == "3":
                self.manage_database()
            elif choice == "4":
                os.system('python enable_notifications.py')
            elif choice == "5":
                self.manage_server()
            elif choice == "7":
                self.test_system()
            elif choice == "8":
                print("📋 تقارير النظام متاحة في الملفات:")
                print("   - LOGIN_FIX_REPORT.md")
                print("   - FINAL_SUCCESS_REPORT.md")
                print("   - SYSTEM_STATUS_REPORT.md")
            else:
                print("❌ خيار غير صحيح")
            
            input("\nاضغط Enter للمتابعة...")

if __name__ == "__main__":
    manager = SystemManager()
    manager.run()
