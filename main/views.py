from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from main.models import *

import hashlib

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
        return HttpResponseRedirect(URL_PREFIX + "?iv=%s" % stadiumName)
    
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
        return HttpResponseRedirect(URL_PREFIX + "?iv=%s" % stadiumName)
    except Vendors.DoesNotExist:
        return HttpResponseRedirect(URL_PREFIX + stadiumName + '/' + "?iv=%s" % vendorName)

    if itemList is None:
        print "miss items"
        itemList = Vendor_items.objects.filter(vendor=foundVendor.id)
        cache.set(cache_items_key, itemList, CACHE_TIMEOUT)
    context['itemList'] = itemList
    context['vendor'] = foundVendor
    context['stadium'] = foundStadium

    return render_to_response('vendor_view.html',context,context_instance=RequestContext(request))

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
        return HttpResponseRedirect(URL_PREFIX + "?iv=%s" % stadiumName)
    except Vendors.DoesNotExist:
        return HttpResponseRedirect(URL_PREFIX + stadiumName + '/' + "?iv=%s" % vendorName)
    except Vendor_items.DoesNotExist:
        return HttpResponseRedirect(URL_PREFIX + stadiumName + '/' + vendorName + '/' + "?iv=%s" % itemName)
    
    context['vendor'] = foundVendor
    context['stadium'] = foundStadium
    context['item'] = foundItem
    return render_to_response('item_view.html',context,context_instance=RequestContext(request))
