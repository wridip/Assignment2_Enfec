from django.urls import path
from . import views

urlpatterns = [
    path("search/keyword/", views.keyword_search),
    path("search/semantic/", views.semantic_search),
]