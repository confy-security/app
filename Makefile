changelog:
	github_changelog_generator -u confy-security -p app -o CHANGELOG --no-verbose;

icons:
	./scripts/images.sh confy/assets/icon.png icon confy/assets

clean:
	rm -rf build dist logs

install:
	sudo pacman -U dist/confy-*.tar.zst

uninstall:
	sudo pacman -Rns confy

.PHONY: changelog icons clean install uninstall