from django.db import models

# Create your models here.
class Token(models.Model):
    # ユーザ管理
    # id = models.IntegerField(primary_key=True)
    token = models.CharField(max_length=255)
    create_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.token

class Shokuhi(models.Model):
    # 食費管理
    # id = models.IntegerField(primary_key=True)
    token = models.ForeignKey("Token", on_delete=models.CASCADE)
    money = models.IntegerField()
    create_date = models.DateTimeField(auto_now_add=True)
        
    def __str__(self):
        return "%s %s" % (self.token, self.money)