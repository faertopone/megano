# Migrations
makemigrations:
	cd /vagrant && python3 manage.py makemigrations

migrate:
	cd /vagrant && python3 manage.py migrate

apply-migrations: makemigrations migrate


# Load fixtures
load-superuser:
	cd /vagrant && python3 manage.py loaddata fixtures/superuser.json

load-categories:
	cd /vagrant && python3 manage.py loaddata fixtures/products/category.json

load-products:
	cd /vagrant && python3 manage.py loaddata fixtures/products/product.json \
		fixtures/products/property.json \
		fixtures/products/property_product.json

load-fixtures: load-superuser load-categories load-products


# Dump fixtures
dump-categories:
	cd /vagrant && python3 -Xtf8 manage.py dumpdata products.Category --indent 2 -o fixtures/products/category.json

dump-products:
	cd /vagrant && \
		python3 -Xtf8 manage.py dumpdata products.Product --indent 2 -o fixtures/products/product.json \
		python3 -Xtf8 manage.py dumpdata products.Property --indent 2 -o fixtures/products/property.json \
		python3 -Xtf8 manage.py dumpdata products.PropertyProduct --indent 2 -o fixtures/products/property_product.json

dump-fixtures: dump-categories dump-products


# Run django test server
runserver:
	ip=$$(hostname -I | xargs) && \
	cd /vagrant && python3 manage.py runserver $$ip:8000


# Flake8
flake8:
	cd /vagrant && python3 -m flake8 --exclude migrations
