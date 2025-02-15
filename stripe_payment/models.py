from django.db import models

class Payment(models.Model):
    # id_User = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, unique=True)
    amount = models.IntegerField()  # Valor em centavos
    currency = models.CharField(max_length=10, default='usd')
    place = models.CharField(max_length=255, default='Cabo Verde')
    time = models.CharField(max_length=255, default='1 hour')
    service = models.CharField(max_length=255, default='Tour')
    distance = models.CharField(max_length=255, default='10 km')
    status = models.CharField(max_length=50, default='pending')  # pending, paid, failed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.session_id} - {self.status}"


