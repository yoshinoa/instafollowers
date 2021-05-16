import instaloader
from typing import List, Dict, Union, Tuple
import pandas as pd
import os
import shutil

from instaloader import NodeIterator

L = instaloader.Instaloader()
local_username = input("Input username used in setup.py: \n")
try:
    L.load_session_from_file(local_username,
                             filename=f"session-{local_username}")
except:
    print("File doesn't exist, run setup.py and try again.")
    quit()
print("Fetching account")
profile = instaloader.Profile.\
    from_username(L.context, input("Give an account to analyze: \n"))
print("Got account")


def load_function(context, folder) -> \
        List[Union[instaloader.Post, instaloader.Profile]]:
    temp_var = []
    for item in os.listdir(folder):
        temp_var.append(instaloader.load_structure_from_file
                        (context, os.path.join(folder, item)))
    return temp_var


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
    loaded_from_file: bool

    def __init__(self, user_profile: instaloader.Profile, old=False) -> None:
        self.username = user_profile.username
        self.unghosted_users = []
        self.ghoster_users = []
        self.follower_likes = {}
        self.unfollower_likes = {}
        self.sus = []
        self.weishenmefollow = []
        if old:
            print("Loading from file...")
            self.username += "_old"
            self.load_from_file()
            self.loaded_from_file = True
            print("Load from old successful")
            self.ghoster_init()
            self.follower_likes_init()
            self.why_following()
            self.sus_check()
            return
        if self.username in os.listdir():
            check = input('Local copy '
                          'of information available use that? y/n:\n')
            if check in ['y', 'Y']:
                print("Loading from file...")
                self.load_from_file()
                self.loaded_from_file = True
                print("Load successful")
                self.ghoster_init()
                self.follower_likes_init()
                self.why_following()
                self.sus_check()
                return
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
            print(f"Getting likes:"
                  f" {self.posts.index(i)}/{len(self.posts)} posts", end='\r')
            self.likes[i] = list(i.get_likes())
        print(f"Getting likes: {len(self.posts)}/{len(self.posts)} posts")
        print("Done likes")
        self.ghoster_init()
        self.follower_likes_init()
        self.why_following()
        self.sus_check()
        self.loaded_from_file = False

    def __str__(self) -> str:
        return f"{len(self.posts)} posts \n" \
                      f"{len(self.followers)} followers \n" \
                      f"Users that don't ghost: " \
               f"{fupn(self.unghosted_users)} \n" \
                      f"Users that ghost: {fupn(self.ghoster_users)} \n" \
                      f"Ratio of likes Dict {self.follower_likes}"

    def give_filenames(self, path) -> tuple[str, str, str, str, str, str, str]:
        dirname = os.path.join(path, self.username)
        followers_folder = os.path.join(dirname, 'followers')
        following_folder = os.path.join(dirname, 'following')
        likes_folder = os.path.join(dirname, 'likes')
        posts_folder = os.path.join(dirname, 'posts')
        unghosted_users_folder = os.path.join(dirname, 'unghosted_users')
        ghoster_users_folder = os.path.join(dirname, 'ghoster_users')
        return dirname, followers_folder, following_folder, likes_folder, \
            posts_folder, unghosted_users_folder, ghoster_users_folder

    def load_from_file(self) -> None:
        dirname = os.path.dirname(os.path.abspath(__file__))
        dirname, followers_folder, following_folder, \
            likes_folder, posts_folder, unghosted_users_folder, \
            ghoster_users_folder = self.give_filenames(dirname)
        self.followers = load_function(L.context, followers_folder)
        self.following = load_function(L.context, following_folder)
        self.posts = load_function(L.context, posts_folder)
        self.unghosted_users = load_function(L.context, unghosted_users_folder)
        self.ghoster_users = load_function(L.context, ghoster_users_folder)
        self.likes = {}
        for item in self.posts:
            self.likes[item] = []
            local_path = os.path.join(likes_folder, item.shortcode)
            for item2 in os.listdir(local_path):
                self.likes[item].append(instaloader.load_structure_from_file(
                    L.context, os.path.join(local_path, item2)))

    def save_to_file(self) -> None:
        if not self.loaded_from_file:
            print("Saving to file")
            dirname = os.path.dirname(os.path.abspath(__file__))
            dirname, followers_folder, following_folder, \
                likes_folder, posts_folder, unghosted_users_folder, \
                ghoster_users_folder = self.give_filenames(dirname)
            files_list = [followers_folder, following_folder, likes_folder,
                          posts_folder, unghosted_users_folder,
                          ghoster_users_folder]
            if os.path.exists(dirname):
                if os.path.exists(dirname + '_old'):
                    print(f'{dirname}_old exists already, '
                          f'deleting and replacing.')
                    shutil.rmtree(dirname + '_old')
                os.rename(dirname, dirname + '_old')
            os.mkdir(dirname)
            for item in files_list:
                os.mkdir(item)
            for item in self.followers:
                instaloader.save_structure_to_file(item, os.path.join(
                    followers_folder,
                    str(self.followers.index(item)) + '.json'))
            for item in self.following:
                instaloader.save_structure_to_file(item, os.path.join(
                    following_folder,
                    str(self.following.index(item)) + '.json'))
            for item in self.posts:
                instaloader.save_structure_to_file(item, os.path.join(
                    posts_folder,
                    str(self.posts.index(item)) + '.json'))
            for item in self.likes:
                local_path = os.path.join(likes_folder, item.shortcode)
                os.mkdir(local_path)
                for another_item in self.likes[item]:
                    instaloader.save_structure_to_file(
                        another_item,
                        os.path.join(local_path, str(
                            self.likes[item].index(another_item)) + '.json'))
            for item in self.unghosted_users:
                instaloader.save_structure_to_file(item, os.path.join(
                    unghosted_users_folder,
                    str(self.unghosted_users.index(item)) + '.json'))
            for item in self.ghoster_users:
                instaloader.save_structure_to_file(
                    item, os.path.join(ghoster_users_folder, str(
                        self.ghoster_users.index(item)) + '.json'))
            print("Saved to file.")
        else:
            print("Was originally loaded from file, cannot save this")

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
        self.unghosted_users, self.ghoster_users = \
            not_ghoster_list, ghoster_list

    def follower_likes_init(self) -> None:
        final_dict_followers = {}
        final_dict_unfollowers = {}
        print("follower likes started")
        for post in self.likes:
            for user2 in self.likes[post]:
                if user2 in self.followers:
                    if user2.username in final_dict_followers:
                        final_dict_followers[user2.username] += 1
                    else:
                        final_dict_followers[user2.username] = 1
                else:
                    if user2.username in final_dict_unfollowers:
                        final_dict_unfollowers[user2.username] += 1
                    else:
                        final_dict_unfollowers[user2.username] = 1
        print("follower likes done")
        self.follower_likes = final_dict_followers
        self.unfollower_likes = final_dict_unfollowers

    def sus_check(self) -> None:
        print("Sus check starting")
        # if not self.sus:
        #     for item in self.follower_amounts:
        #         if self.follower_amounts[item] > 10000 and item not in
        #         self.followers:
        #             self.sus.append(item.username)
        print("Sus check done")

    def why_following(self) -> None:
        print("Why following done")
        for item in self.following:
            if item not in self.followers:
                self.weishenmefollow.append(item.username)
        print("Why following done")

    def write_to_excel(self):
        unghost_followers = ["Unghosted Users"] + fupn(self.unghosted_users)
        ghost_followers = ["Ghosted Users"] + fupn(self.ghoster_users)
        following_users_pt1 = ["Following User"] + list(
            self.follower_likes.keys())
        following_users_pt2 = ["Likes"] + list(
            self.follower_likes.values())
        unfollowing_users_pt1 = ["Unfollowing User"] + list(
            self.unfollower_likes.keys())
        unfollowing_users_pt2 = ["Likes"] + list(self.unfollower_likes.values())
        sus_people = ["SUS"] + list(self.sus)
        why_follow = ["why follow"] + list(self.weishenmefollow)
        df = pd.DataFrame([unghost_followers, ghost_followers,
                           following_users_pt1, following_users_pt2,
                           unfollowing_users_pt1, unfollowing_users_pt2,
                           sus_people, why_follow])
        df = df.transpose()
        df.to_csv(self.username + ".csv", index=False)
        print(f"CSV has been outputted to {self.username}.csv")


def fupn(users: List[instaloader.Profile]) -> List[str]:
    """Acrnoym from users print name"""
    new_ret = []
    for item in users:
        new_ret.append(item.username)
    return new_ret


def gen_container_ft(local_profile: instaloader.Profile) -> GenContainer:
    temp_var = GenContainer(local_profile)
    temp_var.save_to_file()
    temp_var.write_to_excel()
    return temp_var


user = gen_container_ft(profile)
