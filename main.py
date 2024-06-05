import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import yfinance as yf
import telebot
from decouple import config
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

#######################

def load_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    return data

def engineer_features(data):
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['SMA_200'] = data['Close'].rolling(window=200).mean()
    
    data['Price_Momentum'] = data['Close'].pct_change(1)
    
    return data.dropna()

def train_model(X_train, y_train):
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    return mse

def predict_price(model, latest_data):
    return model.predict(latest_data)[0]

def make_trading_decision(predicted_price, current_price):
    if predicted_price > current_price:
        return "Recommendation: Buy"
    else:
        return "Recommendation: Sell"


@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(message.chat.id, "welcom to Parker Bot")


@bot.message_handler(commands=['help'])
def help_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            'Message the developer', url='telegram.me/mrparker1'
        )
    )
    bot.send_message(
        message.chat.id,
        '1) To receive a list of available currencies press /exchange.\n' +
        '2) Click on the currency you are interested in.\n' +
        '3) You will receive a message containing information regarding the source and the target currencies, ' +
        'buying rates and selling rates.\n' +
        '4) Click “Update” to receive the current information regarding the request. ' +
        'The bot will also show the difference between the previous and the current exchange rates.\n' +
        '5) The bot supports inline. Type @<botusername> in any chat and the first letters of a currency.',
        reply_markup=keyboard
    )


@bot.message_handler(commands=['test'])
def test_tretement(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            'Message the developer', url='telegram.me/mrparker1'
        )
    )


    bot.send_message(
        message.chat.id,
        'test your coins',
        reply_markup=keyboard
    )


@bot.message_handler(commands=['predict'])
def send_prediction(message):
    symbol = 'AAPL'  
    start_date = '2023-06-01'
    end_date = '2024-06-01'
    
    data = load_data(symbol, start_date, end_date)
    
    data = engineer_features(data)
    
    X = data.drop(['Close'], axis=1)
    y = data['Close']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = train_model(X_train, y_train)
    
    latest_data = X.iloc[-1].values.reshape(1, -1)
    predicted_price = predict_price(model, latest_data)
    
    current_price = data['Close'].iloc[-1]
    decision = make_trading_decision(predicted_price, current_price)
    
    bot.reply_to(message, f"Predicted Price: {predicted_price}\n{decision}")




bot.polling()
