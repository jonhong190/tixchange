from __future__ import unicode_literals
from django.db import models
import bcrypt
import re
from datetime import date
from django.contrib import admin

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
    def basic_validator(self,postData):
        errors ={}
        if len(postData['first_name']) < 2:
            errors['first_name'] = 'First name must be at least 2 characters long!'
        elif len(postData['first_name']) < 1:
            errors['first_name'] = 'First name required!'
        if len(postData['last_name']) < 2:
            errors['last_name'] = 'Last name must be at least 2 characters long!'
        elif len(postData['last_name']) < 1:
            errors['last_name'] = 'Last name required!'    
        if len(postData['username']) < 2:
            errors['username'] = 'Username must be at least 2 characters long!'
        elif User.objects.filter(username=postData['username']).exists():
            errors['username'] = 'Username already taken'
        elif len(postData['username'])< 1:
            errors['username'] = 'Username required!'
        if len(postData['email']) < 1:
            errors['email'] = 'Email required!'
        elif not EMAIL_REGEX.match(postData['email']):
            errors['email']= 'Invalid Email Format!'
        elif User.objects.filter(email=postData['email']).exists():
            errors['password'] = 'Email already registered!'
        if len(postData['password']) < 8:
            errors['password'] = 'Password must be at least 8 characters long!'
        elif postData['password'] != postData['confirm']:
            errors['password'] = 'Passwords must match!'
        elif len(postData['password']) < 1:
            errors['password'] = 'Password required!'
        if len(postData['confirm']) < 1:
            errors['confirm'] = 'Please confirm password!'
        if len(postData['birthday']) < 1:
            errors['birthday'] = 'Please enter birthday!'
        elif int(postData['birthday'][:4]) > 2000:
            errors['birthday'] = 'You must be at least 18 years old to register!'
        if len(errors):
            result={
                'errors': errors
            }
            return result
        else:
            users= self.create(first_name=postData['first_name'], last_name=postData['last_name'], username=postData['username'], email=postData['email'], password=bcrypt.hashpw(postData['password'].encode(), bcrypt.gensalt()), birthday=postData['birthday'])

            result= {
                'users': users
            }
            return result


class User(models.Model):
    first_name=models.CharField(max_length=255)
    last_name=models.CharField(max_length=255)
    username=models.CharField(max_length=255, unique=True)
    email=models.CharField(max_length=255, unique=True)
    birthday=models.CharField(max_length=25)
    password=models.CharField(max_length=255, default='')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects=UserManager()
    # def __str__(self):
    #     return '%s '(self.username)

class Location(models.Model):
    venue_name=models.CharField(max_length=255)
    city=models.CharField(max_length=255)
    state=models.CharField(max_length=255, default='')
    zip_code=models.IntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class Event(models.Model):
    event_date=models.CharField(max_length=255, default='')
    event_name=models.CharField(max_length=255, unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    location=models.ForeignKey(Location, related_name='events', default='')
    
class Ticket(models.Model):
    price=models.IntegerField(default=0)
    AVERAGE = 0
    GOOD= 1
    GREAT= 2
    SELL_SCORE_CHOICES=(
        (AVERAGE, 'average'),
        (GOOD, 'good'),
        (GREAT, 'great')
    )
    sell_score=models.IntegerField(
        choices= SELL_SCORE_CHOICES,
        default=AVERAGE
    )
    face_value=models.IntegerField(default=0)
    AVAILABLE = 0
    PENDING= 1
    SOLD= 2
    SALE_STATUS_CHOICES = (
        (AVAILABLE,'available'),
        (PENDING, 'pending'),
        (SOLD, 'sold'),
    )
    sale_status= models.IntegerField(
        # max_length=1,
        choices = SALE_STATUS_CHOICES,
        default= AVAILABLE
    )
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    event=models.ForeignKey(Event, related_name='event_tickets')
    event_location=models.ForeignKey(Location, related_name='event_tickets_locations')
    user=models.ForeignKey(User, related_name='ticket_posts')
    def __str__(self):
        return 'Seller:%s, Event:%s, Price:%s, Face Value:%s, Status:%s' %(self.user.username, self.event.event_name, self.price, self.face_value, self.sale_status)

class Photo(models.Model):
    receipt_file=models.FileField(upload_to='receipt', default='')
    photo_file=models.FileField(upload_to='ticket_photo', default='')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    user=models.ForeignKey(User, related_name='photo_uploads',default='')
    ticket=models.ForeignKey(Ticket,related_name='ticket_photos', default='')

class Review(models.Model):
    review_content=models.TextField(max_length=1000)
    seller_rating=models.IntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    user=models.ForeignKey(User, related_name='seller_reviews')

class Offer_message(models.Model):
    offer_content=models.TextField(max_length=1000)
    offer_price=models.IntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    user=models.ForeignKey(User, related_name='user_offers')
    ticket=models.ForeignKey(Ticket, related_name='ticket_offers')