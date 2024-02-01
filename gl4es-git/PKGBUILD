# Maintainer: Mahmut Dikcizgi <boogiepop a~t gmx com>
# Maintainer: 7Ji <pugokushin@gmail.com>

pkgname=gl4es-git
pkgver=r2647.e39434a2
pkgrel=1
pkgdesc='OpenGL for GLES Hardware'
arch=('x86_64' 'aarch64' 'arm7h')
url='https://github.com/ptitSeb/gl4es'
license=('MIT')
depends=('coreutils' 'libx11')
makedepends=('cmake')
options=(!lto strip)
source=(git+https://github.com/ptitSeb/gl4es.git#branch=master)
sha256sums=('SKIP')

prepare() {
  local _cmake_opts=(
    '-DCMAKE_BUILD_TYPE=RelWithDebInfo'
  )
  if [[ ${CARCH} != 'x86_64' ]]; then
    _cmake_opts+=('-DODROID=1')
  fi
  mkdir -p build
  cmake -S gl4es -B build "${_cmake_opts[@]}"
}

pkgver() {
  cd gl4es
  printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

build() {
  cmake --build build
}


package() {
  provides=(gl4es $pkgname)
  conflicts=(gl4es $pkgname)
  DESTDIR="$pkgdir" cmake --install build
  ln -s libGL.so.1 "$pkgdir"/usr/lib/gl4es/libGL.so
}
