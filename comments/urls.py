# comments/urls.py
from django.urls import path
from .views import CommentListCreateView

urlpatterns = [
    path("comments/<str:commentable_type>/<int:commentable_id>/", CommentListCreateView.as_view()),
]