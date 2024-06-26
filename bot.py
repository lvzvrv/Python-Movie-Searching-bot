from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import requests

TOKEN = '7396006417:AAG0FXPqn_GaeX5S7S1xdehN2XzW7knTGAY'

API_KEY = '7194c3a4fa6c11fc9ec271c5b5b2a729'

DATABASE_URL = "postgresql://postgres:BratkaIlya2015@localhost/mydatabase"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    registration_date = Column(DateTime, default=datetime.datetime.utcnow)

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

# Включение логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def search_person(name):
    url = f'https://api.themoviedb.org/3/search/person'
    params = {
        'api_key': API_KEY,
        'query': name
    }
    response = requests.get(url, params=params)
    results = response.json().get('results', [])
    if results:
        return results[0]  # Возвращаем первого найденного человека
    return None

def get_movies(person_id):
    url = f'https://api.themoviedb.org/3/person/{person_id}/movie_credits'
    params = {
        'api_key': API_KEY
    }
    response = requests.get(url, params=params)
    return response.json().get('cast', [])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('''Hello! 
                        Use /register to register yourself. 
                        Or /help to see list of commands''')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('''Hi. There is list of commands:
                                    
    /register - for registration
    /delete_user - for delete yourself from bot users database
    /search_movies - for searching all movies by actor or director''')

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    session = SessionLocal()
    try:
        existing_user = session.query(User).filter(User.username == user.username).first()
        if (existing_user):
            await update.message.reply_text('You are already registered.')
        else:
            new_user = User(username=user.username, first_name=user.first_name, last_name=user.last_name)
            session.add(new_user)
            session.commit()
            await update.message.reply_text('You have been registered!')
    except Exception as e:
        logging.error(f"Error registering user: {e}")
        session.rollback()
        await update.message.reply_text('There was an error during registration.')
    finally:
        session.close()

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()
    try:
        users = session.query(User).all()
        if users:
            user_list = "\n".join([f"{user.username} - {user.first_name} {user.last_name}" for user in users])
            await update.message.reply_text(f"Registered users:\n{user_list}")
        else:
            await update.message.reply_text('No registered users.')
    except Exception as e:
        logging.error(f"Error listing users: {e}")
        await update.message.reply_text('There was an error retrieving the user list.')
    finally:
        session.close()

async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    session = SessionLocal()
    try:
        user_to_delete = session.query(User).filter(User.username == user.username).first()
        if user_to_delete:
            session.delete(user_to_delete)
            session.commit()
            await update.message.reply_text('You have been deleted from the database.')
        else:
            await update.message.reply_text('You are not registered.')
    except Exception as e:
        logging.error(f"Error deleting user: {e}")
        session.rollback()
        await update.message.reply_text('There was an error deleting your registration.')
    finally:
        session.close()

async def search_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text('Please provide the name of the actor or director. Usage: /search_movies <name>')
        return

    name = " ".join(context.args)
    person = search_person(name)
    if person:
        movies = get_movies(person['id'])
        if movies:
            movie_list = "\n".join([f"{movie['title']} ({movie['release_date']})" for movie in movies])
            await update.message.reply_text(f"Movies with {person['name']}:\n{movie_list}")
        else:
            await update.message.reply_text(f"No movies found for {person['name']}.")
    else:
        await update.message.reply_text(f"No person found with the name {name}.")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("list_users", list_users))
    application.add_handler(CommandHandler("delete_user", delete_user))
    application.add_handler(CommandHandler("search_movies", search_movies)) 

    application.run_polling()

if __name__ == '__main__':
    main()
