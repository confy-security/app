changelog:
	github_changelog_generator -u confy-security -p app -o CHANGELOG --no-verbose;

build:
	poetry run briefcase build
	briefcase package

flatpak:
	poetry run briefcase build linux flatpak --test --no-input --log
	poetry run briefcase package linux flatpak --update --adhoc-sign --no-input --log

icons:
	./scripts/images.sh confy/assets/icon.png icon confy/assets

clean:
	rm -rf build dist logs

install:
	sudo pacman -U dist/confy-*.tar.zst

uninstall:
	sudo pacman -Rns confy

.PHONY: changelog icons clean install uninstall