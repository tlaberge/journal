from passlib.apps import custom_app_context as password_context
from argparse import ArgumentParser
import json
import logging


class User(object):
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    def verify_password(self, password):
        if password_context.verify(password, self.password_hash):
            return True

        return False

    def to_json(self):
        return {'user': self.username, 'password_hash': self.password_hash}

    @staticmethod
    def user_from_json(user_json):
        return User(user_json['user'], user_json['password_hash'])

    @staticmethod
    def users_from_password_file(password_file_name):
        try:
            with open(password_file_name, 'r') as password_file:
                users_json = json.load(password_file)
                users = dict()
                for username, password_hash in users_json.items():
                    user = User(username, password_hash)
                    users[user.username] = user
                return users
        except FileNotFoundError:
            return dict()

    @staticmethod
    def users_to_password_file(users, password_file_name):
        users_json = dict()
        for user in users.values():
            users_json[user.username] = user.password_hash
        with open(password_file_name, 'w') as password_file:
            json.dump(users_json, password_file)


def main():
    parser = ArgumentParser()
    parser.add_argument('--username', '-u', action='store', help='Username')
    parser.add_argument('--password', '-p', action='store', help='password')
    parser.add_argument('--password-file', '-f', action='store', default='.passwords', help='password file')
    parser.add_argument('--verify', '-v', action='store_true', default=False, help="Verify username and password")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    username = args.username
    password = args.password
    password_file = args.password_file

    users = User.users_from_password_file(args.password_file)
    if args.verify:
        if username not in users:
            logging.error("User {} not in password database".format(username))
            exit(1)
        verified = users[username].verify_password(password)
        if verified:
            logging.info("Password verified")
            exit(0)

        logging.error("Password verification failed")
        exit(1)

    user = User(username, password_context.encrypt(password))
    users[username] = user

    User.users_to_password_file(users, password_file)


if __name__ == '__main__':
    main()
