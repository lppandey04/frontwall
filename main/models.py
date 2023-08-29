from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=250, blank=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)  

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Wallpaper(models.Model):
    caption = models.CharField(max_length=50, default='This is a beautifull wallpaper')
    tags = models.TextField(default='#wallpaper #frontwall')
    pub_date = models.DateTimeField(default =timezone.now)
    time = str(timezone.now())
    name = str('wallpaper'+time)
    image = models.ImageField(null=False, upload_to='wallpaper/')
    publisher = models.ForeignKey(User,on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='wallpaper_posts')

    def __str__(self):
        return self.caption
    
    def total_likes(self):
        return self.likes.all().count()

    class Meta:
        ordering = ["-pub_date"]
    
    
class Contact(models.Model):
    name = models.CharField(max_length=100, default='not provided')
    email = models.EmailField(null=False)
    subject = models.CharField(default='Not provided', max_length=100)
    date = models.DateTimeField(default=timezone.now)
    message = models.TextField(null=False)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.name
    
