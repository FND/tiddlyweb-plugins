.PHONY: test dist release

clean:
	find . -name "*.pyc" | xargs rm || true
	rm -r build dist *.egg-info || true

test:
	py.test -x test

dist: test
	python setup.py sdist

release: clean test pypi

pypi:
	python setup.py sdist upload
