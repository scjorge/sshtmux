.PHONY:

PROJECT = sshtmux

linter:
	ruff check --select I --fix ${PROJECT} && \
    ruff format ${PROJECT}
