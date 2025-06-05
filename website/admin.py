from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import (
    User, Service, Master, MasterService,
    AppointmentStatus, Appointment, Review,
    Promotion, GalleryImage, Favorite
)

# Inline для MasterService
class MasterServiceInline(admin.TabularInline):
    model = MasterService
    extra = 1
    raw_id_fields = ('service',)
    verbose_name = 'Услуга мастера'
    verbose_name_plural = 'Услуги мастеров'

# Inline для Appointment в MasterAdmin
class AppointmentInline(admin.TabularInline):
    model = Appointment
    extra = 0
    fk_name = 'master'
    readonly_fields = ('created_at', 'updated_at', 'client_name', 'service_name')
    fields = (
        'client', 'client_name', 'service', 'service_name',
        'appointment_date', 'appointment_time', 'status',
        'price_paid', 'created_at', 'updated_at'
    )
    show_change_link = True

    @admin.display(description='Клиент')
    def client_name(self, obj):
        return obj.client.username if obj.client else '-'

    @admin.display(description='Услуга')
    def service_name(self, obj):
        return obj.service.name if obj.service else '-'

# Inline для Favorite в UserAdmin
class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 0
    fk_name = 'client'
    raw_id_fields = ('service',)
    readonly_fields = ('created_at',)
    fields = ('service', 'created_at')

@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2'),
        }),
    )
    list_display = ('id', 'username', 'email', 'role', 'is_staff', 'created_at', 'appointment_count')
    list_display_links = ('username', 'email')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    date_hierarchy = 'date_joined'
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at')
    inlines = [FavoriteInline]

    @admin.display(description='Количество записей')
    def appointment_count(self, obj):
        return obj.appointments.count()

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'duration_minutes', 'created_at')
    list_display_links = ('name',)
    list_filter = ('price',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ()

@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'specialization', 'services_list')
    list_display_links = ('name',)
    search_fields = ('name', 'specialization')
    inlines = [MasterServiceInline, AppointmentInline]

    @admin.display(description='Услуги мастера')
    def services_list(self, obj):
        # Получаем все записи MasterService для данного мастера и берём название услуги
        services_qs = MasterService.objects.filter(master=obj)
        return ", ".join(ms.service.name for ms in services_qs)

@admin.register(MasterService)
class MasterServiceAdmin(admin.ModelAdmin):
    list_display = ('master', 'service')
    list_filter = ('master', 'service')
    search_fields = ('master__name', 'service__name')
    raw_id_fields = ('master', 'service')

@admin.register(AppointmentStatus)
class AppointmentStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    list_display_links = ('name',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client_name', 'master_name',
        'service', 'appointment_date', 'appointment_time', 'status'
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
        'client', 'master', 'service',
        'appointment_date', 'appointment_time', 'status',
        'price_paid', 'created_at', 'updated_at'
    )

    @admin.display(description='Клиент')
    def client_name(self, obj):
        return obj.client.username if obj.client else '-'

    @admin.display(description='Мастер')
    def master_name(self, obj):
        return obj.master.name if obj.master else '-'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('client__username', 'text')
    raw_id_fields = ('client', 'appointment')
    readonly_fields = ('created_at',)
    fields = ('client', 'appointment', 'text', 'rating', 'created_at')

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'start_date', 'end_date', 'is_active_display')
    list_filter = ('start_date', 'end_date')
    date_hierarchy = 'start_date'
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fields = (
        'title', 'description', 'image',
        'start_date', 'end_date',
        'created_at', 'updated_at'
    )

    @admin.display(boolean=True, description='Акция активна?')
    def is_active_display(self, obj):
        return obj.is_active()

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at', 'uploaded_by')
    date_hierarchy = 'uploaded_at'
    search_fields = ('description', 'uploaded_by__username')
    raw_id_fields = ('uploaded_by',)
    readonly_fields = ('uploaded_at',)
    fields = ('image', 'description', 'uploaded_by', 'uploaded_at')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'service', 'created_at')
    list_display_links = ('client', 'service')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    search_fields = ('client__username', 'service__name')
    raw_id_fields = ('client', 'service')
    readonly_fields = ('created_at',)
    fields = ('client', 'service', 'created_at')
