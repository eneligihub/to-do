from django.db import models
from django.contrib.auth.models import User

class Location(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

# class UserProfile(models.Model):
#     first_name = models.CharField(max_length=100)
#     surname = models.CharField(max_length=100)
#     email = models.EmailField()
#     phone = models.CharField(max_length=100)
#     location = models.ForeignKey(Location, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self.first_name

class Event_catagory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
class Event(models.Model):
    category = models.ForeignKey(Event_catagory, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)  # can be optional
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)  # can be optional
    # location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=False, null=False)
    is_public = models.BooleanField(default=True)
    # need to add: pic/video



def __str__(self):
    return self.name



class CartItem(models.Model):
    # time = models.DateField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


def __str__(self):
    return self.title

