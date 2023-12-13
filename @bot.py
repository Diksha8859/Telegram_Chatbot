import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext

# Replace 'YOUR_TOKEN' with the token you obtained from BotFather
TOKEN = '6443623453:AAGgFl6aRvvE8q__FVevJYBBF-GvZJs0vbI'

# SQLite database file
DB_FILE = 'database.db'

# Create a connection to the SQLite database
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create a table for storing questions and answers
cursor.execute('''
    CREATE TABLE IF NOT EXISTS college_qa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT
    )
''')
conn.commit()

# Function to handle the "/start" command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your College Admission Bot. Ask me anything about college admissions.')

# Function to handle regular messages
def handle_messages(update: Update, context: CallbackContext) -> None:
    message = update.message.text.lower().strip()

    # Create a new SQLite connection and cursor
    conn_handle_messages = sqlite3.connect(DB_FILE)
    cursor_handle_messages = conn_handle_messages.cursor()

    try:
        # Query the database for an answer
        cursor_handle_messages.execute('SELECT answer FROM college_qa WHERE question LIKE ?', ('%' + message + '%',))
        result = cursor_handle_messages.fetchone()

        # Send the answer if found, or a default message if not found
        if result:
            update.message.reply_text(result[0])
        else:
            update.message.reply_text('I am sorry, but I do not have an answer to that question.')
    except sqlite3.Error as e:
        update.message.reply_text(f'Error querying database: {e}')
    finally:
        # Close the connection
        conn_handle_messages.close()


# Function to handle the "/addqa" command for adding new Q&A pairs to the database
def add_qa(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) < 2:
        update.message.reply_text('Usage: /addqa <question> <answer>')
        return

    question = ' '.join(args[:-1])
    # Join all remaining arguments as a single string for the answer
    answer = ' '.join(args[-1:])

    # Create a new SQLite connection and cursor
    conn_add_qa = sqlite3.connect(DB_FILE)
    cursor_add_qa = conn_add_qa.cursor()

    try:
        # Insert the new Q&A pair into the database
        cursor_add_qa.execute('INSERT INTO college_qa (question, answer) VALUES (?, ?)', (question, answer))
        conn_add_qa.commit()
        update.message.reply_text('Q&A pair added successfully!')
    except sqlite3.Error as e:
        update.message.reply_text(f'Error adding Q&A pair: {e}')
    finally:
        # Close the connection
        conn_add_qa.close()



# Function to handle errors
def error(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    context.error('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("addqa", add_qa, pass_args=True))

    # Message handler
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_messages))

    # Log errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
