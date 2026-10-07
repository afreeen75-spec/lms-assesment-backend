from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from .models import Category, Course, Enrollment, Lesson
from .permissions import IsTeacher, IsStudent, IsCourseOwner, can_access_lessons
from .serializers import (CategorySerializer, CourseSerializer,
                          EnrollmentSerializer, LessonSerializer)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        qs = Course.objects.select_related("category", "teacher")
        if self.action == "list":                      # Task 3.4: published only
            return qs.filter(status="published")
        # detail/update/delete: published for everyone, drafts only for their owner
        return qs.filter(Q(status="published") | Q(teacher=self.request.user))

    def get_permissions(self):
        if self.action in ("create", "mine"):
            return [IsTeacher()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsTeacher(), IsCourseOwner()]      # Task 3.3
        if self.action == "enroll":
            return [IsStudent()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    @action(detail=False, methods=["get"])
    def mine(self, request):
        """GET /api/courses/mine/ : the teacher's own courses, drafts included."""
        qs = self.get_queryset().filter(teacher=request.user)
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=True, methods=["post"])
    def enroll(self, request, pk=None):
        """POST /api/courses/<id>/enroll/"""
        course = self.get_object()
        if course.status != "published":
            return Response({"detail": "Cannot enroll in an unpublished course."},
                            status=status.HTTP_400_BAD_REQUEST)
        enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
        if not created:
            return Response({"detail": "You are already enrolled in this course."},
                            status=status.HTTP_400_BAD_REQUEST)
        data = EnrollmentSerializer(enrollment, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED)


class MyCoursesView(generics.ListAPIView):
    """Task 4.5"""
    serializer_class = EnrollmentSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return (Enrollment.objects.filter(student=self.request.user)
                .select_related("course__category", "course__teacher"))


class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer

    def get_permissions(self):
        return [IsTeacher()] if self.request.method == "POST" else [IsAuthenticated()]

    def get_course(self):
        return get_object_or_404(Course, pk=self.kwargs["course_id"])

    def get_queryset(self):
        course = self.get_course()
        if not can_access_lessons(self.request.user, course):   # Task 5.4
            raise PermissionDenied("Enroll in this course to view its lessons.")
        return course.lessons.all()                              # already sorted by order

    def perform_create(self, serializer):
        course = self.get_course()
        if course.teacher_id != self.request.user.id:
            raise PermissionDenied("You can only add lessons to your own courses.")
        serializer.save(course=course)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.select_related("course")
    serializer_class = LessonSerializer

    def get_permissions(self):
        return [IsAuthenticated()] if self.request.method in SAFE_METHODS else [IsTeacher()]

    def get_object(self):
        lesson = super().get_object()
        user = self.request.user
        if self.request.method in SAFE_METHODS:
            if not can_access_lessons(user, lesson.course):
                raise PermissionDenied("Enroll in this course to view this lesson.")
        elif lesson.course.teacher_id != user.id:
            raise PermissionDenied("You can only modify lessons in your own courses.")
        return lesson