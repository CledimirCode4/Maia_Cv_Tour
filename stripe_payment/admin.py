from django.contrib import admin
from .models import Payment

# Register your models here.
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'amount', 'currency', 'status', 'created_at')  # Campos que aparecem na listagem
    search_fields = ('session_id', 'status')  # Permite pesquisa por sessão e status
    list_filter = ('status', 'currency')  # Filtros na lateral
    readonly_fields = ('created_at',)  # O campo created_at não pode ser editado
    
    def has_change_permission(self, request, obj=None):
            return False  # Bloqueia qualquer tentativa de edição

    def has_delete_permission(self, request, obj=None):
        return False  # Opcional: Bloqueia a exclusão também


# Registrando o modelo no Django Admin
admin.site.register(Payment, PaymentAdmin)