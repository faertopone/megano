from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from promotions.models import PromotionsShowProduct


@receiver(post_save, sender=PromotionsShowProduct)
def new_setting_period_task(sender, instance, created, **kwargs):
    """
    После изменения модели товара дня, обновляем настройки период таск
    """
    task_period = PeriodicTask.objects.get(task='Автономно смена товара')
    schedule = CrontabSchedule.objects.create(
        minute=0,
        hour=0,
        day_of_week='*',
        day_of_month=f'*/{instance.limit_day_show_product}',
        month_of_year='*',
    )
    task_period.crontab = schedule
    task_period.save()
