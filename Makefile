.PHONY: help

help:
	@echo "Opciones posibles para ejecutar:\n\t'new'\n\t'old'"

new:
ifeq (,$(wildcard ./media/usuario.json))
	@echo "Debe exportar los datos antes de ejecutar esta tarea\nEjecute 'make old'"
else
	python3 manage.py makemigrations estacionamiento usuario usuariosistema registroGeneral registroTenis registroPileta
	python3 manage.py migrate
	@python3 manage.py shell < scripts/new_db.py
endif

old:
	python3 manage.py dumpdata usuario > media/usuario.json
	python3 manage.py dumpdata registroGeneral > media/registroGeneral.json
