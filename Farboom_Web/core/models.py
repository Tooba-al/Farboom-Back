from django.db import models

from django.db import models, transaction
from django.contrib.auth.models import User
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.utils import timezone
from Farboom_Web import settings
from django.db.models.signals import post_save
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _
# from .email import *
import json
from sys import platform
import os
from uuid import uuid4
#from django.urls import reverse
#from django.http import HttpRequest as request
#from django.contrib.sites.shortcuts import get_current_site

# def get_video_upload_path(filename, instance):
#     ext = str(filename).split('.')[-1]
#     filename = f'{uuid4()}.{ext}'
#     return os.path.join("uploads/video/", filename)

# def get_audio_upload_path(filename, instance):
#     ext = str(filename).split('.')[-1]
#     filename = f'{uuid4()}.{ext}'
#     return os.path.join("uploads/audio/", filename)


# def get_image_upload_path(filename, instance):
#     ext = str(filename).split('.')[-1]
#     filename = f'{uuid4()}.{ext}'
#     return os.path.join("uploads/image/", filename)

# model User

class UserProfileManager(models.Manager):

    #def get_by_username(self, username):
    #     return self.get(username__iexact=username)

    def get_if_available(self, username, email):
        try:
            by_username = self.get(username__iexact=username)
            if by_username == None:
                return self.get(email = email)
            return by_username
        except:
            return None
        
class UserProfile(models.Model):
    """
        User Profile object, one to one with django user
        additional info about the user
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")
    email = models.CharField(max_length =255, unique=True)
    phone_number = models.CharField(max_length=13, blank= True, null = True, unique=True)
    username = models.CharField(max_length=32, blank=False, null=True, unique=True)
    password = models.CharField(max_length=100, blank=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # verification_status = models.CharField(max_length=1, choices=UserProfileConsts.states,
    #                                        default=UserProfileConsts.PENDING)

    objects = UserProfileManager()

    #is_admin = models.BooleanField(default=False)

    @property
    def token(self):
        token, created = Token.objects.get_or_create(user=self.user)
        return token.key
        
    @property
    def projects_count(self):
        return Project.objects.filter(care_giver = self).count()

    def __str__(self):
        return "%s" % (self.user.username)

class UserProfilePhoneVerificationObjectManager(models.Manager):
    def create(self, **kwargs):
        created = False

        with transaction.atomic():
            user_profile = kwargs.get('user_profile')

            # lock the user profile to prevent concurrent creations
            user_profile = UserProfile.objects.select_for_update().get(pk=user_profile.pk)

            time = timezone.now() - timezone.timedelta(minutes=UserProfilePhoneVerification.RETRY_TIME)

            # select the latest valid user profile phone verification object
            user_profile_phone = UserProfilePhoneVerification.objects.order_by('-created_at'). \
                filter(created_at__gte=time,
                       user_profile__email=user_profile.email) \
                .last()

            # create a new object if none exists
            if not user_profile_phone:
                obj = UserProfilePhoneVerification(**kwargs)
                obj.save()
                created = True

        if created:
            if settings.DEBUG:
                return {'status': 201, 'obj': obj, 'code': obj.code}
            return {'status': 201, 'obj': obj}

        return {'status': 403,
                'wait': timezone.timedelta(minutes=UserProfilePhoneVerification.RETRY_TIME) +
                        (user_profile_phone.created_at - timezone.now())}

class UserProfilePhoneVerification(models.Model):
    """
        Used for phone verification by sms
        auto generates a 5 digit code
        limits select querying
        time intervals between consecutive creation
    """

    RETRY_TIME = 2
    MAX_QUERY = 5

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="emails")
    code = models.CharField(max_length=13, default="00000000")
    created_at = models.DateTimeField(auto_now_add=True)
    query_times = models.IntegerField(default=0)
    used = models.BooleanField(default=False)
    burnt = models.BooleanField(default=False)

    objects = UserProfilePhoneVerificationObjectManager()

# class CoUser(models.Model):
#     user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="care_giver")

#     @property
#     def posts_count(self):
#         return Project.objects.filter(care_giver = self).count()


class ProjectCategory(models.Model):
    name = models.CharField(max_length=110)
    
    def __str__(self):
        return self.name
    
class Project(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="posts", default = None)
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ProjectPic(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="pics")
    pic = models.FileField(null = True, blank = True)
    
    @property
    def pic_url(self):
        if self.pic and hasattr(self.pic, 'url'):
            return self.pic.url
        else:
            return None
        
class ProjectAudio(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="audios")
    audio = models.FileField(null = True, blank = True)
    
    @property
    def audio_url(self):
        if self.audio and hasattr(self.audio, 'url'):
            return self.audio.url
        else:
            return None
        
class ProjectVideo(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="videos")
    video = models.FileField(null = True, blank = True)
    
    @property
    def pic_url(self):
        if self.video and hasattr(self.video, 'url'):
            return self.video.url
        else:
            return None

