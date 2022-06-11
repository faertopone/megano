from django.test import TestCase
from banners.models import Banners

COUNT_BANNERS = 10


class BannersTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        name_file = 'Баннер_1_photo_video.png'
        for i_banner in range(COUNT_BANNERS):
            Banners.objects.create(
                name='test_' + str(i_banner),
                photo=name_file,
                name_product='test',
                url_link='test',
                description='test_des',
                version=i_banner,
            )

    def test_banners_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
