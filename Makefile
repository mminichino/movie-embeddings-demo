export PROJECT_NAME := $$(basename $$(pwd))
export PROJECT_VERSION := $(shell cat VERSION)

commit:
		git commit -am "Version $(shell cat VERSION)"
		git push
patch:
		bumpversion --allow-dirty patch
minor:
		bumpversion --allow-dirty minor
major:
		bumpversion --allow-dirty major
release:
		gh release create -R "mminichino/$(PROJECT_NAME)" \
		-t "Release $(PROJECT_VERSION)" \
		-n "Release $(PROJECT_VERSION)" \
		$(PROJECT_VERSION)
upload:
		$(eval DATA_FILE := $(shell ls -tr *.json | tail -1))
		gh release upload -R "mminichino/$(PROJECT_NAME)" $(PROJECT_VERSION) $(DATA_FILE)
remove:
		$(eval DATA_FILE := $(shell ls -tr *.json | tail -1))
		$(eval ASSET_NAME := $(shell basename $(DATA_FILE)))
		gh release delete-asset -R "mminichino/$(PROJECT_NAME)" $(PROJECT_VERSION) $(ASSET_NAME) -y
