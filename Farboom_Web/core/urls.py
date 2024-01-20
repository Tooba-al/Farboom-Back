from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .views import *

app_name = "core"

schema_view = get_schema_view(
    openapi.Info(
        title="uMind Plus API",
        default_version='development version',
        description="uMind Plus API Documentation",
        contact=openapi.Contact(email="siavash.005@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('user-profile/sign-up/', UserProfileSignUpView.as_view()),
    # path('forget-password/', ForgetPasswordView.as_view()),
    # path('change-password/<str:change_link>/', ChangePasswordView.as_view()),
    # path('resend-code/', ResendVerificationCodeView.as_view()),
    path('verify-email/', UserProfileAuthTokenView.as_view()),
    path('profile/data/', RetrieveUserProfileDataView.as_view()),
    path('profile/edit/', RetrieveUserProfileEditView.as_view()),
    path('login/', LoginView.as_view()),
    path('projects/cat/all/', ProjectCategoriesView.as_view()),
    path('projects/cat/<int:cat_id>/', ProjectCategoryView.as_view()),
    path('projects/', ProjectListView.as_view()),
    path('projects/<int:project_id>/', ProjectView.as_view()),
    path('projects/create/', ProjectCreateView.as_view()),
    path('user-profile/all/', UserProfileListView.as_view()),
    path('user-profile/<int:user_profile_id>/', UserProfileView.as_view()),
    path('user-profile/<int:user_profile_id>/projects/', UserProfileProjectsView.as_view()),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
