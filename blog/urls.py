from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.blog_list, name='list'),
    path('<slug:post_slug>/<int:year>/<int:month>/<int:day>/', views.blog_detail, name='detail'),
]