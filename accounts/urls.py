from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from accounts import views
from accounts.forms import PwdResetForm
from accounts.views import ProfileView, ProfileEditView, HistoryUserView

urlpatterns = [
    path('registration/', views.registration_view, name='registration'),
    path(
        'activate/<slug:uidb64>/<slug:token>/',
        views.account_activate,
        name='activate'
    ),
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        form_class=AuthenticationForm), name='login'),
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        success_url='password_reset_email_confirm',
        form_class=PwdResetForm),
        name='password_reset'),
    path('password_reset_confirm/<slug:uidb64>/<slug:token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/password_reset_complete/',
             form_class=SetPasswordForm),
         name='password_reset_confirm'),
    path('password_reset/password_reset_email_confirm',
         TemplateView.as_view(template_name='accounts/reset_status.html'),
         name='password_reset_done'),
    path('password_reset_complete/',
         TemplateView.as_view(template_name='accounts/reset_status.html'),
         name='password_reset_complete'),

    # urls Профилей пользователей
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/<int:pk>', ProfileEditView.as_view(), name='profile-edit'),
    path('profile/history/<int:pk>', HistoryUserView.as_view(), name='history_user'),



]
