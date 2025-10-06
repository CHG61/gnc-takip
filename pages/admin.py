# pages/admin.py
from django.contrib import admin
from django import forms
from django.db.models import Case, When, F, IntegerField, Sum
from django.http import HttpResponse
from django.urls import path, reverse
from django.utils import timezone
from calendar import monthrange
from datetime import datetime, timedelta
import openpyxl

from .models import Product, StockMovement

admin.site.site_header = "GNC Merzifon - Yönetim"
admin.site.site_title  = "GNC Merzifon Admin"
admin.site.index_title = "Yönetim Paneli"


class StockMovementAdminForm(forms.ModelForm):
    # Açılır seçmeli sebep
    reason = forms.ChoiceField(label="Sebep", choices=[], widget=forms.Select)
    # Açılır seçmeli birim
    UNIT_CHOICES = [("Adet", "Adet"), ("Palet", "Palet")]
    unit = forms.ChoiceField(label="Birim", choices=UNIT_CHOICES, initial="Adet")

    class Meta:
        model = StockMovement
        fields = "__all__"
        help_texts = {
            "quantity": "Palet seçilirse miktar otomatik olarak palet büyüklüğü ile çarpılır.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        move_type = (
            self.data.get("move_type")
            or self.initial.get("move_type")
            or getattr(self.instance, "move_type", None)
        )
        if move_type == StockMovement.IN:
            self.fields["reason"].choices = StockMovement.IN_REASONS
        elif move_type == StockMovement.OUT:
            self.fields["reason"].choices = StockMovement.OUT_REASONS
        else:
            self.fields["reason"].choices = [("", "--- Seçiniz ---")] + \
                list(StockMovement.IN_REASONS) + list(StockMovement.OUT_REASONS)

    def clean(self):
        cleaned = super().clean()
        move_type = cleaned.get("move_type")
        reason    = cleaned.get("reason")
        product   = cleaned.get("product")
        qty       = cleaned.get("quantity") or 0
        unit      = cleaned.get("unit") or "Adet"

        # Sebep doğrulama
        if move_type == StockMovement.IN and reason not in dict(StockMovement.IN_REASONS):
            self.add_error("reason", "Giriş için geçerli sebepler: Satın Alma, Üretim, İade, Düzeltme.")
        if move_type == StockMovement.OUT and reason not in dict(StockMovement.OUT_REASONS):
            self.add_error("reason", "Çıkış için geçerli sebepler: Satış, Kullanım, Hasar, Kayıp, Transfer, Fire, Düzeltme.")

        # Palet ise miktarı çuvala çevir
        if product and unit == "Palet":
            pallet_size = product.pallet_size or 64
            cleaned["quantity"] = qty * pallet_size  # sinyal bu çuval miktarıyla çalışacak

        return cleaned


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "unit_price", "current_qty", "min_stock", "stock_ok")
    list_filter  = ("category",)
    search_fields = ("name",)
    readonly_fields = ("current_qty",)
    list_display_links = ("name",)

    # ---- Ay sonu Excel export için özel admin URL ----
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "export-monthly/",
                self.admin_site.admin_view(self.export_monthly),
                name="pages_product_export_monthly",
            ),
        ]
        return my_urls + urls

    def changelist_view(self, request, extra_context=None):
        # Liste sayfasına buton/form için URL ver
        if extra_context is None:
            extra_context = {}
        extra_context["export_monthly_url"] = reverse("admin:pages_product_export_monthly")
        return super().changelist_view(request, extra_context=extra_context)

    def export_monthly(self, request):
        """
        Seçilen YIL/AY sonu itibarıyla stokları .xlsx indirir.
        ?year=2025&month=9 (vermezsen bir önceki ay)
        """
        now = timezone.now()
        year = int(request.GET.get("year", (now - timedelta(days=30)).year))
        month = int(request.GET.get("month", (now - timedelta(days=30)).month))
        last_day = monthrange(year, month)[1]
        cutoff = timezone.make_aware(datetime(year, month, last_day, 23, 59, 59))

        signed_qty = Case(
            When(move_type=StockMovement.IN,  then=F("quantity")),
            When(move_type=StockMovement.OUT, then=-F("quantity")),
            output_field=IntegerField(),
        )

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"{year}-{month:02d}"
        ws.append(["Ürün", "Kategori", "Min Stok", "Palet", "Birim Fiyat", "ASOF Stok", "Toplam Değer"])

        for p in Product.objects.all():
            net_after = (StockMovement.objects
                         .filter(product=p, created_at__gt=cutoff)
                         .aggregate(net=Sum(signed_qty))["net"]) or 0
            asof_qty = max(0, p.current_qty - net_after)
            total_value = float(p.unit_price) * asof_qty
            ws.append([p.name, p.category, p.min_stock, p.pallet_size,
                       float(p.unit_price), asof_qty, total_value])

        filename = f"ay-sonu-stoklari_{year}-{month:02d}.xlsx"
        resp = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        wb.save(resp)
        return resp


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    form = StockMovementAdminForm

    list_display  = ("product", "move_type", "reason", "quantity", "created_at")
    list_filter   = ("move_type", "reason", "created_at")
    search_fields = ("product__name", "reason", "note")
    autocomplete_fields = ("product",)
    date_hierarchy = "created_at"

    fieldsets = (
        ("Hareket Bilgileri", {
            "fields": ("product", "move_type", "reason", "quantity", "unit", "note")
        }),
    )

    class Media:
        js = ("pages/admin/stockmovement.js",)  # Sebep seçeneklerini canlı yenileyen JS (kaldırma)
