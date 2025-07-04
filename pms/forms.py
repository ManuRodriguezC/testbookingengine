from datetime import datetime, date
from django import forms
from django.forms import ModelForm

from .models import Booking, Customer


class RoomSearchForm(ModelForm):
    class Meta:
        model = Booking
        fields = ['checkin', 'checkout', 'guests']
        labels = {
            "guests": "Huéspedes"
        }
        widgets = {
            'checkin': forms.DateInput(attrs={'type': 'date', 'min': datetime.today().strftime('%Y-%m-%d')}),
            'checkout': forms.DateInput(
                attrs={'type': 'date', 'max': datetime.today().replace(month=12, day=31).strftime('%Y-%m-%d')}),
            'guests': forms.DateInput(attrs={'type': 'number', 'min': 1, 'max': 4}),
        }


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"
        labels = {
            "name": "Nombre y apellido",
            "phone": "Teléfono"
        }


class BookingForm(ModelForm):
    class Meta:
        model = Booking
        fields = "__all__"
        labels = {
        }
        widgets = {
            'checkin': forms.HiddenInput(),
            'checkout': forms.HiddenInput(),
            'guests': forms.HiddenInput()
        }


class BookingFormExcluded(ModelForm):
    class Meta:
        model = Booking
        exclude = ["customer", "room", "code"]
        labels = {
        }
        widgets = {
            'checkin': forms.HiddenInput(),
            'checkout': forms.HiddenInput(),
            'guests': forms.HiddenInput(),
            'total': forms.HiddenInput(),
            'state': forms.HiddenInput(),
        }

class BookingFormEditDate(ModelForm):
    class Meta:
        model = Booking
        fields = ['checkin', 'checkout']
        labels = {
            "checkin": "Nueva Fecha de entrada",
            "checkout": "Nueva Fecha de salida"
        }
        widgets = {
            'checkin': forms.DateInput(attrs={'type': 'date','class': 'form-control datepicker-style'}),
            'checkout': forms.DateInput(attrs={'type': 'date', 'class': 'form-control datepicker-style'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        checkin = self.cleaned_data.get('checkin')
        checkout = self.cleaned_data.get('checkout')
        
        if checkout is None or checkin is None:
            return checkout
        if checkout <= self.cleaned_data.get('checkin'):
            raise forms.ValidationError("La fecha de salida debe ser posterior a la fecha de entrada.")
        if isinstance(checkout, date) and checkout < date.today():
            raise forms.ValidationError("La fecha de salida no puede ser anterior a la fecha actual.")
        if isinstance(checkin, date) and checkin < date.today():
            raise forms.ValidationError("La fecha de salida no puede ser anterior a la fecha actual.")
        
        booking = self.instance
        room = booking.room
        
        find_bookind_room = Booking.objects.filter(
            room=room,
            checkin__lte=cleaned_data.get('checkout'),
            checkout__gte=cleaned_data.get('checkin'),
            state="NEW",
        ).exclude(pk=self.instance.pk)
        
        if find_bookind_room.exists():
            raise forms.ValidationError("La habitación ya está reservada para las fechas seleccionadas.")
        return cleaned_data