from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Wallpaper, Contact
from django.contrib import messages
from .helper import send_otp
from frontwall.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, authenticate, logout
from django.db.models import Q
from django.http import JsonResponse
from django.db.models import F
from django.views.decorators.http import require_POST

# Create your views here.

def index(request):
    wallpapers = Wallpaper.objects.all()
    context = {
        'wallpapers': wallpapers
    }
    return render(request,'main/index.html',context)

def upload(request):
    if request.method == "POST":
        caption = request.POST['caption']
        tags = request.POST['tags']
        image = request.FILES['wallpaper']
        user = request.user
        wallpaperu = Wallpaper(caption=caption,tags=tags,image=image, publisher=user)
        wallpaperu.save()
        messages.info(request,' Wallpaper Uploaded Successfully')
        return redirect('Frontwall')
    else:
        return render(request,'main/upload.html')
    
def vwallpaper(request,id):
    wallimage = get_object_or_404(Wallpaper, pk=id)
    wallimagelikes = wallimage.total_likes()
    current_url = request.build_absolute_uri()
    data = {'obj':wallimage,
            'likes': wallimagelikes,
            }
    return render(request, 'main/wallpaper.html', data)

def me(request):
    u = request.user
    user_wallpaper = Wallpaper.objects.filter(publisher = u)
    fav_wallpaper = Wallpaper.objects.filter(likes = u)
    data = {
        "username": u,
        'user_wallpapers': user_wallpaper,
        'fav_wallpapers': fav_wallpaper
    }
    return render(request,'main/me.html',data)

def search(request):
    if request.method == 'GET':
        query= request.GET.get('q')
        if query is not None:
            lookups= Q(caption__icontains=query) | Q(tags__icontains=query)
            results= Wallpaper.objects.filter(lookups).distinct()
            context={'result': results,
                     'query': query}
            
            return render(request, 'main/result.html', context)
        return redirect('Frontwall')
    return redirect('Frontwall')
        
def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        # bio = request.POST['bio']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1==password2:
            request.session['username'] = username
            request.session['email'] = email
            request.session['password']= password1
            # request.session['bio'] = bio
            if User.objects.filter(username=username).exists():
                print('username error')
                messages.info(request,'username already taken')
                return HttpResponseRedirect(reverse('signup'))
            if User.objects.filter(email=email).exists():
                print("email error")
                messages.info(request,'email already taken')
                return HttpResponseRedirect(reverse('signup'))
            else:
                sub = 'Account confirmation'
                action = 'account confirmation'
                global otp
                otp = send_otp(sub,username,email,action)
                ts = {'ts':'verify_otps'}
                messages.info(request,f'OTP has been sent to {email}')
                return render(request,'main/otp.html',ts)
        else:
            messages.info(request,'Password not matched')
            return HttpResponseRedirect(reverse('signup'))
    return render(request,'main/signup.html')

def reset_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            request.session['email'] = email
            username = user.username
            request.session['username'] = username
            sub = 'Reset Password'
            action = 'reset password'
            global potp
            potp = send_otp(sub,username,email,action)
            ts = {'ts':'verify_otpp'}
            return render(request,'main/otp.html',ts)
        else:
            messages.info(request,'Email not registered')
            return render(request,'main/rp.html')
    else:
        return render(request, 'main/rp.html')

def verify_otps(request):
    if request.method=="POST":
        otpu = request.POST.get('otp')
        if otp == otpu:
            enp = make_password(request.session['password'])
            user = User(username=request.session['username'],email=request.session['email'],password=enp)
            # user.profile.bio = request.session['bio']
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('Frontwall'))
        else:
            ts = {'ts':'verify_otps'}
            messages.info(request,'OTP is invalid')
            return render(request,'main/otp.html',ts)
    else:
        return HttpResponseRedirect(reverse('signup'))
    
def verify_otpp(request):
    if request.method=="POST":
        otpu = request.POST.get('otp')
        if potp == otpu:
            return render(request,'main/cp.html')
        else:
            messages.info(request,'OTP is invalid')
            ts = {'ts':'verify_otpp'}
            return render(request,'main/otp.html',ts)
    else:
        return HttpResponseRedirect(reverse('signup'))

def resend_otp(request):
    if request.method == "POST":
        pre_url = request.META.get("HTTP_REFERER").lower().strip()
        if pre_url.endswith('/signup/'):
            sub = 'Account confirmation'
            action = 'account confirmation'
            username = request.session['username']
            email = request.session['email']
            global otp
            otp = send_otp(sub,username,email,action)
            ts = {'ts':'verify_otps'}
            return render(request, 'main/otp.html',ts)
        elif pre_url.endswith('/reset_password/'):
            sub = 'Reset Password'
            action = 'reset password'
            username = request.session['username']
            email = request.session['email']
            global potp
            potp = send_otp(sub,username,email,action)
            ts = {'ts':'verify_otpp'}
            return render(request, 'main/otp.html', ts)   
        else:
            messages.info(request,'OTP validation exceed! Try again')
            return HttpResponseRedirect(reverse('signup'))
    else:
        return HttpResponseRedirect(reverse('signup'))        

def change_password(request):
    if request.method == "POST":
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            try:
                user = User.objects.get(username=request.session['username'])  # Get the user instance
            except:
                user = request.user

            user.set_password(password1)
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('Frontwall'))
        else:
            print('nah')
            messages.info(request, 'Password not matched')
            return render(request,'main/cp.html')
    else:
        return redirect('Frontwall')
        
def loginw(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password1']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('Frontwall'))
        else:
            messages.info(request,'Invalid username or password')
            return HttpResponseRedirect(reverse('login'))
    return render(request,'main/login.html')

def logoutw(request):
    logout(request)
    messages.info(request, 'Logout successfully')
    return HttpResponseRedirect(reverse('Frontwall'))

def like_view(request):
    if request.method == "POST":
        wallpaper_id = request.POST.get('wallpaper_id')
        wallpaper = get_object_or_404(Wallpaper, id=wallpaper_id)
        user = request.user
        if user.is_authenticated:
            if request.user in wallpaper.likes.all():
                wallpaper.likes.remove(request.user)
                liked = False
            else:
                wallpaper.likes.add(request.user)
                liked = True    
            
            return JsonResponse({'liked': liked, 'likes_count': wallpaper.likes.count()})
        else:
            messages.info(request,'You need to login first')
            return redirect('Frontwall')
    
def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        contact = Contact(name=name,email=email,subject=subject,message=message)
        contact.save()
        send_mail(subject=f'In response of "{subject}"',message=f'Hey {name},\n \nYour response has been received and been under consideration.\nOne of our member will contact you soon.\n\nThank You,\nTeam Frontwall',from_email=EMAIL_HOST_USER,recipient_list=[email],fail_silently=False)
        messages.info(request,f"Thank you for contacting us! We will respond soon")
        return render(request,'main/contact.html')
    return render(request,'main/contact.html')

def chpu(request):
    user = request.user
    if user.is_authenticated:
        return render(request,'main/cp.html')
    else:
        return redirect("Frontwall")
    
def useredit(request):
    user = request.user
    if user.is_authenticated:
        username = user.username
        bio = user.profile.bio
        email = user.email
        data = {'username':username,
                'bio': bio,
                'email':email,
                }
        
        if request.method == "POST":
            nusername = request.POST['username']
            nbio = request.POST['bio']
            nemail = request.POST['email']
            
            user.username = nusername
            user.email = nemail
            user.profile.bio = nbio
            user.save()
            messages.info(request,'Profile Updated successfully')
            return redirect('me')

        return render(request,'main/edituser.html', data)
    else:
        return redirect('Fronwall')
    
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    user_wallpaper = Wallpaper.objects.filter(publisher=user)
    data = {'user':user, 'user_wallpapers':user_wallpaper}
    return render(request,'main/profile.html',data)

def greet(request):
    user = request.user
    if user.is_authenticated():
        messages.info(request, f"Hello, {user}")
        return redirect("Frontwall")    
    else:
        messages.info(request, "You need to log in first")
        return redirect("Frontwall")
