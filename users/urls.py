from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

app_name = 'users'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_redirect, name='logout'),
    path('profile/', views.profile, name='profile'),

    # Восстановление пароля
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',
             form_class=CustomPasswordResetForm,
             email_template_name='users/password_reset_email.html',
             subject_template_name='users/password_reset_subject.txt',
             success_url='/users/password_reset/done/'
         ),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             form_class=CustomSetPasswordForm,
             success_url='/users/reset/done/'
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
