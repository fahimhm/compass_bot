import os

# ENV = "DEV"
ENV = "PROD"

# # keys
if ENV == "DEV":
    import constant as keys
    telegram_key = keys.API_KEY
    mongodb_key = keys.MONGO_KEY
elif ENV == "PROD":
    import ast
    telegram_key = ast.literal_eval(os.environ["telegram_key"])
    mongodb_key = ast.literal_eval(os.environ["mongodb_key"])

# # server
host = "0.0.0.0"
port = int(os.environ.get("PORT", '8443'))