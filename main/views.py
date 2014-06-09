from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from main.models import *

import hashlib

import json # For javascript responses
from collections import defaultdict # nested dictionaries

from django.core.cache import cache

from django.conf import settings

# How long items should stay in the cache
CACHE_TIMEOUT = 60

#####################
# Private Functions #
#####################
def initContext(request):
    ''' Initialize the context object'''
    context = {}
    context['urlPrefix'] = settings.URL_PREFIX
    if 'iv' in request.GET:
        context['invalid'] = request.GET['iv']
    context['error'] = []
    return context

# Cache Keys
def get_stadium_key(stadiumName):
    '''Store a Stadium object by name'''
    return hashlib.md5("stadium|%s" % stadiumName).hexdigest()

def get_vendor_key(stadiumName, vendorName):
    '''Store a Vendor object by stadium vendor keypair'''
    return hashlib.md5("stadium|%s vendor|%s" % (stadiumName,vendorName)).hexdigest()

def get_items_key(stadiumName, vendorName):
    '''Store an item list for a given vendor object by its stadium vendor keypair'''
    return hashlib.md5("stadium|%s vendor|%s items" % (stadiumName,vendorName)).hexdigest()

def get_item_key(stadiumName, vendorName, itemName):
    '''Store a single item for a given vendor by its stadium vendor item keytrio'''
    return hashlib.md5("stadium|%s vendor|%s item|%s" % (stadiumName, vendorName,itemName)).hexdigest()

#########
# Views #
#########
def home(request):
    '''Home Landing Page'''
    context = initContext(request)
    if 'invalid' in context:
        context['error'].append( "Unknown Stadium: %s" % context['invalid'])
    stadium_list = Stadiums.objects.all()
    context['stadiums'] = stadium_list
    return render_to_response('home.html',context,context_instance=RequestContext(request))

def StadiumView(request, stadiumName=None):
    '''A Specific Stadium'''
    context = initContext(request)
    if 'invalid' in context:
        context['error'].append( "Unknown Vendor: %s" % context['invalid'])

    cache_stadium_key = get_stadium_key(stadiumName)
    foundStadium = cache.get(cache_stadium_key)
    
    try:
        if foundStadium is None:
            print "Stadium miss"
            foundStadium = Stadiums.objects.get(name=stadiumName)
            cache.set(cache_stadium_key, foundStadium, CACHE_TIMEOUT)
    except Stadiums.DoesNotExist:
        return HttpResponseRedirect(settings.URL_PREFIX + "?iv=%s" % stadiumName)
    
    context['stadium'] = foundStadium
    # Get a list of vendors for this stadium
    vendorList = Vendors.objects.filter(stadium=context['stadium'].id)
    context['vendorList'] = vendorList
    return render_to_response('stadium_view.html',context,context_instance=RequestContext(request))

def VendorView(request, stadiumName=None, vendorName=None):
    '''A Specific Vendor (for a specific stadium'''
    context = initContext(request)
    if 'invalid' in context:
        context['error'].append("Unknown Item: %s" % context['invalid'])

    # Generate Cache Keys
    cache_stadium_key = get_stadium_key(stadiumName)
    cache_vendor_key = get_vendor_key(stadiumName,vendorName)
    cache_items_key = get_items_key(stadiumName,vendorName)

    # The Stadium object
    foundStadium = cache.get(cache_stadium_key)
    # The Vendor object
    foundVendor = cache.get(cache_vendor_key)
    # The list of items belonging to this vendor
    itemList = None
    # Do not trust the itemlist if the vendor has been invalidated
    if foundVendor is not None:
        itemList = cache.get(cache_items_key)

    try:
        if foundStadium is None:
            print "miss stadium"
            foundStadium = Stadiums.objects.get(name=stadiumName)
            cache.set(cache_stadium_key,foundStadium,CACHE_TIMEOUT)
        if foundVendor is None:
            print "miss vendor"
            foundVendor = Vendors.objects.get(stadium=foundStadium.id, name=vendorName)
            cache.set(cache_vendor_key,foundVendor,CACHE_TIMEOUT) 
    except Stadiums.DoesNotExist:
        return HttpResponseRedirect(settings.URL_PREFIX + "?iv=%s" % stadiumName)
    except Vendors.DoesNotExist:
        return HttpResponseRedirect(settings.URL_PREFIX + stadiumName + '/' + "?iv=%s" % vendorName)

    if itemList is None:
        print "miss items"
        itemList = Vendor_items.objects.filter(vendor=foundVendor.id)
        cache.set(cache_items_key, itemList, CACHE_TIMEOUT)
    context['itemList'] = itemList
    context['vendor'] = foundVendor
    context['stadium'] = foundStadium

    # Send shopping cart info if it exists
    if 'cart' in request.session:
        context['cart'] = request.session['cart']
        # If there is cart info for this current page (used to grab quantities
        if foundStadium.name in context['cart'] and foundVendor.name in context['cart'][foundStadium.name]:
            context['current_cart'] = context['cart'][foundStadium.name][foundVendor.name]

            for item in itemList:
                if item.name in context['current_cart']:
                    item.quantity = context['current_cart'][item.name]
        
        
    return render_to_response('vendor_view.html',context,context_instance=RequestContext(request))

def double_dict():
    return defaultdict(dict)

def ItemView(request, stadiumName=None, vendorName=None, itemName=None):
    context = initContext(request)

    # Generate Cache Keys
    cache_stadium_key = get_stadium_key(stadiumName)
    cache_vendor_key = get_vendor_key(stadiumName,vendorName)
    cache_item_key = get_item_key(stadiumName,vendorName,itemName)

    foundStadium = cache.get(cache_stadium_key)
    foundVendor = cache.get(cache_vendor_key)
    foundItem = cache.get(cache_item_key)

    try:
        if foundStadium is None:
            print "miss stadium"
            foundStadium = Stadiums.objects.get(name=stadiumName)
            cache.set(cache_stadium_key, foundStadium,CACHE_TIMEOUT)
        if foundVendor is None:
            print "miss vendor"
            foundVendor = Vendors.objects.get(stadium=foundStadium.id, name=vendorName)
            cache.set(cache_vendor_key, foundVendor, CACHE_TIMEOUT)
        if foundItem is None:
            print "miss item"
            foundItem = Vendor_items.objects.get(vendor=foundVendor.id, name=itemName)
            cache.set(cache_item_key, foundItem, CACHE_TIMEOUT)
    except Stadiums.DoesNotExist:
        return HttpResponseRedirect(settings.URL_PREFIX + "?iv=%s" % stadiumName)
    except Vendors.DoesNotExist:
        return HttpResponseRedirect(settings.URL_PREFIX + stadiumName + '/' + "?iv=%s" % vendorName)
    except Vendor_items.DoesNotExist:
        return HttpResponseRedirect(settings.URL_PREFIX + stadiumName + '/' + vendorName + '/' + "?iv=%s" % itemName)
    
    context['vendor'] = foundVendor
    context['stadium'] = foundStadium
    context['item'] = foundItem

    # Current assumes a javascript request @@TODO: Check header to see if it's requesting json
    if request.method == 'POST':
        if request.POST['quantity']:
            if request.POST['quantity'].isdigit():
                # Either retrieve the cart or initialize a 3d dictionary
                cart = request.session.get('cart',defaultdict(double_dict))
                if foundStadium.name not in cart:
                    cart[foundStadium.name] = defaultdict(dict)
                if foundVendor.name not in cart[foundStadium.name]:
                    cart[foundStadium.name][foundVendor.name] = {}
                # Verify that it's a positive number, delete otherwise
                if int(request.POST['quantity']) <= 0:
                    cart[foundStadium.name][foundVendor.name].pop(foundItem.name, None)
                    # remove vendor if no more items exist
                    if len(cart[foundStadium.name][foundVendor.name]) <= 0:
                        cart[foundStadium.name].pop(foundVendor.name, None)
                        # remove stadium if no more vendors exist
                        if len(cart[foundStadium.name]) <= 0:
                            cart.pop(foundStadium.name, None)
                else:           # end if (quantity <= 0)
                    cart[foundStadium.name][foundVendor.name][foundItem.name] = int(request.POST['quantity'])

                
                request.session['cart'] = cart
                return HttpResponse(json.dumps(request.session['cart']), content_type="application/json")
            # end if (quantity is digit)
            return HttpResponse(json.dumps({'error':'invalid quantity: "' + request.POST['quantity'] + '"'}), content_type="application/json")
        # end if (quantity)
        return HttpResponse(json.dumps({'error':'no quantity specified'}), content_type="application/json")
    # end if (post)

    # Send shopping cart info if it exists
    if 'cart' in request.session:
        context['cart'] = request.session['cart']

    return render_to_response('item_view.html',context,context_instance=RequestContext(request))

'''
Determines whether or not to treat the specified request as a json request or not
returns true if yes, no otherwise
'''
def acceptJson(request):
    accept_header = request.META.get('HTTP_ACCEPT',False)
    if not accept_header:
        return False
    accept_types = accept_header.split(',')
    if accept_types[0] == "application/json":
        return True
    return False


def cart(request, stadiumName=None, vendorName=None):
    '''
    Loads the shopping cart page
    '''
    context = initContext(request)
    if request.session.get('cart', False):
        context['cart'] = request.session.get('cart')
    else:
        context['cart'] = [];
        vendor = {
            'name': 'Branton',
        }
        context['cart'].append(vendor)
    if stadiumName in context['cart']:
        context['cart'] = {stadiumName: context['cart'][stadiumName]}
        if vendorName in context['cart'][stadiumName]:
            context['cart'][stadiumName] = {vendorName:context['cart'][stadiumName][vendorName]}

    if (acceptJson(request)):
        return HttpResponse(json.dumps(context['cart']), content_type="application/json")
    # else:
    #     return HttpResponse(json.dumps(request.META['HTTP_ACCEPT']), content_type="application/json")
    return render_to_response('cart.html',context,context_instance=RequestContext(request))

        
