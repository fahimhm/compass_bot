import os

# ENV = "DEV"
ENV = "PROD"

# # keys
if ENV == "DEV":
    import constant as keys
    telegram_key = keys.API_KEY
    mongodb_key = keys.MONGO_KEY
elif ENV == "PROD":
    # import ast
    from boto.s3.connection import S3Connection
    telegram_key = S3Connection(os.environ["telegram_key"])
    mongodb_key = S3Connection(os.environ["mongodb_key"])

# # server
host = "0.0.0.0"
port = int(os.environ.get("PORT", 5000))