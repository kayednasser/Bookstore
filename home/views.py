from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.conf import settings 
from django.core.mail import send_mail 
from django.contrib import messages
from product.models import *
from .models import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required


# Create your views here.


def home(request):
    books_on_offer = Book.objects.filter(on_offer=True)
    try:
        recommendations = Recommendation.objects.filter(user=request.user)
        if len(recommendations) < 1:
            recommendations = Book.objects.filter(rating__gte=3).order_by('-rating')
    except:
        recommendations = Book.objects.filter(rating__gte=3).order_by('-rating')
    
    print('recom: ',recommendations)

    
    context = {
        'books_on_offer':books_on_offer,
        'recommendations':recommendations
    }

    try:
        books_cart = Cart.objects.filter(user=request.user)
        books_cart_count = 0
        for b in list(books_cart):
            books_cart_count+= int(b.quantity)

        context['books_cart_count'] = books_cart_count
    except:
        print('user is not logged in...')

    return render(request, 'index.html',context)

def search(request):
    if request.method == 'POST':
        search = request.POST['search']
        searched_books = Book.objects.filter(
            Q(name__icontains = search) | Q(author__icontains=search)).order_by('-rating')
        context  = {
            'all_books':searched_books,
            'all_books_count':len(searched_books)

        }

    try:
        books_cart = Cart.objects.filter(user=request.user)
        books_cart_count = 0
        for b in list(books_cart):
            books_cart_count+= int(b.quantity)
        context['books_cart_count'] = books_cart_count
    except:
        print('user is not logged in...')

    return render(request,'products.html',context)


def register(request):

    if request.method == 'POST':

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:

            if User.objects.filter(username=username).exists():
                messages.info(request,'username is already taken!!!')
                return redirect('register')

            elif User.objects.filter(email=email).exists():
                messages.info(request,'email is already used!!!')
                return redirect('/')

            else:
                user = User.objects.create_user(
                    username=username, password=password1, email=email,first_name=first_name,last_name=last_name)
                user.save()

                print('user is created...')

                try:
                    subject = f'new user {username}'
                    message = f'First name:{first_name},Last name:{last_name},Username:{username},Email:{email}'
                    email_from = settings.EMAIL_HOST_USER 
                    superusers = User.objects.filter(is_superuser=True)
                    superusers_emails = superusers.values_list('email')
                    recipient_list = [superusers[0].email,]
                    send_mail( subject, message, email_from, recipient_list ) 
                    print('mail successfully sent...')
                except:
                    print('mail send failled...')

                user_auth = auth.authenticate(username=username, password=password1)

                if user_auth is not None:
                    auth.login(request, user_auth)
                    return render(request, 'index.html')

        else:
            messages.info(request,'passwords are not matched!!!')
            return redirect('register')
    else:
        return render(request, 'register.html')




def login(request):

    if request.method== 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.info(request,'invalid credentials!!!')
            return redirect('login')

    else:
        return render(request,'login.html')  
    

def logout(request):
    auth.logout(request)
    return redirect('/')  


    

def contact(request):
    
    context = {}

    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']

        if request.user.is_authenticated:
            user = request.user
        else:
            user = None


        contact_obj = Contact(
            user  = user,
            name = name,
            email = email,
            message = message
        )
        contact_obj.save()
        messages.info(request,'your message is recieved...')

        
        
        try:
            subject = f'contacted by {name}'
            message = message
            email_from = settings.EMAIL_HOST_USER 
            superusers = User.objects.filter(is_superuser=True)
            superusers_emails = superusers.values_list('email')
            recipient_list = [superusers[0].email,]
            send_mail( subject, message, email_from, recipient_list ) 
            print('mail successfully sent...')
        except:
            print('mail send failled...')


        
    try:
        books_cart = Cart.objects.filter(user=request.user)
        books_cart_count = 0
        for b in list(books_cart):
            books_cart_count+= int(b.quantity)
        print(books_cart_count)
        context['books_cart_count'] = books_cart_count
    except:
        print('user is not logged in...')
        
    return render(request,'contact.html',context)
