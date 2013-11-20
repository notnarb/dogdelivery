from django.db import models
from django.db.models import ImageField

from django.contrib.auth.models import User

class Stadiums(models.Model):
    name = models.CharField(max_length=50)
    def space_out(self):
        return self.name.replace("_", " ")

# http://stackoverflow.com/questions/8189800/django-store-user-image-in-model
def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.id), filename)

class Vendors(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150, blank=True)
    stadium = models.ForeignKey(Stadiums)
    profile_image = ImageField(upload_to=get_image_path, blank=True, null=True)
    def space_out(self):
        return self.name.replace("_", " ")
    
class Vendor_items(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    vendor = models.ForeignKey(Vendors)
    profile_image = ImageField(upload_to=get_image_path, blank=True, null=True)
    def space_out(self):
        return self.name.replace("_", " ")

class Transactions(models.Model):
    user = models.ForeignKey(User)
    vendor_item = models.ForeignKey(Vendor_items)
    order_time = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=50)
    completed = models.BooleanField(default=False)
