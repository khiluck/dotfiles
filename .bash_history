sudo rm -rf copy/
ls
mc
cd /home/aex/dotfiles/
git reset
git reset --hard
ls
cd dmenu/
ls
cat config.h 
vi config.h 
cd dotfiles/
ls
cd dmenu/
ls
rm *
cp /usr/src/dmenu/config.h ./
ll
cd ..
ls
cd dwm/
ls
rm *
cp /usr/src/dwm/config.h ./
vi /usr/src/dwm/drw.c 
ls
cd ..
ls
cd scr
cd scroll/
ls
vi config.h 
cp /usr/src/scroll/config.h ./
cd ..
ls
cd st/
ls
rm config.h 
cp /usr/src/st/config.h ./
rm st-alpha-0.8.2.diff 
cp /usr/src/st/st-alpha-20240814-a0274bc.diff ./
ls
rm st-clipboard-0.8.3.diff 
ls
wget https://st.suckless.org/patches/clipboard/st-clipboard-0.8.3.diff
ls
patch < st-clipboard-0.8.3.diff 
ls
vi st-clipboard-0.8.3.diff 
ls
sudo cp st-clipboard-0.8.3.diff /usr/src/st/
cd /usr/src/st/
ls
sudo patch < st-clipboard-0.8.3.diff 
sudo make clean install
ip a
pacman -Sy --noconfirm --needed bash-completion usbutils lsof dmidecode dialog xclip flameshot wget
sudo pacman -Sy --noconfirm --needed bash-completion usbutils lsof dmidecode dialog xclip flameshot wget
pacman -Sy --noconfirm --needed zip unzip unrar p7zip lzop
sudo pacman -Sy --noconfirm --needed zip unzip unrar p7zip lzop
sudo pacman -Sy --noconfirm --needed rsync traceroute bind-tools nmap
pacman -Sy --noconfirm --needed openssh cronie xdg-user-dirs haveged acpi
sudo pacman -Sy --noconfirm --needed openssh cronie xdg-user-dirs haveged acpi
pacman -Sy --noconfirm --needed f2fs-tools dosfstools ntfs-3g btrfs-progs exfat-utils gptfdisk autofs fuse2 fuse3 fuseiso sshfs cifs-utils smbclient
sudo pacman -Sy --noconfirm --needed f2fs-tools dosfstools ntfs-3g btrfs-progs exfat-utils gptfdisk autofs fuse2 fuse3 fuseiso sshfs cifs-utils smbclient
pacman -Sy --noconfirm --needed f2fs-tools dosfstools ntfs-3g btrfs-progs exfat-utils gptfdisk fuse2 fuse3 fuseiso sshfs cifs-utils smbclient
sudo pacman -Sy --noconfirm --needed f2fs-tools dosfstools ntfs-3g btrfs-progs exfat-utils gptfdisk fuse2 fuse3 fuseiso sshfs cifs-utils smbclient
sudo pacman -Sy --noconfirm --needed alsa-utils alsa-plugins pulseaudio pulseaudio-alsa pulseaudio-bluetooth
sudo pacman -Sy --noconfirm --needed alsa-utils alsa-plugins pulseaudio-alsa pulseaudio-bluetooth
sudo pacman -Sy --noconfirm --needed alsa-utils
alsamixer 
sudo pacman -Sy --noconfirm --needed xorg-server xorg-xinit xorg xorg-drivers mesa
sudo pacman -Sy --noconfirm --needed ttf-linux-libertine ttf-inconsolata noto-fonts ttf-joypixels
sudo pacman -Sy --noconfirm --needed ttf-linux-libertine ttf-inconsolata noto-fonts
sudo -u aurbuilder yay -S --noconfirm --needed ttf-joypixels
pacman -Sy --noconfirm --needed font-bh-ttf font-bitstream-speedo gsfonts sdl_ttf ttf-bitstream-vera ttf-dejavu ttf-liberation xorg-fonts-type1
sudo pacman -Sy --noconfirm --needed font-bh-ttf font-bitstream-speedo gsfonts sdl_ttf ttf-bitstream-vera ttf-dejavu ttf-liberation xorg-fonts-type1
pacman -Sy --noconfirm --needed gsfonts sdl_ttf ttf-bitstream-vera ttf-dejavu ttf-liberation xorg-fonts-type1
sudo pacman -Sy --noconfirm --needed gsfonts sdl_ttf ttf-bitstream-vera ttf-dejavu ttf-liberation xorg-fonts-type1
sudo -u aurbuilder yay -S --noconfirm --needed font-bh-ttf font-bitstream-speedo
pacman -Sy --noconfirm --needed gnu-free-fonts ttf-linux-libertine-g
sudo pacman -Sy --noconfirm --needed gnu-free-fonts ttf-linux-libertine-g
sudo -u aurbuilder yay -S --noconfirm --needed ttf-ms-fonts
sudo -u aurbuilder yay -S --noconfirm --needed terminus-font-ttf
sudo -u aurbuilder yay -S --noconfirm --needed ttf-dejavu noto-fonts noto-fonts-emoji
fc-cache -vf
sudo -u aurbuilder yay -Sy --noconfirm --needed libxft-bgra
fc-cache -vf
sudo pacman -Sy --noconfirm --needed xf86-input-libinput
pacman -Sy --noconfirm libva-utils
sudo pacman -Sy --noconfirm libva-utils
pacman -Sy --noconfirm --needed libva-vdpau-driver lib32-libva-vdpau-driver libvdpau-va-gl
sudo pacman -Sy --noconfirm --needed libva-vdpau-driver lib32-libva-vdpau-driver libvdpau-va-gl
sudo pacman -Sy --noconfirm --needed libva-vdpau-driver lib32-libva-vdpau-driver libvdpau-va-gl
sudo pacman -Sy --noconfirm --needed libvdpau-va-gl
sudo -u aurbuilder yay -Sy --noconfirm --needed libva-vdpau-driver lib32-libva-vdpau-driver
sudo pacman -Sy --noconfirm --needed vim mc chromium pavucontrol glu lib32-openal util-linux pamixer feh xcompmgr freerdp sxiv galculator mpv clipmenu youtube-dl
sudo pacman -S lib32-openal
yay -S lib32-openal
pacman -Sy --noconfirm --needed libnotify dunst feh clipmenu flameshot xcompmgr
sudo pacman -Sy --noconfirm --needed libnotify dunst feh clipmenu flameshot xcompmgr
15~
update
ip a
ll
cd dotfiles/
ls
ls
ls /usr/src/
cd dmenu/
ls
cd ..
ls
cd dwm/
ls
cd ..
ls
cd scr
cd scroll/
ls
cat config.h 
ls
cd ..
ls
cd st/
ls
cd ..
ls
git add .
git commit -am "Update configs for suckless software"
git commit -am "Update configs for suckless software"
git config --global user.email "khiluck@gmail.com"
git config --global user.name "Oleksandr Khiliuk"
git commit -am "Update configs for suckless software"
git push
vi ~/.ssh/config 
git push
vi ~/.ssh/config 
ssh -T khiluck@github.com
vi ~/.ssh/config 
ls
cd ..
ls
cd DOw
cd Downloads/
ls
git clone https://github.com/khiluck/ansible
git clone git@github.com:khiluck/ansible.git
ls
rm -rf ansible/
ls
cd ..
ls
cd dotfiles/
ls
git push
ls
ll
cd .config/
ls
cd ..
ls
cd ..
ls
ll
vi .gitconfig 
cd dotfiles/
ls
git push
ssh -T git@github.com
vi ~/.gitconfig 
git push
ls
mc
cd ~/Downloads/
ls
git clone git@github.com:khiluck/dotfiles.git
ls
cd archlinux-install-scripts/
ls
cd ..
ls
cd dotfiles/
ls
ls
mc
git add .
git commit -am "Update configs for suckless software"
git push
s
ls
cd ..
ls
cd ..
ls
rm -rf dotfiles/
ls
ls
cd Downloads/
ls
cd archlinux-install-scripts/
ls
cd ..
ls
rm -rf archlinux-install-scripts/
git clone git@github.com:khiluck/archlinux-install-scripts.git
ls
cd archlinux-install-scripts/
ls
ls
vi dwm_download.sh 
history 
:q
history | grep pacman
vi add.txt
cat "dunst" >> add.txt 
echo "dunst" >> add.txt 
echo "feh" >> add.txt 
echo "clipmenu" >> add.txt 
echo "flameshot" >> add.txt 
echo "xcompmgr" >> add.txt 
ls
cat add.txt 
vi dwm_download.sh 
vi part2.sh \
vi part2.sh 
sudo pacman -S xclip
vi part2.sh 
pacman -Sy --noconfirm --needed vim mc chromium pavucontrol glu util-linux pamixer feh xcompmgr freerdp sxiv galculator mpv clipmenu
sudo pacman -Sy --noconfirm --needed vim mc chromium pavucontrol glu util-linux pamixer feh xcompmgr freerdp sxiv galculator mpv clipmenu
vi part2.sh 
ls
rm add.txt 
ls
git add .
git commit -am "Fix scripts to fit modern installation"
git push
cd ..
ls
cd dotfiles/
ls
ll
l
ll
ll
mc
vi ~/.bashrc 
mc
vi ~/.bashrc 
mc
[1~
OA
mc
vi ~/Downloads/dotfiles/.bashrc 
ls
vi ~/Downloads/dotfiles/.bash_profile 
cat /usr/src/slock/
cat /usr/src/slock/config.h 
ls
cd Downloads/
ls
cd dotfiles/
ls
mkdir slock
ls
cd slock/
ls
cp /usr/src/slock/config.h ./
ls
cd ..
ls
git add .
git commit -am "Add config.h for slock"
git push
cd ..
ls
cd archlinux-install-scripts/
ls
ls
cat add.txt 
vi .bashrc 
ls
vi scripts/rdpconnect.sh 
cd scripts/
ls
mc
ls
cd ..
ls
cd Downloads/dotfiles/
ls
ls
git add .
git commit -am "Update scripts"
git push
cd ..
ls
vi ~/.bashrc 
vi ~/.bashrc 
sudo pacman -S nvim
sudo pacman -S nvim
ls
cd Downloads/
ls
cd archlinux-install-scripts/
ls
vi part2.sh 
git commit -am "Change vim to nvim"
git push
vi ~/.bashrc 
sudo pacman -S yt-dlp
ls
vi part2.sh 
vi ~/.bashrc 
git commit -am "Add yt-dlp"
git push
vi scripts/dwm_status 
ping google.com
cd /usr/src/dmenu/
ls
cd ..
ls
cd dwm/
ls
sudo vi config.h 
sudo yay -Ss "sfmono"
sudo pacman -Ss "sfmono"
sudo yay -S otf-sfmono-patched
fc-cache -vf
fc-cache -l
fc-cache list
fc-cache 
fc-list 
fc-list | grep otf-sfmono-patched
fc-list | grep sfmono
fc-list | grep -i "sfmono"
fc-list | grep -i "sf mono"

sudo vi config.h 
sudo make clean install
cd Downloads/
ls
cd archlinux-install-scripts/
ls
vi part2.sh 
git commit -am "Add SF Mono Powerline font"
git push
cd /usr/src/dmenu/
ls
sudo vi config.h
sudo make clean install
ls
cp config.h ~/Downloads/dotfiles/dmenu/config.h 
cd ../dwm/
cp config.h ~/Downloads/dotfiles/dwm/config.h 
cd ~/Downloads/dotfiles/
ls
git commit -am "Change SF Mono Powerline font"
git push
cd 
ls
cd scripts/
ls
./sysact 
cd /usr/src/dwm/
vi config.h 
sudo vi config.h 
sudo make clean install
startx
startx
sudo systemctl restart wg-quick@wg-client0.service 
10Gfhjkm
cd scripts/
ls
vi webcamtoggle 
ls
vi webcamtoggle 
vi scripts/webcamtoggle 
crontab -e
/home/aex/scripts/syncunison
rdp 192.168.10.2 aex 10Gfhjkm!
ip a
alsamixer 
exit
journalctl -xe wg-client
journalctl -xe
traceroute google.com
exit
crontab -e
exit
vi scripts/rdpconnect.sh 
vi Work/secret/rdp.list 
vi Work/secret/rdp.list 
vi Work/secret/rdp.list 
rdp 192.168.10.254 aex 10Gfhjkm!
rdp 192.168.10.99 aex 10Gfhjkm!
pkill -9 teams-for-linux 
update
update
sudo pacman -S anydesk
sudo pacman -Ss anydesk
yay -Ss anydesk
yay -S anydesk
pkill -9 anydesk 
pkill -9 anydesk 
setxkbmap -print -verbose 10
vi Work/secret/rdp.list 
vi Work/secret/rdp.list 
vi Work/secret/rdp.list 
vim
cd Work/Documents/MyDoc/
ls
cd ..
cd MyDoc/
ping google.com
traceroute google.com
exit
cd Work/
ls
cd Projects/
ls
mkdir pentest
cd pentest/
ls
mkdir discovery
ls
mkdir documentation
mkdir focus-penetration
ls
cd discovery/
ls
mkdir hosts
mkdir services
ls
cd ..
ls
ls
cd documentation/
ls
mkdir logs
mkdir screenshots
cd ..
ls
ls
cd discovery/
ls
cd scripts/
swlayout 
swlayout de
cd Work/Books/
ls
cd IT/
ls
zathura 'Искусство тестирования на проникновение в сеть.pdf'
traceroute google.com
crontab -e
/home/aex/scripts/syncunison
htop
sudo tcpdump -n -e arp or netbios-ns or mdns or dhcp
sudo pacman -S tcpdump
sudo tcpdump -n -e arp or netbios-ns or mdns or dhcp
sudo tcpdump -n -e arp
sudo tcpdump -n -e netbios-ns
sudo tcpdump -n -e netbios
sudo tcpdump -n -e mdns
sudo tcpdump -n -e dhcp
sudo tcpdump -n -e arp or netbios-ns or mdns or dhcp
sudo tcpdump -n -e 'arp or netbios-ns or mdns or dhcp'
sudo tcpdump -n -e 'arp or udp port 137 or udp port 5353 or port 67 or port 68'
sudo tcpdump -n -e '(arp) or (udp port 137) or (udp port 5353) or (port 67 or 68)'
ip a
ip a
cd Work/Books/IT/
ls
zathura 'Искусство тестирования на проникновение в сеть.pdf'
cat Work/secret/rdp.list | grep kalachev2
cat Work/secret/rdp.list | grep Kalachev2
cat Work/Companies/kalachev2/users.txt 
pkill -9 anydesk 
startx
ip a
traceroute google.com
exit
ip -br -c a
ip -br a
ip -c a
ip a
ip -br a
ip -br -c a
ip a
vi ~/.bashrc 
ip a
ip
ip a
ls /usr/share/fonts/local
ls /usr/share/fonts/
ls /usr/local/bin/slock 
ls /usr/bin/slock 
exit
setxkbmap de
