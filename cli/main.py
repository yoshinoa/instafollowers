import argparse

import instaloader.exceptions
from instaloader import Instaloader
from cli.containers.profilecontainer import ProfileContainer
import os
import pickle


def login(loader: Instaloader, username: str, password: str) -> None:
    if not username or not password:
        print("Setup specified but no username or password provided (-u, -p).")
        return
    try:
        if not os.path.exists('session'):
            os.mkdir('sessions')
        loader.login(username, password)
        print("Login successful, saving session to file.\n")
        loader.save_session_to_file(f"sessions/sessions-{username}")
    except instaloader.exceptions.BadCredentialsException:
        print("Bad credentials.")


def main():
    parser = argparse.ArgumentParser(description="Perform analysis on instagram accounts.")
    parser.add_argument('-s', '--setup', help="Run with -s to setup authorization.", action='store_true')
    parser.add_argument('-u', '--username', help="Set the username to run with.", action='store', dest='username', required=True)
    parser.add_argument('-p', '--password', help="Set the password to run with.", action='store', dest='password')
    parser.add_argument('-t', '--target', help="Set the target to run against.", action='store', dest='target')
    parser.add_argument('-o', '--output', help="Set the output file to write to.", action='store', dest='output')
    parser.add_argument('-c', '--compare', help="Compare an old pickle to a new username", action='store_true')
    parser.add_argument('-l', '--local', help="Load a pickle file", action='store_true', dest='local')
    parser.add_argument('-date', '--date', help="Check the dates of the pickle files currently stored", action='store_true', dest='date')
    parser.add_argument('-n', '--omit')
    args = parser.parse_args()
    loader = instaloader.Instaloader()
    if args.date:
        if os.path.exists('pickles'):
            for file in os.listdir('pickles'):
                if file.endswith('.pickle'):
                    with open (f'pickles/{file}', 'rb') as f:
                        print(f'File: {file} - Date: {pickle.load(f).updated_at}')
    if args.setup:
        login(loader, args.username, args.password)
    else:
        try:
            loader.load_session_from_file(args.username, filename=f'sessions/session-{args.username}')
        except FileNotFoundError:
            print("Cannot find session file. Run with -s to setup authorization.")
            return
    if args.compare and args.target:
        with open(f'pickles/{args.target}.pickle', 'rb') as f:
            old = pickle.load(f)
        # look at pickle info
        target = ProfileContainer(args.target, loader)
        target.get_posts()
        target.get_followers()
        target.get_following()
        target.get_likes()
        target.compare(old)
        target.serialize()

    elif args.target:
        if args.local:
            with open(f'pickles/{args.target}.pickle', 'rb') as f:
                target = pickle.load(f)
        else:
            target = ProfileContainer(args.target, loader)
            target.get_posts()
            target.get_followers()
            target.get_following()
            target.get_likes()
            target.serialize()
        target.write_to_excel()



