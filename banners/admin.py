from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Banners
from .forms import BannersForm
from django.utils.translation import gettext_lazy as _

# Админ панель для создания баннера
@admin.register(Banners)
class BannersAdmin(admin.ModelAdmin):
    form = BannersForm
    list_display = ('name', 'id', 'url_link', 'banner_photo', 'min_description_admin', 'is_active', 'creation_date')
    readonly_fields = ['banner_photo']
    list_filter = ['name', 'is_active', 'creation_date']
    actions = ['active', 'not_active']
    search_fields = ['name']
    fieldsets = (
        (_('Наименования банера и товара'), {
            'fields': (('name', 'name_product', 'version'), )
        }),
        (None, {
            'fields': (('url_link'),)
        }),
        (_('Фотографии для баннера'), {
            'fields': (('photo', 'banner_photo'),)
        }),
        (None, {
            'fields': (('description'),)
        }),
        (None, {
            'fields': (('is_active'),)
        }),


    )

    def active(self, requests, queryset ):
        queryset.update(is_active=True)

    def not_active(self, requests, queryset):
        queryset.update(is_active=False)

    active.short_description = _('Включить баннер')
    not_active.short_description = _('Выключить баннер')

    #Если фотографии нету, выберем в описании
    def banner_photo(self, obj):
        if not obj.photo:
            return 'Нету фотографии'
        return mark_safe('<img src="{}" width="50" height="50" />'.format(obj.photo.url))

    banner_photo.short_description = _('Изображение баннера')

    # Функция для отображения описания, только первые 30 символов
    def min_description_admin(self, obj):
        text_str = obj.description
        text = list(text_str)
        if len(text) > 30:
            text_str = obj.description[:30] + '...'
        return text_str

    min_description_admin.short_description = _('Мини описание')





admin.site.site_title = _('Django Megano Admin')
admin.site.site_header = _('Django Megano Admin')