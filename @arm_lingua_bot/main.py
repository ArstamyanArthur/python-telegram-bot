import json
import tracemalloc
from uuid import uuid4

from model import claude
from typing import Final
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, \
    filters, ContextTypes, InlineQueryHandler, ConversationHandler
import os
import logging
from dotenv import load_dotenv
load_dotenv()

langs = {}
user_messages = {}
sent_messages = {}

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

key = 'token_key'
for i in range(int(os.getenv('n'))-1):
    key = os.getenv(key)

Token: Final = os.getenv(key)
BOT_USERNAME: Final = '@arm_lingua_bot'

#               Using KeyboardButtons instead of Inlinekeyboard buttons
finish = ReplyKeyboardMarkup([['Ավարտել']])  # one_time_keyboard=True
help_keyboard_1 = InlineKeyboardMarkup([[InlineKeyboardButton('<', callback_data='1000'), InlineKeyboardButton('1/2', callback_data='1000'), InlineKeyboardButton('>', callback_data='200')]])
help_keyboard_2 = InlineKeyboardMarkup([[InlineKeyboardButton('<', callback_data='100'), InlineKeyboardButton('2/2', callback_data='1000'), InlineKeyboardButton('>', callback_data='1000')]])
geometry_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Երկիր մոլորակ', callback_data='Երկիր մոլորակ')],
                                          [InlineKeyboardButton('Թեստեր', callback_data='Թեստեր')]])
earth_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Մայրցամաքներ', callback_data='Մայրցամաքներ')],
                                       [InlineKeyboardButton('Օվկիանոսներ', callback_data='Օվկիանոսներ')],
                                       [InlineKeyboardButton('Պետություններ', callback_data='Պետություններ')],
                                       [InlineKeyboardButton('Հետ գնալ', callback_data='geometry')]])

tests_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Թեստ 1', callback_data='Թեստ 1')],
                                       [InlineKeyboardButton('Թեստ 2', callback_data='Թեստ 2')],
                                       [InlineKeyboardButton('Թեստ 3', callback_data='Թեստ 3')],
                                       [InlineKeyboardButton('Հետ գնալ', callback_data='geometry')]])

continents_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Հյս Ամերիկա', callback_data='Հյս Ամերիկա'), InlineKeyboardButton('Եվրասիա', callback_data='Եվրասիա')],
                                            [InlineKeyboardButton('Հրվ Ամերիկա', callback_data='Հրվ Ամերիկա'), InlineKeyboardButton('Աֆրիկա', callback_data='Աֆրիկա'), InlineKeyboardButton('Ավստրալիա', callback_data='Ավստրալիա')],
                                            [InlineKeyboardButton('Անտարկտիդա', callback_data='Անտարկտիդա')],
                                            [InlineKeyboardButton('Հետ գնալ', callback_data='Երկիր մոլորակ')]])

oceans_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Հյուսիսային Սառուցյալ', callback_data='Սառուցյալ')],
                                        [InlineKeyboardButton('Խաղաղ', callback_data='Խաղաղ'), InlineKeyboardButton('Ատլանտյան', callback_data='Ատլանտյան'), InlineKeyboardButton('Հնդկական', callback_data='Հնդկական')],
                                        [InlineKeyboardButton('Հարավային (Անտարկտիկական)', callback_data='Անտարկտիկական')],
                                        [InlineKeyboardButton('Հետ գնալ', callback_data='Երկիր մոլորակ')]])

countries_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Վիքիպեդիա', url='https://hy.m.wikipedia.org/wiki/%D5%8A%D5%A5%D5%BF%D5%B8%D6%82%D5%A9%D5%B5%D5%B8%D6%82%D5%B6',
                                                                 callback_data='Վիքիպեդիա')],
                                           [InlineKeyboardButton('Հետ գնալ', callback_data='Երկիր մոլորակ')]])

# commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Ուղղել տեքստը"],
        [KeyboardButton("Թարգմանել հայերենից")],
        [KeyboardButton("Թարգմանել հայերեն")]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, input_field_placeholder='Ընտրեք')
    await update.message.reply_text('Բարև ձեզ, ընտրեք ներքևում բերված տարբերակներից մեկը', reply_markup=reply_markup)

async def geometry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sent_messages[update.message.chat.id] = []
    await update.message.reply_photo(photo='ss.PNG',
                                     caption='Աշխարհը գեղեցիկ է իր բազմազանությամբ։',
                                     reply_markup=geometry_keyboard)

async def geometry_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.delete_message()
    await context.bot.send_photo(chat_id=query.message.chat.id, photo='ss.PNG',
                                 caption='Աշխարհը գեղեցիկ է իր բազմազանությամբ։',
                                 reply_markup=geometry_keyboard)

async def geometry_queries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    for message_id in sent_messages[query.from_user.id]:
        await context.bot.delete_message(chat_id=query.message.chat.id, message_id=message_id)
    sent_messages[query.from_user.id] = []
    await query.delete_message() # below code does the same
    # await context.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    if query.data == 'Թեստեր':
        await context.bot.send_photo(chat_id=query.message.chat.id, photo='test_2.JPG',
                                     caption='Փորձիր գիտելիքներդ և համեմատիր արդյունքներդ մյուս մասնակիցների արդյունքների հետ։',
                                     reply_markup=tests_keyboard)
    else:
        await context.bot.send_photo(chat_id=query.message.chat.id, photo='earth.jpg',
                                     caption='[Երկիրը](https://hy.wikipedia.org/wiki/%D4%B5%D6%80%D5%AF%D5%AB%D6%80) 3-րդ մոլորակն է Արեգակից և միակ հայտնին, որտեղ կա կյանք։',
                                     parse_mode='Markdown',
                                     reply_markup=earth_keyboard)

async def earth_queries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.delete_message()
    if query.data == 'Մայրցամաքներ':
        await context.bot.send_photo(chat_id=query.message.chat.id, photo='continents.jpg',
                                     caption='Երկիր մոլորակի վրա կան 6 մայրցամաքներ՝ Հյուսիսային Ամերիկա, Հարավային Ամերիկա, Եվրասիա, Աֆրիկա, Ավստրալիա, Անտարկտիդա։',
                                     reply_markup=continents_keyboard)
    elif query.data == 'Օվկիանոսներ':   # below instead of ocean_1 its url is used
        photos = [InputMediaPhoto('https://earthhow.com/wp-content/uploads/2017/11/5-oceans-675x429.png', caption='1'), InputMediaPhoto(open('ocean_2.PNG', 'rb'), caption='2'),
                  InputMediaPhoto(open('ocean_3.jpg', 'rb'), caption='3'), InputMediaPhoto(open('ocean_4.jpg', 'rb'), caption='4')]
        sent_messages_list = await context.bot.send_media_group(chat_id=query.message.chat.id, media=photos)
        for message in sent_messages_list:
            sent_messages[query.from_user.id].append(message.message_id)
        await context.bot.send_message(chat_id=query.message.chat.id,
                                       text='Պատմականորեն կան չորս անվանված օվկիանոսներ՝ Ատլանտյան, Խաղաղ, Հնդկական և Հյուսիսային Սառուցյալ: Այնուամենայնիվ, երկրների մեծ մասը՝ ներառյալ Միացյալ Նահանգները, այժմ ճանաչում են Հարավային (Անտարկտիկական) օվկիանոսը որպես հինգերորդ օվկիանոս:',
                                       reply_markup=oceans_keyboard)
    else:
        await context.bot.send_photo(chat_id=query.message.chat.id, photo='countries.PNG',
                                     caption='Աշխարհի սխեմատիկ քարտեզ. պետություններն ըստ տարածքի մեծության։',
                                     reply_markup=countries_keyboard)



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(photo='IMG_5236.PNG',
    caption='Ներքևի կոճակների անհետանալու դեպքում սեղմեք կարմիրով նշված պատկերի վրա և նրանք նորից կհայտնվեն։',
    reply_markup=help_keyboard_1)

async def help_query_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.delete_message()
    await context.bot.send_photo(chat_id=query.message.chat.id,
                                 photo='IMG_5237.PNG',
                                 caption='Աշխատանքը վերսկսելու համար նախ ավարտել ընթացիկ աշխատանքը՝ սեղմելով /end հրամանը, և սկսել նոր աշխատանք /start հրամանի միջոցով։\nՀրամանները կարող եք գտնել Menu կոճակի օգնությամբ։',
                                 reply_markup=help_keyboard_2)

async def help_query_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.delete_message()
    await context.bot.send_photo(chat_id=query.message.chat.id,
                                 photo='IMG_5236.PNG',
                                 caption='Ներքևի կոճակների անհետանալու դեպքում սեղմեք կարմիրով նշված պատկերի վրա և նրանք նորից կհայտնվեն։',
                                 reply_markup=help_keyboard_1)

async def help_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer('Սխալ կոճակ եք սեղմում')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == 'Ուղղել տեքստը':
        await update.message.reply_text('Ուղարկեք տեքստը', reply_markup=finish)
        return 0
    elif text == 'Թարգմանել հայերենից':
        keyboard = [
            [KeyboardButton("Անգլերեն"), KeyboardButton('Ռուսերեն')],
            [KeyboardButton("Չինարեն"), KeyboardButton("Հնդկերեն")],
            [KeyboardButton("Ֆրանսերեն"), KeyboardButton("Գերմաներեն")],
            [KeyboardButton("Իտալերեն"), KeyboardButton("Այլ")],
            ['Ավարտել']
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, input_field_placeholder='Ընտրեք լեզուն')
        await update.message.reply_text(text='Ընտրեք լեզուն', reply_markup=reply_markup)
        return 1
    await update.message.reply_text('Ուղարկեք տեքստը', reply_markup=finish)
    return 2

async def correct_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    reply_text = claude(text)
    print(f'User: {update.message.chat.first_name} {update.message.chat.last_name}\nUsername: @{update.message.chat.username}\nid: {update.message.chat.id}\nMessage_type:  {update.message.chat.type}\nInput: "{text}"')
    print('Reply_text: ', reply_text)
    await update.message.reply_text(reply_text, reply_markup=finish)
    return 0

async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    langs[update.message.chat.username] = text
    await update.message.reply_text('Ուղարկեք տեքստը', reply_markup=finish)
    return 12

async def custom_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Գրեք ձեր նախընտրած լեզուն', reply_markup=finish)
    return 11

async def trans_from(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    langs[update.message.chat.username] = text
    await update.message.reply_text(claude(text, lang=langs[update.message.chat.username]), reply_markup=finish)
    return 12

async def trans_into(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(claude(text, True), reply_markup=finish)
    return 2

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

# handling inline queries
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    print(query)
    if not query:  # empty query should not be handled
        return
    # response = punctuate(query)
    # results = [
    #     InlineQueryResultArticle(
    #         id=str(uuid4()),
    #         title="Կետադրված տարբերակը",
    #         input_message_content=InputTextMessageContent(response),
    #         description=response
    #     )]
    # await update.inline_query.answer(results)

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    await update.message.reply_text("Շնորհակալություն \nԱշխատանքը վերսկսելու համար \nսեղմեք /start հրամանը։", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# App
if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(Token).build()
    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('geometry', geometry_command))
    app.add_handler(CommandHandler('help', help_command))
    # Inline queries
    app.add_handler(InlineQueryHandler(inline_query))
    # Error
    app.add_error_handler(error)
    # CallbackQueryHandlers
        #geometry
    app.add_handler(CallbackQueryHandler(geometry_restart, pattern='^geometry$'))
    app.add_handler(CallbackQueryHandler(geometry_queries, pattern='^(Երկիր մոլորակ|Թեստեր)$'))
    app.add_handler(CallbackQueryHandler(earth_queries, pattern='^(Մայրցամաքներ|Օվկիանոսներ|Պետություններ)$'))
        #help
    app.add_handler(CallbackQueryHandler(help_query_1, pattern='^200$'))
    app.add_handler(CallbackQueryHandler(help_query_2, pattern='^100$'))
    app.add_handler(CallbackQueryHandler(help_error, pattern='^1000$'))
    #conv_handlers
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(Ուղղել տեքստը|Թարգմանել հայերենից|Թարգմանել հայերեն)$"), button_handler)],
        states={
            0: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Ավարտել$")), correct_text)],
            1: [MessageHandler(filters.Regex("^(Անգլերեն|Ռուսերեն|Չինարեն|Հնդկերեն|Ֆրանսերեն|Գերմաներեն|Իտալերեն)$"), regular_choice),
                MessageHandler(filters.Regex("^Այլ$"), custom_choice)],
            11: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Ավարտել$")), regular_choice)],
            12: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Ավարտել$")), trans_from)],
            2: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Ավարտել$")), trans_into)]
        },
        fallbacks=[MessageHandler(filters.Regex("^Ավարտել$"), done), CommandHandler('end', done)],
        # per_message=True,
        conversation_timeout=5
    )
    app.add_handler(conv_handler)
    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)

# Trying to do all buttons inline with conversation handler
'''
# commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Ուղղել տեքստը", callback_data="1")],
        [InlineKeyboardButton("Թարգմանել հայերենից", callback_data="2")],
        [InlineKeyboardButton("Թարգմանել հայերեն", callback_data="3")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Բարև ձեզ, ընտրեք ներքևում բերված տարբերակներից մեկը', reply_markup = reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Տեքստն ուղարկեք առանց որևէ հավելյալ գրառման։ Նախադասությունները պետք է վերջակետով '
                                    'առանձնացված լինեն։')

async def correct_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text='Ուղարկեք տեքստը։')
    return 0

async def correct_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('shit')
    text = update.message.text
    print(update)
    print(f'User: {update.message.chat.first_name} {update.message.chat.last_name}\nUsername: @{update.message.chat.username}\nid: {update.message.chat.id}\nMessage_type:  {message_type}\nInput: "{text}"')
    await update.message.reply_text(correct(text))

async def trans_from(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("Անգլերեն", callback_data="10"), InlineKeyboardButton("Ռուսերեն", callback_data="11")],
        [InlineKeyboardButton("Չինարեն", callback_data="12"), InlineKeyboardButton("Հնդկերեն", callback_data="13")],
        [InlineKeyboardButton("Ֆրանսերեն", callback_data="14"), InlineKeyboardButton("Գերմաներեն", callback_data="15")],
        [InlineKeyboardButton("Գերմաներեն", callback_data="16"), InlineKeyboardButton("Այլ", callback_data="17")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text='Ընտրեք թարգմանության լեզուն', reply_markup=reply_markup)
    return 1

async def lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.edit_message_text(context)

async def type_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.edit_message_text(context)

async def trans_into(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.edit_message_text(text='Ուղարկեք տեքստը։')
    return 2

async def trans_into_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    storage.append(text)
    print(f'User: {update.message.chat.first_name} {update.message.chat.last_name}\nUsername: @{update.message.chat.username}\nid: {update.message.chat.id}\nMessage_type:  {message_type}\nInput: "{text}"')
    await update.message.reply_text(translate_into_arm(text))
    return -1

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# handling inline queries
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    print(query)
    if not query:  # empty query should not be handled
        return
    response = punctuate(query)
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Կետադրված տարբերակը",
            input_message_content=InputTextMessageContent(response),
            description=response
        )]
    await update.inline_query.answer(results)

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text("I learned these facts about you", reply_markup=ReplyKeyboardRemove())

    user_data.clear()
    return ConversationHandler.END

# App
if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(Token).build()
    print(app.job_queue)
    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    # Inline queries
    app.add_handler(InlineQueryHandler(inline_query))
    # Error
    app.add_error_handler(error)
    #conv_handlers
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(correct_text, pattern="^" + '1' + "$"), CallbackQueryHandler(trans_from, pattern="^" + '2' + "$"), CallbackQueryHandler(trans_into, pattern="^" + '3' + "$")],
        states={
            0: [MessageHandler(filters.TEXT, correct_reply)],
            1: [CallbackQueryHandler(lang, filters.Regex("^(10|11|12|13|14|15|16)$")), CallbackQueryHandler(type_lang, '^17$')],
            2: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), trans_into_reply)],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
        # per_message=True,
        conversation_timeout=5
    )
    app.add_handler(conv_handler)
    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)

'''

