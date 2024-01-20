from hashlib import new
from .serializers import *
from rest_framework import generics,status,filters
from rest_framework.response import Response
# from .permissions import *
from django.utils.translation import gettext as _
from django.contrib.auth.hashers import make_password, check_password
from .models import *
import ast
import os
import datetime

class UserProfileSignUpView(generics.GenericAPIView):
    """
        Send verification code
        if send failed respond with wait time
    """

    serializer_class = UserProfileSignUpSerializer

    def get_object(self):
        email = self.request.data.get('email')
        username = self.request.data.get('username')

        try:
            return UserProfile.objects.get_if_available(username, email)
        except UserProfile.DoesNotExist:
            return None

    def post(self, request, *args, **kwargs):
        s = self.serializer_class(data=request.data)
        s.is_valid(raise_exception=True)

        user_profile = self.get_object()

        if not user_profile:
            try:
                with transaction.atomic():
                    valid = s.validated_data
                    hash = make_password(valid.get("password"))
                    user_profile = UserProfile.objects.create(phone_number=valid.get('phone_number'),
                                                            username = valid.get('username'),
                                                            password = hash,
                                                            email = valid.get('email'),                                           
                                                            user=User.objects.create(
                                                                    username=s.validated_data.get('username')))
                    user_profile = UserProfile.objects.create(
                    )
                    user_profile.save()
                    user_profile.save()

                    # upv = UserProfilePhoneVerification.objects.create(user_profile=self.get_object())

                    # if upv['status'] != 201:
                    #     return Response({'detail': _("Code not sent"), 'wait': upv['wait']}, status=upv['status'])

                    # if settings.DEBUG:
                    #     return Response({'detail': _("Code sent"), 'code': upv['code']})

                    # return Response({'detail': _("Code sent")})

            except:
                return Response({'detail': _("Problem with signing up")}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': _("This profile already exists.")}, status=status.HTTP_400_BAD_REQUEST)

class RetrieveUserProfileDataView(generics.RetrieveAPIView):
    serializer_class = UserProfileDataSerializer
    # permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            return self.request.user.user_profile
        except UserProfile.DoesNotExist:
            return None

class RetrieveUserProfileEditView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileDataEditSerializer
    # permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            return self.request.user.user_profile
        except UserProfile.DoesNotExist:
            return None

class UserProfileAuthTokenView(generics.CreateAPIView):
    """
        match phone number and verification code
        return user token on success
    """

    serializer_class = UserProfilePhoneVerificationSerializer

    def post(self, request, *args, **kwargs):

        email = request.data.get('email')
        code = request.data.get('code')

        user_profile_phone_ = UserProfilePhoneVerification.objects.order_by('created_at'). \
            filter(
            query_times__lt=UserProfilePhoneVerification.MAX_QUERY,
            used=False,
            burnt=False,
            user_profile__email=email
        )
        user_profile_phone = user_profile_phone_.last()

        if not user_profile_phone:
            return Response({'detail': _('Email not found')}, status=status.HTTP_404_NOT_FOUND)

        if code != user_profile_phone.code:
            user_profile_phone.query_times += 1
            user_profile_phone.save()

            return Response({'detail': _('Invalid verification code'),
                             'allowed_retry_times':
                                 UserProfilePhoneVerification.MAX_QUERY -
                                 user_profile_phone.query_times},
                            status=status.HTTP_403_FORBIDDEN)

        user_profile_phone.user_profile.save()
        token, created = Token.objects.get_or_create(user=user_profile_phone.user_profile.user)

        # user_profile_phone.used = True
        # user_profile_phone.save()

        # # mark all other codes as burnt
        # user_profile_phone_.update(burnt=True)

        #return Response({'phone_number': phone, 'token': token.key})
        return Response({'detail': _('You are verified.'), 'token': token.key})

class LoginView(generics.GenericAPIView):

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):

        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user_profile = UserProfile.objects.get(username = username)
        except:
            user_profile = None

        if not user_profile:
            return Response({'detail': _('Username not found')}, status=status.HTTP_404_NOT_FOUND)
        try:
            if password==user_profile.password:
                token = Token.objects.get(user=user_profile.user)
                data = UserProfileDataSerializer(instance = user_profile).data
                return Response({'data': data, 'token': token.key})
            else:
                return Response({'detail': _('Wrong password'),}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'detail': _('You may not be verified yet.'),}, status=status.HTTP_404_NOT_FOUND)

class ProjectListView(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializers
    # permission_classes = [IsAuthenticated,]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['likes_count', 'created_at']
     
class ProjectView(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializers
    lookup_field = 'id'
    lookup_url_kwarg = 'post_id'
    # permission_classes = [IsAuthenticated,]

class UserProfileProjectsView(generics.ListAPIView):
    serializer_class = ProjectSerializers
    # permission_classes = [IsAuthenticated,]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']

    def get_queryset(self):
        user_profile_id = self.kwargs['user_profile_id']

        try:
            return Project.objects.filter(care_giver__id = user_profile_id)
        except Project.DoesNotExist:
            return None
 
class ProjectCategoriesView(generics.ListAPIView):
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategoriesSerializer
    # permission_classes = (IsAuthenticated,)
    
  
    serializer_class = ProjectSerializers

    def get_queryset(self):
        cat_id = self.kwargs['cat_id']

        try:
            return Project.objects.filter(category__id = cat_id)
        except Project.DoesNotExist:
            return None

class ProjectCategoryView(generics.ListAPIView):
    serializer_class = ProjectCategoriesSerializer
    queryset = ProjectCategory.objects.all()
    # permission_classes = [IsAuthenticated,]
      
class ProjectCreateView(generics.CreateAPIView):
    serializer_class = ProjectCreateSerializer
    queryset = Project.objects.all()
    # permission_classes = [IsCareGiver,]

    def post(self, request, *args, **kwargs):
        s = self.serializer_class(data=request.data)
        s.is_valid(raise_exception=True)
        #with transaction.atomic():
        valid = s.validated_data
        care_giver = self.request.user.user_profile.care_giver
        project = Project.objects.create(care_giver = care_giver,
                                    text = valid.get('text'))
        project.save()

        pics = valid.get('pic_files')
        for i in pics:
            post_pic = ProjectPic.objects.create(post = project, pic = i)
            post_pic.save()
            
        audios = valid.get('audio_files')
        for i in audios:
            post_audio = ProjectAudio.objects.create(post = project, audio = i)
            post_audio.save()
            
        videos = valid.get('video_files')
        for i in videos:
            post_video = ProjectVideo.objects.create(post = project, video = i)
            post_video.save()

        return Response({'detail': _("Post created.")}, status=status.HTTP_200_OK)
          
class UserProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileListSerializer
    # permission_classes = [IsAuthenticated,]

class UserProfileView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'user_profile_id'
    # permission_classes = [IsAuthenticated,]
    
# class ForgetPasswordView(generics.CreateAPIView):

#     serializer_class = ForgetPasswordSerializer

#     def post(self, request, *args, **kwargs):
#         s = self.serializer_class(data=request.data)
#         s.is_valid(raise_exception=True)

#         try:
#             with transaction.atomic():
#                 valid = s.validated_data
#                 user_profile = UserProfile.objects.get(email = valid.get('email'))
#                 # fpl = ForgetPasswordLink.objects.create(user_profile=user_profile)

#                 if fpl['status'] != 201:
#                     return Response({'detail': _("Code not sent"), 'wait': fpl['wait']}, status=fpl['status'])

#                 if settings.DEBUG:
#                     return Response({'detail': _("Code sent"), 'link': fpl['link']})

#                 return Response({'detail': _("Code sent")})

#         except UserProfile.DoesNotExist:
#             return Response({'detail': _("No user profiles with this email.")}, status=status.HTTP_400_BAD_REQUEST)

# class ChangePasswordView(generics.UpdateAPIView):

#     serializer_class = ChangePasswordSerializer

#     def put(self, request, *args, **kwargs):
#         s = self.serializer_class(data=request.data)
#         s.is_valid(raise_exception=True)

#         try:
#             with transaction.atomic():
#                 valid = s.validated_data
#                 change_link = self.kwargs['change_link']

#                 fpl = ForgetPasswordLink.objects.get(link = change_link)
#                 time = datetime.datetime.now(datetime.timezone.utc) - fpl.created_at

#                 if fpl.used == True:
#                     return Response({'detail': _("You have already used this link.")}, status=status.HTTP_400_BAD_REQUEST)
#                 elif time > datetime.timedelta(hours = 1):
#                     return Response({'detail': _("This link has surpassed its valid time.")}, status=status.HTTP_400_BAD_REQUEST)
#                 else:
#                     fpl.used = True
#                     new_password = make_password(valid.get("password"))
#                     user_profile = fpl.user_profile
#                     user_profile.password = new_password
#                     user_profile.save()
#                     fpl.save()
#                     return Response({'detail': _("Your password changed successfully")}, status=status.HTTP_200_OK)


#         except ForgetPasswordLink.DoesNotExist:
#             return Response({'detail': _("This link isn't valid.")}, status=status.HTTP_400_BAD_REQUEST)

# class ResendVerificationCodeView(generics.CreateAPIView):

#     serializer_class = ResendVerificationCodeSerializer

#     def post(self, request, *args, **kwargs):
#         s = self.serializer_class(data=request.data)
#         s.is_valid(raise_exception=True)

#         try:
#             with transaction.atomic():
#                 valid = s.validated_data
#                 user_profile = UserProfile.objects.get(email = valid.get('email'))

#                 upv = UserProfilePhoneVerification.objects.create(user_profile=user_profile)

#                 if upv['status'] != 201:
#                     return Response({'detail': _("Code not sent"), 'wait': upv['wait']}, status=upv['status'])

#                 if settings.DEBUG:
#                     return Response({'detail': _("Code sent"), 'code': upv['code']})

#                 return Response({'detail': _("Code sent")})

#         except UserProfile.DoesNotExist:
#             return Response({'detail': _("This user doesn't exist.")}, status=status.HTTP_400_BAD_REQUEST)
