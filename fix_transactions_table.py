"""
إصلاح جدول المعاملات
"""
import sqlite3

def fix_transactions_table():
    """إصلاح جدول المعاملات"""
    print("🔧 إصلاح جدول المعاملات...")
    
    conn = sqlite3.connect('instance/cofflow.db')
    cursor = conn.cursor()
    
    try:
        # فحص هيكل الجدول
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 أعمدة جدول المعاملات: {columns}")
        
        # إضافة الأعمدة المفقودة
        missing_columns = [
            ('description', 'TEXT'),
            ('cups_added', 'INTEGER DEFAULT 1'),
            ('coupon_id', 'INTEGER')
        ]
        
        for column_name, column_type in missing_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE transactions ADD COLUMN {column_name} {column_type}")
                    print(f"   ✅ تم إضافة عمود {column_name}")
                except Exception as e:
                    print(f"   ⚠️ عمود {column_name}: {e}")
            else:
                print(f"   ✅ عمود {column_name}: موجود بالفعل")
        
        conn.commit()
        print("✅ تم إصلاح جدول المعاملات")
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_transactions_table()
