from django.db.models.signals import post_save
from django.dispatch import receiver
import threading
import time

from .models import VisitRecord, VisitHistory

@receiver(post_save, sender=VisitRecord)
def move_to_history_and_schedule_deletion(sender, instance, created, **kwargs):
    """Переносит запись в VisitHistory и запускает таймер на удаление"""
    if instance.payment_status == 'paid_finish':
        instance.refresh_from_db()  # ✅ Гарантируем, что объект сохранён
        visit_history = VisitHistory.objects.create(
            patient=instance.patient,
            doctor=instance.doctor,
            nurse=instance.nurse,
            visit_date=instance.visit_date,
            visit_time=instance.visit_time,
            total_price=instance.total_price,
            is_online=instance.is_online,
        )
        visit_history.services.set(instance.services.all())  # ✅ Копируем услуги

        # Запускаем фоновый процесс на удаление
        threading.Thread(target=schedule_delete, args=(instance.pk,), daemon=True).start()

def schedule_delete(record_id):
    """Удаляет запись через 60 секунд"""
    time.sleep(60)
    VisitRecord.objects.filter(pk=record_id).delete()
    print(f"✅ VisitRecord с ID {record_id} удален через 60 секунд.")
