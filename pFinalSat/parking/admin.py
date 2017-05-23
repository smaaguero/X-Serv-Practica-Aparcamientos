from django.contrib import admin
from .models import Comment
from .models import Parking
from .models import UserData
from .models import Selected

# Register your models here.
admin.site.register(Comment)
admin.site.register(Parking)
admin.site.register(UserData)
admin.site.register(Selected)
