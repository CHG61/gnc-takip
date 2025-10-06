from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.db.models import Sum, F, Q, Case, When, IntegerField
from .models import Product, StockMovement

def index(request):
    products = Product.objects.all()
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    # Özetler
    total_products = products.count()
    total_qty = products.aggregate(q=Sum('current_qty'))['q'] or 0

    total_value = products.aggregate(
        val=Sum(F('unit_price') * F('current_qty'),
                output_field=models.DecimalField(max_digits=18, decimal_places=2))
    )['val'] or 0

    today_in = StockMovement.objects.filter(
        created_at__gte=today_start, move_type=StockMovement.IN
    ).aggregate(q=Sum('quantity'))['q'] or 0

    today_out = StockMovement.objects.filter(
        created_at__gte=today_start, move_type=StockMovement.OUT
    ).aggregate(q=Sum('quantity'))['q'] or 0

    low_stock = products.filter(current_qty__lt=F('min_stock')).order_by('current_qty')
    low_stock_count = low_stock.count()
    out_of_stock_count = products.filter(current_qty=0).count()

    # Son 7 gün en aktif ürünler (toplam hareket)
    active_products = (
        StockMovement.objects.filter(created_at__gte=week_ago)
        .values('product__id', 'product__name')
        .annotate(total=Sum('quantity'))
        .order_by('-total')[:10]
    )

    # Son 7 günde net değişim (IN=+qty, OUT=-qty) → en çok azalanlar
    signed_qty = Case(
        When(move_type=StockMovement.IN, then=F('quantity')),
        When(move_type=StockMovement.OUT, then=-F('quantity')),
        default=0,
        output_field=IntegerField()
    )
    decreasing_products = (
        StockMovement.objects.filter(created_at__gte=week_ago)
        .values('product__id', 'product__name')
        .annotate(net=Sum(signed_qty))
        .filter(net__lt=0)
        .order_by('net')[:5]   # en çok eksiye giden ilk 5
    )

    week_in = StockMovement.objects.filter(
        created_at__gte=week_ago, move_type=StockMovement.IN
    ).aggregate(q=Sum('quantity'))['q'] or 0
    week_out = StockMovement.objects.filter(
        created_at__gte=week_ago, move_type=StockMovement.OUT
    ).aggregate(q=Sum('quantity'))['q'] or 0
    week_net = (week_in or 0) - (week_out or 0)

    # Son 10 işlem
    recent_movements = StockMovement.objects.select_related('product').all()[:10]

    context = {
        "products": products,
        "total_products": total_products,
        "total_qty": total_qty,
        "total_value": total_value,
        "today_in": today_in,
        "today_out": today_out,
        "low_stock": low_stock,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "active_products": active_products,
        "decreasing_products": decreasing_products,
        "week_in": week_in,
        "week_out": week_out,
        "week_net": week_net,
        "week_ago": week_ago,
        "movements": StockMovement.objects.all()[:200],   # İşlem Geçmişi tabı
        "recent_movements": recent_movements,             # Dashboard mini akış
    }
    return render(request, "index.html", context)
