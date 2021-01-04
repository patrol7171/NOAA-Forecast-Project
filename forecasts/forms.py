from django import forms
from .models import Location
from localflavor.us.forms import USZipCodeField
import zipcodes


class LocationForm(forms.ModelForm):
    zipcode = USZipCodeField()

    class Meta:
        model = Location
        fields = ('zipcode',)

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner')
        super(LocationForm, self).__init__(*args, **kwargs)

    def clean_zipcode(self):
        zipcode = self.cleaned_data['zipcode']
        if Location.objects.filter(owner_id=self.owner, zipcode=zipcode).exists():
            raise forms.ValidationError("You already have this zipcode in your list.")
        elif zipcodes.is_real(zipcode) == False:
            raise forms.ValidationError("You must enter a real US zipcode.")
        return zipcode