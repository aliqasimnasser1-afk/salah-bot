from __future__ import annotations

from datetime import datetime, timedelta

PRAYER_NAMES = {
    "ar": {
        "Fajr": "الفجر",
        "Sunrise": "الشروق",
        "Dhuhr": "الظهر",
        "Asr": "العصر",
        "Maghrib": "المغرب",
        "Isha": "العشاء",
    },
    "en": {
        "Fajr": "Fajr",
        "Sunrise": "Sunrise",
        "Dhuhr": "Dhuhr",
        "Asr": "Asr",
        "Maghrib": "Maghrib",
        "Isha": "Isha",
    },
}

ICONS = {"Fajr": "🌙", "Sunrise": "🌅", "Dhuhr": "☀️", "Asr": "🌤", "Maghrib": "🌇", "Isha": "🌌"}

METHODS = {
    4: {"ar": "أم القرى (مكة)", "en": "Umm Al-Qura (Makkah)"},
    3: {"ar": "رابطة العالم الإسلامي", "en": "Muslim World League"},
    5: {"ar": "الهيئة المصرية", "en": "Egyptian General Authority"},
    2: {"ar": "أمريكا الشمالية (ISNA)", "en": "ISNA (North America)"},
    1: {"ar": "جامعة كراتشي", "en": "University of Karachi"},
    15: {"ar": "رؤية الهلال", "en": "Moonsighting Committee"},
}

REMINDER_CHOICES = (0, 5, 10, 15, 30)

LANGUAGE_PROMPT = (
    "🌐 <b>اختر لغتك | Choose your language</b>\n\n"
    "اختر اللغة التي تريد استخدام البوت بها.\n"
    "Pick the language you want to use the bot in."
)
LANGUAGES = {"ar": "🇸🇦 العربية", "en": "🇬🇧 English"}

STRINGS = {
    "ar": {
        "welcome": (
            "🕌 <b>أهلًا بك في بوت مواقيت الصلاة</b>\n\n"
            "أرسل لي موقعك وسأرسل لك:\n"
            "• تنبيه قبل كل صلاة وعند دخول وقتها\n"
            "• أذكار الصباح والمساء تلقائيًا\n"
            "• اتجاه القبلة والتاريخ الهجري\n\n"
            "اضغط الزر في الأسفل لإرسال موقعك، أو اكتب اسم مدينتك (مثال: <code>حائل</code>)."
            "💡 موقع الكمبيوتر قد يكون تقريبيًا؛ الجوال أدق، أو اكتب اسم مدينتك."
        ),
        "share_location": "📍 إرسال موقعي",
        "btn_ok": "✅ صحيح",
        "pick_region": "🗺 <b>اختر منطقتك في المملكة</b>\n\nأو أرسل موقعك الدقيق، أو اختر «مدينة أخرى» إن كنت خارج السعودية.",
        "pick_city": "🏙 <b>{region}</b>\n\nاختر مدينتك:",
        "btn_gps": "📍 موقعي الدقيق",
        "btn_other": "🌍 مدينة أخرى",
        "btn_regions": "⬅️ المناطق",
        "btn_change_city": "✏️ غيّر المدينة",
        "ask_city": "✏️ اكتب اسم مدينتك (مثال: <code>حائل</code>):",
        "menu_place": "📍 {place}",
        "location_saved": "✅ تم حفظ موقعك: <b>{place}</b>\n🕒 {tz}\n\nليس موقعك؟ اضغط «غيّر المدينة» واكتب اسم مدينتك.",
        "location_failed": "❌ لم أستطع تحديد هذا المكان. جرّب اسم مدينة آخر أو أرسل موقعك مباشرة.",
        "service_down": "⚠️ خدمة المواقيت لا تستجيب الآن. حاول بعد قليل.",
        "need_location": "📍 أحتاج موقعك أولًا. اكتب اسم مدينتك أو أرسل موقعك.",
        "menu_title": "اختر من القائمة:",
        "btn_times": "🕋 مواقيت اليوم",
        "btn_next": "⏳ الصلاة القادمة",
        "btn_qibla": "🧭 القبلة",
        "btn_morning": "🌅 أذكار الصباح",
        "btn_evening": "🌇 أذكار المساء",
        "btn_settings": "⚙️ الإعدادات",
        "btn_back": "⬅️ رجوع",
        "btn_prev": "السابق",
        "btn_next": "التالي",
        "btn_home": "🏠 القائمة",
        "times_title": "🕋 <b>مواقيت الصلاة</b>",
        "next_line": "⏳ الصلاة القادمة: <b>{name}</b> {icon} بعد <b>{left}</b>",
        "next_title": "⏳ <b>الصلاة القادمة</b>",
        "qibla": (
            "🧭 <b>اتجاه القبلة</b>\n\n"
            "الزاوية: <b>{deg:.0f}°</b> من الشمال باتجاه عقارب الساعة ({dir})\n"
            "المسافة إلى الكعبة: <b>{km:,.0f} كم</b>\n\n"
            "وجّه رأس هاتفك نحو الشمال في تطبيق البوصلة، ثم استدر إلى الزاوية المذكورة."
        ),
        "settings_title": "⚙️ <b>الإعدادات</b>",
        "settings_body": (
            "اللغة: <b>العربية</b>\n"
            "طريقة الحساب: <b>{method}</b>\n"
            "التنبيه قبل الصلاة: <b>{remind}</b>\n"
            "الأذكار التلقائية: <b>{adhkar}</b>\n"
            "الموقع: <b>{place}</b>\n"
            "المنطقة الزمنية: <b>{tz}</b>"
        ),
        "off": "إيقاف",
        "on": "تشغيل",
        "minutes": "{n} دقيقة",
        "btn_lang": "🌐 English",
        "btn_method": "📐 طريقة الحساب",
        "btn_remind": "🔔 وقت التنبيه",
        "btn_adhkar": "📿 الأذكار: {state}",
        "btn_location": "📍 تغيير الموقع",
        "pick_method": "اختر طريقة الحساب:",
        "pick_remind": "كم دقيقة قبل الصلاة تريد التنبيه؟",
        "saved": "✅ تم الحفظ",
        "remind_msg": "🔔 بقي <b>{n} دقيقة</b> على صلاة <b>{name}</b> {icon}",
        "adhan_msg": "{icon} حان الآن وقت صلاة <b>{name}</b>",
        "hours_short": "س",
        "minutes_short": "د",
        "stats": "👥 المستخدمون: <b>{total}</b>\n📍 لديهم موقع: <b>{located}</b>",
        "help": (
            "<b>الأوامر</b>\n"
            "/times — مواقيت اليوم\n"
            "/next — الصلاة القادمة\n"
            "/qibla — اتجاه القبلة\n"
            "/morning — أذكار الصباح\n"
            "/evening — أذكار المساء\n"
            "/settings — الإعدادات\n"
            "/start — القائمة الرئيسية"
        ),
        "hint_menu": "استخدم القائمة أو الأوامر. /help",
    },
    "en": {
        "welcome": (
            "🕌 <b>Welcome to the Prayer Times bot</b>\n\n"
            "Share your location and I will send you:\n"
            "• A reminder before each prayer and when it begins\n"
            "• Morning and evening adhkar automatically\n"
            "• Qibla direction and the Hijri date\n\n"
            "Tap the button below to share your location, or type your city (e.g. <code>Hail</code>)."
            "💡 A computer's location can be approximate; a phone is more precise, or just type your city."
        ),
        "share_location": "📍 Share my location",
        "btn_ok": "✅ Correct",
        "pick_region": "🗺 <b>Choose your region in Saudi Arabia</b>\n\nOr share your exact location, or tap “Other city” if you are outside Saudi Arabia.",
        "pick_city": "🏙 <b>{region}</b>\n\nChoose your city:",
        "btn_gps": "📍 My exact location",
        "btn_other": "🌍 Other city",
        "btn_regions": "⬅️ Regions",
        "btn_change_city": "✏️ Change city",
        "ask_city": "✏️ Type your city name (e.g. <code>Hail</code>):",
        "menu_place": "📍 {place}",
        "location_saved": "✅ Location saved: <b>{place}</b>\n🕒 {tz}\n\nNot your location? Tap “Change city” and type your city name.",
        "location_failed": "❌ I could not find that place. Try another city name or share your location.",
        "service_down": "⚠️ The prayer-times service is not responding. Please try again shortly.",
        "need_location": "📍 I need your location first. Type your city or share your location.",
        "menu_title": "Choose from the menu:",
        "btn_times": "🕋 Today's times",
        "btn_next": "⏳ Next prayer",
        "btn_qibla": "🧭 Qibla",
        "btn_morning": "🌅 Morning adhkar",
        "btn_evening": "🌇 Evening adhkar",
        "btn_settings": "⚙️ Settings",
        "btn_back": "⬅️ Back",
        "btn_prev": "Previous",
        "btn_next": "Next",
        "btn_home": "🏠 Menu",
        "times_title": "🕋 <b>Prayer times</b>",
        "next_line": "⏳ Next prayer: <b>{name}</b> {icon} in <b>{left}</b>",
        "next_title": "⏳ <b>Next prayer</b>",
        "qibla": (
            "🧭 <b>Qibla direction</b>\n\n"
            "Bearing: <b>{deg:.0f}°</b> clockwise from north ({dir})\n"
            "Distance to the Kaaba: <b>{km:,.0f} km</b>\n\n"
            "Point your phone north in a compass app, then turn to the bearing above."
        ),
        "settings_title": "⚙️ <b>Settings</b>",
        "settings_body": (
            "Language: <b>English</b>\n"
            "Calculation method: <b>{method}</b>\n"
            "Reminder before prayer: <b>{remind}</b>\n"
            "Automatic adhkar: <b>{adhkar}</b>\n"
            "Location: <b>{place}</b>\n"
            "Time zone: <b>{tz}</b>"
        ),
        "off": "Off",
        "on": "On",
        "minutes": "{n} min",
        "btn_lang": "🌐 العربية",
        "btn_method": "📐 Calculation method",
        "btn_remind": "🔔 Reminder time",
        "btn_adhkar": "📿 Adhkar: {state}",
        "btn_location": "📍 Change location",
        "pick_method": "Choose a calculation method:",
        "pick_remind": "How many minutes before prayer should I remind you?",
        "saved": "✅ Saved",
        "remind_msg": "🔔 <b>{n} minutes</b> until <b>{name}</b> {icon}",
        "adhan_msg": "{icon} It is now time for <b>{name}</b>",
        "hours_short": "h",
        "minutes_short": "m",
        "stats": "👥 Users: <b>{total}</b>\n📍 With location: <b>{located}</b>",
        "help": (
            "<b>Commands</b>\n"
            "/times — today's prayer times\n"
            "/next — next prayer\n"
            "/qibla — Qibla direction\n"
            "/morning — morning adhkar\n"
            "/evening — evening adhkar\n"
            "/settings — settings\n"
            "/start — main menu"
        ),
        "hint_menu": "Use the menu or commands. /help",
    },
}


def t(lang: str, key: str, **kwargs: object) -> str:
    text = STRINGS.get(lang, STRINGS["ar"])[key]
    return text.format(**kwargs) if kwargs else text


def prayer_name(lang: str, prayer: str) -> str:
    return PRAYER_NAMES.get(lang, PRAYER_NAMES["ar"])[prayer]


def format_left(lang: str, delta: timedelta) -> str:
    total = max(int(delta.total_seconds()), 0)
    hours, rem = divmod(total, 3600)
    minutes = rem // 60
    h, m = t(lang, "hours_short"), t(lang, "minutes_short")
    if hours:
        return f"{hours}{h} {minutes}{m}"
    return f"{max(minutes, 1)}{m}"


def format_clock(moment: datetime) -> str:
    return moment.strftime("%H:%M")
