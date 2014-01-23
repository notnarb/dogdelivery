from django.conf.urls import patterns, include, url

from django.contrib import admin
#from dogdelivery.settings import URL_PREFIX
from django.conf import settings
admin.autodiscover()

prefix = settings.URL_PREFIX[1:]
# Note: root directories don't currently work with these regexes
if prefix == "":
    prefix="/"

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dogdelivery.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
                       
#    url(r'^admin/', include(admin.site.urls)),
    url(r'%s(?P<stadiumName>\w+)/(?P<vendorName>\w+)/(?P<itemName>\w+)/' % prefix, 'main.views.ItemView'),
    url(r'%s(?P<stadiumName>\w+)/(?P<vendorName>\w+)/(?P<itemName>\w+)' % prefix, 'main.views.ItemView'),
    url(r'%s(?P<stadiumName>\w+)/(?P<vendorName>\w+)/' % prefix, 'main.views.VendorView'),
    url(r'%s(?P<stadiumName>\w+)/(?P<vendorName>\w+)' % prefix, 'main.views.VendorView'),
    url(r'%s(?P<stadiumName>\w+)/' % prefix, 'main.views.StadiumView'),
    url(r'%s(?P<stadiumName>\w+)' % prefix, 'main.views.StadiumView'),
    url(r'%s*' % prefix, 'main.views.home'),
)
