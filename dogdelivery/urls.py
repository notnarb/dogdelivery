from django.conf.urls import patterns, include, url

from django.contrib import admin
from dogdelivery.settings import URL_PREFIX
admin.autodiscover()

prefix = URL_PREFIX[1:]

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
