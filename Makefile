# Migrations
makemigrations:
	cd /vagrant && python3 manage.py makemigrations

migrate:
	cd /vagrant && python3 manage.py migrate

apply-migrations: makemigrations migrate


# Load fixtures
load-superuser:
	cd /vagrant && python3 manage.py loaddata fixtures/superuser.json

load-promotions:
	cd /vagrant && \
		python3 manage.py loaddata fixtures/promotions/promotions.json fixtures/promotions/promotion_group.json

load-products:
	cd /vagrant && \
		python3 manage.py loaddata fixtures/products/category.json fixtures/products/product.json

load-props:
	cd /vagrant && \
		python3 manage.py loaddata fixtures/products/property.json \
			fixtures/products/property_product.json \
			fixtures/products/property_category.json

load-banners:
	cd /vagrant && python3 manage.py loaddata fixtures/banners/banners.json

load-clients:
	cd /vagrant && python3 manage.py loaddata fixtures/accounts/client.json

load-shops:
	cd /vagrant && \
		python3 manage.py loaddata fixtures/shops/shops.json fixtures/shops/shop_product.json

load-fixtures: load-superuser load-promotions load-products load-props load-banners load-clients load-shops


# Dump fixtures
dump-categories:
	cd /vagrant && \
		python3 -Xtf8 manage.py dumpdata products.Category --indent 2 -o fixtures/products/category.json && \
		python3 -Xtf8 manage.py dumpdata products.PropertyCategory --indent 2 -o fixtures/products/property_category.json

dump-promotions:
	cd /vagrant && \
		python3 -Xutf8 manage.py dumpdata promotions.Promotions --indent 2 -o fixtures/promotions/promotions.json && \
		python3 -Xutf8 manage.py dumpdata promotions.PromotionGroup --indent 2 -o fixtures/promotions/promotion_group.json

dump-products:
	cd /vagrant && \
		python3 -Xtf8 manage.py dumpdata products.Product --indent 2 -o fixtures/products/product.json && \
		python3 -Xtf8 manage.py dumpdata products.Property --indent 2 -o fixtures/products/property.json && \
		python3 -Xtf8 manage.py dumpdata products.PropertyProduct --indent 2 -o fixtures/products/property_product.json

dump-banners:
	cd /vagrant && \
		python3 -Xutf8 manage.py dumpdata banners.Banners --indent 2 -o fixtures/banners/banners.json

dump-clients:
	cd /vagrant && \
		python3 -Xutf8 manage.py dumpdata accounts.Client --indent 2 -o fixtures/accounts/client.json

dump-shops:
	cd /vagrant && \
		python3 -Xutf8 manage.py dumpdata shops.Shops --indent 2 -o fixtures/shops/shops.json && \
		python3 -Xutf8 manage.py dumpdata shops.ShopProduct --indent 2 -o fixtures/shops/shop_product.json

dump-fixtures: dump-categories dump-promotions dump-products dump-banners dump-clients dump-shops


# Run django test server
runserver:
	ip=$$(hostname -I | xargs | awk -F' ' '{print $$1}') && \
	cd /vagrant && python3 manage.py runserver $$ip:8000


# Flake8
flake8:
	cd /vagrant && python3 -m flake8 --exclude migrations
