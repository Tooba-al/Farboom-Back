from dataclasses import fields
from rest_framework import serializers
from .models import *
from django.utils.translation import gettext as _

class UserProfileDataSerializer(serializers.ModelSerializer):
    situation = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile

class UserProfileDataEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields =  ['email',]

class UserProfileSignUpSerializer(serializers.ModelSerializer):
    """
        Used to fetch phone number and send verification code to it
        if a user profile with the given phone number exists then only
        a verification code will be sent to it
        if not, one will be created
        A user will be created with the details
        This is for clients
    """
    phone_number = serializers.CharField(max_length=15, validators=[
        RegexValidator(
            regex=r"^(\+98|0)?9\d{9}$",
            message=_("Enter a valid phone number"),
            code='invalid_phone_number'
        ),],
        required = False,
        allow_null = True
    )

    class Meta:
        model = UserProfile
        fields = ['username','password','phone_number','email']

class UserProfilePhoneVerificationSerializer(serializers.Serializer):
    """
        Used for verifying phone numbers
    """
    code = serializers.CharField(max_length=10)
    email = serializers.CharField(max_length=15)

    
class UserProfileSerializer(serializers.ModelSerializer):
    profile_data = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['id', 'profile_data']
        
    def get_profile_data(self, instance):
        _user_profile = instance.user_profile
        _profile_data = {}
        _profile_data['username'] = _user_profile.username

class UserProfileListSerializer(serializers.ModelSerializer):
    profile_data = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['id', 'profile_data',]
        
    def get_profile_data(self, instance):
        _user_profile = instance.user_profile
        _profile_data = {}
        _profile_data['username'] = _user_profile.username

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=32)
    password = serializers.CharField(max_length=32)
     
class ProjectSerializers(serializers.ModelSerializer):
    is_writer = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    user_profile_data = serializers.SerializerMethodField()
    pictures = serializers.SerializerMethodField()
    audios = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'user_profile_data','text','pictures', 'audios', 'videos', 'created_at', 'is_writer', 'audio', 'video']

    def get_user_profile_data(self, instance):
        _user_profile = instance.user_profile
        return UserProfileListSerializer(instance = _user_profile).data
    
    def get_is_writer(self, instance):
        request = self.context.get('request',None)
        try:
            _user_profile = request.user.user_profile.user_profile
            return instance.user_profile == _user_profile
        except:
            return False

    def get_pictures(self, instance):
        pic_list = instance.pics.all()
        return [i.pic_url for i in pic_list]
    
    def get_audios(self, instance):
        audio_list = instance.audios.all()
        return [i.audio_url for i in audio_list]
    
    def get_videos(self, instance):
        video_list = instance.videos.all()
        return [i.video_url for i in video_list]

class ProjectCreateSerializer(serializers.ModelSerializer):
    pic_files = serializers.ListField(
                    child=serializers.ImageField(
                                max_length=100000,
                                allow_empty_file=True,
                                use_url=False),
                    required = False,
                    allow_null = True
                )
    audio_files = serializers.ListField(
                    child=serializers.FileField(
                                allow_empty_file=True,
                                use_url=False),
                    required = False,
                    allow_null = True
                )
    video_files = serializers.ListField(
                    child=serializers.FileField(
                    allow_empty_file=True,
                    use_url=False),
                    required = False,
                    allow_null = True
                )
    class Meta:
        model = Project
        fields = ['id', 'text', 'created_at', 'pic_files', 'audio_files', 'video_files', 'image']


class ProjectCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCategory
        fields = ['id','name']


class UserProfileIdSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ['id', 'username',]

class UserProfileProfileIdSerializer(serializers.ModelSerializer):

    user_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'user_id', 'username',]

    def get_user_id(self,instance):
        return instance.user_profile.id

    def get_username(self,instance):
        return instance.user_profile.username


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)

class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100)

class ResendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)

 