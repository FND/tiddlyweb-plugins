.PHONY: test dist upload

clean:
	find . -name "*.pyc" | xargs rm || true
	rm -r build dist || true

test:
	py.test -x test

dist: test
	python setup.py sdist

upload: clean pypi

pypi:
	python setup.py sdist upload
