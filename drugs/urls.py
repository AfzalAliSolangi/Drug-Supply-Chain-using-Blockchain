from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('blog', views.blog, name='blog'),
    path('blogsingle', views.blogsingle, name='blogsingle'),
    path('features', views.features, name='features'),
    path('pricing', views.pricing, name='pricing'),
    path('contact', views.contact, name='contact'),
    path('login_master', views.login_master, name='login_master'),
    path('login_manufacturer', views.login_manufacturer, name='login_manufacturer'),
    path('login_distributor', views.login_distributor, name='login_distributor'),
    path('login_pharmacy', views.login_pharmacy, name='login_pharmacy'),
    path('login_check_manufacturer', views.login_check_manufacturer, name='login_check_manufacturer'),
    path('login_check_master', views.login_check_master, name='login_check_master'),
    path('signup-master', views.signup_master, name='signup-master'),
    path('signup-manufacturer', views.signup_manufacturer, name='signup-manufacturer'),
    path('signup-distributor', views.signup_distributor, name='signup-distributor'),
    path('signup-pharmacy', views.signup_pharmacy, name='signup-pharmacy'),
    path('base', views.base, name='base'),
    path('prddata', views.prddata, name='dealup'),
    path('masup', views.manufacturer, name='masup'),
    path('hosup', views.hostpitalinput, name='hosup'),
    path('drgby', views.distributor, name='drgby'),
    path('seedet', views.getdetails, name='seedet'),
    path('products', views.products, name='products'),  
    path('checkout', views.checkout, name='checkout'),
    path('publish', views.publish, name='publish'),
    path('email_check_master', views.email_check_master, name='email_check_master'),
    path('email_check_manufacturer', views.email_check_manufacturer, name='email_check_manufacturer'),
    path('email_check_distributor', views.email_check_distributor, name='email_check_distributor'),
    path('email_check_pharmacy', views.email_check_pharmacy, name='email_check_pharmacy'),
    path('process_registration_manufacturer', views.process_registration_manufacturer, name='process_registration_manufacturer'),
    path('process_registration_master', views.process_registration_master, name='process_registration_master'),
]
