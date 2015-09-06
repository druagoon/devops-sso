.PHONY: run reload example help

run:
	python sso.py -s

reload:
	python sso.py --reload -s

example:
	cp config.inc.py config.py
	@if [ ! -d "data" ]; then mkdir data; fi
	cp -r demo/servers data/

help:
	python sso.py --help
