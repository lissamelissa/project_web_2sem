from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError

class User(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Клиент'),
        ('master', 'Мастер'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name='Роль'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    # Переопределяем группы и права, чтобы не конфликтовать с auth.User
    groups = models.ManyToManyField(
        Group,
        related_name='website_user_set',
        blank=True,
        verbose_name='Группы',
        help_text='Группы пользователя',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='website_user_permissions_set',
        blank=True,
        verbose_name='Права пользователя',
        help_text='Пользовательские права',
        related_query_name='user',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'


class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название услуги')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    duration_minutes = models.PositiveIntegerField(verbose_name='Длительность (мин)')
    image = models.ImageField(upload_to='services/', blank=True, verbose_name='Картинка услуги')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Master(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя мастера')
    specialization = models.TextField(blank=True, verbose_name='Специализация')
    photo = models.ImageField(upload_to='masters/', blank=True, verbose_name='Фото мастера')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'
        ordering = ['name']

    def __str__(self):
        return self.name


class MasterService(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE, verbose_name='Мастер')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Услуга')

    class Meta:
        verbose_name = 'Услуга мастера'
        verbose_name_plural = 'Услуги мастеров'
        unique_together = ('master', 'service')

    def __str__(self):
        return f'{self.master.name} — {self.service.name}'


class AppointmentStatus(models.Model):
    name = models.CharField(max_length=50, verbose_name='Статус записи')

    class Meta:
        verbose_name = 'Статус записи'
        verbose_name_plural = 'Статусы записей'

    def __str__(self):
        return self.name


class Appointment(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'client'},
        related_name='appointments',
        verbose_name='Клиент'
    )
    master = models.ForeignKey(
        Master,
        on_delete=models.SET_NULL,
        null=True,
        related_name='appointments',
        verbose_name='Мастер'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        related_name='appointments',
        verbose_name='Услуга'
    )
    appointment_date = models.DateField(default=timezone.now, verbose_name='Дата записи')
    appointment_time = models.TimeField(verbose_name='Время записи')
    status = models.ForeignKey(
        AppointmentStatus,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Статус'
    )
    price_paid = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Оплачено'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-appointment_date', '-appointment_time']

    def __str__(self):
        client = self.client.username if self.client else 'Не указан'
        service = self.service.name if self.service else '—'
        return f'Запись: {client} — {service} ({self.appointment_date} {self.appointment_time})'

    def clean(self):
        # Бизнес-логика: запрет двойного бронирования мастера
        if self.master and self.appointment_date and self.appointment_time:
            conflict = Appointment.objects.filter(
                master=self.master,
                appointment_date=self.appointment_date,
                appointment_time=self.appointment_time
            ).exclude(id=self.id).filter(
                status__name__in=['Подтверждена', 'В процессе']
            ).exists()
            if conflict:
                raise ValidationError("Мастер уже занят в это время.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Review(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'client'},
        verbose_name='Клиент'
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Запись'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name='Рейтинг'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        client = self.client.username if self.client else 'Аноним'
        return f'Отзыв {client} — {self.rating}★'


class Promotion(models.Model):
    title = models.CharField(max_length=100, verbose_name='Заголовок акции')
    description = models.TextField(blank=True, verbose_name='Описание акции')
    image = models.ImageField(upload_to='promotions/', blank=True, verbose_name='Картинка акции')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    is_active.boolean = True
    is_active.short_description = 'Активна?'


class GalleryImage(models.Model):
    image = models.ImageField(upload_to='gallery/', verbose_name='Изображение')
    description = models.CharField(max_length=255, blank=True, verbose_name='Описание')
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Загружено пользователем'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')

    class Meta:
        verbose_name = 'Изображение галереи'
        verbose_name_plural = 'Изображения галереи'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.description or "Без описания"}'


class Favorite(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'client'},
        related_name='favorites',
        verbose_name='Клиент'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Услуга'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Избранная услуга'
        verbose_name_plural = 'Избранные услуги'
        unique_together = ('client', 'service')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.client.username} → {self.service.name}'
