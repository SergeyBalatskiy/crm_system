from .models import FinanceHistoryInfo

# Находим все записи, где age равен NULL, и выставляем им 0
FinanceHistoryInfo.objects.filter(product_name__isnull=True).update('Нет данных')

