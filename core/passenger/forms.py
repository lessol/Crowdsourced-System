from django import forms
from django.contrib.auth.models import User

from core.models import Spot, passenger

class StandardUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class BasicPassengerForm(forms.ModelForm):
    class Meta:
        model = passenger
        fields = ('avatar',)

class SpotCreationStep1Form(forms.ModelForm):
    origin_point = forms.CharField(required=True)

    class Meta:
        model = Spot
        fields = ('origin_point', 'origin_lat', 'origin_lng',)


class SpotCreationStep2Form(forms.ModelForm):
    end_point = forms.CharField(required=True)

    class Meta:
        model = Spot
        fields = ('end_point', 'end_lat', 'end_lng',)


class SpotCreationStep3Form(forms.ModelForm):
    Number_of_Guest = forms.IntegerField(required=True)
    class Meta:
        model = Spot
        fields = ('description', 'Types_of_Vehicle','Number_of_Guest','photo',)

        

