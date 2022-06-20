import django_filters
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured


class CustomFilterSet(django_filters.FilterSet):
    """
    Кастомынй набор фильтров.
    """

    cache_key_prefix = "filter_set"

    def filter_queryset(self, queryset):
        """
        Возвращает пустой queryset, если форма фильтра невалидна,
        в противном случае вернет отфильтрованный queryset.
        """
        if not len(self.form.cleaned_data.items()):
            return queryset.none()
        return super().filter_queryset(queryset)

    def cache(self, key, timeout):
        """
        Кэширует фильтр.
        """
        key = f"{self.cache_key_prefix}:{key}"

        if key in cache:
            filter_set = cache.get(key)
        else:
            filter_set = self.form.as_p()
            cache.set(key, filter_set, timeout=timeout)

        return filter_set

    @staticmethod
    def delete_cache(key):
        """
        Удаляет фильтр из кэша.
        """
        cache.delete(key)


def filterset_factory(model, filterset=django_filters.FilterSet, model_fields="__all__", fields=None, exclude=None,
                      form=None, filter_overrides=None):
    """
    Фабрика для создания FilterSet.
    """
    # Код скопирован из django.forms.models.modelform_factory и адаптирован
    # для filterset.

    # Собираем атрибуты для класса Meta.
    attrs = {"model": model}
    if model_fields is not None:
        attrs["fields"] = model_fields
    if exclude is not None:
        attrs["exclude"] = exclude
    if form is not None:
        attrs["form"] = form
    if filter_overrides is not None:
        attrs["filter_overrides"] = filter_overrides

    # Если родительский filterset имеет свой класс Meta, то
    # нужно унаследовать этот класс.
    bases = (filterset.Meta,) if hasattr(filterset, "Meta") else ()
    meta_cls = type("Meta", bases, attrs)
    # Имя класса для нового filterset.
    class_name = model.__name__ + "FilterSet"

    # Атрибуты класса для нового filterset.
    filterset_class_attrs = {
        "Meta": meta_cls,
    }
    if fields:
        filterset_class_attrs.update(fields)

    if (getattr(meta_cls, "fields", None) is None and
            getattr(meta_cls, "exclude", None) is None):
        raise ImproperlyConfigured(
            "Calling filterset_factory without defining 'fields' or "
            "'exclude' explicitly is prohibited."
        )

    # Создание нового класса filterset.
    return type(filterset)(class_name, (filterset,), filterset_class_attrs)
