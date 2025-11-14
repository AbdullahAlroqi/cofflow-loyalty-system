
// تسجيل اشتراك الإشعارات
document.addEventListener('DOMContentLoaded', function() {
    // التحقق من دعم الإشعارات
    if (!('Notification' in window)) {
        console.log('❌ هذا المتصفح لا يدعم إشعارات الويب');
        return;
    }

    // طلب إذن الإشعارات بعد تفاعل المستخدم
    const requestNotificationPermission = async () => {
        if (Notification.permission !== 'granted') {
            try {
                const permission = await Notification.requestPermission();
                if (permission === 'granted') {
                    console.log('✅ تم منح إذن الإشعارات');
                    registerPushSubscription();
                } else {
                    console.log('❌ تم رفض إذن الإشعارات');
                }
            } catch (error) {
                console.error('❌ خطأ في طلب إذن الإشعارات:', error);
            }
        } else {
            // الإذن ممنوح بالفعل، تسجيل الاشتراك
            registerPushSubscription();
        }
    };

    // تسجيل اشتراك الإشعارات
    async function registerPushSubscription() {
        try {
            if ('serviceWorker' in navigator && 'PushManager' in window) {
                const registration = await navigator.serviceWorker.ready;
                
                // الحصول على مفاتيح VAPID العامة من الخادم
                const response = await fetch('/api/notifications/vapid-public-key');
                const data = await response.json();
                
                if (!data.publicKey) {
                    console.error('❌ لم يتم استلام مفتاح VAPID العام');
                    return;
                }
                
                // تحويل المفتاح العام من Base64 إلى ArrayBuffer
                const publicKeyBase64 = data.publicKey;
                const publicKey = urlBase64ToUint8Array(publicKeyBase64);
                
                // إلغاء أي اشتراكات سابقة
                const existingSubscription = await registration.pushManager.getSubscription();
                if (existingSubscription) {
                    await existingSubscription.unsubscribe();
                }
                
                // إنشاء اشتراك جديد
                const subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: publicKey
                });
                
                // إرسال الاشتراك إلى الخادم
                await fetch('/api/notifications/subscribe', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ subscription: JSON.stringify(subscription) })
                });
                
                console.log('✅ تم تسجيل اشتراك الإشعارات بنجاح');
            }
        } catch (error) {
            console.error('❌ خطأ في تسجيل اشتراك الإشعارات:', error);
        }
    }
    
    // تحويل Base64 URL Safe إلى Uint8Array
    function urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');
        
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        
        return outputArray;
    }
    
    // زر طلب الإشعارات
    const notificationBtn = document.getElementById('enable-notifications-btn');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', requestNotificationPermission);
    }
    
    // إذا كان المستخدم مسجل الدخول وسبق منح الإذن، تسجيل الاشتراك تلقائياً
    if (document.body.classList.contains('user-authenticated') && Notification.permission === 'granted') {
        registerPushSubscription();
    }
});
