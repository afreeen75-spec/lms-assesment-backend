from django.contrib import admin
from .models import Category, Course, Enrollment, Lesson
for m in (Category, Course, Enrollment, Lesson):
    admin.site.register(m)