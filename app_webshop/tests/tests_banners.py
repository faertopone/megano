from unittest.mock import patch
from django.test import TestCase
from app_webshop.models import Banners
from django.test.signals import template_rendered
from django.shortcuts import render


COUNT_BANNERS = 10

class BannersTest(TestCase):

    # @staticmethod
    # def render_patch(request, template, context):
    #     """Work-around for the django test client not working properly with
    #     jinga2 templates (https://code.djangoproject.com/ticket/24622).
    #
    #     """
    #     template_rendered.send(sender=None, template=template, context=context)
    #     return render(request, template, context)

    @classmethod
    def setUpTestData(cls):

        name_file = 'Баннер_1_photo_videoca.png'
        for i_baner in range(COUNT_BANNERS):
            Banners.objects.create(
                name='test_' + str(i_baner),
                photo=name_file,
                name_product='test',
                url_link='test',
                description='test_desp',
                version=i_baner,
            )


    def test_banners_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(len(response.context['banners']), COUNT_BANNERS)
        # self.assertTemplateUsed(response.tempalate, 'index.html')