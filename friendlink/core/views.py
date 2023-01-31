from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from . models import Profile, Post, LikePost

# Create your views here.

# home path view
@login_required(login_url='signin')
def index(request):
    # object of current user
    user_object = User.objects.get(username=request.user.username)
    # use object of current user to get his profile
    user_profile = Profile.objects.get(user=user_object)

    # list of posts
    posts = Post.objects.all()
    return render(request, 'index.html', {'user_profile': user_profile, 'posts': posts})


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
def profile(request):
    return render(request, 'profile.html')