import instaloader
L = instaloader.Instaloader()


def logger():
    try:
        L.login(username, password)
        return True
    except instaloader.exceptions.BadCredentialsException:
        return False


username = input("Type your username:\n")
password = input("Type your password:\n")
while not logger():
    print("Invalid please input again:\n")
    username = input("Type your username:\n")
    password = input("Type your password:\n")

L.save_session_to_file(f"session-{username}")

