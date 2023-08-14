from sqlalchemy import create_engine, Column, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Создаем базу данных SQLite в памяти
# Создаем базу данных SQLite в файле profit_data.db
engine = create_engine('sqlite:///profit_data.db', echo=True)


# Создаем базовый класс моделей
Base = declarative_base(bind=engine)

# Определяем модель данных
class Profit(Base):
    __tablename__ = 'profit'

    id = Column(Integer, primary_key=True)
    revenue = Column(Float)
    logistic_expenses = Column(Float)
     other_expenses = Column(Float)

# Создаем таблицу в базе данных
Base.metadata.create_all()

# Создаем сессию для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()


def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start."""
    update.message.reply_text('Я бот для подсчета чистой прибыли. Пожалуйста, отправь мне данные.')


def calculate_profit(update: Update, context: CallbackContext) -> None:
    """Обработчик для расчета чистой прибыли."""
    # Получаем данные от пользователя
    try:
        revenue, logistic_expenses, product_expenses, other_expenses = map(float, context.args)
    except (ValueError, TypeError):
        update.message.reply_text('Ошибка ввода данных. Пожалуйста, введите данные в виде чисел.')
        return

    # Вычисляем чистую прибыль
    net_profit = revenue - logistic_expenses - product_expenses - other_expenses

    # Сохраняем данные в базу данных
    profit = Profit(
        revenue=revenue,
        logistic_expenses=logistic_expenses,
        product_expenses=product_expenses,
        other_expenses=other_expenses
    )
    session.add(profit)
    session.commit()

    update.message.reply_text(f'Чистая прибыль: {net_profit}')


def show_profit(update: Update, context: CallbackContext) -> None:
    """Обработчик для отображения итоговой чистой прибыли."""
    total_profit = session.query(Profit).with_entities(Profit.revenue - Profit.logistic_expenses - Profit.product_expenses - Profit.other_expenses).scalar()

    update.message.reply_text(f'Итоговая чистая прибыль: {total_profit}')


def main() -> None:
    """Основная функция для запуска бота."""
    updater = Updater("6131023828:AAGB6CCOgOyeLoFyR8coRtbmJ7itVaKSWag", use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("calculate_profit", calculate_profit))
    dispatcher.add_handler(CommandHandler("show_profit", show_profit))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
