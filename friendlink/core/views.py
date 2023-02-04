from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from . models import Profile, Post, LikePost, FollowersCount
from itertools import chain

# Create your views here.

# home path view
@login_required(login_url='signin')
def index(request):
    # object of current user
    user_object = User.objects.get(username=request.user.username)
    # use object of current user to get his profile
    user_profile = Profile.objects.get(user=user_object)

    # list of users that current user is following
    user_following_list = []
    # posts of users that current user is following
    feed = []
    # objects of other users that current user is following
    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for user_fol in user_following:
        # add every user that current user is following to the list
        user_following_list.append(user_fol.user)

    for usernames in user_following_list:
        # add posts of users that current user is following to the list
        post_of_user_following = Post.objects.filter(user=usernames)
        feed.append(post_of_user_following)

    # create grouped iterable list of feeds
    feed_list = list(chain(*feed))

    # list of posts
    posts = Post.objects.all()
    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_list})


# signup view
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # create Profile object for new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')

        else:
            messages.info(request, 'Passwords does not match')
            return redirect('signup')

    else:
        return render(request, 'signup.html')


# signin view
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        # if user exists in database
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')

    else:
        return render(request, 'signin.html')


# logout view
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


# settings view
@login_required(login_url='signin')
def settings(request):
    # get profile of currently logged in user
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        # if user did not submit new image
        if request.FILES.get('image') == None:
            # get current image for user profile
            image = user_profile.profileimg
            # get bio from form field
            bio = request.POST['bio']
            # get location from form field
            location = request.POST['location']
            # save received user data
            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        # if user did submit new image
        if request.FILES.get('image') != None:
            # get new image 
            image = request.FILES.get('image')
            # get bio from form field
            bio = request.POST['bio']
            # get location from form field
            location = request.POST['location']
            # save received user data
            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect('settings')

    return render(request, 'setting.html', {'user_profile': user_profile})


# upload view
@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')
    return HttpResponse('<h1> Upload View </h1>')


# like_post view
@login_required(login_url='signin')
def like_post(request):
    # get current user name
    username = request.user.username
    # get liked post id
    post_id = request.GET.get('post_id')

    # get entire post object
    post = Post.objects.get(id=post_id)

    # check if like for current post from current user exists
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
   
    # user has not liked post 
    if like_filter == None: 
        # create like
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        # increase number of likes
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    # user has liked post
    else:
        # remove like
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')


# profile view
@login_required(login_url='signin')
def profile(request, pk):
    # get user object
    user_object = User.objects.get(username=pk)
    # get user profile using user object
    user_profile = Profile. objects.get(user=user_object)
    # get amount of posts made by user
    user_posts = Post.objects.filter(user=pk)
    user_posts_length = len(user_posts)

    follower = request.user.username
    # username of current user
    user = pk
    
    # if follower is already following user
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    # how many users follow current user
    user_followers = len(FollowersCount.objects.filter(user=pk))
    # how many users current user follows
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_posts_length': user_posts_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following
    }
    return render(request, 'profile.html', context)


# follow view
@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        # who will follow
        follower = request.POST['follower']
        # who will be followed
        user = request.POST['user']

        # if follower is already following user
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            # unfollow
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        # if follower is not following user
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)

    else:
        return redirect('/')

# search view
@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    if request.method == 'POST':
        username = request.POST['username']
        # get list of objects where search query is contained in username 
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
    
        username_profile_list = list(chain(*username_profile_list))

    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})