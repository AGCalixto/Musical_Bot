import os
from Chords import search_chords_link, fetch_chords
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ChatAction
from pdf_creation import generate_song_pdf
from telegram import InputFile
from dotenv import load_dotenv
import re

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
BOT_USERNAME = '@Kingdddbot'


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Yoooo! It\'s so dope to have you here. I am DeDeDe Bot. ;)'
                                    '\nType: \'/Song Name of a song \' and I\'ll return the lyrics and the tabs for '
                                    'that song :D')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am King DeDeDe but bot. Type \'/Song\' and the name of any song and i\'ll '
                                    'return the letter and the tabs!')


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This needs to be edited')


async def Song_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text('Please use: `/song Your song name`', parse_mode='Markdown')
        return

    song_text = ' '.join(context.args)
    context.user_data['last_song'] = song_text
    context.user_data['iteration_count'] = 1
    await update.message.chat.send_action(action=ChatAction.TYPING)
    await update.message.reply_text(f'Searching the chords for \n🔥{song_text.capitalize()}🔥...')
    await update.message.reply_text(f'It may take a while... Please be patient...')

    try:
        chords, state = fetch_chords(search_chords_link(song_text), 0)
        file_path = generate_song_pdf(song_text, chords)
        safe_name = re.sub(r'[\\/*?:"<>|]', "", song_text.replace(" ", "_"))
        print(f'Generando PDF en: {file_path}')
        if os.path.exists(file_path):
            await update.message.reply_text('Chords Found!!!')
            with open(file_path, 'rb') as pdf_file:
                await update.message.reply_document(InputFile(pdf_file, filename=f'{safe_name}.pdf'))

            keyboard = [[InlineKeyboardButton('✅ Yes', callback_data='yes'),
                         InlineKeyboardButton('❌ No', callback_data='no')]]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text('Are you satisfied with the results?', reply_markup=reply_markup)
            return chords, reply_markup

        else:
            await update.message.reply_text('Lyrics were not generated :(\n'
                                            'Please try again...')
            return

    except Exception as e:
        print(f'Error in /song command: {e}')
        await update.message.reply_text(f"Something went wrong trying to fetch that song.\n\n {e}")
        return


def get_song_name(text):
    text = text.lower().strip()
    match = re.search(r"song[=: -]*([\w\s'\"-]+)", text, re.IGNORECASE)
    return match.group(1).strip() if match else None


# Responses
async def handle_responses(text, context, update):
    lower_text = text.lower()

    song_text = get_song_name(lower_text)
    if song_text:
        context.user_data['last_song'] = song_text
        context.user_data['iteration_count'] = 1

        try:
            chords, state = fetch_chords(search_chords_link(song_text), 0)
            file_path = generate_song_pdf(song_text, chords)
            safe_name = re.sub(r'[\\/*?:"<>|]', '', song_text.replace(' ', '_'))

            if os.path.exists(file_path):
                with open(file_path, 'rb') as pdf_file:
                    await update.message.reply_document(document=(InputFile(pdf_file, filename=f'{safe_name}.pdf')),
                                                        caption=f'Here are the chords for 🔥{song_text}🔥:')

                    keyboard = [[InlineKeyboardButton('✅ Yes', callback_data='yes'),
                                 InlineKeyboardButton('❌ No', callback_data='no')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    return "Are you satisfied with the results?", InlineKeyboardMarkup(keyboard)

            return "Couldn't generate the PDF. Please try again.", None
        except Exception as e:
            print(f'Error fetching results for the song... {e}')
            return "Something went wrong trying to fetch that song. \nPlease try again later.", None

    return ("Oops! I didn't understand that. 🤔\n"
            "To get song lyrics and tabs, type:\n"
            "`/Song Your song name here`"), None


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text

    print(f'User: {update.message.chat.id} in {message_type} = {text}')
    await update.message.chat.send_action(action=ChatAction.TYPING)

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, '').strip()
            await update.message.chat.send_action(action=ChatAction.TYPING)
            response, markup = handle_responses(new_text, context, update)
        else:
            return
    else:
        await update.message.chat.send_action(action=ChatAction.TYPING)
        response, markup = await handle_responses(text, context, update)

    print(f'Bot: {response}')
    if markup:
        await update.message.reply_text(response, reply_markup=markup)
    else:
        await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    song_text = context.user_data.get('last_song')

    if not song_text:
        await query.edit_message_text('I don\'t know which song you are referring to...')
        return

    if data == 'yes':
        await query.message.reply_text('Awesome! Glad you liked it 🎸')
        context.user_data['iteration_count'] = 0
        return

    # If data == 'no'
    iteration = context.user_data['iteration_count', 1]

    try:
        chords, state = fetch_chords(search_chords_link(song_text), iteration)
        file_path = generate_song_pdf(song_text, chords)
        safe_name = re.sub(r'[\\/*?:"<>|]', '', song_text.replace(' ', '_'))

        if os.path.exists(file_path):
            with open(file_path, 'rb') as pdf_file:
                await query.message.reply_document(InputFile(pdf_file, filename=f'{safe_name}_alt{iteration}.pdf'))

            keyboard = [[InlineKeyboardButton('✅ Yes', callback_data='yes'),
                         InlineKeyboardButton('❌ No', callback_data='no')]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.message.reply_text('Do you like this version?', reply_markup=reply_markup)
            context.user_data['iteration_count'] = iteration + 1
        else:
            await query.message.reply_text('No more versions found 😔')
            context.user_data['iteration_count'] = 0  # Reset the iterations

    except Exception as e:
        print(f'Error fetching alternative: {e}')
        await query.message.reply_text('No more available versions or an error occured')
        context.user_data['iteration_count'] = 0


if __name__ == '__main__':
    print(f'Program Starting...')
    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler('song', Song_command))
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the Bot
    print('Polling...')
    app.run_polling(poll_interval=1)
