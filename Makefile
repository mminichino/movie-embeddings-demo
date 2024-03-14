#

commit:
		git commit -am "Version $(shell cat VERSION)"
		git push
patch:
		bumpversion --allow-dirty patch
minor:
		bumpversion --allow-dirty minor
major:
		bumpversion --allow-dirty major
