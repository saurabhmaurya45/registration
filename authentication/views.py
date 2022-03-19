from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from gfg import settings
from django.core.mail import send_mail,EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_text
from . tokens import *


# Create your views here.
def signin(request):

    if request.method == "POST":
        username = request.POST['username'] 
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request,user)
            fname = user.first_name
            return render(request, "index.html", {"name": fname})
        else:
            messages.error(request,'Bad Credentials')
            return redirect('signin')
    return render(request, 'signin.html')
    
def home(request):
    return render(request, 'index.html')

def signup(request):

    if request.method == "POST":
        username = request.POST['email']
        name = request.POST['name']
        password = request.POST['pass']
        conform_password = request.POST['conpass']
        if User.objects.filter(username=username):
            messages.error(request,'User already exist Please login')
            return redirect('signin')
        if password != conform_password:
            messages.error(request,"Password didn't matched")
        
        myuser = User.objects.create_user(username=username,email=username, password=password)
        myuser.first_name = name
        myuser.is_active = False
        myuser.save()

        # Welcome email message
        subject = "Welcome to GFG - Django Login"
        message = "Hello " + myuser.first_name + "!!\n"+ "Welcome to GFG!! \nThank you for visiting to our website\n We have also sent conformation email, please visit there to conform your email address in order to activate your account.\n\n Thank you!\n\n\n Saurabh Maurya"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.username]
        send_mail(subject,message,from_email,to_list,fail_silently=True)

        # conformation email
        current_site = get_current_site(request)
        email_subject = "conform your email @ GFG - Django Login"
        con_message = render_to_string('emailconformation.html',{
            'name' : myuser.first_name,
            'domain' : current_site,
            'uid' : urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token' : generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            con_message,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()


        messages.success(request,'Your account created successfully.\n We have sent you  conformation email. Check your mail to conform your accont')
        return redirect('signin')
        
    return render(request, 'signup.html')
 


def signout(request):
    logout(request)
    messages.success(request,"Logged out successfully")
    return redirect('signin')

def activate(request, uid64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uid64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None
    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        myuser.save()
        login(request,myuser)
        message.success(request,"Activation Successfully")
        return redirect('signin')
    else:
        return render(request, 'activation_failed.html')
