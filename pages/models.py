# pages/models.py
from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.core.validators import MinValueValidator
from django.templatetags.static import static


class Product(models.Model):
    CATEGORY_CHOICES = [
        ("Yapı Kimyasalları", "Yapı Kimyasalları"),
        ("Isı Yalıtım", "Isı Yalıtım"),
        ("Yapıştırıcı", "Yapıştırıcı"),
        ("Dekoratif Sıva", "Dekoratif Sıva"),
    ]

    name = models.CharField("Ürün Adı", max_length=150)
    description = models.TextField("Açıklama", blank=True)
    unit_price = models.DecimalField("Birim Fiyat", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    min_stock = models.PositiveIntegerField("Asgari Stok", default=0)  # çuval
    category = models.CharField("Kategori", max_length=40, choices=CATEGORY_CHOICES)

    # Admin'den upload opsiyonel; asıl görseller static/images/<dosya> olabilir
    image = models.ImageField("Görsel (Medya)", upload_to="products/", blank=True, null=True)
    image_static = models.CharField("Statik Görsel Adı", max_length=200, blank=True)  # ör: "hazirsiva.jpg"

    # stok (çuval)
    current_qty = models.PositiveIntegerField("Mevcut Stok", default=0)
    pallet_size = models.PositiveIntegerField("Palet Büyüklüğü", default=64)

    created_at = models.DateTimeField("Oluşturma", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"

    def __str__(self):
        return self.name

    @property
    def image_src(self):
        # 1) image varsa media'dan, 2) image_static varsa static/images'ten, 3) yedek görsel
        if self.image:
            return self.image.url
        if self.image_static:
            return static(f"images/{self.image_static}")
        return static("images/no-image.png")

    @property
    def pallet_stock_text(self):
        pallets = self.current_qty // self.pallet_size
        bags = self.current_qty % self.pallet_size
        return f"{pallets} palet + {bags} çuval"

    @property
    def total_value(self):
        return self.unit_price * self.current_qty

    @property
    def stock_ok(self):
        return self.current_qty >= self.min_stock
    stock_ok.fget.short_description = "Stok Yeterli mi?"

    @property
    def pallet_price(self):
        return self.unit_price * self.pallet_size


class StockMovement(models.Model):
    IN = "IN"
    OUT = "OUT"
    TYPE_CHOICES = [(IN, "Giriş (+)"), (OUT, "Çıkış (-)")]

    # Not: Modelde reason'ı serbest bıraktık; formda dinamik choices vereceğiz.
    IN_REASONS = [
        ("Satın Alma", "Satın Alma"),
        ("Üretim", "Üretim"),
        ("İade", "İade"),
        ("Düzeltme", "Düzeltme"),
    ]
    OUT_REASONS = [
        ("Satış", "Satış"),
        ("Kullanım", "Kullanım"),
        ("Hasar", "Hasar"),
        ("Kayıp", "Kayıp"),
        ("Transfer", "Transfer"),
        ("Fire", "Fire"),
        ("Düzeltme", "Düzeltme"),
    ]

    product = models.ForeignKey(Product, verbose_name="Ürün", on_delete=models.CASCADE, related_name="movements")
    move_type = models.CharField("Hareket Tipi", max_length=3, choices=TYPE_CHOICES)
    reason = models.CharField("Sebep", max_length=30)  # choices admin formda dinamik verilecek
    quantity = models.PositiveIntegerField("Miktar", validators=[MinValueValidator(1)])
    unit = models.CharField("Birim", max_length=10, default="Adet")
    note = models.CharField("Not", max_length=255, blank=True)
    created_at = models.DateTimeField("Oluşturma", default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Stok Hareketi"
        verbose_name_plural = "Stok Hareketleri"

    def __str__(self):
        sign = "+" if self.move_type == self.IN else "-"
        return f"{self.product.name} {sign}{self.quantity} ({self.reason})"

    @staticmethod
    def popular_reasons_since(dt):
        return (
            StockMovement.objects
            .filter(created_at__gte=dt)
            .values("reason", "move_type")
            .annotate(total=Sum("quantity"))
            .order_by("-total")
        )
