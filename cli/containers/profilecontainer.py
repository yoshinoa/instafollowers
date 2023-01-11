import instaloader
import pickle
from typing import List, Set, Optional, Dict
import pandas as pd
import os
import datetime

class ProfileContainer:
    username: str
    profile: instaloader.Profile
    posts: Set[instaloader.Post]
    followers: Set[instaloader.Profile]
    following: Set[instaloader.Profile]
    likes: List[Set[instaloader.Profile]]
    updated_at: datetime.datetime
    maps_to: Dict[str, Set[instaloader.Profile]]

    def __init__(self, username: str, loader: instaloader.Instaloader, **kwargs) -> None:
        self.username = username
        self.profile = instaloader.Profile.from_username(loader.context, username)
        self.updated_at = datetime.datetime.now()

    def get_posts(self) -> Optional[Set[instaloader.Post]]:
        print("Getting posts...")
        self.posts = set(self.profile.get_posts())
        return self.posts

    def get_followers(self) -> Optional[Set[instaloader.Profile]]:
        print("Getting followers...")
        self.followers = set(self.profile.get_followers())
        return self.followers

    def get_following(self) -> Optional[Set[instaloader.Profile]]:
        print("Getting following...")
        self.following = set(self.profile.get_followees())
        return self.following

    def get_likes(self) -> Optional[List[Set[instaloader.Profile]]]:
        if not self.posts:
            return None
        counter = 0
        self.likes = []
        self.maps_to = {}
        for post in self.posts:
            print(f"Getting likes:"
                  f" {counter}/{len(self.posts)} posts", end='\r')
            likes = post.get_likes()
            self.likes.append(set(likes))
            self.maps_to[post.shortcode] = set(likes)
            counter += 1
        return self.likes

    def followers_that_liked(self):
        return [x.username for x in self.following if x in {i for sublist in self.likes for i in sublist}]

    def followers_that_didnt_like(self):
        return [x.username for x in self.followers if x not in {i for sublist in self.likes for i in sublist}]

    def follower_like_amounts(self):
        unnested_likes = [item for sublist in self.likes for item in sublist]
        likes = [(x.username, unnested_likes.count(x)) for x in self.followers if unnested_likes.count(x) > 0]
        likes.sort(key=lambda x: x[1], reverse=True)
        return [x[0] for x in likes], [x[1] for x in likes]

    def nonfollower_like_amounts(self):
        unnested_likes = [item for sublist in self.likes for item in sublist]
        usernames = []
        likes = []
        for x in unnested_likes:
            if x not in self.followers and x.username not in usernames:
                usernames.append(x.username)
                likes.append(unnested_likes.count(x))
        likes, usernames = zip(*sorted(zip(likes, usernames), reverse=True))
        return list(usernames), list(likes)

    def not_following_back(self):
        usernames = []
        for x in self.following:
            if x not in self.followers:
                usernames.append(x.username)
        return usernames


    def write_to_excel(self) -> None:
        followed_that_liked = ['Followed users that liked posts'] + self.followers_that_liked()
        followed_that_no_liked = ['Followed users that did not like posts'] + self.followers_that_didnt_like()
        followers, likes = self.follower_like_amounts()
        followers.insert(0, 'Followers')
        likes.insert(0, 'Likes')
        nonfollowers, nonfollow_likes = self.nonfollower_like_amounts()
        nonfollowers.insert(0, 'Nonfollowers')
        nonfollow_likes.insert(0, 'Likes')
        notfollowedback = ['Not followed back'] + self.not_following_back()
        df = pd.DataFrame([followed_that_liked, followed_that_no_liked, followers, likes, nonfollowers, nonfollow_likes, notfollowedback])
        df = df.transpose()
        if not os.path.exists("excel"):
            os.mkdir("excel")
        df.to_excel(f"excel/{self.username}.xlsx", index=False)
        print(f"{self.username}.xlsx written to disk")

    def serialize(self) -> None:
        # Serialize the profile container to a pickle file.
        # Make a directory called "pickles" if it doesn't exist.
        counter = 0
        if not os.path.exists("pickles"):
            os.mkdir("pickles")
        # check if the file exists and save the new one as an incremented version
        if os.path.exists(f"pickles/{self.username}.pickle"):
            counter = 1
            while os.path.exists(f"pickles/{self.username}_{counter}.pickle"):
                counter += 1
        filename = f"pickles/{self.username + (f'_{counter}' if counter else '')}.pickle"
        with open(filename, "wb") as f:
            pickle.dump(self, f)
        print(f"{filename} written to disk")

    def compare(self, other) -> None:
        # Compare the current ProfileContainer with another ProfileContainer.
        # Print the results.
        print(f"Lost followers: {len(other.followers - self.followers)}")
        print(f"Gained followers: {len(self.followers - other.followers)}")
        print(f"Users that unfollowed: {[x.username for x in other.followers - self.followers]}")
        print(f"Users that followed: {[x.username for x in self.followers - other.followers]}")
        print(f"New users followed: {[x.username for x in self.following - other.following]}")
        print(f"Users unfollowed: {[x.username for x in other.following - self.following]}")
        # we want to find users that liked posts in the old profile but not in the new one
        # we can do this by comparing the likes of the old profile with the followers of the new profile

