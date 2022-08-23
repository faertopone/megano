# инициализация виртуальной машины
up:
	vagrant up

# остановка вирутальной машины
stop:
	vagrant halt


# Migrations
makemigrations:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && python manage.py makemigrations"

migrate:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && python manage.py migrate"


# инициализация сервиса
service_init:
	vagrant ssh -c "make migrate && make load-fixtures"


# Load fixtures
load-superuser:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && python manage.py loaddata fixtures/superuser.json"

load-promotions:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && python manage.py loaddata fixtures/promotions/promotions.json fixtures/promotions/promotion_group.json"

load-products:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && python manage.py loaddata fixtures/products/category.json fixtures/products/product.json fixtures/products/product_photo.json"

load-props:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && python manage.py loaddata fixtures/products/property.json fixtures/products/property_product.json fixtures/products/property_category.json"

load-banners:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && python manage.py loaddata fixtures/banners/banners.json"

load-clients:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && python manage.py loaddata fixtures/accounts/client.json"

load-shops:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && python manage.py loaddata fixtures/shops/shop.json fixtures/shops/shop_photo.json fixtures/shops/shop_product.json"

load-fixtures:
	vagrant ssh -c "make migrate && make load-superuser && make load-promotions && make load-products && make load-props && make load-banners && make load-clients && make load-shops"


# Dump fixtures
dump-categories:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/  \
		python -Xtf8 manage.py dumpdata products.Category --indent 2 -o fixtures/products/category.json && \
		python -Xtf8 manage.py dumpdata products.PropertyCategory --indent 2 -o fixtures/products/property_category.json"

dump-promotions:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/  \
		python -Xutf8 manage.py dumpdata promotions.Promotions --indent 2 -o fixtures/promotions/promotions.json && \
		python -Xutf8 manage.py dumpdata promotions.PromotionGroup --indent 2 -o fixtures/promotions/promotion_group.json"

dump-products:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/  \
		python -Xtf8 manage.py dumpdata products.Product --indent 2 -o fixtures/products/product.json && \
		python -Xtf8 manage.py dumpdata products.Property --indent 2 -o fixtures/products/property.json && \
		python -Xtf8 manage.py dumpdata products.PropertyProduct --indent 2 -o fixtures/products/property_product.json && \
		python -Xtf8 manage.py dumpdata products.ProductPhoto --indent 2 -o fixtures/products/product_photo.json"

dump-banners:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/  \
		python -Xutf8 manage.py dumpdata banners.Banners --indent 2 -o fixtures/banners/banners.json"

dump-clients:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/  \
		python -Xutf8 manage.py dumpdata accounts.Client --indent 2 -o fixtures/accounts/client.json"

dump-shops:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/  \
		python -Xutf8 manage.py dumpdata shops.Shops --indent 2 -o fixtures/shops/shop.json && \
		python -Xutf8 manage.py dumpdata shops.ShopPhoto --indent 2 -o fixtures/shops/shop_photo.json && \
		python -Xutf8 manage.py dumpdata shops.ShopProduct --indent 2 -o fixtures/shops/shop_product.json"

dump-fixtures: dump-categories dump-promotions dump-products dump-banners dump-clients dump-shops


# Run django test server
runserver:
	vagrant ssh -c "source ~/venv/bin/activate && \
		ip=$$(hostname -I | xargs | awk -F' ' '{print $$1}') && \
		cd /vagrant/ && python manage.py runserver $$ip:8000"


# Flake8
flake8:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && flake8 --exclude migrations"
