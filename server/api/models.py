from django.db import models


class UmKey(models.Model):
    """
    友盟key的model
    """
    indexes = [
        models.Index(fields=['um_key']),  # 单索引
    ]
    um_key = models.CharField(max_length=128)
    um_name = models.CharField(max_length=20)
    um_master = models.BooleanField(default=False)
    um_add_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.um_key