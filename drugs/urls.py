from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('blog', views.blog, name='blog'),
    path('blogsingle', views.blogsingle, name='blogsingle'),
    path('features', views.features, name='features'),
    path('pricing', views.pricing, name='pricing'),
    path('contact', views.contact, name='contact'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('base', views.base, name='base'),
    path('prddata', views.prddata, name='dealup'),
    path('masup', views.manufacturer, name='masup'),
    path('hosup', views.hostpitalinput, name='hosup'),
    path('drgby', views.distributor, name='drgby'),
    path('seedet', views.getdetails, name='seedet'),
    path('products', views.products, name='products'),  
    path('checkout', views.checkout, name='checkout'),
    path('publish', views.publish, name='publish'),
]
