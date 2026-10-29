from django.contrib.auth.models import User
from django.db import models


# 1. Foydalanuvchi balansi (Standart User'ga qo'shimcha)
class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

  def __str__(self):
    return f"{self.user.username} - {self.balance}"


# 2. Keys ichida tushishi mumkin bo'lgan buyumlar (Item / Skin)
class Item(models.Model):
  RARITY_CHOICES = [
      ('common', 'Oddiy'),
      ('rare', 'Naydob'),
      ('epic', 'Epik'),
      ('legendary', 'Afsonaviy'),
  ]

  name = models.CharField(max_length=100)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  image = models.ImageField(upload_to='items/')
  rarity = models.CharField(
      max_length=20, choices=RARITY_CHOICES, default='common'
  )

  def __str__(self):
    return f"{self.name} ({self.price} so'm)"


# 3. Keyslar (Masalan: "Boshlang'ich", "VIP", "Golden")
class Case(models.Model):
  name = models.CharField(max_length=100)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  image = models.ImageField(upload_to='cases/')
  items = models.ManyToManyField(Item, through='CaseItem')

  def __str__(self):
    return f"{self.name} - {self.price} so'm"


# 4. Keys va Item bog'lanishi (Har bir keys uchun itemning tushish ehtimolligi - chance)
class CaseItem(models.Model):
  case = models.ForeignKey(Case, on_delete=models.CASCADE)
  item = models.ForeignKey(Item, on_delete=models.CASCADE)
  chance = (
      models.FloatField()
  )  # Foiz ko'rinishida, masalan: 10.5 (10.5% ehtimollik)

  def __str__(self):
    return f"{self.case.name} -> {self.item.name} ({self.chance}%)"


# 5. Ochilgan keyslar tarixi (Saytda "Oxirgi yutuqlar" lentasi uchun)
class OpenHistory(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  case = models.ForeignKey(Case, on_delete=models.CASCADE)
  item = models.ForeignKey(Item, on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.user.username} {self.case.name} ochib {self.item.name} yutdi"