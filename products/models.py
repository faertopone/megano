import re

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from timestamps.models import models, SoftDeletes

from promotions.models import PromotionGroup


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


class Product(SoftDeletes):
    """
    Товар.
    """
    name = models.CharField(max_length=1000, verbose_name=_("название товара"))
    article = models.CharField(max_length=100, verbose_name=_("артикул"))
    description = models.CharField(max_length=255, verbose_name=_("описание товара"), blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=1,
                                validators=[MinValueValidator(1)], verbose_name=_("цена"))
    rating = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                 validators=[MinValueValidator(0)], verbose_name=_("рейтинг"))
    flag_limit = models.BooleanField(default=False, verbose_name=_("товар заканчивается"))
    category = models.ForeignKey("Category", on_delete=models.CASCADE,
                                 related_name="products", related_query_name="product",
                                 verbose_name=_("категория каталога"))
    properties = models.ManyToManyField("Property", through="PropertyProduct",
                                        related_name="products", related_query_name="product",
                                        verbose_name=_("свойства товара"))
    tag = models.TextField(max_length=100, verbose_name=_('теги'), blank=True)
    tags = models.ManyToManyField('Tag', related_name='products')
    promotion_group = models.ForeignKey(PromotionGroup, on_delete=models.SET_DEFAULT, default=None,
                                        null=True, blank=True,
                                        related_name="products", related_query_name="product",
                                        verbose_name=_("скидочная группа товаров"),
                                        help_text=_("Товар может входить в группу товаров со скидкой."
                                                    " В этом случае на каждый товар в группе действует"
                                                    " определенная скидка"))

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


class Tag(models.Model):
    """ Модель тегов для товара """
    substance = models.CharField(max_length=30, unique=True)

    class Meta:
        verbose_name = _('тег')
        verbose_name_plural = _('теги')
        db_table = 'Tags'

    def __str__(self):
        return f'{self.substance}'


class Property(models.Model):
    """
    Свойство товара.
    """
    _alias_regexp = re.compile(r"^[a-zA-Z][_a-zA-Z0-9]*$")

    name = models.CharField(max_length=300, unique=True, verbose_name=_("имя свойства"))
    tooltip = models.CharField(max_length=1000, blank=True, default='',
                               help_text=_("Опишите подробнее, что это за свойство товара"),
                               verbose_name=_("примечание"))
    alias = models.CharField(max_length=300, unique=True, validators=[RegexValidator(regex=_alias_regexp)], null=True,
                             verbose_name=_("Псевдоним"),
                             help_text="Псевдоним участвует в построении фильтра для свойства"
                                       " и должен соответствовать выражению " + _alias_regexp.pattern)

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
        return f"{self.value}"


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
    filtered = models.BooleanField(default=True, verbose_name=_("фильтр"),
                                   help_text=_("Если отмечено, то можно будет"
                                               " фильтровать товары по этому свойству"))
    filter_position = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)],
                                                  verbose_name=_("Позиция в фильтре"),
                                                  help_text=_("Свойства в фильтре будут располагаться"
                                                              " в порядке возрастания позиции"))

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
    photo = models.ImageField(upload_to='products_photo/', default='products_photo/default.png',
                              verbose_name=_('фото товара'))
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_('товар'),
        related_name="product_photo"
    )


    class Meta:
        verbose_name = _('фото товара')
        verbose_name_plural = _('фото товаров')


class UserReviews(SoftDeletes):
    """
    Модель добавления комментария к товару
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('пользователь'),
                             related_name="user_review")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('товар'))
    reviews = models.TextField(max_length=1024, blank=True, verbose_name=_('отзыв'))
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("комментарий к товару")
        verbose_name_plural = _("комментарии к товарам")
        ordering = ("product",)

    def __str__(self):
        return f"{self.reviews}"
