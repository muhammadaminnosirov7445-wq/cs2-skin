from django.contrib import admin
from .models import Case, CaseItem, Item, OpenHistory, Profile

admin.site.register(Profile)
admin.site.register(Item)
admin.site.register(Case)
admin.site.register(CaseItem)
admin.site.register(OpenHistory)