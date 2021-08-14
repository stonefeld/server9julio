.PHONY: help

help:
	@echo "Opciones posibles para ejecutar:\n\t'ls'\n\t'new'\n\t'old'"

new:
ifeq (,$(wildcard ./media/usuario.json))
	@echo "Debe exportar los datos antes de ejecutar esta tarea\nEjecute 'make old'"
else
	find . -type d -name "migrations" | xargs -r rm -r
	python3 manage.py makemigrations estacionamiento usuario usuariosistema registroGeneral registroTenis registroPileta
	python3 manage.py migrate
	@python3 manage.py shell < scripts/new_db.py
endif

old:
	python3 manage.py dumpdata usuario > media/usuario.json
	python3 manage.py dumpdata registroGeneral > media/registroGeneral.json

ls:
	@echo "Pasos a seguir:"
	@echo "\tsource .venv/bin/activate"
	@echo "\tpip3 list --outdated | awk '{print \$$1}' | tail -n+3 | xargs -r -n1 pip3 install --upgrade"
	@echo "\tpip3 install qrcode xhtml2pdf pillow"
	@echo "\tmake old"
	@echo "\tmysql -u admin -p"
	@echo "\tDentro de MySQL:"
	@echo "\t\tDROP SCHEMA 9Julio_db;"
	@echo "\t\tCREATE SCHEMA 9Julio_db;"
	@echo "\t\tquit;\n"
	@echo "\tgit status"
	@echo "\tgit restore ."
	@echo "\tgit checkout --track deploy_estacionamiento"
	@echo "\tgit pull"
	@echo "\tmake new"
	@echo "\tgit remote set-url origin https://github.com/stonefeld/server9julio"
	@echo "\tsudo systemctl restart httpd mariadb"
	@echo "\tdeactivate"
