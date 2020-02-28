from django.db import models


class SomeModel(models.Model):
    i = models.IntegerField()
    f = models.FloatField()
    nullable = models.CharField(null=True, max_length=64)
    created = models.DateTimeField(auto_now_add=True)
