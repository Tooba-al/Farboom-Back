from django.contrib import admin
from .models import *

admin.site.register(UserProfile)
admin.site.register(ProjectCategory)
admin.site.register(Project)
admin.site.register(ProjectPic)
admin.site.register(ProjectAudio)
admin.site.register(ProjectVideo)