from rest_framework import serializers
from .models import Category, Course, Enrollment, Lesson


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class CourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.name", read_only=True)
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "title", "description", "category", "category_name", "status",
                  "teacher", "teacher_name", "is_enrolled", "created_at", "updated_at"]
        read_only_fields = ["teacher"]     # set from the logged-in user, never from the request body

    def get_is_enrolled(self, obj):
        user = self.context["request"].user
        return (user.role == "student" and
                obj.enrollments.filter(student=user).exclude(status="cancelled").exists())


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "course", "enrolled_at", "status"]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "course", "title", "description", "video_url", "order"]
        read_only_fields = ["course"]