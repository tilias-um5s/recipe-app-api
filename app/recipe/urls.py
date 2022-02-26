from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('tags', views.TagViewSet, basename='tag')
router.register('ingredients', views.IngredientView, basename='ingredient')

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]
