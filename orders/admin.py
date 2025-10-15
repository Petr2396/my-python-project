from django.contrib import admin
from .models import Order, OrderItem
from .models import PromoCode
from .models import ReturnRequest

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "status", "display_paid_status", "created", "updated")
    list_filter = ("status", "is_paid", "created", "updated")
    inlines = [OrderItemInline]
    search_fields = ("first_name", "last_name", "email", "id")
    ordering = ("-created",)
    
    # Добавьте эти методы:
    def display_paid_status(self, obj):
        if obj.is_paid:
            return "✅ ОПЛАЧЕН"
        else:
            return "❌ НЕ ОПЛАЧЕН"
    display_paid_status.short_description = "Статус оплаты"
    
    # Действия для изменения статуса оплаты
    actions = ['mark_as_paid', 'mark_as_unpaid']
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(is_paid=True)
        self.message_user(request, f"{updated} заказов отмечены как оплаченные")
    mark_as_paid.short_description = "Отметить как оплаченные"
    
    def mark_as_unpaid(self, request, queryset):
        updated = queryset.update(is_paid=False)
        self.message_user(request, f"{updated} заказов отмечены как неоплаченные")
    mark_as_unpaid.short_description = "Отметить как неоплаченные"

# Если нужно, зарегистрируйте OrderItem отдельно
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "price", "quantity")
    list_filter = ("order",)


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'active', 'valid_from', 'valid_to', 'used_count', 'max_usage')
    list_filter = ('active', 'valid_from', 'valid_to')
    search_fields = ('code',)
    list_editable = ('active', 'discount')    



@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order__id", "user__username", "phone", "email")