from passlib.apps import custom_app_context as password_context
from argparse import ArgumentParser
import json
import logging


class User(object):
    def __init__(self, user_name, password_hash, display_name='', subject=''):
        self.user_name = user_name
        self.display_name = user_name
        if display_name:
            self.display_name = display_name
        self.subject = subject
        self.password_hash = password_hash

    def verify_password(self, password):
        if password_context.verify(password, self.password_hash):
            return True

        return False

    def to_json(self):
        return {'user': self.user_name,
                'password_hash': self.password_hash,
                'display_name': self.display_name,
                'subject': self.subject}

    @staticmethod
    def user_from_json(user_json):
        return User(user_json['user'], user_json['password_hash'], user_json['display_name'], user_json['subject'])

    @staticmethod
    def users_from_password_file(password_file_name):
        try:
            with open(password_file_name, 'r') as password_file:
                users_json = json.load(password_file)
                users = dict()
                for user_json in users_json:
                    user = User(user_json['user_name'],
                                user_json['password_hash'],
                                user_json['display_name'],
                                user_json['subject'])
                    users[user.user_name] = user
                return users
        except FileNotFoundError:
            return dict()

    @staticmethod
    def users_to_password_file(users, password_file_name):
        user_list = list()
        for user in users.values():
            json_dict = dict()
            json_dict['user_name'] = user.user_name
            json_dict['password_hash'] = user.password_hash
            json_dict['display_name'] = user.display_name
            json_dict['subject'] = user.subject
            user_list.append(json_dict)
        with open(password_file_name, 'w') as password_file:
            json.dump(user_list, password_file)


def main():
    parser = ArgumentParser()
    parser.add_argument('--username', '-u', action='store')
    parser.add_argument('--password', '-p', action='store')
    parser.add_argument('--display-name', '-d', action='store', default=None)
    parser.add_argument('--subject', '-s', action='store', default=None)
    parser.add_argument('--time-zone', '-t', action='store', default=None)
    parser.add_argument('--password-file', '-f', action='store', default='.passwords', help='password file')
    parser.add_argument('--verify', '-v', action='store_true', default=False, help="Verify username and password")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    user_name = args.username
    password = args.password
    password_file = args.password_file
    subject = args.subject
    display_name = args.display_name

    users = User.users_from_password_file(args.password_file)
    if args.verify:
        if user_name not in users:
            logging.error("User {} not in password database".format(user_name))
            exit(1)
        verified = users[user_name].verify_password(password)
        if verified:
            logging.info("Password verified")
            exit(0)

        logging.error("Password verification failed")
        exit(1)

    user = User(user_name, password_context.encrypt(password), display_name, subject)
    users[user_name] = user

    User.users_to_password_file(users, password_file)


if __name__ == '__main__':
    main()
