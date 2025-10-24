from django import forms
from openpyxl.styles.builtins import styles

from .models import MessageContact

class MessageContactForm(forms.ModelForm):
    class Meta:
        model = MessageContact
        fields = ['nom', 'telephone', 'message']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'stext-111 cl2 plh3 size-116 p-l-62 p-r-30',
                'placeholder': 'Votre nom',
                'maxlength': '25',
                'oninput': "this.value = this.value.slice(0, 25);",  # لا يسمح بأكثر من 25 حرف
                'title': 'Le nom ne doit pas dépasser 25 caractères',
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'stext-111 cl2 plh3 size-116 p-l-62 p-r-30',
                'placeholder': 'Votre téléphone',
                'maxlength': '10',
                'pattern': '^0[0-9]{9}$',
                'title': 'هناك خطاء في رقم الهاتف',
                # هذا السطر يمنع كتابة أي شيء غير الأرقام ويمنع تجاوز 10 أرقام
                'oninput': """
                // إزالة أي شيء غير رقم
                this.value = this.value.replace(/[^0-9]/g, '');
                // إجبار أن يبدأ بـ 0
                if (this.value.length > 0 && this.value[0] !== '0') {
                    this.value = '0' + this.value.replace(/[^0-9]/g, '').slice(0, 9);
                }
                // تحديد الحد الأقصى 10 أرقام
                if (this.value.length > 10) {
                    this.value = this.value.slice(0, 10);
                }
            """,
                'onfocus': """
                if (this.value === '') this.value = '0';
            """,
            }),

            'message': forms.Textarea(attrs={
                'class': 'stext-111 cl2 plh3 size-120 p-lr-28 p-tb-25',
                'placeholder': 'Votre message',
                'maxlength': '500',
                'oninput': "this.value = this.value.slice(0, 500);",
                'title': 'Le message ne doit pas dépasser 500 caractères',
            }),
        }

    # تحقق من الجهة الخلفية أيضًا (backend)
    def clean_telephone(self):
        tel = self.cleaned_data['telephone']
        if not tel.isdigit():
            raise forms.ValidationError("Le numéro ne doit contenir que des chiffres.")
        if not tel.startswith('0'):
            raise forms.ValidationError("Le numéro doit commencer par 0.")
        if len(tel) != 10:
            raise forms.ValidationError("Le numéro doit contenir exactement 10 chiffres.")
        return tel

    def clean_nom(self):
        nom = self.cleaned_data['nom']
        if len(nom) > 25:
            raise forms.ValidationError("Le nom ne doit pas dépasser 25 caractères.")
        return nom

    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message) > 500:
            raise forms.ValidationError("Le message ne doit pas dépasser 500 caractères.")
        return message

