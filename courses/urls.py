from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import (CategoryListView, CourseViewSet, MyCoursesView,
                    LessonListCreateView, LessonDetailView)

router = SimpleRouter()
router.register("courses", CourseViewSet, basename="course")

urlpatterns = [
    path("categories/", CategoryListView.as_view()),
    path("my-courses/", MyCoursesView.as_view()),
    path("courses/<int:course_id>/lessons/", LessonListCreateView.as_view()),
    path("lessons/<int:pk>/", LessonDetailView.as_view()),
    *router.urls,
]