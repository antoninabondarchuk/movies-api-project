import uuid
from django.db import models
from myproject import settings
from treebeard.mp_tree import MP_Node


class Comment(MP_Node):
    """
    The class of Materialized Path Node to implement comments as tree nodes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    film = models.ForeignKey('movies.Film', on_delete=models.CASCADE, null=True, blank=True)
    tv = models.ForeignKey('movies.Tv', on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField(null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    depth = models.PositiveIntegerField(default=1)
    node_order_by = ['path']

    class MPTTMeta:
        order_insertion_by = ['id']

    def __str__(self):
        return f"Comment {self.id}"
