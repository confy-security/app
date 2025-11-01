build:
	makepkg --syncdeps;

install:
	sudo yay -U --noconfirm *.zst;

uninstall:
	sudo yay -R --noconfirm confy-app;

clean:
	rm -rf src pkg cli;
	rm -f *.zst *.tar.gz;

srcinfo:
	makepkg --printsrcinfo > .SRCINFO;

.PHONY: pkgbuild clean build install uninstall srcinfo