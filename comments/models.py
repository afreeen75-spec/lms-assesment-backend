from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    commentable_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # which table
    commentable_id = models.PositiveIntegerField()                              # which row
    commentable = GenericForeignKey("commentable_type", "commentable_id")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["commentable_type", "commentable_id"])]