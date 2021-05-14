import instaloader
from typing import List, Dict, Tuple
import pandas as pd
L = instaloader.Instaloader()
local_username = input("input username: \n")
L.load_session_from_file(local_username, filename=f"session-{local_username}")
profile = instaloader.Profile.from_username(L.context, input("Give an account to analyze: \n"))


class GenContainer:
    username = str
    followers: List[instaloader.Profile]
    likes: Dict[instaloader.Post, List[instaloader.Profile]]
    posts: List[instaloader.Post]
    unghosted_users = List[instaloader.Profile]
    ghoster_users = List[instaloader.Profile]
    follower_likes = Dict[str, int]

    def __init__(self, user_profile: instaloader.Profile):
        self.username = user_profile.username
        print("Getting posts...")
        self.posts = list(user_profile.get_posts())
        print("Done posts")
        print("Getting followers...")
        self.followers = list(user_profile.get_followers())
        print("Done followers")
        self.likes = {}
        for i in self.posts:
            print(f"Getting likes: {self.posts.index(i)}/{len(self.posts)} posts", end='\r')
            self.likes[i] = list(i.get_likes())
        print("Done likes")
        self.unghosted_users = []
        self.ghoster_users = []
        self.follower_likes = {}

    def __str__(self) -> str:
        return f"{len(self.posts)} posts \n" \
                      f"{len(self.followers)} followers \n" \
                      f"Users that don't ghost: {fupn(self.unghosted_users)} \n" \
                      f"Users that ghost: {fupn(self.ghoster_users)} \n" \
                      f"Ratio of likes Dict {self.follower_likes}"

    def ghoster_init(self) -> None:
        ghoster_list = self.followers.copy()
        not_ghoster_list = []
        for post in self.likes:
            for liker in self.likes[post]:
                if liker in ghoster_list:
                    ghoster_list.remove(liker)
                if liker not in not_ghoster_list and liker in self.followers:
                    not_ghoster_list.append(liker)
        self.unghosted_users, self.ghoster_users = not_ghoster_list, ghoster_list

    def follower_likes_init(self) -> None:
        final_dict = {}
        for post in self.likes:
            for user in self.likes[post]:
                if user.username in final_dict:
                    final_dict[user.username] += 1
                else:
                    final_dict[user.username] = 1
        self.follower_likes = final_dict

    def write_to_excel(self):
        unghost_followers = ["Unghosted Users"] + fupn(self.unghosted_users)
        ghost_followers = ["Ghosted Users"] + fupn(self.ghoster_users)
        user_pt1 = ["User"] + list(self.follower_likes.keys())
        user_pt2 = ["Likes"] + list(self.follower_likes.values())
        df = pd.DataFrame([unghost_followers, ghost_followers, user_pt1, user_pt2])
        df = df.transpose()
        df.to_csv(self.username + ".csv", index=False, header=None)


def fupn(users: List[instaloader.Profile]) -> List[str]:
    """Acrnoym from users print name"""
    new_ret = []
    for item in users:
        new_ret.append(item.username)
    return new_ret


def gen_container_FT(local_profile: instaloader.Profile) -> GenContainer:
    temp_var = GenContainer(local_profile)
    temp_var.ghoster_init()
    temp_var.follower_likes_init()
    temp_var.write_to_excel()
    return temp_var


user = gen_container_FT(profile)
