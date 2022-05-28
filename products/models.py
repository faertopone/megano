from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """
    Категория каталога товаров.
    """
    activity = models.BooleanField(
        default=True,
        verbose_name=_("активность"),
        help_text=_("Если категория активна, то она должна отображаться в главном меню сайта")
    )
    icon_photo = models.FileField(upload_to="categories/", max_length=500,
                                  validators=(FileExtensionValidator(["jpeg", "jpg", "png", "svg"]),),
                                  verbose_name=_("иконка категории"))
    category_name = models.CharField(max_length=1000, unique=True, verbose_name=_("название категории"))
    description = models.TextField(blank=True, verbose_name=_("описание"),
                                   help_text=_("Опишите, например, какие товары соответствуют данной категории"))
    properties = models.ManyToManyField("Property", through="PropertyCategory",
                                        related_name="categories", related_query_name="category",
                                        verbose_name=_("свойства товаров в категории"))

    class Meta:
        verbose_name = _("категория каталога товаров")
        verbose_name_plural = _("категории каталога товаров")
        ordering = ("pk",)

    def __str__(self):
        return self.category_name


class Product(models.Model):
    """
    Товар.
    """
    name = models.CharField(max_length=1000, verbose_name=_("название товара"))
    article = models.CharField(max_length=100, verbose_name=_("артикул"))
    price = models.DecimalField(max_digits=12, decimal_places=2, default=1,
                                validators=[MinValueValidator(1)], verbose_name=_("цена"))
    rating = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                 validators=[MinValueValidator(0)], verbose_name=_("рэйтинг"))
    flag_limit = models.BooleanField(default=False, verbose_name=_("товар заканчивается"))
    category = models.ForeignKey("Category", on_delete=models.CASCADE,
                                 related_name="products", related_query_name="product",
                                 verbose_name=_("категория каталога"))
    properties = models.ManyToManyField("Property", through="PropertyProduct",
                                        related_name="products", related_query_name="product",
                                        verbose_name=_("свойства товара"))

    class Meta:
        verbose_name = _("товар")
        verbose_name_plural = _("товары")
        ordering = ("pk",)

        # TODO: когда появится модель магазина, то
        #       надо подумать о возможности добавления
        #       ограничения (constraint), чтобы в одном магазине
        #       не могло быть два товара с одинаковым именем и артикулом.

    def __str__(self):
        return self.name

    def fullname(self):
        """
        Возвращает полное название товара в виде '(артикул) название товара'.
        """
        return f"({self.article}) {self.name}"


class Property(models.Model):
    """
    Свойство товара.
    """
    name = models.CharField(max_length=300, unique=True, verbose_name=_("имя свойства"))
    tooltip = models.CharField(max_length=1000, blank=True, default='',
                               help_text=_("Опишите подробнее, что это за свойство товара"),
                               verbose_name=_("примечание"))

    class Meta:
        verbose_name = _("свойство товара")
        verbose_name_plural = _("свойства товаров")
        ordering = ("name",)

    def __str__(self):
        return f"{self.name}"


class PropertyProduct(models.Model):
    """
    Связующая модель для товаров и их свойств.
    """
    # связи
    product = models.ForeignKey("Product", on_delete=models.CASCADE,
                                related_name="product_properties",
                                related_query_name="product_property",
                                verbose_name=_("товар"))
    property = models.ForeignKey("Property", on_delete=models.CASCADE,
                                 related_name="product_properties",
                                 related_query_name="product_property",
                                 verbose_name=_("свойство товара")
                                 )

    # дополнительные данные
    value = models.CharField(max_length=1000, null=True, blank=True, default=None,
                             verbose_name=_("значение свойства"))

    class Meta:
        verbose_name = _("параметр свойства товара")
        verbose_name_plural = _("параметры свойства товара")
        ordering = ("pk",)

        constraints = (
            models.UniqueConstraint(
                fields=("product", "property"),
                name="%(app_label)s_%(class)s_prop_unique_in_product",
            ),
        )

    def __str__(self):
        return f"{self.property.name} = {self.value}"


class PropertyCategory(models.Model):
    """
    Связующая модель для категорий и их свойств.
    """
    # связи
    category = models.ForeignKey("Category", on_delete=models.CASCADE,
                                 related_name="category_properties",
                                 related_query_name="category_property",
                                 verbose_name=_("категория"))
    property = models.ForeignKey("Property", on_delete=models.CASCADE,
                                 related_name="category_properties",
                                 related_query_name="category_property",
                                 verbose_name=_("свойство товаров в категории")
                                 )

    # дополнительные данные
    # TODO: если нужно

    class Meta:
        verbose_name = _("параметр свойства категории")
        verbose_name_plural = _("параметры свойства категории")
        ordering = ("pk",)

        constraints = (
            models.UniqueConstraint(
                fields=("category", "property"),
                name="%(app_label)s_%(class)s_prop_unique_in_category",
            ),
        )

    def __str__(self):
        return f"{self.property.name}"


class ProductPhoto(models.Model):
    """
    Модель с фотографиями магазинов
    """
    photo = models.ImageField(upload_to='products_photo', default='default.jpg', verbose_name=_('product_photo'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('product'))

    class Meta:
        verbose_name = _('products photo')
        verbose_name_plural = _('products photos')


class UserReviews(models.Model):
    """
    Модель добавления комментария к товару
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('пользователь'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('товар'))
    reviews = models.TextField(max_length=1024, blank=True, verbose_name=_('отзыв'))
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("комментарий к товару")
        verbose_name_plural = _("комментарии к товарам")
        ordering = ("product",)

    def __str__(self):
        return f"{self.reviews}"
