import os
import sys
import django

# 1. Получаем путь к текущей папке (.../crm_system/crm_system/crm_system)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Поднимаемся на 1 уровень выше — в папку, где лежит manage.py и твои приложения (storage, profile_user)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))

# Добавляем её в пути импорта Python
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 3. Теперь Django сможет найти и 'crm_system.settings', и твои приложения
os.environ['DJANGO_SETTINGS_MODULE'] = 'crm_system.settings'

# 4. Запускаем инициализацию
django.setup()

# 5. Все импорты моделей и функций Django выносим строго сюда:
from django.utils import timezone

current_time = timezone.now()
print("Текущее время:", current_time)