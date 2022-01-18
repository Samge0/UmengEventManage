from django.db import models


class User(models.Model):
    """
    用户账号的model
    """
    indexes = [
        models.Index(fields=['u_id']),  # 单索引
    ]
    u_id = models.CharField(max_length=11)
    u_name = models.CharField(max_length=20)
    u_pw = models.CharField(max_length=128)
    u_phone = models.CharField(max_length=11)
    u_email = models.CharField(max_length=128)
    u_token = models.CharField(max_length=128, default="")
    u_reg_time = models.DateTimeField(auto_now_add=True)
    u_last_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.u_id


class UmKey(models.Model):
    """
    友盟key的model
    """
    indexes = [
        models.Index(fields=['um_md5']),  # 单索引
    ]
    u_id = models.CharField(max_length=11, default="")
    um_md5 = models.CharField(max_length=128)
    um_key = models.CharField(max_length=128)
    um_name = models.CharField(max_length=20)
    um_master = models.BooleanField(default=False)
    um_status = models.IntegerField(default=0)      # 是否有效; 0=无效（未选中）；1=有效
    um_add_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.um_md5


class UserConfig(models.Model):
    """
    用户配置
    """
    indexes = [
        models.Index(fields=['u_id']),  # 单索引
    ]
    u_id = models.CharField(max_length=11)
    uc_content_type = models.CharField(max_length=100)
    uc_user_agent = models.CharField(max_length=500)
    uc_token = models.CharField(max_length=100)
    uc_token_haitang = models.CharField(max_length=100)
    uc_cookie = models.CharField(max_length=5000)
    uc_key_master = models.CharField(max_length=50)
    uc_key_slaves = models.CharField(max_length=5000)
    uc_add_time = models.DateTimeField(auto_now_add=True)
    uc_update_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.u_id


class UmEventModel(models.Model):
    """
    友盟自定义事件统计的model
    """
    indexes = [
        models.Index(fields=['um_md5']),  # 单索引
    ]
    u_id = models.CharField(max_length=11, default="")
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
