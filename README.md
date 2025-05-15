# Car Insurance Telegram Bot Documentation

This bot allows users to submit their passport and car document photos, extracts the information (simulated), and offers a car insurance policy. It uses the OpenAI API to provide conversational responses.

## Features

- Accepts passport and car document photos.
- Simulates data extraction (no real OCR).
- Confirms extracted data with the user.
- Offers a fixed-price policy (100 USD).
- Generates and sends a simple policy text to the user.

## Requirements

- Python 3.10+ (3.13 is used in the project)
- Telegram Bot Token
- OpenAI API Key
- python-telegram-bot==20.7
- openai==1.23.2
- reportlab==4.0.8

 ## Setup Instructions

 - Make sure Python 3.10+ is installed
 - Download bot.py file
 - Install required dependencies by running "pip install..." (requirements.txt)
 - Create your BOT Telegram Token, OpenAI Secret API Key and insert it into the bot.py as values of TELEGRAM_BOT_TOKEN and OPENAI_API_KEY Values.
 - Run: python bot.py

### Example Interaction

**User**: /start  
**Bot**: Hello! Please send a photo of your *passport* 
**User**:kjdfkdjfkdjfdkjfdf dfjfkdjfkdjfdkjfkjd; ''''''
**Bot**: Please, send a photo, not text.
**User**: [sends photo]  
**Bot**: Passport received. Now send your *car document* photo  
**User**: [sends photo] 
**Bot**:  
 Here is the extracted data:  
- Full Name: John Doe  
- Passport Number: X1234567  
- Car: Toyota Camry  
- VIN: 123ABC456XYZ  
Is this correct? (yes/no)

**User**: yes  
**Bot**: Great! The price for insurance is 100 USD. Do you agree? (yes/no)  
**User**: yes  
**Bot**: Generating insurance policy...  
 Your Insurance Policy:  
... (details) ...
