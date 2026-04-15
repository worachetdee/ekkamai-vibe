FAMILY_SLUG := patiwat
DESIGNSPACE := sources/$(FAMILY_SLUG).designspace
CONFIG      := sources/config.yaml

.PHONY: build build-vf build-static check clean snapshot

build: build-vf build-static

build-vf:
	gftools builder $(CONFIG)

build-static:
	mkdir -p fonts/ttf
	@for ufo in sources/*.ufo; do \
		name=$$(basename $$ufo .ufo); \
		fontmake -u $$ufo -o ttf \
			--output-path fonts/ttf/$$name.ttf \
			--keep-overlaps --keep-direction ; \
	done
	python3 scripts/patch_metadata.py

check:
	fontbakery check-googlefonts --succinct fonts/variable/*.ttf fonts/ttf/*.ttf

clean:
	rm -rf fonts/ master_ufo/ instance_ufo/ variable_ttf/

snapshot:
	@test -n "$(VERSION)" || (echo "Usage: make snapshot VERSION=1.001"; exit 1)
	mkdir -p versions/v$(VERSION)
	cp -R fonts versions/v$(VERSION)/
	@echo "Snapshot saved to versions/v$(VERSION)/"
