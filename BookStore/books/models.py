from django.contrib.auth.models import User, AbstractUser
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    biography = models.TextField(max_length=1000, null=True, blank=True)
    contact = models.CharField(max_length=15, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    added_on = models.DateTimeField()
    price = models.FloatField()
    rating = models.FloatField()
    total_times_rated = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    cover_image = models.ImageField(upload_to="data/", default="static/no_image.png")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class BookGenre(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    genre = models.CharField(max_length=100)


class StoreUserSavedBooks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)


class UserRatedBooks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.IntegerField(default=3)


class BookPurchases(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField()
