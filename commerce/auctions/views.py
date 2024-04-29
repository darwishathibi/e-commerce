from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comment, Bid


def index(request):
    active_listings = Listing.objects.filter(is_actice=True)
    all_categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": active_listings,
        "categories": all_categories
    })

def display_category(request):
    if request.method == "POST":
        category_form = request.POST["category"]
        category = Category.objects.get(categoryName=category_form)
        active_listings = Listing.objects.filter(is_actice=True, category=category)
        all_categories = Category.objects.all()
        return render(request, "auctions/index.html", {
        "listings": active_listings,
        "categories": all_categories
    })



# This view will be used to create a new listing. 
def create_listing(request):
    if request.method == "GET":
        all_categories = Category.objects.all()
        return render(request, "auctions/create_listing.html",{
            "categories": all_categories # Pass all categories to the template
        })
    else:
        # Get all the data from the form
        title = request.POST["title"]
        description = request.POST["description"]
        price = request.POST["price"]
        imageurl = request.POST["imageurl"]
        category = request.POST["category"]
        # Get the user object
        user = request.user
        # Get the category object
        category_data = Category.objects.get(categoryName=category)
        # Create the bid
        bid = Bid(bid=float(price), user=user)
        bid.save()
        # Create the listing
        new_listing = Listing(title=title, description=description, price=bid, image_url=imageurl, category=category_data, owner=user)
        new_listing.save()
        return HttpResponseRedirect(reverse("index"))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
def listing(request, id):
    listing_data = Listing.objects.get(pk=id)
    is_listing_in_watchlist = request.user in listing_data.wacthlist.all()
    all_comments = Comment.objects.filter(listing=listing_data)
    is_owner = request.user.username == listing_data.owner.username
    return render(request, "auctions/listing.html",{
        "listing": listing_data,
        "is_listing_in_watchlist": is_listing_in_watchlist,
        "all_comments": all_comments,
        "is_owner": is_owner
    })

def close_auction(request, id):
    listing_data = Listing.objects.get(pk=id)
    listing_data.is_actice = False
    listing_data.save()
    is_listing_in_watchlist = request.user in listing_data.wacthlist.all()
    all_comments = Comment.objects.filter(listing=listing_data)
    is_owner = request.user.username == listing_data.owner.username
    return render(request, "auctions/listing.html",{
        "listing": listing_data,
        "is_listing_in_watchlist": is_listing_in_watchlist,
        "all_comments": all_comments,
        "is_owner": is_owner,
        "update": True,
        "message": "Auction closed"
    })
    

def remove_watchlist(request, id):
    listing_data = Listing.objects.get(pk=id)
    current_user = request.user
    listing_data.wacthlist.remove(current_user)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def add_watchlist(request, id):
    listing_data = Listing.objects.get(pk=id)
    current_user = request.user
    listing_data.wacthlist.add(current_user)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def display_watchlist(request):
    current_user = request.user
    listings = current_user.listing_watchlist.all()
    return render(request, "auctions/watchlist.html",{
        "listings": listings
    })

def add_comment(request, id):
    current_user = request.user
    listing_data = Listing.objects.get(pk=id)
    message = request.POST["new_comment"]
    new_comment = Comment(author=current_user, listing=listing_data, message=message)
    new_comment.save()
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def add_bid(request, id):
    new_bid = request.POST["new_bid"]
    listing_data = Listing.objects.get(pk=id)
    is_listing_in_watchlist = request.user in listing_data.wacthlist.all()
    all_comments = Comment.objects.filter(listing=listing_data)
    is_owner = request.user.username == listing_data.owner.username
    if float(new_bid) > listing_data.price.bid:
        update_bid = Bid(bid=float(new_bid), user=request.user)
        update_bid.save()
        listing_data.price = update_bid
        listing_data.save()
        return render(request, "auctions/listing.html",{
            "listing": listing_data,
            "message": "Bid successfully added",
            "update": True,
            "is_listing_in_watchlist": is_listing_in_watchlist,
            "is_owner": is_owner,
            "all_comments": all_comments
        })
    else:
        return render(request, "auctions/listing.html",{
            "listing": listing_data,
            "message": "Bid must be greater than the current bid",
            "update": False,
            "is_listing_in_watchlist": is_listing_in_watchlist,
            "is_owner": is_owner,
            "all_comments": all_comments
        })


