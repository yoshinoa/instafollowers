import instaloader
from typing import List, Dict, Tuple
import pandas as pd
import os
import json

from instaloader import NodeIterator

L = instaloader.Instaloader()
local_username = input("input username: \n")
try:
    L.load_session_from_file(local_username, filename=f"session-{local_username}")
except:
    print("File doesn't exist, run setup.py and try again.")
    quit()
print("Fetching account")
profile = instaloader.Profile.from_username(L.context, input("Give an account to analyze: \n"))
print("Got account")

class GenContainer:
    username: str
    followers: List[instaloader.Profile]
    following: List[instaloader.Profile]
    follower_amounts: Dict[instaloader.Profile, int]
    likes: Dict[instaloader.Post, List[instaloader.Profile]]
    posts: List[instaloader.Post]
    unghosted_users: List[instaloader.Profile]
    ghoster_users: List[instaloader.Profile]
    follower_likes: Dict[str, int]
    unfollower_likes: Dict[str, int]
    sus: List[str]
    weishenmefollow: List[str]

    def __init__(self, user_profile: instaloader.Profile, from_file=False):
        self.username = user_profile.username
        print("Getting posts...")
        self.posts = list(user_profile.get_posts())
        print("Done posts")
        print("Getting followers...")
        self.followers = list(user_profile.get_followers())
        print("Done followers")
        print("Getting following...")
        self.following = list(user_profile.get_followees())
        print("Done following")
        self.follower_amounts = {}
        # print("Getting following followers")
        # for following in self.following:
        #     self.follower_amounts[following] = following.mediacount
        # print("Got following followers")
        self.likes = {}
        for i in self.posts:
            print(f"Getting likes: {self.posts.index(i)}/{len(self.posts)} posts", end='\r')
            self.likes[i] = list(i.get_likes())
        print(f"Getting likes: {len(self.posts)}/{len(self.posts)} posts")
        print("Done likes")
        self.unghosted_users = []
        self.ghoster_users = []
        self.follower_likes = {}
        self.unfollower_likes = {}
        self.sus = []
        self.weishenmefollow = []

    def __str__(self) -> str:
        return f"{len(self.posts)} posts \n" \
                      f"{len(self.followers)} followers \n" \
                      f"Users that don't ghost: {fupn(self.unghosted_users)} \n" \
                      f"Users that ghost: {fupn(self.ghoster_users)} \n" \
                      f"Ratio of likes Dict {self.follower_likes}"

    def save_to_file(self):
        print("Saving to file")
        dirname = os.path.dirname(os.path.abspath(__file__))
        dirname = os.path.join(dirname, self.username)
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        jsonable = {}
        jsonable["username"] = self.username
        jsonable["sus"] = self.sus
        jsonable["weishenmefollow"] = self.weishenmefollow
        jsonable["follower_likes"] = self.follower_likes
        jsonable["unfollower_likes"] = self.unfollower_likes
        likes: Dict[instaloader.Post, List[instaloader.Profile]]
        posts: List[instaloader.Post]
        generic_json = os.path.join(dirname, f'generic_json.json')
        with open(generic_json, "w") as outfile:
            json.dump(jsonable, outfile)
        print("Saved to file.")
        # self.posts.thaw(instaloader.load_structure_from_file(L.context, dirname + '/followers.json'))
        # self.posts.thaw(instaloader.load_structure_from_file(L.context, dirname + '/followers.json'))
        # self.posts.thaw(instaloader.load_structure_from_file(L.context, dirname + '/followers.json'))
        # for item in self.posts:
        #     instaloader.save_structure_to_file()



    def ghoster_init(self) -> None:
        print("Ghoster/Unghoster Checks")
        ghoster_list = self.followers.copy()
        not_ghoster_list = []
        for post in self.likes:
            for liker in self.likes[post]:
                if liker in ghoster_list:
                    ghoster_list.remove(liker)
                if liker not in not_ghoster_list and liker in self.followers:
                    not_ghoster_list.append(liker)
        print("Ghoster/Unghoster Checks done")
        self.unghosted_users, self.ghoster_users = not_ghoster_list, ghoster_list

    def follower_likes_init(self) -> None:
        final_dict_followers = {}
        final_dict_unfollowers = {}
        print("follower likes started")
        for post in self.likes:
            for user in self.likes[post]:
                if user in self.followers:
                    if user.username in final_dict_followers:
                        final_dict_followers[user.username] += 1
                    else:
                        final_dict_followers[user.username] = 1
                else:
                    if user.username in final_dict_unfollowers:
                        final_dict_unfollowers[user.username] += 1
                    else:
                        final_dict_unfollowers[user.username] = 1
        print("follower likes done")
        self.follower_likes = final_dict_followers
        self.unfollower_likes = final_dict_unfollowers

    def sus_check(self) -> None:
        print("Sus check starting")
        # if not self.sus:
        #     for item in self.follower_amounts:
        #         if self.follower_amounts[item] > 10000 and item not in self.followers:
        #             self.sus.append(item.username)
        print("Sus check done")

    def why_following(self) -> None:
        print("Why following done")
        if not self.following:
            for item in self.following:
                if item not in self.followers:
                    self.weishenmefollow.append(item.username)
        print("Why following done")

    def write_to_excel(self):
        unghost_followers = ["Unghosted Users"] + fupn(self.unghosted_users)
        ghost_followers = ["Ghosted Users"] + fupn(self.ghoster_users)
        following_users_pt1 = ["Following User"] + list(self.follower_likes.keys())
        following_users_pt2 = ["Likes"] + list(self.follower_likes.values())
        unfollowing_users_pt1 = ["Unfollowing User"] + list(self.unfollower_likes.keys())
        unfollowing_users_pt2 = ["Likes"] + list(self.unfollower_likes.values())
        sus_people = ["SUS"] + list(self.sus)
        why_follow = ["why follow"] + list(self.weishenmefollow)
        df = pd.DataFrame([unghost_followers, ghost_followers, following_users_pt1, following_users_pt2, unfollowing_users_pt1, unfollowing_users_pt2, sus_people, why_follow])
        df = df.transpose()
        df.to_csv(self.username + ".csv", index=False, header=None)
        print(f"CSV has been outputted to {self.username}.csv")


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
    temp_var.why_following()
    temp_var.sus_check()
    temp_var.save_to_file()
    temp_var.write_to_excel()
    return temp_var


user = gen_container_FT(profile)
