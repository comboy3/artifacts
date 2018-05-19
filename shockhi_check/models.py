from django.db import models
import uuid

# Create your models here.
class User(models.Model):
    # ユーザ管理
    # id = models.IntegerField(primary_key=True)
    user_id = models.CharField(primary_key=True, default=uuid.uuid4, max_length=255)
    create_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user_id

class Shokuhi(models.Model):
    # 食費管理
    # id = models.IntegerField(primary_key=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    money = models.IntegerField()
    eat = models.CharField(max_length=255, null=True)
    date = models.DateField()
    time_zone = models.CharField(max_length=1, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
        
    def __str__(self):
        return "%s %s" % (self.user_id, self.money)