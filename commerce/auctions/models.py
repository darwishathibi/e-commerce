from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass

# Category class same as table in the database
class Category(models.Model):
    categoryName = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.categoryName}"
    
# Bid class same as table in the database
class Bid(models.Model):
    bid = models.FloatField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user_bid")

    def __str__(self):
        return f"{self.bid}"

# Listing class same as table in the database
class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1000)
    image_url = models.CharField(max_length=1000)
    # price = models.FloatField()
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True, related_name="bid_price")
    is_actice = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    wacthlist = models.ManyToManyField(User, blank=True, null=True, related_name="listing_watchlist")
    def __str__(self):
        return f"{self.title}"

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user_comment")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listing_comment")
    message = models.CharField(max_length=1000)

    def __str__(self):
        return f"{self.author} commented on {self.listing}"
    
