
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, JobSeekerProfile, JobProviderProfile

admin.site.register(User, UserAdmin)
admin.site.register(JobSeekerProfile)
admin.site.register(JobProviderProfile)
