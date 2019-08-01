from django.urls import path
from . import views

urlpatterns = [
    path('<int:movie_id>/', views.detail_page),
    path('<int:movie_id>/casts/', views.casts_page),
    path('<int:movie_id>/stills/', views.stills_page),
    path('<int:movie_id>/get_comment/', views.get_comment),
    path('comment/', views.comment),
    path('like_it/', views.like_it),
]