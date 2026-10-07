from rest_framework.permissions import BasePermission
from .models import Enrollment


class IsTeacher(BasePermission):
    message = "Only teachers can perform this action."
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "teacher"


class IsStudent(BasePermission):
    message = "Only students can perform this action."
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "student"


class IsCourseOwner(BasePermission):
    message = "You can only modify your own courses."
    def has_object_permission(self, request, view, obj):
        return obj.teacher_id == request.user.id


def can_access_lessons(user, course):
    """Owner teacher, or a student with a non-cancelled enrollment."""
    if course.teacher_id == user.id:
        return True
    return Enrollment.objects.filter(student=user, course=course).exclude(status="cancelled").exists()