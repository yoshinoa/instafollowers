import argparse

import instaloader.exceptions
from instaloader import Instaloader
from cli.containers.profilecontainer import ProfileContainer
import os
import pickle
from cli.auth import export_get_session


def login(loader: Instaloader, username: str, password: str) -> None:
    # if not username or not password:
    #     print("Setup specified but no username or password provided (-u, -p).")
    #     return
    try:
        if not os.path.exists("sessions"):
            os.mkdir("sessions")
        # loader.login(username, password)
        export_get_session()
        # print("Login successful, saving session to file.\n")
        # loader.save_session_to_file(f"sessions/sessions-{username}")
    except instaloader.exceptions.BadCredentialsException:
        print("Bad credentials.")


def main():
    parser = argparse.ArgumentParser(
        description="Perform analysis on instagram accounts."
    )
    parser.add_argument(
        "-s", "--setup", help="Run with -s to setup authorization.", action="store_true"
    )
    parser.add_argument(
        "-u",
        "--username",
        help="Set the username to run with.",
        action="store",
        dest="username",
        required=True,
    )
    parser.add_argument(
        "-p",
        "--password",
        help="Set the password to run with.",
        action="store",
        dest="password",
    )
    parser.add_argument(
        "-t",
        "--target",
        help="Set the target to run against.",
        action="store",
        dest="target",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Set the output file to write to.",
        action="store",
        dest="output",
    )
    parser.add_argument(
        "-c",
        "--compare",
        help="Compare an old pickle to a new username, input the revision number or 0 for no revision number",
        action="store",
        dest="compare",
    )
    parser.add_argument(
        "-l", "--local", help="Load a pickle file", action="store", dest="local"
    )
    parser.add_argument(
        "-date",
        "--date",
        help="Check the dates of the pickle files currently stored",
        action="store_true",
        dest="date",
    )
    parser.add_argument("-n", "--omit")
    args = parser.parse_args()
    loader = instaloader.Instaloader()
    if args.date:
        if os.path.exists("pickles"):
            for file in os.listdir("pickles"):
                if file.endswith(".pickle"):
                    with open(f"pickles/{file}", "rb") as f:
                        print(f"File: {file} - Date: {pickle.load(f).updated_at}")
    if args.setup:
        login(loader, args.username, args.password)
    else:
        try:
            loader.load_session_from_file(
                args.username, filename=f"sessions/session-{args.username}"
            )
        except FileNotFoundError:
            print("Cannot find session file. Run with -s to setup authorization.")
            return
    if args.compare and args.target:
        with open(
            f'pickles/{args.target}{"_" + args.compare if args.compare != 0 else ""}.pickle',
            "rb",
        ) as f:
            old = pickle.load(f)
        # look at pickle info
        if args.local:
            print(args.local)
            print(args.local)
            with open(
                f'pickles/{args.target}{"_" + args.local if args.local != "0" else ""}.pickle',
                "rb",
            ) as f:
                target = pickle.load(f)
        else:
            target = ProfileContainer(args.target, loader)
            target.get_posts()
            target.get_followers()
            target.get_following()
            target.get_likes()
            target.serialize()
        target.compare(old)

    elif args.target:
        if args.local:
            with open(
                f'pickles/{args.target}{"_" + args.local if args.local != "0" else ""}.pickle',
                "rb",
            ) as f:
                target = pickle.load(f)
        else:
            target = ProfileContainer(args.target, loader)
            target.get_posts()
            target.get_followers()
            target.get_following()
            target.get_likes()
            target.serialize()
        target.write_to_excel()
