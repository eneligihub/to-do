from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
class UserProfile(models.Model):
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return self.first_name

class Event_catagory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
class Event(models.Model):
    category = models.ForeignKey(Event_catagory, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    description = models.TextField()
    creator = models.ForeignKey(UserProfile , on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()  # can be optional
    start_time = models.TimeField()
    end_time = models.TimeField()  # can be optional

    # need to add: pic/video
    # public or private


def __str__(self):
    return self.name


class CartItem(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)


