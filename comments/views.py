from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from courses.models import Course, Lesson
from courses.permissions import can_access_lessons
from .models import Comment
from .serializers import CommentSerializer

ALLOWED_TYPES = {"course": Course, "lesson": Lesson}   # Task 6.3: whitelist


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_target(self):
        model = ALLOWED_TYPES.get(self.kwargs["commentable_type"])
        if model is None:
            raise ValidationError({"commentable_type": f"Must be one of: {', '.join(ALLOWED_TYPES)}."})
        try:
            target = model.objects.get(pk=self.kwargs["commentable_id"])
        except model.DoesNotExist:
            raise NotFound(f"{model.__name__} not found.")

        user = self.request.user
        if isinstance(target, Course):
            if target.status != "published" and target.teacher_id != user.id:
                raise NotFound("Course not found.")
        elif not can_access_lessons(user, target.course):
            raise PermissionDenied("Enroll in this course to view or comment on its lessons.")
        return target

    def get_queryset(self):
        target = self.get_target()
        ct = ContentType.objects.get_for_model(target)
        return (Comment.objects.filter(commentable_type=ct, commentable_id=target.pk)
                .select_related("user", "commentable_type"))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, commentable=self.get_target())