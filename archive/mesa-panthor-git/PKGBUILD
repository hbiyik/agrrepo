# Maintainer: Jan Keith Darunday <jkcdarunday+aur.archlinux.org@gmail.com>
# Contributor: Laurent Carlier <lordheavym@gmail.com>
# Contributor: Felix Yan <felixonmars@archlinux.org>
# Contributor: Jan de Groot <jgc@archlinux.org>
# Contributor: Andreas Radke <andyrtr@archlinux.org>
# Contributor: Dan Johansen <strit@manjaro.org>

# ALARM: Kevin Mihelich <kevin@archlinuxarm.org>
#  - Removed Gallium3D drivers/packages for chipsets that don't exist in our ARM devices (intel, VMware svga).
#  - added broadcom and panfrost vulkan packages
#  - enable lto for aarch64

highmem=1
_branch="v10+reg-cache"
pkgbase=mesa-panthor-git
pkgname=('vulkan-mesa-layers-panthor-git' 'opencl-mesa-panthor-git' 'vulkan-swrast-panthor-git' 'libva-mesa-driver-panthor-git' 'mesa-vdpau-panthor-git' 'mesa-panthor-git')
pkgdesc="Mesa with Panfrost that supports Mali G610/G710 GPUs (Valhall v10 CSF)"
pkgver=r163343.3504c9b1b31
pkgrel=1
arch=('aarch64' 'arm7vh' 'x86_64' 'i686')
makedepends=('python-mako' 'libxml2' 'libx11' 'xorgproto' 'libdrm' 'libxshmfence' 'libxxf86vm'
             'libxdamage' 'libvdpau' 'libva' 'wayland' 'wayland-protocols' 'zstd' 'elfutils' 'llvm'
             'libomxil-bellagio' 'libclc' 'clang' 'libglvnd' 'libunwind' 'lm_sensors' 'libxrandr'
             'systemd' 'valgrind' 'glslang' 'vulkan-icd-loader' 'directx-headers' 'cmake' 'meson')
url="https://www.mesa3d.org/"
license=('custom')
options=('!lto')
source=(mesa::git+https://gitlab.freedesktop.org/bbrezillon/mesa.git#branch=${_branch}
        LICENSE
        "001-fix_build_egldriver_EGLAttrib.patch")

sha512sums=('SKIP'
            'f9f0d0ccf166fe6cb684478b6f1e1ab1f2850431c06aa041738563eb1808a004e52cdec823c103c9e180f03ffc083e95974d291353f0220fe52ae6d4897fecc7'
            'b50fcb24f65464996f29eeed060fc09c7c6a8864c0a84230967e0a98166721d1dec2833bd0989a2e67b0bc06059e69910b48618f9631eb51833e51f4563462f4')

prepare() {
  cd mesa
  patch -p1 -N -i ../001-fix_build_egldriver_EGLAttrib.patch
}

pkgver() {
  cd mesa
  ( set -o pipefail
    git describe --long 2>/dev/null | sed 's/\([^-]*-g\)/r\1/;s/-/./g' ||
    printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
  )
}


build() {
  arch-meson mesa build \
    -D b_ndebug=true \
    -D b_lto=false \
    -D platforms=x11,wayland \
    -D gallium-drivers=r300,r600,radeonsi,nouveau,swrast,virgl,kmsro,panfrost \
    -D vulkan-drivers=swrast \
    -D vulkan-layers=device-select,overlay \
    -D dri3=enabled \
    -D egl=enabled \
    -D gallium-extra-hud=true \
    -D gallium-nine=true \
    -D gallium-omx=bellagio \
    -D gallium-opencl=icd \
    -D gallium-va=enabled \
    -D gallium-vdpau=enabled \
    -D gallium-xa=disabled \
    -D gbm=enabled \
    -D gles1=disabled \
    -D gles2=enabled \
    -D glvnd=true \
    -D glx=dri \
    -D libunwind=disabled \
    -D llvm=enabled \
    -D lmsensors=enabled \
    -D osmesa=true \
    -D shared-glapi=enabled \
    -D microsoft-clc=disabled \
    -D video-codecs=vc1dec,h264dec,h264enc,h265dec,h265enc \
    -D valgrind=enabled \
    -D android-libbacktrace=disabled

  # Print config
  meson configure build --no-pager

  ninja -C build
  meson compile -C build

  # fake installation to be seperated into packages
  # outside of fakeroot but mesa doesn't need to chown/mod
  DESTDIR="${srcdir}/fakeinstall" meson install -C build
}

_install() {
  local src f dir
  for src; do
    f="${src#fakeinstall/}"
    dir="${pkgdir}/${f%/*}"
    install -m755 -d "${dir}"
    mv -v "${src}" "${dir}/"
  done
}

package_vulkan-mesa-layers-panthor-git() {
  pkgdesc="Mesa's Vulkan layers - Panfork"
  depends=('libdrm' 'libxcb' 'wayland' 'python')
  conflicts=('vulkan-mesa-layer' 'vulkan-mesa-layers')
  provides=('vulkan-mesa-layers')
  replaces=('vulkan-mesa-layer')

  _install fakeinstall/usr/share/vulkan/explicit_layer.d
  _install fakeinstall/usr/share/vulkan/implicit_layer.d
  _install fakeinstall/usr/lib/libVkLayer_*.so
  _install fakeinstall/usr/bin/mesa-overlay-control.py

  install -m644 -Dt "${pkgdir}/usr/share/licenses/${pkgname}" LICENSE
}

package_opencl-mesa-panthor-git() {
  pkgdesc="OpenCL support for AMD/ATI Radeon mesa drivers - Panfork"
  depends=('libdrm' 'libclc' 'clang' 'expat')
  optdepends=('opencl-headers: headers necessary for OpenCL development')
  conflicts=('opencl-mesa')
  provides=('opencl-driver' 'opencl-mesa')

  _install fakeinstall/etc/OpenCL
  _install fakeinstall/usr/lib/lib*OpenCL*
  _install fakeinstall/usr/lib/gallium-pipe

  install -m644 -Dt "${pkgdir}/usr/share/licenses/${pkgname}" LICENSE
}

package_vulkan-swrast-panthor-git() {
  pkgdesc="Vulkan software rasteriser driver - Panfork"
  depends=('wayland' 'libx11' 'libxshmfence' 'libdrm' 'zstd' 'llvm-libs')
  optdepends=('vulkan-mesa-layers: additional vulkan layers')
  conflicts=('vulkan-mesa' 'vulkan-swrast')
  replaces=('vulkan-mesa')
  provides=('vulkan-driver' 'vulkan-swrast')

  _install fakeinstall/usr/share/vulkan/icd.d/lvp_icd*.json
  _install fakeinstall/usr/lib/libvulkan_lvp.so

  install -m644 -Dt "${pkgdir}/usr/share/licenses/${pkgname}" LICENSE
}

package_libva-mesa-driver-panthor-git() {
  pkgdesc="VA-API implementation for gallium - Panfork"
  depends=('libdrm' 'libx11' 'llvm-libs' 'expat' 'libelf' 'libxshmfence')
  depends+=('libexpat.so')
  conflicts=('libva-mesa-driver')
  provides=('libva-mesa-driver')

  _install fakeinstall/usr/lib/dri/*_drv_video.so

  install -m644 -Dt "${pkgdir}/usr/share/licenses/${pkgname}" LICENSE
}

package_mesa-vdpau-panthor-git() {
  pkgdesc="Mesa VDPAU drivers - Panfork"
  depends=('libdrm' 'libx11' 'llvm-libs' 'expat' 'libelf' 'libxshmfence')
  depends+=('libexpat.so')
  conflicts=('mesa-vdpau')
  provides=('mesa-vdpau')


  _install fakeinstall/usr/lib/vdpau

  install -m644 -Dt "${pkgdir}/usr/share/licenses/${pkgname}" LICENSE
}

package_mesa-panthor-git() {
  depends=('libdrm' 'wayland' 'libxxf86vm' 'libxdamage' 'libxshmfence' 'libelf'
           'libomxil-bellagio' 'libunwind' 'llvm-libs' 'lm_sensors' 'libglvnd'
           'zstd' 'vulkan-icd-loader')
  depends+=('libsensors.so' 'libexpat.so' 'libvulkan.so')
  optdepends=('opengl-man-pages: for the OpenGL API man pages'
              'mesa-vdpau: for accelerated video playback'
              'libva-mesa-driver: for accelerated video playback')
  provides=('mesa-libgl' 'opengl-driver' 'mesa')
  conflicts=('mesa-libgl' 'mesa')
  replaces=('mesa-libgl')

  _install fakeinstall/usr/share/drirc.d/00-mesa-defaults.conf
  _install fakeinstall/usr/share/glvnd/egl_vendor.d/50_mesa.json

  # ati-dri, nouveau-dri, intel-dri, svga-dri, swrast, swr
  _install fakeinstall/usr/lib/dri/*_dri.so

  _install fakeinstall/usr/lib/bellagio
  _install fakeinstall/usr/lib/d3d
  _install fakeinstall/usr/lib/lib{gbm,glapi}.so*
  _install fakeinstall/usr/lib/libOSMesa.so*

  _install fakeinstall/usr/include
  rm -f fakeinstall/usr/lib/pkgconfig/{egl,gl}.pc
  _install fakeinstall/usr/lib/pkgconfig

  # libglvnd support
  _install fakeinstall/usr/lib/libGLX_mesa.so*
  _install fakeinstall/usr/lib/libEGL_mesa.so*

  # indirect rendering
  ln -s /usr/lib/libGLX_mesa.so.0 "${pkgdir}/usr/lib/libGLX_indirect.so.0"

  # make sure there are no files left to install
  find fakeinstall -depth -print0 | xargs -0 rmdir

  install -m644 -Dt "${pkgdir}/usr/share/licenses/${pkgname}" LICENSE
}
