import datetime
import json
import string

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models.fields.files import ImageFieldFile
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.http import require_POST

from books.models import UserProfile, Book, BookGenre, StoreUserSavedBooks, UserRatedBooks, BookPurchases
from django.contrib import messages


def register_view(request):
    if request.POST:
        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]
        user = User.objects.create_user(username=username, password=password, email=email)
        user_profile = UserProfile.objects.create(user=user)
        login(request, user)
        # print(password)
        return redirect('index')
    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            error_message = "Invalid username or password. Please try again."
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect('login')


def index(request):
    search_result = None
    reserved = False
    message = None
    is_search = False
    is_select = False
    book_name = None
    input_genres = None
    books_per_page = 20
    if request.POST:
        try:
            book_name = request.POST["book_name"]
        except Exception:
            pass
        try:
            input_genres = request.POST.getlist("input_genre")

        except Exception:
            pass
        reserved = True
        if book_name is not None:
            search_result = Book.objects.filter(title__icontains=book_name)
            is_search = True
            if len(search_result) == 0:
                search_result = None
                message = "No books matching your search term were found."
        elif input_genres is not None:
            genre_book = BookGenre.objects.filter(genre__in=input_genres)
            book_keys = genre_book.values_list('book', flat=True)
            search_result = Book.objects.filter(pk__in=book_keys)
            is_select = True
            if len(search_result) == 0:
                is_select = None
                message = "No books were found"
    queryset = Book.objects.all()
    paginator = Paginator(queryset, books_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"books": page_obj,
               "search_result": search_result,
               "reserved": reserved,
               "message": message,
               "is_search": is_search,
               "is_select": is_select,
               "book_name": book_name,
               "input_genres": input_genres,
               "pagination_books": page_obj,
               "site": "index"}
    return render(request, "index.html", context)


@login_required(login_url='login')
def sell_book(request):
    if request.POST:
        if request.user is None:
            return redirect("login")

        cover_image = None
        try:
            cover_image = request.FILES["cover_image"]
        except MultiValueDictKeyError:
            pass

        title = request.POST["title"]
        author = request.POST["author"]
        description = request.POST["description"]
        genres = request.POST.getlist("book_genre")
        price = request.POST["price"]

        flag = False
        error_messages = []

        if not title:
            error_messages.append("The field 'Title' is required")
            flag = True
        if not price:
            error_messages.append("The field 'Price' is required")
            flag = True
        if flag:
            errors = {"errors": error_messages}
            return render(request, "sell.html", errors)

        added_on = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        book = Book.objects.create(title=title, author=author, added_on=added_on, price=price, rating=0,
                                   description=description, cover_image=cover_image, user=request.user)
        for genre in genres:
            BookGenre.objects.create(book=book, genre=genre)
        return redirect("index")
    return render(request, "sell.html")


@login_required(login_url='login')
def favourites(request):
    books_per_page = 20
    if request.POST:
        book_id = request.POST["book_id"]
        book = Book.objects.get(pk=book_id)
        if not StoreUserSavedBooks.objects.filter(user=request.user, book=book).exists():
            StoreUserSavedBooks.objects.create(user=request.user, book=book)
        return redirect("index")
    saved_books = StoreUserSavedBooks.objects.filter(user=request.user)
    book_ids = saved_books.values_list('book', flat=True)
    books = Book.objects.filter(id__in=book_ids)

    paginator = Paginator(books, books_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {"books": page_obj}
    return render(request, "favourites.html", context)


@login_required(login_url='login')
def save_book_details(request):
    if request.POST:
        book_id = request.POST["book_id"]
        book = Book.objects.get(pk=book_id)
        if not StoreUserSavedBooks.objects.filter(user=request.user, book=book).exists():
            StoreUserSavedBooks.objects.create(user=request.user, book=book)
        genres = BookGenre.objects.filter(book=book)
        context = {"book": book, "genres": genres, "saved": True}
        return render(request, "details.html", context)
    return redirect("index")


@login_required(login_url='login')
def remove_favourite(request):
    if request.POST:
        book_id = request.POST["book_id"]
        book = Book.objects.get(pk=book_id)
        book_to_delete = StoreUserSavedBooks.objects.get(user=request.user, book=book)
        book_to_delete.delete()
    return redirect("favourites")


@login_required(login_url='login')
def profile(request):
    queryset = Book.objects.filter(user=request.user)
    transactions = BookPurchases.objects.filter(user=request.user)
    profile_settings = UserProfile.objects.get(user=request.user)
    books_per_page = 20
    transactions_per_page = 10

    paginator = Paginator(queryset, books_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    paginator_transactions = Paginator(transactions, transactions_per_page)
    page_number_transactions = request.GET.get('page_transactions')
    page_transactions = paginator_transactions.get_page(page_number_transactions)

    context = {"books": page_obj, "transactions": page_transactions, "settings": profile_settings}
    return render(request, "profile.html", context)


def details(request):
    if request.POST:
        book_id = request.POST["book_id"]
        book = Book.objects.get(pk=book_id)
        genres = BookGenre.objects.filter(book=book)
        rated = None
        phone_number = None
        purchase_permission = True
        if UserRatedBooks.objects.filter(user=request.user, book=book).exists():
            rated = UserRatedBooks.objects.get(user=request.user, book=book).rating
        if UserProfile.objects.get(user=book.user):
            phone_number = UserProfile.objects.get(user=book.user).contact
        if book.user == request.user:
            purchase_permission = False

        context = {"book": book,
                   "genres": genres,
                   "rated": rated,
                   "phone": phone_number,
                   "purchase_permission": purchase_permission}
        return render(request, "details.html", context)
    return redirect("index")


@login_required(login_url='login')
# @require_POST
def delete_book(request):
    if request.POST:
        book_id = request.POST["book_id"]
        try:
            book = Book.objects.get(pk=book_id, user=request.user)
            book_genres = BookGenre.objects.filter(book=book)
            saved_book = StoreUserSavedBooks.objects.filter(book=book)
            for b in book_genres:
                b.delete()
            for b in saved_book:
                b.delete()
            book.delete()
            queryset = Book.objects.filter(user=request.user)
            context = {"books": queryset, "deleted": True}
            return render(request, "profile.html", context)
        except Book.DoesNotExist:
            return redirect("profile")
    return redirect("index")


@login_required(login_url='login')
def get_update_book(request):
    if request.POST:
        book_id = request.POST["book_id"]
        book = Book.objects.get(pk=book_id)
        book_genres = BookGenre.objects.filter(book=book)
        genres = book_genres.values_list("genre", flat=True)
        genres_json = json.dumps(list(genres))
        context = {"book": book, "genres": genres}
        return render(request, "updateBook.html", context)
    return redirect("index")


@login_required(login_url='login')
def update_book(request):
    if request.POST:
        book_id = request.POST["book_id"]
        book = Book.objects.get(pk=book_id)
        title = request.POST["title"]
        author = request.POST["author"]
        price = request.POST["price"]
        genres = request.POST.getlist("book_genre")
        description = request.POST["description"]
        cover_image = None
        try:
            cover_image = request.FILES["cover_image"]
        except MultiValueDictKeyError:
            pass

        error_messages = []
        failed = False

        if not title:
            error_messages.append("Title is required")
            failed = True
        if not price:
            error_messages.append("Price is required")
            failed = True

        if not failed:
            book.title = title
            book.author = author
            book.price = price
            book.description = description
            if cover_image is not None:
                book.cover_image = cover_image
            book_genres = BookGenre.objects.filter(book=book)
            for genre in book_genres:
                genre.delete()
            for genre in genres:
                BookGenre.objects.create(book=book, genre=genre)
            book.save()
            book_genres = BookGenre.objects.filter(book=book)
            context = {"book": book, "genres": book_genres}
            return render(request, "details.html", context)
        if failed:
            book_genres = BookGenre.objects.filter(book=book)
            genres = book_genres.values_list("genre", flat=True)
            context = {"book": book, "genres": genres, "errors": error_messages}
            return render(request, "updateBook.html", context)
    return redirect("index")


@login_required(login_url='login')
def rate_book(request):
    if request.method == "POST":
        rating = int(request.POST.get("book_rating"))  # print("rate: ", isinstance(rating, str))
        book_id = request.POST.get("book_id")
        book = Book.objects.get(pk=book_id)
        rated_successfully = None
        message = None
        user_rate = None
        rated = None
        if book.user == request.user:
            rated_successfully = False
            message = "You cannot rate your own book."
        else:
            if rating == 0:  # user chooses to remove the rating
                to_delete = UserRatedBooks.objects.get(user=request.user, book=book)
                to_delete.delete()
                book.total_times_rated -= 1

            elif UserRatedBooks.objects.filter(user=request.user, book=book).exists():  # user updates his rating
                user_rate = UserRatedBooks.objects.get(user=request.user, book=book)
                user_rate.rating = rating
                user_rate.save()
                user_rate = user_rate.rating
            elif not rating == 0:  # user rates the book for the first time
                user_rate = UserRatedBooks.objects.create(user=request.user, book=book, rating=rating)
                book.total_times_rated += 1

            ratings = UserRatedBooks.objects.filter(book=book).values_list("rating", flat=True)
            if len(ratings) == 0:  # to avoid 0 / 0 in case it's the last rating for that book
                book.rating = 0
            else:
                sum_rating = 0
                for r in ratings:
                    sum_rating += r
                book.rating = sum_rating / book.total_times_rated
            book.save()
            rated_successfully = True
            rated = user_rate  # the previous rating that the user entered
            message = "Thank you for rating the book!"
        genres = BookGenre.objects.filter(book=book)
        context = {"book": book,
                   "genres": genres,
                   "rated_successfully": rated_successfully,
                   "rate_book_called": True,
                   "message": message,
                   "rated": rated}
        return render(request, "details.html", context)
    return redirect("index")


@login_required(login_url='login')
def purchase(request):
    if request.method == "POST":
        book_id = request.POST.get("book_id")
        book = Book.objects.get(pk=book_id)
        purchased_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if book is not None:
            BookPurchases.objects.create(user=request.user, book=book, purchased_at=purchased_at)
            return JsonResponse({'message': 'Successfully'})
        else:
            return JsonResponse({'message': 'Something went wrong... Please try again later.'})
    return redirect("index")


@login_required(login_url='login')
def refund_request(request):
    if request.method == "POST":
        transaction_id = request.POST.get("transaction_id")
        transaction = None
        now = datetime.datetime.now()
        message = None
        refund_success = False
        try:
            transaction = BookPurchases.objects.get(pk=transaction_id)
            purchased_at = transaction.purchased_at
            three_days_ago = now - datetime.timedelta(days=3)
            purchased_at = purchased_at.replace(tzinfo=None)  # Remove timezone information
            if purchased_at > three_days_ago:
                transaction.delete()
                message = "Transaction refunded successfully."
                refund_success = True
            else:
                message = "Transaction refund failed. Three days have not yet expired."
            queryset = Book.objects.filter(user=request.user)
            transactions = BookPurchases.objects.filter(user=request.user)
            profile_settings = UserProfile.objects.get(user=request.user)
            print("email: ", profile_settings.user.email)
            context = {"books": queryset, "transactions": transactions, "message": message,
                       "refund_success": refund_success,
                       "settings": profile_settings}
            return render(request, "profile.html", context)
        except Exception:
            transaction = None
    return redirect("index")


@login_required(login_url='login')
@require_POST
def change_phone_number(request):
    try:
        phone_number = request.POST.get("change_phone_number")
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.contact = phone_number
        user_profile.save()
        messages.success(request, "Your phone number has been successfully updated.")
    except Exception:
        messages.error(request, "Something went wrong... Please try again later.")

    return redirect("profile")


@login_required(login_url='login')
@require_POST
def change_email(request):
    try:
        email = request.POST.get("change_email")  # Updated the form field name to "change_email"
        user = request.user
        user.email = email
        user.save()
        messages.success(request,
                         "Your email has been successfully updated.")  # Use Django's messages framework for success message
    except Exception:
        messages.error(request,
                       "Something went wrong... Please try again later.")  # Use Django's messages framework for error message
    return redirect("profile")  # Redirect to the profile page after updating email


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = authenticate(request, username=request.user.username, password=current_password)

        if user is not None and new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Update the session with the new password hash
            messages.success(request, 'Your password has been successfully changed.')
            return redirect('profile')  # Replace 'profile' with the appropriate URL name for the profile page
        else:
            messages.error(request,
                           'Please enter a valid current password and ensure the new password matches the confirmation.')
            return redirect('profile')

    return redirect("index")


@login_required(login_url='login')
def deactivate_account(request):
    if request.method == 'POST':
        password = request.POST.get("password")
        user = authenticate(request, username=request.user.username, password=password)
        if user is not None:
            books = Book.objects.filter(user=user)
            for book in books:
                book.delete()
            user.is_active = False
            user.save()
            logout(request)  # Log out the user after deactivating the account
            messages.success(request, 'Your account has been deactivated.')
            return redirect('login')
        else:
            messages.error(request, 'Make sure your password is correct.')
            return redirect("profile")
    return redirect("index")
