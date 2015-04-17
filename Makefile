.PHONY: run reload

run:
	python sso.py -s

reload:
	python sso.py --reload -s

help:
	python sso.py --help
