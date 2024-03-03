import logging
import sqlite3

from config import *
from db import db, create_db
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

import asyncio

import re

set_role_user_id = 0

# Define a list of available languages with their flags
languages = {
    "English": "🇺🇸",
    "French": "🇫🇷",
    "Spanish": "🇪🇸",
    "German": "🇩🇪",
    "Italian": "🇮🇹",
    "Chinese": "🇨🇳",
    "Russian": "🇷🇺",
    "Portugales": "🇵🇹",
    "Indian": "🇮🇳",
    "Polish": "🇵🇱",
    "Korea": "🇰🇷",
    "Japan": "🇯🇵",
    "Turkish": "🇹🇷",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bot = Bot(token=token, parse_mode="HTML")
dp = Dispatcher(bot=bot, storage=MemoryStorage())

states = [State('user', StatesGroup),
          State('image', StatesGroup)]

# SQLite database connection
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

Send_Image = False

photo_for_mailing = ""
previous_message = None
previous_reply_markup = None

admin_replies = {}  

class user(StatesGroup):
    name = State()
    text = State()
    image = State()
    input_image = State()
    text_template = State()

@dp.message_handler(commands=["start"], state="*")
async def start(message: types.Message, state: FSMContext):
    await state.finish()

    user_id = message.from_user.id
    user_un = message.from_user.username
    if user_un is None:
        user_un = message.from_user.first_name

    # Create an inline markup for language selection
    lang_select_markup = InlineKeyboardMarkup(row_width=2)
    lang_buttons = []

    for lang_text, lang_code in languages.items():
        lang_btn = InlineKeyboardButton(text=f"{lang_text} {lang_code}", callback_data=f"select_lang_{lang_text}")
        lang_buttons.append(lang_btn)

    # Add buttons to the markup with 2 buttons in a row
    for i in range(0, len(lang_buttons), 2):
        if i + 1 < len(lang_buttons):
            lang_select_markup.add(lang_buttons[i], lang_buttons[i + 1])
        else:
            lang_select_markup.add(lang_buttons[i])

    # Check if the user ID is already present in the database
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id, ))
    existing_user = cursor.fetchone()

    if not existing_user:
        print("bebra")
        # Insert the user ID into the database
        await bot.send_message(text="🟢 Добавлен новый пользователь " + "@" + str(message.from_user.username), chat_id=admin)
        print(f"User: {user_id} added to data base")
        cursor.execute("INSERT INTO users (id, role) VALUES (?, ?)", (user_id, "Default"))
        conn.commit()

    # Send the greeting message with inline language selection options
    greeting_message = "Escape the Matrix's grasp on poverty, weakness, and loneliness. Embrace our powerful tool, crafted to set you free. With courage, carve your own path to success."
    await message.answer(greeting_message, reply_markup=lang_select_markup)


    if user_id == int(admin):
        await message.answer("<b>Вы являетесь администратором, пропишите команду /admin</b>")
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=5)
        row = []
        try:
            for template in db.get_templates():
                template_btn = types.InlineKeyboardButton(text=template, callback_data=f"send_{template}_{user_id}")
                row.append(template_btn)
            keyboard.add(*row)
        except:
            pass

        delete_message_button = types.InlineKeyboardButton(text="Удалить это сообщение", callback_data="delete_message")
        keyboard.add(delete_message_button)
        print("add")

        user_id = message.from_user.id

        # Query the database to retrieve the user's role
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            role = result[0]
        else:
            role = "Unknown"

        string_role = ""

        if role == "Default":
            string_role = "Обычный клиент 🤖"
        elif role == "Want Client":
            string_role = "Потенциальный покупатель 💸"
        elif role == "Buy Client":
            string_role = "Купивший 💳"

        message_text = f"<b>Новое сообщение</b>\n\n" \
                       f"<code>{message.text}</code>\n\n" \
                       f"<b>От: <a href='tg://user?id={user_id}'>{user_un}</a></b>\n" \
                       f"Статус пользователя: {string_role}\n" \
                       f"<b>Айди пользователя:</b> <code>{user_id}</code>"

        add = types.InlineKeyboardButton(text="Изменить статус ✨", callback_data="change_role")
        keyboard.add(add)

        await bot.send_message(text=message_text, reply_markup=keyboard, chat_id=admin)

@dp.callback_query_handler(lambda query: query.data.startswith("back_to_multilingual_message_"))
async def back_to_multilingual_message_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    user_language = query.data.split("_")[-1]
    await send_multilingual_message(user_id, user_language)

async def send_multilingual_message(user_id, user_language, media_path=None):
        caption = "Info"

        buttons_text = []

        if user_language == "English":      # 1
            button_texts = ["🎬 Video\\Text instruction of the software", "📝 How it works in text format", "📱 How to log in to crypto wallets on your phone", 
                            "🆓 Demo Version", "✔️ About guarantees", "📚 Answers to questions (FAQ)", 
                            "🔥 How we withdraw crypto from wallets", "👀 Difference between blockchains and packages", 
                            "⚠️ Customer reviews", "💰 Official Price-List", "⚡️ History of the development of our software", "⭐️ BUY"] ##
        elif user_language == "Italian":    # 2
            button_texts = ["🎬 Video\\Istruzioni testuali del software", "📝 Come funziona in formato di testo", "📱 Come accedere ai portafogli crittografici sul tuo telefono", 
                    "🆓 Versione demo", "✔️ Informazioni sulle garanzie", "📚 Risposte alle domande (FAQ)", 
                    "🔥 Come preleviamo cripto dai portafogli", "👀 Differenza tra blockchain e pacchetti", 
                    "⚠️ Recensioni dei clienti", "💰 Lista prezzi ufficiale", "⚡️ Storia dello sviluppo del nostro software", "⭐️ ACQUISTA"] ##
        elif user_language == "French":     # 3
            button_texts = ["🎬 Vidéo\\Instructions textuelles du logiciel", "📝 Comment ça fonctionne en format texte", "📱 Comment se connecter aux portefeuilles de crypto sur votre téléphone", 
                    "🆓 Version de démonstration", "✔️ À propos des garanties", "📚 Réponses aux questions (FAQ)", 
                    "🔥 Comment nous retirons la crypto de portefeuilles", "👀 Différence entre les blockchains et les packages", 
                    "⚠️ Avis clients", "💰 Liste de prix officielle", "⚡️ Histoire du développement de notre logiciel", "⭐️ ACHETER"] ##
        elif user_language == "Spanish":    # 4
            button_texts = ["🎬 Instrucciones de video\\texto del software", "📝 Cómo funciona en formato de texto", "📱 Cómo iniciar sesión en billeteras de criptomonedas en tu teléfono", 
                    "🆓 Versión de demostración", "✔️ Acerca de las garantías", "📚 Respuestas a preguntas (FAQ)", 
                    "🔥 Cómo retiramos cripto de billeteras", "👀 Diferencia entre blockchains y paquetes", 
                    "⚠️ Reseñas de clientes", "💰 Lista de precios oficial", "⚡️ Historia del desarrollo de nuestro software", "⭐️ COMPRAR"] ##
        elif user_language == "Portugales": # 5
            button_texts = ["🎬 Vídeo\\Instrução de texto do software", "📝 Como funciona em formato de texto", "📱 Como fazer login em carteiras de criptomoedas no seu telefone", 
                    "🆓 Versão de demonstração", "✔️ Sobre garantias", "📚 Respostas às perguntas (FAQ)", 
                    "🔥 Como retiramos cripto de carteiras", "👀 Diferença entre blockchains e pacotes", 
                    "⚠️ Avaliações dos clientes", "💰 Lista de preços oficial", "⚡️ História do desenvolvimento do nosso software", "⭐️ COMPRAR"] ##
        elif user_language == "Russian":    # 6
            button_texts = ["🎬 Видео\\Текстовая инструкция по программному обеспечению", "📝 Как это работает в текстовом формате", "📱 Как войти в криптовалютные кошельки на вашем телефоне", 
                    "🆓 Демо-версия", "✔️ О гарантиях", "📚 Ответы на вопросы (FAQ)", 
                    "🔥 Как мы выводим криптовалюту из кошельков", "👀 Разница между блокчейнами и пакетами", 
                    "⚠️ Отзывы клиентов", "💰 Официальный прайс-лист", "⚡️ История развития нашего программного обеспечения", "⭐️ КУПИТЬ"] ##
        elif user_language == "Indian":    # 7
            button_texts = ["🎬 सॉफ़्टवेयर के वीडियो\\टेक्स्ट निर्देश", "📝 पाठ प्रारूप में यह कैसे काम करता है", "📱 अपने फोन पर क्रिप्टो वॉलेट्स में लॉग इन कैसे करें", 
                    "🆓 डेमो संस्करण", "✔️ गारंटीज के बारे में", "📚 प्रश्नों के जवाब (FAQ)", 
                    "🔥 हम कैसे वॉलेट से क्रिप्टो निकालते हैं", "👀 ब्लॉकचेन्स और पैकेजेस के बीच अंतर", 
                    "⚠️ ग्राहक समीक्षा", "💰 आधिकारिक मूल्य-सूची", "⚡️ हमारे सॉफ़्टवेयर के विकास का इतिहास", "⭐️ खरीदें"] ##
        elif user_language == "Chinese":   # 8
            button_texts = ["🎬 软件的视频\\文字说明", "📝 如何在文本格式中运作", "📱 如何在手机上登录加密货币钱包", 
                    "🆓 演示版本", "✔️ 关于保证", "📚 问题的答案 (FAQ)", 
                    "🔥 我们如何从钱包中提取加密货币", "👀 区块链和包的区别", 
                    "⚠️ 客户评价", "💰 官方价格表", "⚡️ 我们软件的发展历程", "⭐️ 购买"] ##
        elif user_language == "German":    # 9
            button_texts = ["🎬 Video\\Textanleitung der Software", "📝 Wie es im Textformat funktioniert", "📱 So melden Sie sich bei Kryptowallets auf Ihrem Telefon an", 
                    "🆓 Demo-Version", "✔️ Über Garantien", "📚 Antworten auf Fragen (FAQ)", 
                    "🔥 Wie wir Krypto aus Geldbörsen abheben", "👀 Unterschied zwischen Blockchains und Paketen", 
                    "⚠️ Kundenbewertungen", "💰 Offizielle Preisliste", "⚡️ Geschichte der Entwicklung unserer Software", "⭐️ KAUFEN"] ##
        elif user_language == "Polish":       # 10
            button_texts = ["🎬 Wideo\Instrukcja tekstowa oprogramowania", "📝 Jak to działa w formacie tekstowym", "📱 Jak zalogować się do portfeli kryptowalut na telefonie", 
                    "🆓 Wersja demonstracyjna", "✔️ O gwarancjach", "📚 Odpowiedzi na pytania (FAQ)", 
                    "🔥 Jak wypłacamy kryptowaluty z portfeli", "👀 Różnica między blockchainami a pakietami", 
                    "⚠️ Opinie klientów", "💰 Oficjalna lista cen", "⚡️ Historia rozwoju naszego oprogramowania", "⭐️ KUP"] ##
        elif user_language == "Korea":       # 11
            button_texts = ["🎬 소프트웨어의 비디오\텍스트 지침", "📝 텍스트 형식으로 작동하는 방법", "📱 휴대폰에서 암호화폐 지갑에 로그인하는 방법", 
                    "🆓 데모 버전", "✔️ 보증에 관하여", "📚 질문에 대한 답변 (FAQ)", 
                    "🔥 지갑에서 암호화폐를 인출하는 방법", "👀 블록체인과 패키지의 차이", 
                    "⚠️ 고객 리뷰", "💰 공식 가격표", "⚡️ 저희 소프트웨어 개발 역사", "⭐️ 구매"] ##
        elif user_language == "Japan":     # 12
            button_texts = ["🎬 ソフトウェアのビデオ\テキスト説明", "📝 テキスト形式での動作方法", "📱 スマートフォンで暗号通貨ウォレットにログインする方法", 
                    "🆓 デモ版", "✔️ 保証について", "📚 質問への回答 (FAQ)", 
                    "🔥 ウォレットから暗号通貨を引き出す方法", "👀 ブロックチェーンとパッケージの違い", 
                    "⚠️ 顧客レビュー", "💰 公式価格リスト", "⚡️ 当社ソフトウェアの開発経緯", "⭐️ 購入"]  ##
        elif user_language == "Turkish":       # 13
            button_texts = ["🎬 Yazılımın Video\Metin Talimatı", "📝 Metin formatında nasıl çalıştığı", "📱 Telefonunuzdaki kripto cüzdanlarına nasıl giriş yapılır", 
                    "🆓 Demo Sürüm", "✔️ Garantiler Hakkında", "📚 Soruların Cevapları (SSS)", 
                    "🔥 Cüzdanlardan kripto para çekme yöntemimiz", "👀 Blockchains ve paketler arasındaki fark", 
                    "⚠️ Müşteri Değerlendirmeleri", "💰 Resmi Fiyat Listesi", "⚡️ Yazılım geliştirmemizin tarihçesi", "⭐️ SATIN AL"] ##

        custom_buttons_markup = InlineKeyboardMarkup()
        
        for i, btn_text in enumerate(button_texts):
            if i == 0:
                btn = InlineKeyboardButton(text=f"{btn_text}", url="https://t.me/c/1131408173/548")
            elif i == 4:
                btn = InlineKeyboardButton(text=f"{btn_text}", callback_data=f"send_infotext_button2_{user_language}")
            elif i == 5:
                btn = InlineKeyboardButton(text=f"{btn_text}", callback_data=f"send_infotext_button3_{user_language}")
            elif i == 1:
                btn = InlineKeyboardButton(text=f"{btn_text}", callback_data=f"send_infotext_button_{user_language}")
            elif i == 7:
                btn = InlineKeyboardButton(text=f"{btn_text}", url="https://t.me/c/1131408173/527")
            elif i == 8:
                btn = InlineKeyboardButton(text=f"{btn_text}", url="https://t.me/aerosoftreviews")
            elif i == 9:
                btn = InlineKeyboardButton(text=f"{btn_text}", callback_data=f"send_infotext_button4_{user_language}")
            elif i == 6:
                btn = InlineKeyboardButton(text=f"{btn_text}", url="https://t.me/c/1131408173/518")
            elif i == 3:
                btn = InlineKeyboardButton(text=f"{btn_text}", url="https://t.me/c/1131408173/544")
            elif i == 2:
                btn = InlineKeyboardButton(text=f"{btn_text}", url="https://t.me/c/1131408173/518")
            elif i == 10:
                btn = InlineKeyboardButton(text=f"{btn_text}", url="https://t.me/c/1131408173/3")
            elif i == 11:
                btn = InlineKeyboardButton(text=f"{btn_text}", url="https://t.me/alexinmoney")
            else:
                btn = InlineKeyboardButton(text=f"{btn_text}", callback_data=f"custom_button_{i}")
    
            custom_buttons_markup.add(btn)

        await bot.send_message(user_id, caption, reply_markup=custom_buttons_markup)

@dp.callback_query_handler(lambda query: query.data.startswith('send_infotext_button4_'))
async def send_infotext_button_callback(query: types.CallbackQuery):
    user_language = query.data.split('_')[-1] 
    file_path = f"./lang_button/ten_button/{user_language}.txt"

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            message_text = file.read()

        # Создаем Inline кнопку "назад"
        back_button = InlineKeyboardButton("⬅️ Back to menu", callback_data=f"back_to_multilingual_message_{user_language}")

        # Создаем Inline клавиатуру с кнопкой "назад"
        keyboard = InlineKeyboardMarkup().add(back_button)

        await query.message.answer(message_text, reply_markup=keyboard)
    else:
        await query.message.answer("Message file not found.")

@dp.callback_query_handler(lambda query: query.data.startswith('send_infotext_button3_'))
async def send_infotext_button_callback(query: types.CallbackQuery):
    user_language = query.data.split('_')[-1] 
    file_path = f"./lang_button/six_button/{user_language}.txt"

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            message_text = file.read()

        # Создаем Inline кнопку "назад"
        back_button = InlineKeyboardButton("⬅️ Back to menu", callback_data=f"back_to_multilingual_message_{user_language}")

        # Создаем Inline клавиатуру с кнопкой "назад"
        keyboard = InlineKeyboardMarkup().add(back_button)

        await query.message.answer(message_text, reply_markup=keyboard)
    else:
        await query.message.answer("Message file not found.")


@dp.callback_query_handler(lambda query: query.data.startswith('send_infotext_button2_'))
async def send_infotext_button_callback(query: types.CallbackQuery):
    user_language = query.data.split('_')[-1] 
    file_path = f"./lang_button/five_button/{user_language}.txt"

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            message_text = file.read()

        # Создаем Inline кнопку "назад"
        back_button = InlineKeyboardButton("⬅️ Back to menu", callback_data=f"back_to_multilingual_message_{user_language}")

        # Создаем Inline клавиатуру с кнопкой "назад"
        keyboard = InlineKeyboardMarkup().add(back_button)

        await query.message.answer(message_text, reply_markup=keyboard)
    else:
        await query.message.answer("Message file not found.")



@dp.callback_query_handler(lambda query: query.data.startswith('send_infotext_button_'))
async def send_infotext_button_callback(query: types.CallbackQuery):
    user_language = query.data.split('_')[-1] 
    file_path = f"./lang_button/one_button/{user_language}.txt"

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            message_text = file.read()

        # Создаем Inline кнопку "назад"
        back_button = InlineKeyboardButton("⬅️ Back to menu", callback_data=f"back_to_multilingual_message_{user_language}")

        # Создаем Inline клавиатуру с кнопкой "назад"
        keyboard = InlineKeyboardMarkup().add(back_button)

        await query.message.answer(message_text, reply_markup=keyboard)
    else:
        await query.message.answer("Message file not found.")




@dp.callback_query_handler(lambda query: query.data.startswith("select_lang_"), state="*")
async def select_language_callback(callback_query: types.CallbackQuery):
    print("callback data: ")
    print(callback_query.data)
    user_id = callback_query.from_user.id
    selected_language = callback_query.data.split("_")[2]
    print("selected lang " + str(selected_language))

    try:
        # Update the user's language preference in the database
        cursor.execute("UPDATE users SET lang = ? WHERE id = ?", (selected_language, user_id))
        conn.commit()

        # Inform the user about the language selection
        await callback_query.answer(f"Вы выбрали язык: {selected_language}")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        await callback_query.answer("Произошла ошибка при обновлении языка в базе данных.")

    print(selected_language)
    if selected_language:
        selection_message = f"Вы выбрали язык: {selected_language}"
        await send_multilingual_message(callback_query.from_user.id, selected_language)
    else:
        selection_message = "Не удалось определить выбранный язык."

    # Inform the user about the language selection
    await callback_query.answer(selection_message)

    # Continue with any other logic or actions as needed

@dp.message_handler(commands=["admin"], state="*")
async def admin_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id != int(admin):
        return

    if user_id == int(admin):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        add = types.InlineKeyboardButton(text="➕ Добавить", callback_data="add_template")
        delete = types.InlineKeyboardButton(text="🗑 Удалить", callback_data="delete_template")
        mailing_button = types.InlineKeyboardButton(text="📧 Рассылка", callback_data="mailing")
        keyboard.add(add, delete, mailing_button)

    await message.answer("<b>🕵️‍♂️ Админ - панель</b>", reply_markup=keyboard)

async def get_username(user_id):
    user = await bot.get_chat(user_id)
    return user.username or user.first_name

@dp.message_handler(state=user.text)
async def send_mailing_text(message: types.Message, state: FSMContext):
    global text_for_malling
    print(message.text)
    text_for_malling = message.text
    print(text_for_malling)

    await message.answer("Прикрепите изображение для рассылки, или введите '-' для пропуска этого шага.")
    await user.next()
    current_state = await state.get_state()
    print(current_state)

@dp.message_handler(content_types=types.ContentType.PHOTO, state=user.image)
async def send_mailing_image(message: types.Message, state: FSMContext):
    photo_for_mailing = message.photo[-1].file_id

    data = await state.get_data()
    selected_role = data.get("selected_role")
    print(selected_role)

    if selected_role == "All":
        cursor.execute("SELECT id FROM users")
    elif selected_role == "Buy":
        cursor.execute("SELECT id FROM users WHERE role = ?", ("Buy Client",))
    elif selected_role == "Default":
        cursor.execute("SELECT id FROM users WHERE role = ?", ("Default",))
    elif selected_role == "Want":
        cursor.execute("SELECT id FROM users WHERE role = ?", ("Want Client",))

    users = [str(user[0]) for user in cursor.fetchall()]

    print("#1")
    print(text_for_malling)

    success_send = 0
    failed_send = 0

    for user_id in users:
        print(user_id)
        if text_for_malling and photo_for_mailing:
            try:
                print(user_id)
                await bot.send_photo(photo=photo_for_mailing, caption=text_for_malling, chat_id=user_id)
                success_send += 1
            except Exception as e:
                print(user_id)
                print(f"An error occurred while sending message to user {user_id}: {e}")
                failed_send += 1
        elif text_for_malling:
            try:
                await bot.send_message(text=text_for_malling, chat_id=user_id)
                success_send += 1
            except Exception as e:
                print(user_id)
                print(f"An error occurred while sending message to user {user_id}: {e}")
                failed_send += 1
        elif photo_for_mailing:
            try:
                await bot.send_photo(photo=photo_for_mailing, caption="", chat_id=user_id)
                success_send += 1
            except Exception as e:
                print(user_id)
                print(f"An error occurred while sending message to user {user_id}: {e}")
                failed_send += 1

    await message.answer("Рассылка завершена.\n\n✅ Удачно" + str(success_send) + "\n❌ Неудачно: " + str(failed_send))
    await state.finish()

@dp.message_handler(state=user.image)
async def send_mailing_image(message: types.Message, state: FSMContext):
    data = await state.get_data()
    selected_role = data.get("selected_role")
    print(selected_role)

    if selected_role == "All":
        cursor.execute("SELECT id FROM users")
    elif selected_role == "Buy":
        cursor.execute("SELECT id FROM users WHERE role = ?", ("Buy Client",))
    elif selected_role == "Default":
        cursor.execute("SELECT id FROM users WHERE role = ?", ("Default",))
    elif selected_role == "Want":
        cursor.execute("SELECT id FROM users WHERE role = ?", ("Want Client",))

    users = [str(user[0]) for user in cursor.fetchall()]

    success_send = 0
    failed_send = 0

    for user_id in users:
        print(user_id)
        if text_for_malling and photo_for_mailing:
            try:
                print(user_id)
                await bot.send_photo(photo=photo_for_mailing, caption=text_for_malling, chat_id=user_id)
                success_send += 1
            except Exception as e:
                print(user_id)
                print(f"An error occurred while sending message to user {user_id}: {e}")
                failed_send += 1
        elif text_for_malling:
            try:
                await bot.send_message(text=text_for_malling, chat_id=user_id)
                success_send += 1
            except Exception as e:
                print(user_id)
                print(f"An error occurred while sending message to user {user_id}: {e}")
                failed_send += 1
        elif photo_for_mailing:
            try:
                await bot.send_photo(photo=photo_for_mailing, caption="", chat_id=user_id)
                success_send += 1
            except Exception as e:
                print(user_id)
                print(f"An error occurred while sending message to user {user_id}: {e}")
                failed_send += 1

    await message.answer("Рассылка завершена.\n\n✅ Удачно: " + str(success_send) + "\n\n❌ Неудачно: " + str(failed_send))
    await state.finish()

async def on_startup(dispatcher):
    create_db()
    
if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)