from django.db import models

# Create your models here.
class User(models.Model):
    # ユーザ管理
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    create_date = models.DateTimeField(auto_now_add=True)

class Shokuhi(models.Model):
    # 食費管理
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    money = models.IntegerField()
    create_date = models.DateTimeField(auto_now_add=True)
    