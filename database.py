""" Required Imports """
import pymongo
import bcrypt


class DBManager():
    def __init__(self):
        self._mongo_uri = "Your Mongo URI Here"
        self._client = pymongo.MongoClient(self._mongo_uri)
        self._db = self._client["users"]
        self._collection = self._db["credentials"]

    def is_present(self, username):
        """ Checks whether user is already present in DB """
        user = self._collection.find_one({"admin_id": username})
        return user

    def add_user(self, username, password, email):
        """ Adds a new user to the DB. If user already exists
        then no changes are made """
        if not self.is_present(username):
            hashed_pass = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            self._collection.insert_one({"admin_id": username,
                                         "password": hashed_pass,
                                         "email": email})

    def validate_user(self, username, password):
        """ Checks whether the login credentials are valid """
        user_record = self.is_present(username)
        return user_record["admin_id"] == username and \
            bcrypt.checkpw(password.encode(), user_record["password"])