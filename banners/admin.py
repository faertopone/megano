from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Banners
from .forms import BannersForm
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import truncatewords


# Админ панель для создания баннера
@admin.register(Banners)
class BannersAdmin(admin.ModelAdmin):
    form = BannersForm
    list_display = ('name', 'id', 'banner_photo', 'min_description_admin', 'is_active', 'creation_date')
    readonly_fields = ['banner_photo']
    list_filter = ['name', 'is_active', 'creation_date']
    actions = ['active', 'not_active']
    # Поиск по имени и совпадение с началом слова типа startswith
    search_fields = ['^name', ]
    # Добавляют полю с FK и M2M поиск, так же не забыть добавить в search_fields, имя поля с поиском из FK , M2M
    autocomplete_fields = ['product_banner']
    fieldsets = (
        (_('Наименования банера и товара'), {
            'fields': ('name', 'product_banner'),
        }),
        (_('Фотография для баннера'), {
            'fields': (('photo', 'banner_photo'),)
        }),
        (None, {
            'fields': ('description',)
        }),
        (None, {
            'fields': ('is_active',)
        }),

    )

    @admin.display(description=_("активировать баннер"))
    def active(self, request: HttpRequest, queryset: QuerySet):
        """
        Активирует выбранный баннер
        """
        update = queryset.update(is_active=True)
        self.message_user(request, f'Активирован {update} баннер!')

    @admin.display(description=_("отключить баннер"))
    def not_active(self, request: HttpRequest, queryset: QuerySet):
        """
        Отключает выбранный баннер
        """
        update = queryset.update(is_active=False)
        self.message_user(request, f'Выключен {update} баннер!')

    @staticmethod
    @admin.display(description=_('изображение баннера'))
    def banner_photo(obj: Banners):
        if not obj.photo:
            return 'Нету фотографии'
        return mark_safe('<img src="{}" width="50" height="50" />'.format(obj.photo.url))

    @staticmethod
    @admin.display(description=_('Мини описание'))
    def min_description_admin(obj: Banners):
        return format_html(
            '<span title="{}">{}</span>'.format(
                obj.description,
                truncatewords(obj.description, 5)
            )
        )


admin.site.site_title = _('Джанго Мегано Админ')
admin.site.site_header = _('Джанго Мегано Админ')
