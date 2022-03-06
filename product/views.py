from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from product.models import *
import pandas as pd
import numpy as np
import sklearn
from sklearn.decomposition import TruncatedSVD
import warnings
from django.contrib.auth.decorators import login_required

# Create your views here.


def mail():
    subject = 'welcome '
    message = f'Hi {request.user.username}, thank you'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['email', ]
    return send_mail(subject, message, email_from, recipient_list)


def products(request, category):

    try:
        all_books = Book.objects.filter(category=Category.objects.get(name=category)).order_by('-rating')
        all_books_count = len(all_books)
    except:
        try:
            all_books = Book.objects.filter(category=(Book.objects.get(id=int(category))).category).order_by('-rating')
            all_books_count = len(all_books)

        except:
            all_books = []
            all_books_count = 0

    context = {
        'all_books': all_books,
        'all_books_count': all_books_count
    }

    # if request.method == 'POST' and 'cart' in request.POST:

    #     cart_obj = Cart.objects.filter(user=request.user).filter(book=Book.objects.get(id=int(category)))

    #     if len(cart_obj) > 0:
    #         cart_obj.update(quantity=(cart_obj[0].quantity+1))
    #         print(cart_obj)
    #         print('cart obj updated...')

    #     else:
    #         cart = Cart(
    #             user = request.user,
    #             book = Book.objects.get(id=int(category)),
    #             quantity = 1
    #         ) 
    #         cart.save()
    #         print('cart obj created...')

    try:
        books_cart = Cart.objects.filter(user=request.user)
        books_cart_count = 0
        for b in list(books_cart):
            books_cart_count+= int(b.quantity)
        print(books_cart_count)
        context['books_cart_count'] = books_cart_count
    except:
        print('user is not logged in...')

    return render(request, 'products.html', context)



def product_details(request, pk):
    book = Book.objects.get(id=pk)
    try:
        recomendations = Recommendation.objects.filter(user=request.user)
        if len(recomendations) < 1:
            recomendations = Book.objects.filter(rating__gte=3).order_by('-rating')
    except:
        recomendations = Book.objects.filter(rating__gte=3).order_by('-rating')
    
    print('recom: ',recomendations)
    context = {
        'book': book,
        'recomendations': recomendations
    }
    
    try:
        books_cart = Cart.objects.filter(user=request.user)
        books_cart_count = 0
        for b in list(books_cart):
            books_cart_count+= int(b.quantity)
        print(books_cart_count)
        context['books_cart_count'] = books_cart_count
    except:
        print('user is not logged in...')
    
    return render(request, 'product_details.html', context)



@login_required(login_url='login')
def checkout(request):
    books_in_cart = Cart.objects.filter(user=request.user)
    total_price = 0
    for book in books_in_cart:
        total_price+=(book.quantity*book.book.price)
    
    context = {
        'books_in_cart': books_in_cart,
        'cart_books_count': len(books_in_cart),
        'message': 'Sorry, No book in your Cart!!!',
        'message_color': 'red',
        'total_price': total_price
    }

    if request.method == "POST" and 'order' in request.POST:

        for book in books_in_cart:
            existed_order = Order.objects.filter(user=request.user).filter(book=book.book).filter(status='Ordered')

            if len(existed_order) > 0:
                existed_order.update(quantity=(existed_order[0].quantity+book.quantity))
                print('existed order...')
            else:
                order = Order(
                    user = request.user,
                    book = book.book,
                    quantity = book.quantity,
                    full_name = request.POST['full_name'],
                    city = request.POST['city'],
                    address = request.POST['address'],
                    landmark = request.POST['landmark'],
                    address_type = request.POST['address_type'],
                    phone = request.POST['phone']
                )
                order.save()
                print('order created...')

        books_in_cart.delete()
        context['cart_books_count'] = 0
        context['message'] = 'Thanks for ordering...'
        context['message_color'] = 'green'

        try:
            subject = f'order by {request.user}'
            message = f'you ordered book is :{book.book}--- quantity :--> {book.quantity}  thank you for ordering from our website to check the status of your order click on the order tab to see the status of your order '
            email_from = settings.EMAIL_HOST_USER
            superusers = User.objects.filter(is_superuser=True)
            superusers_emails = superusers.values_list('email')
            recipient_list = [superusers[0].email, request.user.email]
            send_mail(subject, message, email_from, recipient_list)
            print('mail successfully sent...')
        except:
            print('mail send failled...')

    return render(request, 'checkout.html', context)


@login_required(login_url='login')
def orders(request):

    if request.method == 'POST' and 'rated' in request.POST:
        book_id = request.POST['book_id']
        rating = request.POST['rating']
        comment = request.POST['comment']
        book = Book.objects.get(id=book_id)

        existed_feedback = Feedback.objects.filter(
            user=request.user).filter(book=Book.objects.get(id=book_id))

        if len(existed_feedback) > 0:
            print('existed feedback...')
            existed_feedback.update(rating=rating, comment=comment)

            order_obj = Order.objects.filter(id=request.POST['order_id']).update(rated=True)
            feedbacks = Feedback.objects.filter(book=book)
            ratings = []
            for feedback in feedbacks:
                ratings.append(feedback.rating)

            avg_rating = sum(ratings) // len(ratings)
            book_rating = Book.objects.filter(id=book_id).update(rating=avg_rating)
            print('feedback upadated...')

        else:
            feedback = Feedback(
                user = request.user,
                book = book,
                rating = rating,
                comment = comment
            )
            feedback.save()
            print('feedback saved...')
            
            order_obj = Order.objects.filter(id=request.POST['order_id']).update(rated=True)
            
            feedbacks = Feedback.objects.filter(book=book)
            ratings = []
            for feedback in feedbacks:
                ratings.append(feedback.rating)

            avg_rating = sum(ratings) / len(rating)
            book_rating = Book.objects.filter(id=book_id).update(rating=avg_rating)           

            try:
                subject = f'order by {request.user}'
                message = f'you ordered book is :{book.book}--- quantity :--> {book.quantity}    *****thank you for ordering from our website to check the status of your order click on the order tab to see the status of your order '
                email_from = settings.EMAIL_HOST_USER
                superusers = User.objects.filter(is_superuser=True)
                superusers_emails = superusers.values_list('email')
                recipient_list = [superusers[0].email, request.user.email]
                send_mail(subject, message, email_from, recipient_list)
                print('mail successfully sent...')
            except:
                print('mail send failled...')

    all_orders = Order.objects.filter(user=request.user)
    delivered_orders = all_orders.filter(status='Delivered').filter(rated=False)
    context = {
        'all_orders': all_orders,
        'delivered_orders': delivered_orders,
        'all_orders_count': len(all_orders),
        'delivered_orders_count': len(delivered_orders)
    }

    
    try:
        books_cart = Cart.objects.filter(user=request.user)
        books_cart_count = 0
        for b in list(books_cart):
            books_cart_count+= int(b.quantity)
        print(books_cart_count)
        context['books_cart_count'] = books_cart_count
    except:
        print('user is not logged in...')

    return render(request, 'orders.html', context)


@login_required(login_url='login')
def recomendation(request):
    all_feedback = Feedback.objects.all()
    all_good_book = Book.objects.filter(rating__gte=3).order_by('-rating')
    current_user_feedback = Feedback.objects.filter(user=request.user).order_by('-rating')

    try:
        feedback_dictionary = {}
        feedback_matrix = []
        for feedback in all_feedback:
            single_feedback = {}
            single_feedback['user'] = feedback.user
            single_feedback['book'] = feedback.book
            single_feedback['rating'] = feedback.rating

            feedback_dictionary[feedback.user] = single_feedback
            feedback_matrix.append(single_feedback)
        print('feedback_matrix:', feedback_matrix)

        df = pd.DataFrame(data=feedback_matrix)
        print(df)
        book_rating_pivot = df.pivot(index='user', columns='book', values='rating').fillna(0)
        print(book_rating_pivot)
        X = book_rating_pivot.values.T
        X.shape
        SVD = TruncatedSVD(n_components=len(book_rating_pivot)-1, random_state=17)
        matrix = SVD.fit_transform(X)
        matrix.shape

        warnings.filterwarnings("ignore", category=RuntimeWarning)
        corr = np.corrcoef(matrix)
        corr.shape
        book_title = book_rating_pivot.columns
        book_title_list = list(book_title)
        coffey_hands = book_title_list.index(current_user_feedback[0].book)

        corr_coffey_hands = corr[coffey_hands]
        recomended_books = (list(book_title[(corr_coffey_hands >= 0.9)]))
        print('recomended_books: ',recomended_books)

        for recom in recomended_books:
            if Recommendation.objects.filter(user=request.user).filter(book=recom).exists():
                print(f'{recom} is already recomended')
            else:
                if recom.rating > 2:
                    recom_obj = Recommendation(
                        user=request.user,
                        book=recom
                    )
                    recom_obj.save()
                    print(f'{recom} recom saved')
                else:
                    print(f'recomended book "{recom}" is underrated!!!')

        final_recommendations = []
        for b in Recommendation.objects.filter(user = request.user):
            final_recommendations.append(b.book)
        context = {
            'all_books': final_recommendations,
            'all_books_count': len(final_recommendations)
        }

    except :
        print('not enough data found...')
        context = {
            'all_books': all_good_book,
            'all_books_count': len(all_good_book)
        }
    
    
    try:
        books_cart = Cart.objects.filter(user=request.user)
        books_cart_count = 0
        for b in list(books_cart):
            books_cart_count+= int(b.quantity)
        context['books_cart_count'] = books_cart_count
    except:
        print('user is not logged in...')

    return render(request, 'products.html', context)





# Functions for ajax request

def books_cart_count(request):
    books_cart_count = Cart.objects.filter(user = request.user).count()
    print('data from ajax request: ',books_cart_count)
    return books_cart_count


def add_book(request):
    print('in add_book section...')
    if request.user.is_authenticated:
        print('user is logged in...')
        if request.method == 'POST':
            cart_obj_id = request.POST['post_id']
            print('cart_obj_id =====>>', cart_obj_id)
            cart_obj = Cart.objects.filter(user=request.user).filter(book=Book.objects.get(id=int(cart_obj_id)))
            print('cart_obj =====>>', cart_obj)

            if len(cart_obj) > 0:
                cart_obj.update(quantity=(cart_obj[0].quantity+1))
                print('book is found in cart...')
                print('book is added...')

            else:
                print('book is not found in cart...')
                cart = Cart()
                cart.user = request.user
                cart.book = Book.objects.get(id=int(cart_obj_id))
                cart.quantity = 1
                cart.save()
                print('book is added in cart...')

        return HttpResponse('ok')

    else:
        print('user is not logged in...')
        return HttpResponse('ok')


def remove_book(request):
    print('in remove_book section...')
    if request.user.is_authenticated:
        print('user is logged in...')
        if request.method == 'POST':
            cart_obj_id = request.POST['post_id']
            print('cart_obj_id =====>>', cart_obj_id)
            cart_obj = Cart.objects.filter(user=request.user).filter(book=Book.objects.get(id=int(cart_obj_id)))
            print('cart_obj =====>>', cart_obj)

            if len(cart_obj) > 0 and cart_obj[0].quantity > 1 :
                cart_obj.update(quantity=(cart_obj[0].quantity-1))
                print('book is found in cart...')
                print('book is removed...')

            else:
                
                print('book is not found in cart...')
                # cart = Cart()
                # cart.user = request.user
                # cart.book = Book.objects.get(id=int(category))
                # cart.quantity = 1
                # cart.save()
                # print('book is added in cart...')

        return HttpResponse('ok')

    else:
        print('user is not logged in...')
        return HttpResponse('ok')

def del_book_from_cart(request):
    print('in del_book_from_cart section...')
    if request.user.is_authenticated:
        print('user is logged in...')
        if request.method == 'POST':
            cart_obj_id = request.POST['post_id']

            #cart_obj = Cart.objects.filter(user=request.user).filter(book=Book.objects.get(id=int(category)))
            cart_obj = Cart.objects.get(id=cart_obj_id)
            print('cart_obj =====>>', cart_obj)
            cart_obj.delete()
            print('cart obj is deleted...')

            # if len(cart_obj) > 0:
            #     cart_obj.update(quantity=(cart_obj[0].quantity-1))
            #     print(cart_obj)
            #     print('found')

            # else:
            #     print('not found')
            #     # cart = Cart()
            #     # cart.user = request.user
            #     # cart.book = Book.objects.get(id=int(category))
            #     # cart.quantity = 1
            #     # cart.save()

        return HttpResponse('ok')

    else:
        print('user is not logged in...')
        return HttpResponse('ok')
