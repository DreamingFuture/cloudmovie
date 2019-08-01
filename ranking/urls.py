from django.urls import path
from .views import rank_list

urlpatterns = [
    path('', rank_list),
]
