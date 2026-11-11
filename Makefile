PYTHON ?= python3
VENV := .repro-venv
RUN := $(VENV)/bin/python

.PHONY: reproduce

reproduce: $(VENV)/.ready
	$(RUN) -m roles.train_roles
	$(RUN) -m eval.role_eval
	$(RUN) -m app.build_deck

$(VENV)/.ready: requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(RUN) -m pip install --disable-pip-version-check -r requirements.txt
	touch $@
