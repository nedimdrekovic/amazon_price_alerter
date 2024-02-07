from django import forms
from .models import Product
from django.core.exceptions import ValidationError

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product # model mit dem Formular erstellt werden soll
        fields = ('title', 'url',)

    class ProductForm(forms.ModelForm):
        # Add some custom validation to our image field
        def clean_image(self):
            image = self.cleaned_data.get('image', False)
            if image:
                if image._size > 4 * 1024 * 1024:
                    raise ValidationError("Image file too large ( > 4mb )")
                return image
            else:
                raise ValidationError("Couldn't read uploaded image")
