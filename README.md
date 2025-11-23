## Boogie's AGR Repository

This repository is delivering bunch of packages that enables Archlinux ARM specially on rockchip based devices.

The main focus of the repository is to deliver [mpp](https://github.com/rockchip-linux/mpp) enabled variants of userspace applications like `ffmpeg`, `kodi`, `mpv`, `firefox`, `sunshine` etc. and also several variants of [rockchip-linux](https://github.com/rockchip-linux/kernel.git) but not limited to them, the scope might be flexible.

You can either build them from the source, or use precompiled binary repo. 

# Building from source:
To build packages listed here it is suggested to use [agr](https://github.com/hbiyik/agr) tool but this is not necessary if you know what you are doing.

When direcly interfacing with the repo, the submodules are not always commited to latest version of the packages. If you are manually building without `agr`, please make sure you update the sumbodules to latest `HEAD`s. If you are using `agr` this step is automatically handled and you dont have to take care of that.

Below is a simple example on how to use it with `agr`
```shell
agr rem set boogie https://github.com/hbiyik/agrrepo.git
agr sync --noconfirm
agr build mpp-git 
```

# Using it as binary repository:

Add below snippet to `/etc/pacman.conf` 

```
[boogie]
Server = https://github.com/hbiyik/agrrepo/releases/download/alarm-$arch
SigLevel = Never
```
and use pacman to install the package of your choice

```
sudo pacman -Sy
sudo pacman -S mpp-git
```

# Security

Packages in this repo is patched dynamically with several community maintained other forks.
After this patch process i do not do any audit of security, and the public audits of the main package is no more valid since it is patched against a community fork.
Since there is no audit on those packages i also do not sign them. Please keep this in mind if you are concerned about security.

# Build Status

![testimg](https://github.com/hbiyik/agrrepo/releases/download/alarm-aarch64/gitweb-dlagent.svg)
