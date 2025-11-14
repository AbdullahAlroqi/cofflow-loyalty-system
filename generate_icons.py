"""
سكريبت لتوليد أيقونات PWA بأحجام مختلفة
يستخدم شعار الشركة أو يولد أيقونة افتراضية
"""

import os
from PIL import Image, ImageDraw, ImageFont
import colorsys

def create_default_icon(size, output_path):
    """إنشاء أيقونة افتراضية بتصميم جذاب"""
    # إنشاء صورة بخلفية متدرجة
    img = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(img)
    
    # رسم خلفية متدرجة بألوان القهوة
    primary_color = (139, 69, 19)  # #8B4513 - Brown
    secondary_color = (210, 105, 30)  # #D2691E - Chocolate
    
    for y in range(size):
        ratio = y / size
        r = int(primary_color[0] * (1 - ratio) + secondary_color[0] * ratio)
        g = int(primary_color[1] * (1 - ratio) + secondary_color[1] * ratio)
        b = int(primary_color[2] * (1 - ratio) + secondary_color[2] * ratio)
        draw.rectangle([(0, y), (size, y + 1)], fill=(r, g, b))
    
    # رسم دائرة بيضاء في المنتصف
    circle_size = int(size * 0.6)
    circle_x = (size - circle_size) // 2
    circle_y = (size - circle_size) // 2
    draw.ellipse(
        [(circle_x, circle_y), (circle_x + circle_size, circle_y + circle_size)],
        fill='white',
        outline=secondary_color,
        width=max(2, size // 64)
    )
    
    # رисم رمز القهوة ☕
    try:
        # محاولة استخدام خط يدعم الإيموجي
        font_size = int(size * 0.4)
        try:
            font = ImageFont.truetype("seguiemj.ttf", font_size)  # خط إيموجي ويندوز
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # رسم النص ☕
        text = "☕"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2 - font_size // 8
        
        draw.text((text_x, text_y), text, fill=primary_color, font=font)
    except Exception as e:
        print(f"تحذير: تعذر رسم رمز القهوة - {e}")
        # رسم شكل بديل (فنجان مبسط)
        cup_width = int(size * 0.3)
        cup_height = int(size * 0.35)
        cup_x = (size - cup_width) // 2
        cup_y = (size - cup_height) // 2
        
        # جسم الفنجان
        draw.rounded_rectangle(
            [(cup_x, cup_y), (cup_x + cup_width, cup_y + cup_height)],
            radius=size // 20,
            fill=None,
            outline=primary_color,
            width=max(2, size // 32)
        )
        
        # مقبض الفنجان
        handle_x = cup_x + cup_width
        handle_y = cup_y + cup_height // 4
        handle_size = cup_width // 3
        draw.arc(
            [(handle_x, handle_y), (handle_x + handle_size, handle_y + handle_size)],
            start=270, end=90,
            fill=primary_color,
            width=max(2, size // 32)
        )
    
    img.save(output_path, 'PNG', quality=95)
    print(f"✅ تم إنشاء: {output_path} ({size}x{size})")

def convert_logo_to_icon(logo_path, size, output_path):
    """تحويل شعار الشركة إلى أيقونة بالحجم المطلوب"""
    try:
        img = Image.open(logo_path)
        
        # تحويل الصورة إلى RGBA إذا لم تكن كذلك
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # إنشاء صورة مربعة بخلفية شفافة
        icon = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        
        # حساب الأبعاد للحفاظ على نسبة العرض إلى الارتفاع
        img.thumbnail((int(size * 0.8), int(size * 0.8)), Image.Resampling.LANCZOS)
        
        # وضع الصورة في المنتصف
        x = (size - img.width) // 2
        y = (size - img.height) // 2
        icon.paste(img, (x, y), img)
        
        icon.save(output_path, 'PNG', quality=95)
        print(f"✅ تم تحويل الشعار: {output_path} ({size}x{size})")
        return True
    except Exception as e:
        print(f"❌ فشل تحويل الشعار: {e}")
        return False

def generate_all_icons():
    """توليد جميع الأيقونات المطلوبة"""
    # الأحجام المطلوبة لـ PWA
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    # إنشاء مجلد الأيقونات
    icons_dir = os.path.join('static', 'icons')
    os.makedirs(icons_dir, exist_ok=True)
    
    # البحث عن شعار الشركة
    logo_path = None
    uploads_dir = os.path.join('static', 'uploads')
    
    if os.path.exists(uploads_dir):
        for file in os.listdir(uploads_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                logo_path = os.path.join(uploads_dir, file)
                print(f"🔍 تم العثور على الشعار: {logo_path}")
                break
    
    print(f"\n{'='*50}")
    print(f"🎨 بدء توليد أيقونات PWA")
    print(f"{'='*50}\n")
    
    # توليد جميع الأحجام
    for size in sizes:
        output_path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
        
        if logo_path:
            # محاولة استخدام شعار الشركة
            success = convert_logo_to_icon(logo_path, size, output_path)
            if not success:
                # إنشاء أيقونة افتراضية في حالة الفشل
                create_default_icon(size, output_path)
        else:
            # إنشاء أيقونة افتراضية
            create_default_icon(size, output_path)
    
    # إنشاء favicon.ico
    try:
        favicon_path = os.path.join('static', 'favicon.ico')
        icon_32 = os.path.join(icons_dir, 'icon-192x192.png')
        
        if os.path.exists(icon_32):
            img = Image.open(icon_32)
            img.save(favicon_path, format='ICO', sizes=[(32, 32), (64, 64)])
            print(f"\n✅ تم إنشاء favicon.ico")
    except Exception as e:
        print(f"⚠️ تحذير: فشل إنشاء favicon.ico - {e}")
    
    # إنشاء apple-touch-icon
    try:
        apple_icon_path = os.path.join('static', 'apple-touch-icon.png')
        icon_180 = os.path.join(icons_dir, 'icon-192x192.png')
        
        if os.path.exists(icon_180):
            img = Image.open(icon_180)
            img.thumbnail((180, 180), Image.Resampling.LANCZOS)
            img.save(apple_icon_path, 'PNG')
            print(f"✅ تم إنشاء apple-touch-icon.png")
    except Exception as e:
        print(f"⚠️ تحذير: فشل إنشاء apple-touch-icon - {e}")
    
    print(f"\n{'='*50}")
    print(f"✅ اكتمل توليد جميع الأيقونات بنجاح!")
    print(f"📁 الموقع: {icons_dir}")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    try:
        generate_all_icons()
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
