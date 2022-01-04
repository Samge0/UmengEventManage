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


class KeyValue(models.Model):
    """
    键值对管理的model
    """
    indexes = [
        models.Index(fields=['kv_key']),  # 单索引
    ]
    kv_name = models.CharField(max_length=128, default="")
    kv_key = models.CharField(max_length=128)
    kv_value = models.CharField(max_length=5000)
    kv_status = models.BooleanField(default=True)  # 是否有效
    kv_add_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.kv_key


class UmEventModel(models.Model):
    """
    友盟自定义事件统计的model
    """
    indexes = [
        models.Index(fields=['um_md5']),  # 单索引
    ]
    um_md5 = models.CharField(max_length=128)
    um_key = models.CharField(max_length=128)
    um_eventId = models.CharField(max_length=128)
    um_name = models.CharField(max_length=128, default="")
    um_displayName = models.CharField(max_length=128)
    um_status = models.CharField(max_length=10)  # 状态：normal=正常；stopped=暂停
    um_eventType = models.IntegerField(default=0)         # 类型（multiattribute=0 ;  calculation=1）
    um_countToday = models.IntegerField(default=0)
    um_countYesterday = models.IntegerField(default=0)
    um_deviceYesterday = models.IntegerField(default=0)
    um_date = models.DateTimeField(auto_now_add=False)

    def __unicode__(self):
        return self.um_md5
