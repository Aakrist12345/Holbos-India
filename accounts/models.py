from django.db import models
from django.contrib.auth.models import User

class PortfolioItem(models.Model):
    ITEM_TYPES = (
        ('Image', 'Image'),
        ('Video', 'Video'),
        ('Article', 'Article'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolio_items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    file = models.FileField(upload_to='portfolio_files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.item_type})"
