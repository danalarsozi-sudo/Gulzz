import logging
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- AYARLAR ---
API_TOKEN = '8402284125:AAFa8NCd7WJcydOpZZrtQIpObfRmcczkVdM'
ADMIN_ID = 1748533804
CHANNEL_ID = "@eminvbb"
ADMIN_USERNAME = "@Eminvb"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- VERİ TABANI (Gelişmiş İstatistikler eklendi) ---
db = {
    "users": {}, # user_id: {data, stats: {msg, photo, partners}}
    "active_chats": {},
    "waiting": {
        "tm": {"Gyz": [], "Oglan": []},
        "ru": {"Gyz": [], "Oglan": []}
    }
}

# --- LÜKS DİL PAKETİ (Aynen Korundu) ---
TEXTS = {
    "tm": {
        "welcome": "💎 **VIP Tanyşlyk Botuna Hoş Geldiňiz!**",
        "lang_select": "Dili saýlaň / Выберите язык:",
        "force_sub": "⛔️ **Giriş Gadagan!**\nBoty ulanmak üçin kanalymyza agza bolmaly.\n\nKanal: t.me/eminvbb",
        "check_sub": "Abuna Boldum ✅",
        "gender": "Jynsyňyzy saýlaň:",
        "boy": "Oglan 👨", "girl": "Gyz 👩",
        "age": "Ýaşyňyzy ýazyň (15-60):",
        "age_err": "❌ **Ýalňyş ýaş!** Diňe 15 we 60 aralygynda san ýazyň:",
        "name": "Ismiňizi ýazyň:",
        "phone_ask": "📱 Telefon belgiňizi paýlaşmak isleýärsiňizmi?",
        "phone_yes": "Hawa, Paýlaş 📱", "phone_no": "Gerek däl ❌",
        "menu": "💎 **VIP Menýu**",
        "find": "Taze adam tap 🔍", "profile": "Profilim 👤",
        "search": "🔍 **Gözlenilýär...**",
        "back": "Yza 🔙",
        "found": "✅ **Garşydaş tapyldy!**",
        "stop": "Söhbedi duruz 🛑",
        "stopped": "🛑 **Söhbet tamamlandy.**",
        "admin_btn": "👑 Admin Panel"
    },
    "ru": {
        "welcome": "💎 **Добро пожаловать в VIP Знакомства!**",
        "lang_select": "Выберите язык / Dili saýlaň:",
        "force_sub": "⛔️ **Доступ ограничен!**\nПодпишитесь на канал: t.me/eminvbb",
        "check_sub": "Я Подписался ✅",
        "gender": "Выберите ваш пол:",
        "boy": "Парень 👨", "girl": "Девушка 👩",
        "age": "Введите ваш возраст (15-60):",
        "age_err": "❌ **Ошибка!** От 15 до 60:",
        "name": "Введите ваше имя:",
        "phone_ask": "📱 Хотите поделиться номером телефона?",
        "phone_yes": "Да, Поделиться 📱", "phone_no": "Нет ❌",
        "menu": "💎 **VIP Меню**",
        "find": "Найти собеседника 🔍", "profile": "Мой профиль 👤",
        "search": "🔍 **Поиск...**",
        "back": "Назад 🔙",
        "found": "✅ **Партнер найден!**",
        "stop": "Остановить чат 🛑",
        "stopped": "🛑 **Чат завершен.**",
        "admin_btn": "👑 Админ Панель"
    }
}

class Reg(StatesGroup):
    lang, gender, age, name, phone = State(), State(), State(), State(), State()

class Chat(StatesGroup):
    active = State()

# --- YARDIMCI FONKSİYONLAR ---
async def is_subscribed(user_id):
    try:
        m = await bot.get_chat_member(CHANNEL_ID, user_id)
        return m.status in ["member", "administrator", "creator"]
    except: return False

def get_main_kb(lang, user_id):
    b = ReplyKeyboardBuilder()
    b.button(text=TEXTS[lang]["find"])
    b.button(text=TEXTS[lang]["profile"])
    if user_id == ADMIN_ID: b.button(text=TEXTS[lang]["admin_btn"])
    b.adjust(2)
    return b.as_markup(resize_keyboard=True)

# --- KAYIT VE ANA AKIŞ (Korundu) ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    if not await is_subscribed(message.from_user.id):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Kanal / Канал", url="https://t.me/eminvbb")],
            [InlineKeyboardButton(text=TEXTS["tm"]["check_sub"], callback_data="check_sub")]
        ])
        return await message.answer(TEXTS["tm"]["force_sub"], reply_markup=kb)
    if message.from_user.id in db["users"]:
        lang = db["users"][message.from_user.id]["lang"]
        return await message.answer(TEXTS[lang]["menu"], reply_markup=get_main_kb(lang, message.from_user.id))
    await message.answer(TEXTS["tm"]["lang_select"], reply_markup=ReplyKeyboardBuilder().button(text="TM 🇹🇲").button(text="RU 🇷🇺").as_markup(resize_keyboard=True))
    await state.set_state(Reg.lang)

@dp.callback_query(F.data == "check_sub")
async def callback_check_sub(c: types.CallbackQuery, state: FSMContext):
    if await is_subscribed(c.from_user.id): await cmd_start(c.message, state)
    else: await c.answer("❌ Agza bolmadyňyz!", show_alert=True)

@dp.message(Reg.lang)
async def reg_lang(m: types.Message, state: FSMContext):
    l = "tm" if "TM" in m.text else "ru"
    await state.update_data(lang=l)
    kb = ReplyKeyboardBuilder().button(text=TEXTS[l]["boy"]).button(text=TEXTS[l]["girl"]).as_markup(resize_keyboard=True)
    await m.answer(TEXTS[l]["gender"], reply_markup=kb); await state.set_state(Reg.gender)

@dp.message(Reg.gender)
async def reg_gender(m: types.Message, state: FSMContext):
    d = await state.get_data(); l = d['lang']
    g = "Oglan" if m.text in [TEXTS["tm"]["boy"], TEXTS["ru"]["boy"]] else "Gyz"
    await state.update_data(gender=g)
    await m.answer(TEXTS[l]["age"], reply_markup=types.ReplyKeyboardRemove()); await state.set_state(Reg.age)

@dp.message(Reg.age)
async def reg_age(m: types.Message, state: FSMContext):
    d = await state.get_data(); l = d['lang']
    if not m.text.isdigit() or not (15 <= int(m.text) <= 60): return await m.answer(TEXTS[l]["age_err"])
    await state.update_data(age=m.text); await m.answer(TEXTS[l]["name"]); await state.set_state(Reg.name)

@dp.message(Reg.name)
async def reg_name(m: types.Message, state: FSMContext):
    d = await state.get_data(); l = d['lang']
    await state.update_data(name=m.text)
    kb = ReplyKeyboardBuilder().button(text=TEXTS[l]["phone_yes"], request_contact=True).button(text=TEXTS[l]["phone_no"]).as_markup(resize_keyboard=True)
    await m.answer(TEXTS[l]["phone_ask"], reply_markup=kb); await state.set_state(Reg.phone)

@dp.message(Reg.phone)
async def reg_phone(m: types.Message, state: FSMContext):
    d = await state.get_data(); l = d['lang']
    p = m.contact.phone_number if m.contact else "Gizlin"
    db["users"][m.from_user.id] = {
        "lang": l, "gender": d['gender'], "age": d['age'], "name": d['name'], "phone": p, 
        "username": m.from_user.username, "reg_date": datetime.now().strftime("%d.%m.%Y"),
        "stats": {"msg": 0, "photo": 0, "partners": 0} # İstatistik başlatma
    }
    await m.answer("🎉 **Lüks VIP agzalygyňyz tassyklandy!**", reply_markup=get_main_kb(l, m.from_user.id))
    await state.clear()

# --- GELİŞMİŞ ANALİTİK ADMIN PANEL ---
@dp.message(F.text.in_(["👑 Admin Panel", "Admin Panel"]))
async def admin_main(m: types.Message):
    if m.from_user.id != ADMIN_ID: return
    u = db["users"]
    b = sum(1 for x in u.values() if x['gender'] == "Oglan")
    g = sum(1 for x in u.values() if x['gender'] == "Gyz")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 En Aktiv 10 Ulanyjy", callback_data="admin_top")],
        [InlineKeyboardButton(text="👤 Ähli Ulanyjylar", callback_data="admin_list")]
    ])
    await m.answer(f"👑 **VIP Analitika**\n\nJemi: {len(u)}\n👨 Oglan: {b}\n👩 Gyz: {g}", reply_markup=kb)

@dp.callback_query(F.data == "admin_top")
async def admin_top_users(c: types.CallbackQuery):
    if c.from_user.id != ADMIN_ID: return
    # Mesaj sayısına göre sırala
    top = sorted(db["users"].items(), key=lambda x: x[1]['stats']['msg'], reverse=True)[:10]
    res = "🏆 **En Aktiv 10 Ulanyjy:**\n\n"
    for i, (uid, data) in enumerate(top, 1):
        s = data['stats']
        res += f"{i}. {data['name']} (@{data['username'] or 'n/a'})\n   💬 {s['msg']} msj | 📸 {s['photo']} fto | 🤝 {s['partners']} eş\n"
    await c.message.answer(res); await c.answer()

@dp.callback_query(F.data == "admin_list")
async def admin_list_detailed(c: types.CallbackQuery):
    if c.from_user.id != ADMIN_ID: return
    kb = InlineKeyboardBuilder()
    for uid, u in db["users"].items():
        kb.button(text=f"{u['name']} ({u['gender']})", callback_data=f"info_{uid}")
    kb.adjust(2)
    await c.message.answer("🔍 Maglumat üçin ulanyjynyň üstüne basyň:", reply_markup=kb.as_markup())
    await c.answer()

@dp.callback_query(F.data.startswith("info_"))
async def admin_user_info(c: types.CallbackQuery):
    uid = int(c.data.split("_")[1])
    u = db["users"].get(uid)
    if not u: return await c.answer("Tapylmady.")
    s = u['stats']
    res = (f"👤 **Giňişleýin Maglumat:**\n\n"
           f"Ismi: {u['name']}\nÝaşy: {u['age']}\nJynsy: {u['gender']}\nTel: {u['phone']}\n"
           f"Username: @{u['username'] or 'n/a'}\n"
           f"--- 📊 Statistikasy ---\n"
           f"💬 Jemi ýazan habary: {s['msg']}\n"
           f"📸 Jemi ugradan suraty: {s['photo']}\n"
           f"🤝 Tanyşan adamlarynyň sany: {s['partners']}")
    await c.message.answer(res); await c.answer()

# --- SOHBET SİSTEMİ (İstatistik Sayacı eklendi) ---
@dp.message(F.text.in_(["Taze adam tap 🔍", "Найти собеседника 🔍", "Yza 🔙", "Назад 🔙"]))
async def find_partner(m: types.Message, state: FSMContext):
    uid = m.from_user.id; user = db["users"].get(uid)
    if not user: return await cmd_start(m, state)
    l = user['lang']
    for g in ["Oglan", "Gyz"]:
        if uid in db["waiting"][l][g]: db["waiting"][l][g].remove(uid)

    target = "Gyz" if user['gender'] == "Oglan" else "Oglan"
    if db["waiting"][l][target]:
        pid = db["waiting"][l][target].pop(0)
        db["active_chats"][uid], db["active_chats"][pid] = pid, uid
        # Eşleşme sayısını artır
        db["users"][uid]["stats"]["partners"] += 1
        db["users"][pid]["stats"]["partners"] += 1
        
        await state.set_state(Chat.active); await dp.fsm.get_context(bot, pid, pid).set_state(Chat.active)
        for cid, oid in [(uid, pid), (pid, uid)]:
            cl = db["users"][cid]["lang"]
            kb = ReplyKeyboardBuilder().button(text=TEXTS[cl]["stop"]).as_markup(resize_keyboard=True)
            await bot.send_message(cid, TEXTS[cl]["found"], reply_markup=kb)
    else:
        db["waiting"][l][user['gender']].append(uid)
        await m.answer(TEXTS[l]["search"], reply_markup=ReplyKeyboardBuilder().button(text=TEXTS[l]["back"]).as_markup(resize_keyboard=True))

@dp.message(Chat.active)
async def chat_handler(m: types.Message, state: FSMContext):
    uid = m.from_user.id; pid = db["active_chats"].get(uid)
    u = db["users"][uid]; l = u["lang"]

    if m.text in [TEXTS["tm"]["stop"], TEXTS["ru"]["stop"]]:
        if pid:
            pl = db["users"][pid]["lang"]
            await bot.send_message(pid, TEXTS[pl]["stopped"], reply_markup=get_main_kb(pl, pid))
            await dp.fsm.get_context(bot, pid, pid).clear()
            if pid in db["active_chats"]: del db["active_chats"][pid]
        await m.answer(TEXTS[l]["stopped"], reply_markup=get_main_kb(l, uid))
        await state.clear(); 
        if uid in db["active_chats"]: del db["active_chats"][uid]
        return

    if pid:
        # İSTATİSTİK SAYACI
        if m.text: db["users"][uid]["stats"]["msg"] += 1
        if m.photo: db["users"][uid]["stats"]["photo"] += 1

        try:
            if m.text: await bot.send_message(pid, m.text)
            elif m.photo: await bot.send_photo(pid, m.photo[-1].file_id, caption=m.caption)
            elif m.voice: await bot.send_voice(pid, m.voice.file_id)
            elif m.video: await bot.send_video(pid, m.video.file_id, caption=m.caption)
            elif m.sticker: await bot.send_sticker(pid, m.sticker.file_id)
        except: pass

@dp.message(F.text.in_(["Profilim 👤", "Мой профиль 👤"]))
async def view_profile(m: types.Message):
    u = db["users"].get(m.from_user.id)
    if not u: return
    s = u['stats']
    res = {
        "tm": f"👤 **Profilim**\n\nIsmi: {u['name']}\nÝaşy: {u['age']}\n\n📊 Statistikam:\n💬 Habarlar: {s['msg']}\n📸 Suratlar: {s['photo']}\n🤝 Tanyşlyk: {s['partners']}",
        "ru": f"👤 **Мой профиль**\n\nИмя: {u['name']}\nВозраст: {u['age']}\n\n📊 Статистика:\n💬 Сообщения: {s['msg']}\n📸 Фото: {s['photo']}\n🤝 Знакомства: {s['partners']}"
    }
    await m.answer(res[u['lang']])

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
