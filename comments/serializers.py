from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)
    commentable_type = serializers.CharField(source="commentable_type.model", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user_name", "commentable_type", "commentable_id", "body", "created_at"]
        read_only_fields = ["commentable_id", "created_at"]