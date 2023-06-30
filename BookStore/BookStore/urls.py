"""BookStore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import to include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from books.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name="index"),
    path('index/', index, name="index"),
    path('sell/', sell_book, name="sell_book"),
    path('favourites/', favourites, name="favourites"),
    path('profile/', profile, name="profile"),
    path('login/', login_view, name="login"),
    path('register/', register_view, name="register"),
    path('logout/', logout_view, name="logout"),
    path('details/', details, name="details"),
    path('remove_favourite/', remove_favourite, name="remove_favourite"),
    path('save_book_details/', save_book_details, name="save_book_details"),
    path('delete_book/', delete_book, name="delete_book"),
    path('get_update_book/', get_update_book, name="get_update_book"),
    path('update_book/', update_book, name="update_book"),
    path('rate_book/', rate_book, name="rate_book"),
    path('purchase/', purchase, name="purchase"),
    path('refund_request/', refund_request, name="refund_request"),
    path('change_email/', change_email, name="change_email"),
    path('change_phone_number/', change_phone_number, name="change_phone_number"),
    path('change_password/', change_password, name="change_password"),
    path('deactivate_account/', deactivate_account, name="deactivate_account")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)