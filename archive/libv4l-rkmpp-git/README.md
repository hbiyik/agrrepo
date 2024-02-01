To ensure hw-decoding working for Chromium:

 - A patched Chromium needs to be used, which is also maintained by myself: https://github.com/7Ji-PKGBUILDs/chromium-mpp (currently still [on AUR](https://aur.archlinux.org/packages/chromium-mpp) but will be deleted soon as AUR is cleaning non pure-x86_64-Arch packages)
 - User must be a member of group `video`, or be `root`
 - Run `libv4l-rkmpp-setup.sh` with a valid profile (check `/usr/share/libv4l-rkmpp-profiles`) as root before running Chromium. E.g. for `rk3588`, run `sudo libv4l-rkmpp-setup.sh rk3588`
  - _To automatically run the above script on each boot, set a valid profile in /etc/conf.d/libv4l-rkmpp and run `sudo systemctl enable --now libv4l-rkmpp-setup.service`_

To verify if the pacakge itself works (without Chromium), use `qv4l2` and open the dummy devices `/dev/video-enc0` and `/dev/video-dec0` after running the setup script to check if you can get info `card: rkmpp`, `driver: rkmpp`, `bus: platform-rkmpp`