from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import OrderItem, Order

@receiver(post_save, sender=OrderItem)
def reduce_stock(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.stock -= instance.quantity
        product.save()

@receiver(pre_save, sender=Order)
def restore_stock(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_order = Order.objects.get(pk=instance.pk)
            if old_order.status != 'cancelled' and instance.status == 'cancelled':
                for item in instance.items.all():
                    item.product.stock += item.quantity
                    item.product.save()
        except Order.DoesNotExist:
            pass