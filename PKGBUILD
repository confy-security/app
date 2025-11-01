# Maintainer: Henrique Sebastião <contato@henriquesebastiao.com>

_pkgname='confy'
pkgname='confy-app'
_module='confy'
pkgver='1.0.5'
pkgrel=1
pkgdesc="GUI application for the Confy encrypted communication system"
url="https://github.com/confy-security/app"
depends=(
    'python'
    'pyside6'
    'python-cryptography'
    'python-confy-addons'
    'python-httpx'
    'python-websockets'
)
makedepends=()
license=('custom:GNU General Public License v3 (GPLv3)')
arch=('x86_64')
source=(https://github.com/confy-security/app/releases/download/${pkgver}/confy-${pkgver}-1-x86_64.pkg.tar.zst)
sha256sums=('SKIP')

provides=($_pkgname)
conflicts=($_pkgname)

package() {
    # Bin
    install -D -m0755 "${srcdir}/usr/bin/confy" "${pkgdir}/usr/bin/confy"

    # Lib - Install all files from usr/lib recursively
    if [ -d "${srcdir}/usr/lib" ]; then
        find "${srcdir}/usr/lib" -type f | while read -r file; do
            # Get relative path from /usr/lib
            rel_path="${file#${srcdir}/usr/lib/}"
            # Create destination directory structure
            dest_dir="$(dirname "${pkgdir}/usr/lib/${rel_path}")"
            mkdir -p "${dest_dir}"
            # Install the file
            install -D -m0644 "${file}" "${pkgdir}/usr/lib/${rel_path}"
        done
    fi

    # Share
    install -D -m0644 "${srcdir}/usr/share/icons/hicolor/64x64/apps/com.henriquesebastiao.confy.png" "${pkgdir}/usr/share/icons/hicolor/64x64/apps/com.henriquesebastiao.confy.png"
    install -D -m0644 "${srcdir}/usr/share/icons/hicolor/128x128/apps/com.henriquesebastiao.confy.png" "${pkgdir}/usr/share/icons/hicolor/128x128/apps/com.henriquesebastiao.confy.png"
    install -D -m0644 "${srcdir}/usr/share/icons/hicolor/256x256/apps/com.henriquesebastiao.confy.png" "${pkgdir}/usr/share/icons/hicolor/256x256/apps/com.henriquesebastiao.confy.png"
    install -D -m0644 "${srcdir}/usr/share/applications/com.henriquesebastiao.confy.desktop" "${pkgdir}/usr/share/applications/com.henriquesebastiao.confy.desktop"

    rm -rf "confy-${pkgver}-1-x86_64.pkg.tar.zst"
}