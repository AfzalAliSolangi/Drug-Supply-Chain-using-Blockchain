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
    path('login_check_distributor', views.login_check_distributor, name='login_check_distributor'),
    path('login_check_pharmacy', views.login_check_pharmacy, name='login_check_pharmacy'),
    path('signup-master', views.signup_master, name='signup-master'),
    path('signup-manufacturer', views.signup_manufacturer, name='signup-manufacturer'),
    path('signup-distributor', views.signup_distributor, name='signup-distributor'),
    path('signup-pharmacy', views.signup_pharmacy, name='signup-pharmacy'),
    path('user_type', views.user_type, name='user_type'),
    path('deactive_user', views.deactive_user, name='deactive_user'),
    path('active_user', views.active_user, name='active_user'),
    path('base', views.base, name='base'),
    path('prddata', views.prddata, name='dealup'),
    path('adddrug', views.adddrug, name='adddrug'),
    path('adddrugmenu', views.adddrugmenu, name='adddrugmenu'),
    path('manuorders', views.manuorders, name='manuorders'),
    path('manuorderconfirm', views.manuorderconfirm, name='manuorderconfirm'),
    path('manuordercancel', views.manuordercancel, name='manuordercancel'),
    path('viewmanuinvent', views.viewmanuinvent, name='viewmanuinvent'),
    path('distorderprod', views.distorderprod, name='distorderprod'),
    path('viewdistinvent', views.viewdistinvent, name='viewdistinvent'),
    path('pharmorderprod', views.pharmorderprod, name='pharmorderprod'),
    path('pharmorderstatus', views.pharmorderstatus, name='pharmorderstatus'),
    path('distproducts', views.distproducts, name='distproducts'),
    path('pharmcheckout', views.pharmcheckout, name='pharmcheckout'),
    path('pharmreqorder', views.pharmreqorder, name='pharmreqorder'),
    path('pharmorders', views.pharmorders, name='pharmorders'),
    path('distorderconfirm', views.distorderconfirm, name='distorderconfirm'),
    path('distordercancel', views.distordercancel, name='distordercancel'),
    path('viewpharminvent', views.viewpharminvent, name='viewpharminvent'),
    path('hosup', views.hostpitalinput, name='hosup'),
    # path('drgby', views.distributor, name='drgby'),
    path('seedet', views.getdetails, name='seedet'),
    path('manuproducts', views.manuproducts, name='manuproducts'),  
    path('distcheckout', views.distcheckout, name='distcheckout'),
    path('distreqorder', views.distreqorder, name='distreqorder'),
    path('email_check_master', views.email_check_master, name='email_check_master'),
    path('email_check_manufacturer', views.email_check_manufacturer, name='email_check_manufacturer'),
    path('email_check_distributor', views.email_check_distributor, name='email_check_distributor'),
    path('email_check_pharmacy', views.email_check_pharmacy, name='email_check_pharmacy'),
    path('process_registration_manufacturer', views.process_registration_manufacturer, name='process_registration_manufacturer'),
    path('process_registration_master', views.process_registration_master, name='process_registration_master'),
    path('process_registration_distributor', views.process_registration_distributor, name='process_registration_distributor'),
    path('process_registration_pharmacy', views.process_registration_pharmacy, name='process_registration_pharmacy'),
]
