from django import forms
from .models import Booking, Review
from schedule.models import WorkingHours, SpecialHours
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from services.models import ServiceCategory


class BookingForm(forms.ModelForm):
    # Фиксированные временные слоты
    TIME_CHOICES = [
        ("09:00", "09:00"),
        ("10:00", "10:00"),
        ("11:00", "11:00"),
        ("12:00", "12:00"),
        ("13:00", "13:00"),
        ("14:00", "14:00"),
        ("15:00", "15:00"),
        ("16:00", "16:00"),
        ("17:00", "17:00"),
        ("18:00", "18:00"),
    ]

    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.all(),
        label="Категория услуги",
        required=False,
        empty_label="Выберите категорию",
    )

    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="Дата записи"
    )
    appointment_time = forms.ChoiceField(choices=TIME_CHOICES, label="Время записи")

    class Meta:
        model = Booking
        fields = [
            "category",
            "service",
            "staff",
            "appointment_date",
            "appointment_time",
        ]
        exclude = ["client"]  # Исключаем client, устанавливаем в представлении

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = self.fields["category"].queryset.order_by(
            "name"
        )
        # Сортируем услуги по названию
        self.fields["service"].queryset = self.fields["service"].queryset.order_by(
            "name"
        )

        # Настраиваем отображение мастеров - только имя
        self.fields["staff"].label_from_instance = (
            lambda obj: obj.first_name or obj.username
        )

        # Сортируем мастеров по имени пользователя
        self.fields["staff"].queryset = (
            self.fields["staff"].queryset.filter(role="staff").order_by("first_name")
        )

    def clean(self):
        """Валидация доступности времени"""
        cleaned_data = super().clean()
        staff = cleaned_data.get("staff")
        appointment_date = cleaned_data.get("appointment_date")
        appointment_time = cleaned_data.get("appointment_time")

        # Импорт datetime для использования в функции
        from datetime import datetime
        service = cleaned_data.get("service")

        # Валидация даты и времени - проверяем всегда, если дата указана
        if appointment_date:
            # Используем локальное время вместо UTC
            now_local = timezone.localtime(timezone.now())
            today = now_local.date()

            # Отладка для ServiceBookingForm
            print(f"SERVICE FORM DEBUG: today={today}, appointment_date={appointment_date}, local_time={now_local}")

            if appointment_date < today:
                print("SERVICE FORM DEBUG: Raising ValidationError for past date")
                raise ValidationError("Нельзя записаться на прошедшую дату")
            elif appointment_date == today and appointment_time:
                # Для сегодняшней даты проверяем время
                current_time = now_local.time()

                if isinstance(appointment_time, str):
                    booking_time = datetime.strptime(appointment_time, "%H:%M").time()
                else:
                    booking_time = appointment_time

                # Добавляем 5 минут буфера на случай задержки
                buffer_time = (
                    datetime.combine(today, current_time) + timedelta(minutes=5)
                ).time()

                print(f"SERVICE FORM DEBUG: buffer_time={buffer_time}, booking_time={booking_time}")

                if booking_time <= buffer_time:
                    print("SERVICE FORM DEBUG: Raising ValidationError for past time")
                    raise ValidationError(
                        "Нельзя записаться на прошедшее время сегодня (минимум за 5 минут)"
                    )

        # Проверяем доступность мастера только если все поля заполнены
        if all([staff, appointment_date, appointment_time, service]):
            # Конвертируем время в time объект
            if isinstance(appointment_time, str):
                time_obj = datetime.strptime(appointment_time, "%H:%M").time()
            else:
                time_obj = appointment_time

            # Проверка доступности мастера в указанное время
            if not self.is_staff_available(
                staff, appointment_date, time_obj, service.duration_minutes
            ):
                raise ValidationError(
                    "Мастер в это время занят или услуга не помещается в расписание"
                )

        return cleaned_data

    def is_staff_available(self, staff, date, time, duration_minutes):
        """Проверка доступности мастера в указанное время"""
        # Проверка специальных часов (праздники, выходные)
        special_hours = SpecialHours.objects.filter(staff=staff, date=date).first()
        if special_hours:
            if special_hours.start_time is None:  # Выходной
                return False
            if not (special_hours.start_time <= time <= special_hours.end_time):
                return False
        else:
            # Проверка обычных рабочих часов
            day_of_week = date.weekday()
            working_hours = WorkingHours.objects.filter(
                staff=staff, day_of_week=day_of_week, is_active=True
            ).first()

            if not working_hours:
                return False

            if not (working_hours.start_time <= time <= working_hours.end_time):
                return False

        # Проверка конфликтов с существующими записями
        end_time = (
            datetime.combine(date, time) + timedelta(minutes=duration_minutes)
        ).time()

        conflicts = (
            Booking.objects.filter(
                staff=staff,
                appointment_date=date,
                appointment_time__lt=end_time,
                appointment_time__gte=time,
            )
            .exclude(status="cancelled")
            .exists()
        )

        return not conflicts


class ServiceBookingForm(forms.ModelForm):
    """Форма бронирования для детальной страницы услуги (без поля service)"""

    TIME_CHOICES = [
        ("09:00", "09:00"),
        ("10:00", "10:00"),
        ("11:00", "11:00"),
        ("12:00", "12:00"),
        ("13:00", "13:00"),
        ("14:00", "14:00"),
        ("15:00", "15:00"),
        ("16:00", "16:00"),
        ("17:00", "17:00"),
        ("18:00", "18:00"),
    ]

    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="Дата записи"
    )
    appointment_time = forms.ChoiceField(choices=TIME_CHOICES, label="Время записи")

    class Meta:
        model = Booking
        fields = ["staff", "appointment_date", "appointment_time"]  # Без поля service
        exclude = ["client", "service"]  # Исключаем client и service

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Убираем пустой choice из поля staff
        self.fields["staff"].empty_label = None

        # Настраиваем отображение мастеров - только имя
        self.fields["staff"].label_from_instance = (
            lambda obj: obj.first_name or obj.username
        )

        # Фильтруем мастеров по специализации выбранной услуги
        selected_service = self.initial.get("service") or self.data.get("service")
        if selected_service:
            try:
                from services.models import Service

                # Если selected_service - это объект Service, берем его ID
                if hasattr(selected_service, "pk"):
                    service_id = selected_service.pk
                else:
                    service_id = selected_service

                service = Service.objects.get(pk=service_id)
                # Показываем только мастеров, специализирующихся на категории этой услуги
                self.fields["staff"].queryset = (
                    self.fields["staff"]
                    .queryset.filter(role="staff", specialization=service.category)
                    .order_by("username")
                )
            except (Service.DoesNotExist, ValueError, AttributeError):
                # Если услуга не найдена, показываем всех мастеров
                self.fields["staff"].queryset = (
                    self.fields["staff"]
                    .queryset.filter(role="staff")
                    .order_by("username")
                )
        else:
            # Если услуга не выбрана, показываем всех мастеров
            self.fields["staff"].queryset = (
                self.fields["staff"].queryset.filter(role="staff").order_by("username")
            )

    def _post_clean(self):
        """Пропускаем валидацию модели, так как client устанавливается в представлении"""
        pass

    def clean(self):
        """Валидация доступности времени"""
        cleaned_data = super().clean()
        staff = cleaned_data.get("staff")
        appointment_date = cleaned_data.get("appointment_date")
        appointment_time = cleaned_data.get("appointment_time")

        # Валидация даты и времени - проверяем всегда, если дата указана
        if appointment_date:
            # Используем локальное время вместо UTC
            now_local = timezone.localtime(timezone.now())
            today = now_local.date()

            if appointment_date < today:
                raise ValidationError("Нельзя записаться на прошедшую дату")
            elif appointment_date == today and appointment_time:
                # Для сегодняшней даты проверяем время
                current_time = now_local.time()

                if isinstance(appointment_time, str):
                    booking_time = datetime.strptime(appointment_time, "%H:%M").time()
                else:
                    booking_time = appointment_time

                # Добавляем 5 минут буфера на случай задержки
                buffer_time = (
                    datetime.combine(today, current_time) + timedelta(minutes=5)
                ).time()

                if booking_time <= buffer_time:
                    raise ValidationError(
                        "Нельзя записаться на прошедшее время сегодня (минимум за 5 минут)"
                    )

        # Проверяем, что все поля заполнены для валидации доступности
        if not all([staff, appointment_date, appointment_time]):
            return cleaned_data

        # Для ServiceBookingForm услуга берется из initial или передается отдельно
        selected_service = self.initial.get("service") or self.data.get("service")
        if selected_service:
            try:
                from services.models import Service

                if hasattr(selected_service, "pk"):
                    service_id = selected_service.pk
                else:
                    service_id = selected_service
                service = Service.objects.get(pk=service_id)

                # Конвертируем время в time объект
                if isinstance(appointment_time, str):
                    time_obj = datetime.strptime(appointment_time, "%H:%M").time()
                else:
                    time_obj = appointment_time

                # Проверка доступности мастера в указанное время
                if not self.is_staff_available(
                    staff, appointment_date, time_obj, service.duration_minutes
                ):
                    raise ValidationError(
                        "Мастер в это время занят или услуга не помещается в расписание"
                    )
            except Service.DoesNotExist:
                raise ValidationError("Выбранная услуга не найдена")

        return cleaned_data

    def is_staff_available(self, staff, date, time, duration_minutes):
        """Проверка доступности мастера в указанное время"""
        # Проверка специальных часов (праздники, выходные)
        special_hours = SpecialHours.objects.filter(staff=staff, date=date).first()
        if special_hours:
            if special_hours.start_time is None:  # Выходной
                return False
            if not (special_hours.start_time <= time <= special_hours.end_time):
                return False
        else:
            # Проверка обычных рабочих часов
            day_of_week = date.weekday()
            working_hours = WorkingHours.objects.filter(
                staff=staff, day_of_week=day_of_week, is_active=True
            ).first()

            if not working_hours:
                return False

            if not (working_hours.start_time <= time <= working_hours.end_time):
                return False

        # Проверка конфликтов с существующими записями
        end_time = (
            datetime.combine(date, time) + timedelta(minutes=duration_minutes)
        ).time()

        conflicts = (
            Booking.objects.filter(
                staff=staff,
                appointment_date=date,
                appointment_time__lt=end_time,
                appointment_time__gte=time,
            )
            .exclude(status="cancelled")
            .exists()
        )

        return not conflicts
    

class ReviewForm(forms.ModelForm):
    """Форма для отзывов о мастерах"""

    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput,  # Скрытое поле, значение будет устанавливаться JavaScript
        label="Оценка мастера"
    )

    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Расскажите о вашем опыте...'}),
        required=False,
        label="Комментарий"
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
