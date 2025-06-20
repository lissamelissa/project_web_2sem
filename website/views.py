from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import date, timedelta
from .models import Service, Master, Promotion, Appointment
from .forms import AppointmentForm
from django.contrib.auth import login
from .forms import RegistrationForm
from django.shortcuts import render, get_object_or_404, redirect

def index(request):
    # Виджет 1: Топ-3 популярных услуг за последний месяц
    one_month_ago = date.today() - timedelta(days=30)
    popular_services = (
        Service.objects
        .filter(appointments__appointment_date__gte=one_month_ago)  # <— здесь было appointment__, а нужно appointments__
        .annotate(bookings_count=Count('appointments'))
        .order_by('-bookings_count')[:3]
    )

    # Виджет 2: Топ-3 мастера по среднему рейтингу
    top_masters = (
        Master.objects
        .annotate(avg_rating=Avg('appointments__review__rating'))
        .order_by('-avg_rating')[:3]
    )

    # Виджет 3: Ближайшие активные акции
    today = date.today()
    upcoming_promotions = (
        Promotion.objects
        .filter(end_date__gte=today)
        .order_by('start_date')[:3]
    )

    # Поиск услуг (если задан параметр q)
    query = request.GET.get('q', '').strip()
    if query:
        search_results = Service.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    else:
        search_results = None

    context = {
        'popular_services': popular_services,
        'top_masters': top_masters,
        'upcoming_promotions': upcoming_promotions,
        'search_results': search_results,
        'query': query,
    }
    return render(request, 'website/index.html', context)

def services_list(request):
    query = request.GET.get('q', '').strip()
    if query:
        services = Service.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    else:
        services = Service.objects.all()
    return render(request, 'website/services_list.html', {'services': services, 'query': query})

def book_appointment(request, master_id):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            # Бизнес-логика: скидка для «частого клиента»
            six_months_ago = timezone.now() - timedelta(days=182)
            past_count = Appointment.objects.filter(
                client=request.user,
                created_at__gte=six_months_ago
            ).count()
            if past_count > 10:
                appointment.price_paid = appointment.service.price * 0.9
            else:
                appointment.price_paid = appointment.service.price
            appointment.save()
            return redirect('index')
    else:
        form = AppointmentForm(initial={'master': master_id, 'client': request.user})
    return render(request, 'website/book_appointment.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Не активируем здесь staff или superuser, роль задаётся полем role
            user.save()
            login(request, user)  # автоматически логиним нового пользователя
            return redirect('index')
    else:
        form = RegistrationForm()
    return render(request, 'website/register.html', {'form': form})

def appointment_list(request):
    appointments = Appointment.objects.select_related('client','master','service').all()
    return render(request, 'website/appointment_list.html', {'appointments': appointments})

def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'website/appointment_detail.html', {'appointment': appointment})

def appointment_add(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            return redirect('appointment_detail', pk=appointment.pk)
    else:
        form = AppointmentForm()
    return render(request, 'website/appointment_form.html', {
        'form': form,
        'title': 'Новая запись'
    })

def appointment_edit(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('appointment_detail', pk=pk)
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'website/appointment_form.html', {
        'form': form,
        'title': f'Редактировать запись #{pk}'
    })

def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment_list')
    return render(request, 'website/appointment_confirm_delete.html', {
        'appointment': appointment
    })
