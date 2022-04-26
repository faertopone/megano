from django.db import models


class Product(models.Model):
    """
    Модель товара
    """
    name = models.CharField(max_length=256)
    property = models.ManyToManyField('Property', through='ProductProperty', null=True, blank=True)


class Property(models.Model):
    """
    Модель измеримых свойств товара.
    Поле measure можно определить через предопределенный список единиц измерения
    """
    name = models.CharField(max_length=256)
    measure = models.CharField(max_length=256, verbose_name='Единица измерения')


class ProductProperty(models.Model):
    """
    Модель измеримых свойств товара.
    Поле measure можно определить через предопределенный список единиц измерения
    """
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    property = models.ForeignKey(Property, on_delete=models.RESTRICT)
    value = models.IntegerField(verbose_name='Значение свойства')
