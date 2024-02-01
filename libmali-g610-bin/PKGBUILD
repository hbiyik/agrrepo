# Maintainer: 7Ji <pugokughin@gmail.com>

_model_canonical='ARM Mali-G610'
_model='mali-valhall-g610'
_suffixes=(dummy gbm wayland-gbm x11-gbm x11-wayland-gbm)
_repo='https://github.com/JeffyCN/mirrors'
_libver_major=g13p0
_libver_minor=10
_lib_commit='bd6bb095780f880bf8f368ef6770563a313aebb4'
_lib_parent="${_repo}/raw/${_lib_commit}/lib"
_eula_commit='8605a3c81b60ac5bd8e492cc02e84a2e0aa8e524'

pkgbase="lib${_model}"
pkgname=("${pkgbase}-base")
# Actual version uses -, but it is forbidden in pkgver
pkgver="${_libver_major}.${_libver_minor}"
pkgrel=1
url='https://developer.arm.com/Processors/Mali-G610'
license=('custom')
source=(
  "${_repo}/raw/${_eula_commit}/END_USER_LICENCE_AGREEMENT.txt"
  'libmali-wrapper'
)
source_aarch64=()
source_armv7h=()
sha256sums=(
  'a78acc73de9909efb879800d4daa4640c4aaa55cd751238a133954aba15e4285'
  '564faeead74b92e6edd590a34b361994de9eff21586fd2e66097b33fe1639834'
)
sha256sums_aarch64=(
  'a83746b3a9e3b70ada5441f44eae6f36a89c17f3f78b35fbfdf89af1e6988e9f'
  'f329dd7809f3033b457d37209bce34a3e8e790e6126e215d1dff57c7a59c51bb'
  '447dabfb1f3faa2aa4ee88aa9611840ff44635a1a3082b55d769900d6cd797f8'
  '628fea07308dcca8c2fe9154cd62ba8a7dba0c5d6605e049deb9a8514624d562'
  '3a6fcb0ada4c94410cca9f67634f45addde5202d14d52221bd0ad450200d2d2f'
)
sha256sums_armv7h=(
  'd453d1d322fd12f2d93f8b9e71c5bb96a38c3550c64f83c5aa23cd6852a5d1a9'
  '40d45e5fdb8dfe2c5e3cf5fee517d4c2e38b89e2b3e65593575c9fb15db80269'
  '39b29041225ec4e7fe0474f983c40acca659c1a02598d0f6727aee77f86e036b'
  '34708b7738ed42b9fac1d48e995ca29f3cc52ce3641c286bedfc814bbf834f69'
  '30007066c412aa5a6398d2fe128d909d3091e62bfa85d607482335f3635ddd3a'
)
arch=('x86_64' 'aarch64' 'armv7h') # Allow the wrapper to build on x86_64 for testing
options=(!strip)

_package-base() {
  local LD=
  case "${CARCH}" in
    x86_64)
      LD=ld-linux-x86-64.so.2
      ;;
    aarch64)
      LD=ld-linux-aarch64.so.1
      ;;
    armv7h)
      LD=ld-linux-armhf.so.3
      ;;
  esac
  if [[ -z "${LD}" ]]; then
    echo "Failed to decide package arch"
    return 1
  fi
  sed "s/%MODEL%/${_model}/
       s/%LD%/${LD}/" libmali-wrapper |
    install -D --mode=755 /dev/stdin "${pkgdir}"/usr/bin/libmali

  install -D --mode=644 END_USER_LICENCE_AGREEMENT.txt --target-directory="${pkgdir}/usr/share/licenses/${pkgbase}"
}

eval "package_${pkgname}() {
  pkgdesc='License and wrapper for ${_model_canonical}'
  optdepends=(
    'chrpath: To identify and fix rpath issues'
    'dri2to3: Compatibility layer for Dri2-only driver'
    'gl4es: OpenGL to OpenGLES translation layer'
  )
  _package-base
}"

_package-lib() {
  local _srcname="${pkgbase}-${_libver_major}-${_suffix}.so"
  local _libdir="${pkgdir}/usr/lib/${_model}/${_suffix}"
  local _soname=libmali.so.1
  local _reallib=${_soname}.9.0
  local _wrapper=
  case ${CARCH} in 
    aarch64|armv7h)
      install -D --mode=755 "${_srcname}" "${_libdir}/${_reallib}"
      ;;
    *)
      install -d --mode=755 "${_libdir}"
      ;;
  esac
  local _libs=(
    EGL.so.1
    GLESv1_CM.so.1
    GLESv2.so.2
    GLESv3.so.1
    MaliOpenCL.so.1
    OpenCL.so.1 
    # MaliVulkan.so.1   X not enabled by Rockchip
    # vulkan.so.1       X not enabled by Rockchip
    mali.so.1
  )
  if [[ "${_suffix}" =~ wayland ]]; then
    _libs+=(wayland-egl.so.1)
  fi
  if [[ "${_suffix}" =~ gbm ]]; then
    _libs+=(gbm.so.1 )
  fi
  case "${_suffix}" in
    dummy)
      _wrapper=d
      ;;
    gbm)
      _wrapper=g
      ;;
    wayland-gbm)
      _wrapper=w
      ;;
    x11-gbm)
      _wrapper=x
      ;;
    x11-wayland-gbm)
      _wrapper=-x11-wayland-gbm
      ;;
  esac
  local _lib _lib_bare
  for _lib in ${_libs[@]}; do
    _lib=lib${_lib}
    _lib_bare="${_lib%%so.*}"so
    ln -s ${_lib} "${_libdir}"/${_lib_bare}
    ln -s ${_soname} "${_libdir}"/${_lib}
  done
  ln -sf ${_reallib} "${_libdir}"/${_soname}

  local _bindir="${pkgdir}"/usr/bin
  mkdir -p "${_bindir}"
  ln -s libmali "${_bindir}"/libmali"${_wrapper}"
}

for _suffix in ${_suffixes[@]}; do
  pkgname+=("${pkgbase}-${_suffix}")
  source_aarch64+=("${_lib_parent}/aarch64-linux-gnu/${pkgbase}-${_libver_major}-${_suffix}.so")
  source_armv7h+=("${_lib_parent}/arm-linux-gnueabihf/${pkgbase}-${_libver_major}-${_suffix}.so")
  eval "package_${pkgbase}-${_suffix}() {
    pkgdesc='Blob driver for ${_model_canonical}, for ${_suffix} target'
    depends=('${pkgname}' '${_model}-firmware')
    provides=(libmali{,-${_suffix}})
    install=install_${_suffix}
    local _suffix=${_suffix}
    _package-lib
  }"
done