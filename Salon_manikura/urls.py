from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from website.forms import CustomAuthenticationForm

urlpatterns = [
    path('admin/', admin.site.urls),

    # Явно подключаем LoginView с нашей формой:
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html',
            authentication_form=CustomAuthenticationForm
        ),
        name='login'
    ),
    # Остальные аутентификационные маршруты (logout, password_change и т.д.)
    path('accounts/', include('django.contrib.auth.urls')),

    # Ваши муниципальные маршруты
    path('', include('website.urls')),
]

if settings.DEBUG:
    # В режиме разработки Django отдаёт статику
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
