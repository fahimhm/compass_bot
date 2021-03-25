import os

# ENV = "DEV"
ENV = "PROD"

# # keys
if ENV == "DEV":
    from script import constant as keys
    telegram_key = keys.API_KEY
    mongodb_key = keys.MONGO_KEY
elif ENV == "PROD":
    telegram_key = os.environ["telegram_key"]
    mongodb_key = os.environ["mongodb_key"]

# # server
host = "0.0.0.0"
port = int(os.environ.get("PORT", '8443'))