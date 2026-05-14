# Reproduction targets for the nontrivial-snark $S^2$-flow theorem package.
#
# Fast path -- replay stored certificates only:
#     make verify
#     make verify-certs
#
# Slow path -- regenerate everything from `geng` upward:
#     make clean catalogue sweep certs verify-certs
#
# All targets are designed to be run from this directory.

VENV_PYTHON ?= ../../.venv/bin/python
GENG ?= geng
ORDERS := 10 14 16 18 20 22 24
SNARK_ORDERS := 10 18 20 22 24
RADIUS ?= 1e-5
DPS ?= 50
RESTARTS ?= 200

.PHONY: help verify verify-certs catalogue sweep certs clean manifest

help:
	@echo "Targets:"
	@echo "  verify         pytest regression (41 tests, ~6s)"
	@echo "  verify-certs   replay 3247 interval certificates (~50 min for n=26, ~70 min more for n=28)"
	@echo "  catalogue      regenerate cubic-g5 catalogues via geng, then filter to nontrivial snarks"
	@echo "  sweep          run numerical witness sweep on the nontrivial-snark catalogue"
	@echo "  certs          run Krawczyk interval certifier on the sweep output"
	@echo "  manifest       (re)write data/catalogues/nontrivial_snarks_n10_to_28.manifest.json"
	@echo "  clean          remove generated intermediate files (keeps committed catalogues)"
	@echo ""
	@echo "Variables: VENV_PYTHON=$(VENV_PYTHON), GENG=$(GENG), RADIUS=$(RADIUS), DPS=$(DPS)"

verify:
	$(VENV_PYTHON) -m pytest tests/ -q

verify-certs:
	$(VENV_PYTHON) scripts/verify_sweep.py data/interval_certs/nontrivial_n10_to_28

# Regeneration pipeline ---------------------------------------------------

CUBIC_FILES := $(foreach n,$(ORDERS),data/catalogues/cubic_g5_n$(n).g6)
SNARK_FILES := $(foreach n,$(SNARK_ORDERS),data/catalogues/nontrivial_snarks_n$(n).g6)

data/catalogues/cubic_g5_n%.g6:
	@mkdir -p $(@D)
	$(GENG) -d3 -D3 -c -tf -q $* > $@

data/catalogues/nontrivial_snarks_n%.jsonl: data/catalogues/cubic_g5_n%.g6
	$(VENV_PYTHON) scripts/catalogue.py $< --filter nontrivial-snark --emit-jsonl > $@

data/catalogues/nontrivial_snarks_n%.g6: data/catalogues/nontrivial_snarks_n%.jsonl
	$(VENV_PYTHON) -c "import json,sys; \
		[print(json.loads(l)['graph6']) for l in open('$<')]" > $@

data/catalogues/nontrivial_snarks_n10_to_28.g6: $(SNARK_FILES)
	cat $^ > $@

catalogue: data/catalogues/nontrivial_snarks_n10_to_28.g6

sweep: catalogue
	$(VENV_PYTHON) scripts/sweep.py \
	    --from-catalogue data/catalogues/nontrivial_snarks_n10_to_28.g6 \
	    --out data/sweep_results/nontrivial_n10_to_28 \
	    --restarts $(RESTARTS)

certs: sweep
	$(VENV_PYTHON) scripts/interval.py \
	    data/sweep_results/nontrivial_n10_to_28/*.json \
	    --radius $(RADIUS) --dps $(DPS) \
	    --out data/interval_certs/nontrivial_n10_to_28

manifest:
	$(VENV_PYTHON) scripts/manifest.py \
	    --catalogue data/catalogues/nontrivial_snarks_n10_to_28.g6 \
	    --orders $(SNARK_ORDERS) \
	    --intermediate-dir data/catalogues \
	    --cert-dir data/interval_certs/nontrivial_n10_to_28 \
	    --name nontrivial_snarks_n10_to_28 \
	    --out data/catalogues/nontrivial_snarks_n10_to_28.manifest.json

clean:
	rm -rf data/sweep_results/nontrivial_n10_to_28
	rm -rf data/interval_certs/nontrivial_n10_to_28
	rm -f data/catalogues/nontrivial_snarks_n*.jsonl
