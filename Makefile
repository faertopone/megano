# инициализация виртуальной машины
up:
	vagrant up

# миграции бд
makemigrations:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && python manage.py makemigrations"

migrate:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && python manage.py migrate"

# инициализация сервиса
service_init:
	vagrant ssh -c "make migrate && make load-fixtures"

# остановка вирутальной машины
stop:
	vagrant halt



# Load fixtures
load-superuser:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && python manage.py loaddata fixtures/superuser.json"


load-products:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && python manage.py loaddata fixtures/products/category.json fixtures/products/product.json"

load-props:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && python manage.py loaddata fixtures/products/property.json fixtures/products/property_product.json fixtures/products/property_category.json"

load-fixtures:
	vagrant ssh -c "make migrate && make load-superuser && make load-products && make load-props"


# Dump fixtures
dump-categories:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/  \
		python -Xtf8 manage.py dumpdata products.Category --indent 2 -o fixtures/products/category.json && \
		python -Xtf8 manage.py dumpdata products.PropertyCategory --indent 2 -o fixtures/products/property_category.json"

dump-products:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/  \
		python -Xtf8 manage.py dumpdata products.Product --indent 2 -o fixtures/products/product.json && \
		python -Xtf8 manage.py dumpdata products.Property --indent 2 -o fixtures/products/property.json && \
		python -Xtf8 manage.py dumpdata products.PropertyProduct --indent 2 -o fixtures/products/property_product.json"

dump-fixtures: dump-categories dump-products

# Run django test server
runserver:
    vagrant ssh -c "source ~/venv/bin/activate && ip=$$(hostname -I | xargs) && cd /vagrant/ && python manage.py runserver $$ip:8000"

# Flake8
flake8:
	vagrant ssh -c "source ~/venv/bin/activate && cd /vagrant/ && flake8 --exclude migrations"
