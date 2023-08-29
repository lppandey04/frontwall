from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='Frontwall'),
    path('signup/',views.signup, name='signup'),
    path('verify_otps/', views.verify_otps, name='verify_otps'),
    path('verify_otpp/', views.verify_otpp, name='verify_otpp'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('login/', views.loginw, name='login'),
    path('logout/', views.logoutw, name='logout'),
    path('change_password/', views.change_password, name='change_password'),
    path('reset_password/',views.reset_password, name='reset_password'),
    path('upload/', views.upload, name='upload'),
    path('wallpaper/<int:id>/',views.vwallpaper, name='wallpaper'),
    path('me/',views.me, name='me'),
    path('search/', views.search, name='search'),
    path('like/',views.like_view, name='like_view'),
    path('contact/',views.contact, name='contact'),
    path('user/change_password/',views.chpu, name='Change Password'),
    path('user/edit/', views.useredit, name='Edit'),
    path('<str:username>/',views.user_profile, name='user'),

]