from django.urls import path, include
from . import views

app_name = 'realty'
urlpatterns = [
    path('list/<str:prop_type>/', views.property_list, name='properties'),
    path('property/<slug:slug>/', views.detail, name='property'),
    path('about_us/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search, name='search'),
    path('admin/sale/receipt/<int:obj_id>', views.receipt, name='receipt'),
    path('admin/sale/sending-receipt/<int:obj_id>', views.send_receipt, name='send_receipt'),
    path('', views.index, name='home'),
]
