from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .models import User, Event, Location, Ticket, Review, Offer_message, Photo
import bcrypt
from .states import all_states
from datetime import date
import re
import os
import math


def index(request):
    
    if 'user' in request.session and request.session['user'] !=0:
        messages.success(request, 'You are logged in!')
    return render(request, 'tix_app/index.html')

def new_register(request):
    if 'user' not in request.session:
        request.session['user'] = 0
    # elif 'user' in request.session:
    #     return redirect('/main_tix_page')
    return render(request, 'tix_app/register_login.html')

def register(request):
    if request.method=='POST':
        result= User.objects.basic_validator(request.POST)
        if 'errors' in result:
            for key, value in result['errors'].items():
                messages.error(request,value)
            return redirect('/new_register')
        else:
            
            request.session['user'] = result['users'].id
            return redirect('/main_tix_page')

def login(request):
    if request.method=='POST':
        user= User.objects.get(email=request.POST['email'])
        
        if bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
            request.session['user'] = user.id
            return redirect('/main_tix_page')
        else:
            messages.error(request,'Invalid Login Attempt')
            return redirect('/new_register')

def main_tix_page(request):
    context = {
        'users': User.objects.get(id=request.session['user']),
        'tickets': Ticket.objects.order_by('-sell_score').all()
    }
    return render(request, 'tix_app/main_tix_page.html', context)

def add_ticket(request):
    context= {
        'users': User.objects.get(id=request.session['user']),
        'all_states' : all_states
    }
    return render(request, 'tix_app/add_new_ticket.html',context)

def add_ticket_process(request):
    if request.method=='POST':
        errors ={}
        today=date.today().isoformat()
        if len(request.POST['venue'])<1:
            errors['venue'] = 'Venue name required!'
        if len(request.POST['city'])< 1:
            errors['city'] = 'City required!'
        if len(request.POST['zip_code'])< 1:
            errors['zip_code'] = 'Zipcode required!'
        elif len(request.POST['zip_code']) > 6:
            errors['zip_code'] = 'Invalide Zipcode'
        if len(request.POST['event_name'])< 1:
            errors['event_name']= 'Event name required!'
        if (request.POST['event_date']) < today:
            errors['event_date'] = 'That event already passed dumb dumb!'
        elif int(request.POST['event_date'][:4]) > 2019:
            errors['event_date'] = 'Posted TiX cannot be more than one year in advance'
        if re.search('[A-Z]', request.POST['face_value']) is not None:
            errors['face_value'] = 'Please enter valid numerical price'
        elif len(request.POST['face_value'])< 1:
            errors['face-value']='Original face value required!'
        if len(request.POST['price'])< 1:
            errors['price'] = 'Ticket price required!'
        elif int(request.POST['price']) > (int(request.POST['face_value']) * 115 / 100):
            errors['price'] = 'Only 15% markup allowed'
        if len(errors):
            for key, value in errors.items():
                messages.error(request,value)
                return redirect('/add_ticket')
        else:
            location= Location.objects.create(venue_name=request.POST['venue'], city=request.POST['city'], state=request.POST['state'], zip_code=request.POST['zip_code'])
            if len(Event.objects.filter(event_name=request.POST['event_name'])) > 0:
                event = Event.objects.filter(event_name=request.POST['event_name']).first()
            else:
                event = Event.objects.create(event_name=request.POST['event_name'], location=location, event_date=request.POST['event_date'])
            event.save()
            ticket=Ticket.objects.create(price=request.POST['price'], face_value=request.POST['face_value'], event=event, event_location=location, user=User.objects.get(id=request.session['user']))
            

            if 'upload_ticket_receipt' in request.FILES and 'upload_ticket_pic' not in request.FILES:
                photo = Photo.objects.create(receipt_file=request.FILES['upload_ticket_receipt'],user=User.objects.get(id=request.session['user']), ticket=ticket)  
                if len(photo.receipt_file):
                    ticket.sell_score = 1
                ticket.save()
            if 'upload_ticket_pic' in request.FILES and 'upload_ticket_receipt' not in request.FILES: 
                photo = Photo.objects.create(photo_file=request.FILES['upload_ticket_pic'],user=User.objects.get(id=request.session['user']), ticket=ticket)
                if len(photo.photo_file):
                    ticket.sell_score = 1
                ticket.save()
           
            if 'upload_ticket_receipt' in request.FILES and 'upload_ticket_pic' in request.FILES:
                photo = Photo.objects.create(photo_file=request.FILES['upload_ticket_pic'],receipt_file=request.FILES['upload_ticket_receipt'],user=User.objects.get(id=request.session['user']), ticket=ticket)
                if len(photo.photo_file) and len(photo.receipt_file):
                    ticket.sell_score = 2
                ticket.save()
            
            messages.success(request,'Ticket Added!')
            return redirect('/add_ticket')

def your_profile(request,id):
    context={
        'users': User.objects.get(id=request.session['user']),
        'user': User.objects.get(id=Ticket.objects.filter(id=id)),
        'tickets': Ticket.objects.filter(user__id=id)
        
    }
    return render(request, 'tix_app/your_profile.html', context)

def user_profile(request,id):
    context={
        'user': User.objects.get(id=request.session['user']),
        'tickets': Ticket.objects.filter(user__id=request.session['user'])
    }
    return render(request, 'tix_app/user_profile.html', context)

def buy(request, ticket_id):
    ticket= Ticket.objects.filter(id=ticket_id)
    print(ticket.first().price)
    charge = math.ceil(ticket.first().price*.05)
    finalPrice = ticket.first().price + charge
    

    context={
        'users': User.objects.get(id=request.session['user']),
        'tickets': Ticket.objects.filter(id=ticket_id),
        'charge':charge,
        'finalPrice': finalPrice
        }
    
    return render(request, 'tix_app/buy_ticket.html', context)

def offer(request,ticket_id):
    context={
        'tickets': Ticket.objects.filter(id=ticket_id),
        'user': User.objects.get(id=request.session['user'])
    }
    return render(request, 'tix_app/offer.html', context)

def send_offer(request):
    if request.method=='POST':
        errors={}
        if len(request.POST['offer_price']) < 1:
            errors['offer_price']= 'You must submit a new price!'
        if len(errors):
           for key, value in errors.items():
               messages.error(request, value)
               return redirect('/offer/{}'.format(request.POST['hidden']))
        else:
            offer_message = Offer_message.objects.create(offer_content=request.POST['user_offer_message'], offer_price=request.POST['offer_price'], user=User.objects.get(id=request.session['user']), ticket=Ticket.objects.get(id=request.POST['hidden']))
            messages.success(request, 'Your offer has been sent!')
            return redirect('/offer/{}'.format(request.POST['hidden']))
    else:
        print('fail')
        return redirect('/offer')

def logout(request):
    request.session.clear()
    return redirect('/')

def remove_offer(request, offer_id):
    user = User.objects.get(id=request.session['user'])
    Offer_message.objects.filter(id=offer_id).delete()
    return redirect('/user_profile/{}'.format(user.id))

def accept_offer(request, offer_id):
    context = {
        'users': User.objects.get(id=request.session['user']),
        'tickets': Ticket.objects.filter(ticket_offers__id=offer_id),
        'offers': Offer_message.objects.filter(id=offer_id)
    }
    return render(request, 'tix_app/accept_offer.html',context)

def accept_offer_proccess(request):
    if request.method=='POST':
        ticket= Ticket.objects.get(id=request.POST['offer_accept'])
        ticket.sale_status = 1
        ticket.save()
        return redirect('/user_profile/{}'.format(request.session['user']))
    else:
        return redirect('/')

def delete_ticket(request,ticket_id):
    ticket = Ticket.objects.filter(id=ticket_id)
    ticket.delete()
    return redirect('/user_profile/{}'.format(request.session['user']))

def edit(request, ticket_id):
    context= {
        'user': User.objects.get(id=request.session['user']),
        'tickets': Ticket.objects.filter(id=ticket_id)
    }
    return render(request, 'tix_app/edit.html', context)

def edit_ticket_process(request):
    if request.method=='POST':
        ticket = Ticket.objects.filter(id=request.POST['edit_hidden'])
        if 'price' in request.POST['price']:
            ticket.update(price=request.POST['price'])
        if 'upload_ticket_pic' in request.FILES and 'upload_ticket_receipt' not in request.FILES:
            photo = Photo.objects.filter(ticket=Ticket.objects.filter(id=request.POST['edit_hidden']))
            photo.delete()
            Photo.objects.create(photo_file=request.FILES['upload_ticket_pic'], user=User.objects.get(id=request.session['user']), ticket=Ticket.objects.get(id=request.POST['edit_hidden']))
            ticket.update(sell_score=1)
            

        if 'upload_ticket_receipt' in request.FILES and 'upload_ticket_pic' not in request.FILES:
            photo = Photo.objects.filter(ticket=Ticket.objects.filter(id=request.POST['edit_hidden']))
            photo.delete()
            Photo.objects.create(receipt_file=request.FILES['upload_ticket_receipt'], user=User.objects.get(id=request.session['user']), ticket=Ticket.objects.get(id=request.POST['edit_hidden']))      
            ticket.update(sell_score=1)

        if 'upload_ticket_receipt' in request.FILES and 'upload_ticket_pic' in request.FILES:
            photo = Photo.objects.filter(ticket=Ticket.objects.filter(id=request.POST['edit_hidden']))
            photo.delete()
            photo = Photo.objects.filter(ticket=Ticket.objects.filter(id=request.POST['edit_hidden']))
            photo.delete()
            Photo.objects.create(photo_file=request.FILES['upload_ticket_pic'],receipt_file=request.FILES['upload_ticket_receipt'], user=User.objects.get(id=request.session['user']), ticket=Ticket.objects.get(id=request.POST['edit_hidden']))
            ticket.update(sell_score=2)
        
        return redirect('/user_profile/{}'.format(request.session['user']))

def buy_process(request):
    if request.method=='POST':
        ticket= Ticket.objects.get(id=request.POST['buy_hidden'])
        ticket.sale_status = 1
        ticket.save()
        
        messages.success(request, 'Payment has been sent to the TiX Admin account!  Your TiX will be sent to you after it has been verified!')

    return redirect('/buy/{}'.format(ticket.id))

def search_events(request):
    context ={
        'events': Event.objects.filter(event_name__startswith=request.POST['searchbar']),
        'user': User.objects.get(id=request.session['user']),
        'tickets': Ticket.objects.filter(event__event_name__startswith=request.POST['searchbar']).order_by('-sell_score')
    }
    return render(request, 'tix_app/event_search.html', context)

    