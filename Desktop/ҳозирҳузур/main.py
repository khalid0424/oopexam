import telebot
import psycopg2
from psycopg2 import sql
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from secret import *
from telebot import TeleBot
a

bot = telebot.TeleBot(API_TOKEN)

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id BIGINT PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        class_name VARCHAR(50) NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id SERIAL PRIMARY KEY,
        student_id BIGINT REFERENCES students(id),
        date DATE NOT NULL,
        status VARCHAR(50) NOT NULL
    );
    """)

    conn.commit()
    cur.close()
    conn.close()

def register_student(user_id, full_name, class_name):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM students WHERE id = %s", (user_id,))
    student = cur.fetchone()

    if not student:
        cur.execute(
            "INSERT INTO students (id, full_name, class_name) VALUES (%s, %s, %s)",
            (user_id, full_name, class_name)
        )
        conn.commit()

    cur.close()
    conn.close()

def mark_attendance(user_id, status):
    conn = get_db_connection()
    cur = conn.cursor()

    today = datetime.now().date()
    cur.execute(
        "INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s)",
        (user_id, today, status)
    )
    conn.commit()

    cur.close()
    conn.close()

def check_attendance(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    today = datetime.now().date()
    cur.execute("SELECT * FROM attendance WHERE student_id = %s AND date = %s", (user_id, today))
    attendance = cur.fetchone()

    cur.close()
    conn.close()
    return attendance

def show_main_menu(chat_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("Ман ба дарс омадам", callback_data='present'),
        InlineKeyboardButton("Ман наметавонам биёям", callback_data='absent')
    )
    bot.send_message(chat_id, "Лутфан интихоб кунед:", reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name

    msg = bot.send_message(message.chat.id, "Лутфан синф ва номи худро ворид кунед (мисол: 10А - Али Иброҳим):")
    bot.register_next_step_handler(msg, process_registration, user_id)

def process_registration(message, user_id):
    try:
        class_name, full_name = message.text.split(" - ")
        register_student(user_id, full_name, class_name)
        bot.send_message(message.chat.id, f"Хуш омадед {full_name} аз синфи {class_name}!")
        show_main_menu(message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, "Лутфан маълумоти дурустро дар формати 'синф - ном' ворид кунед.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    
    if check_attendance(user_id):
        bot.send_message(call.message.chat.id, "Шумо аллакай ҳузури худро сабт кардаед.")
        return

    if call.data == 'present':
        mark_attendance(user_id, 'present')
        bot.send_message(call.message.chat.id, "Ҳузури шумо сабт шуд. Ташаккур!")
    
    elif call.data == 'absent':
        mark_attendance(user_id, 'absent')
        bot.send_message(call.message.chat.id, "Ғайри ҳузурии шумо сабт шуд. Умедворам, ки дарсҳоро надиред!")
    
    show_main_menu(call.message.chat.id)

@bot.message_handler(commands=['report'])
def attendance_report(message):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT students.full_name, students.class_name, attendance.date, attendance.status FROM attendance JOIN students ON attendance.student_id = students.id")
    records = cur.fetchall()

    if records:
        response = "\n".join([f"{rec[0]} (синф {rec[1]}), сана {rec[2]} - {rec[3]}" for rec in records])
    else:
        response = "Маълумоти ҳузурӣ вуҷуд надорад."

    bot.send_message(message.chat.id, response)
    cur.close()
    conn.close()

create_tables()
bot.polling()
