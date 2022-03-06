from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('products/<str:category>', views.products,name = 'products'),
    path('product_details/<str:pk>',views.product_details,name='product_details'),
    path('checkout',views.checkout,name='checkout'),
    path('orders',views.orders,name='orders'),
    path('recomendation',views.recomendation,name='recom'),
    path('books_cart_count',views.books_cart_count,name='books_cart_count'),
    path('add_book',views.add_book,name='add_book'),
    path('remove_book',views.remove_book,name='remove_book'),
    path('del_book_from_cart',views.del_book_from_cart,name='del_book_from_cart'),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="password_reset.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"), name="password_reset_complete"),
   
]