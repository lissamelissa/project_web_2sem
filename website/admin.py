from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import (
    User,
    Service,
    Master,
    MasterService,
    AppointmentStatus,
    Appointment,
    GalleryImage,
    Review,
    Promotion,
    Favorite
)

# === 1. Inline для MasterService (в карточке мастера показываем его услуги) ===
class MasterServiceInline(admin.TabularInline):
    model = MasterService
    extra = 1
    verbose_name = 'Услуга мастера'
    verbose_name_plural = 'Услуги мастеров'
    raw_id_fields = ('service',)  # селектор услуги по ID


# === 2. Inline для Appointment (в карточке мастера показываем его записи) ===
class AppointmentInline(admin.TabularInline):
    model = Appointment
    extra = 0
    fk_name = 'master'
    readonly_fields = (
        'created_at',
        'updated_at',
        'client_username',
        'service_name'
    )
    fields = (
        'client',
        'client_username',
        'service',
        'service_name',
        'appointment_date',
        'appointment_time',
        'status',
        'created_at',
        'updated_at'
    )
    show_change_link = True  # ссылка на редактирование записи

    @admin.display(description='Имя клиента')
    def client_username(self, obj):
        return obj.client.username if obj.client else '-'

    @admin.display(description='Наименование услуги')
    def service_name(self, obj):
        return obj.service.name if obj.service else '-'


# === 3. Inline для Favorite (в карточке пользователя показываем избранные услуги) ===
class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 0
    fk_name = 'client'
    raw_id_fields = ('service',)
    readonly_fields = ('created_at',)
    fields = ('service', 'created_at')


# === 4. Учётная запись пользователя (наследуемся от встроенного) ===
@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'email', 'role')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Даты', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2'),
        }),
    )

    list_display = (
        'id',
        'username',
        'email',
        'role',
        'is_staff',
        'created_at',
        'appointment_count'
    )
    list_display_links = ('username', 'email')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    date_hierarchy = 'date_joined'
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at')
    inlines = [FavoriteInline]

    @admin.display(description='Количество записей')
    def appointment_count(self, obj):
        return obj.appointments.count()


# === 5. Услуги ===
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'price',
        'duration_minutes',
        'created_at'
    )
    list_display_links = ('name',)
    list_filter = ('price',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ()


# === 6. Мастера ===
@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'specialization',
        'user',
        'services_list'
    )
    list_display_links = ('name',)
    list_filter = ('services',)
    search_fields = ('name', 'specialization', 'user__username')
    readonly_fields = ()
    inlines = [MasterServiceInline, AppointmentInline]

    @admin.display(description='Услуги мастера')
    def services_list(self, obj):
        return ", ".join([service.name for service in obj.services.all()])


# === 7. MasterService ===
@admin.register(MasterService)
class MasterServiceAdmin(admin.ModelAdmin):
    list_display = ('master', 'service')
    list_filter = ('master', 'service')
    search_fields = ('master__name', 'service__name')
    raw_id_fields = ('master', 'service')
    autocomplete_fields = ('master', 'service')


# === 8. Статусы записи ===
@admin.register(AppointmentStatus)
class AppointmentStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    list_display_links = ('name',)


# === 9. Записи (Appointments) ===
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client_username',
        'master_name',
        'service',
        'appointment_date',
        'appointment_time',
        'status'
    )
    list_display_links = ('id',)
    list_filter = ('status', 'appointment_date')
    date_hierarchy = 'appointment_date'
    search_fields = (
        'client__username',
        'master__name',
        'service__name'
    )
    raw_id_fields = ('client', 'master', 'service', 'status')
    readonly_fields = ('created_at', 'updated_at')
    fields = (
        'client',
        'master',
        'service',
        'appointment_date',
        'appointment_time',
        'status',
        'created_at',
        'updated_at'
    )

    @admin.display(description='Имя клиента')
    def client_username(self, obj):
        return obj.client.username if obj.client else '-'

    @admin.display(description='Имя мастера')
    def master_name(self, obj):
        return obj.master.name if obj.master else '-'


# === 10. Галерея изображений ===
@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'description',
        'uploaded_by_username',
        'uploaded_at'
    )
    list_filter = ('uploaded_at', 'uploaded_by')
    date_hierarchy = 'uploaded_at'
    search_fields = ('description', 'uploaded_by__username')
    raw_id_fields = ('uploaded_by',)
    readonly_fields = ('uploaded_at',)
    fields = ('image', 'description', 'uploaded_by', 'uploaded_at')

    @admin.display(description='Загружено пользователем')
    def uploaded_by_username(self, obj):
        return obj.uploaded_by.username if obj.uploaded_by else '-'


# === 11. Отзывы ===
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client_username',
        'rating',
        'created_at'
    )
    list_display_links = ('client_username',)
    list_filter = ('rating', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = ('client__username', 'text')
    raw_id_fields = ('client',)
    readonly_fields = ('created_at',)
    fields = ('client', 'text', 'rating', 'created_at')

    @admin.display(description='Клиент')
    def client_username(self, obj):
        return obj.client.username if obj.client else '-'


# === 12. Акции ===
@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'start_date',
        'end_date',
        'is_active_display'
    )
    list_filter = ('start_date', 'end_date')
    date_hierarchy = 'start_date'
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fields = (
        'title',
        'description',
        'image',
        'start_date',
        'end_date',
        'created_at',
        'updated_at'
    )

    @admin.display(boolean=True, description='Акция активна?')
    def is_active_display(self, obj):
        return obj.is_active()


# === 13. Избранные услуги ===
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client_username',
        'service',
        'created_at'
    )
    list_display_links = ('client_username', 'service')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    search_fields = ('client__username', 'service__name')
    raw_id_fields = ('client', 'service')
    readonly_fields = ('created_at',)
    fields = ('client', 'service', 'created_at')

    @admin.display(description='Клиент')
    def client_username(self, obj):
        return obj.client.username if obj.client else '-'
