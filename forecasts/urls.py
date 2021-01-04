from django.urls import path
from . import views
from .views import CreateLocationView
from .views import DeleteLocationView


urlpatterns = [
    path('add-location/', CreateLocationView.as_view(), name='add_location'),
    path('delete-location/<pk>/', DeleteLocationView.as_view(), name='delete_location'),
]