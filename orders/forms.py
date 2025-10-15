from django import forms
from .models import Order
from .models import ReturnRequest, OrderItem

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["first_name", "last_name", "email", "address", "phone"]
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Электронная почта',
            'address': 'Адрес доставки',
            'phone': 'Телефон',
        }



class ReturnRequestForm(forms.ModelForm):
    items = forms.ModelMultipleChoiceField(
        queryset=OrderItem.objects.none(),  # Будет установлен в __init__
        widget=forms.CheckboxSelectMultiple,
        label="Выберите товары для возврата"
    )
    
    class Meta:
        model = ReturnRequest
        fields = ["items", "reason", "photo", "phone", "email"]

    def __init__(self, *args, **kwargs):
        order = kwargs.pop("order", None)
        super().__init__(*args, **kwargs)
        
        if order:
            self.fields["items"].queryset = order.items.all()
        
        # Переопределяем label для каждого элемента
        self.fields['items'].label_from_instance = lambda obj: f"{obj.product.name} - {obj.quantity} шт. × {obj.price} руб."