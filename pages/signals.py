from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import StockMovement, Product

def _apply(product: Product, move_type: str, qty: int, reverse=False):
    if move_type == StockMovement.IN:
        delta = qty if not reverse else -qty
    else:
        delta = -qty if not reverse else qty
    product.current_qty = max(0, product.current_qty + delta)
    product.save(update_fields=["current_qty"])

@receiver(post_save, sender=StockMovement)
def movement_saved(sender, instance: StockMovement, created, **kwargs):
    # created=True ise yeni hareket eklendi, değilse miktar/alan değişmiş olabilir.
    # Basitçe: önceki etkileri takip etmiyoruz; pratik kullanımda admin'de "değiştince" stok sapması olmaması için
    # gerçek projede versionlama gerekir. İlk sürüm için sadece ilk oluşturmadaki etkiyi uygula:
    if created:
        _apply(instance.product, instance.move_type, instance.quantity, reverse=False)

@receiver(post_delete, sender=StockMovement)
def movement_deleted(sender, instance: StockMovement, **kwargs):
    _apply(instance.product, instance.move_type, instance.quantity, reverse=True)
