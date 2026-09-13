# Восстановление suckless-сборки после переустановки системы

Проверено 2026-09-03: по этой инструкции все четыре бинарника собираются
**бит-в-бит** такими же, как установленные.

## Зафиксированные коммиты upstream

Диффы и конфиги в этом репозитории применяются именно к этим версиям.
Если брать `master`, патчи могут не наложиться.

| Проект | Коммит / тег      | Что своё |
|--------|-------------------|----------|
| dmenu  | `7175c48` (5.4+3) | `config.h` + 3 диффа (center, alpha, lazy-width) |
| dwm    | `44dbc68` (6.8+5) | `config.h` + `dwm-sticky-20260910.diff` (sticky-окна: камера на всех столах без индикаторов занятости) |
| st     | `04ce0d6` (0.9.3+1) | `config.h` + `st-local-patches-20260903.diff` (alpha + scrollback-reflow + clipboard) |
| slock  | тег `1.7`         | только `config.h`, исходники чистые |
| scroll | `51ee387` (0.1)   | ничего, конфиг по умолчанию |
| pauzer | своё, upstream нет | целиком в `pauzer/pauzer-src.tar.gz` |
| todo   | своё, upstream нет | целиком в `todo/todo-src.tar.gz` |

## Пакеты

```
pacman -S --needed base-devel git libx11 libxft libxinerama libxrandr libxext \
                   fontconfig freetype2 picom xorg-xrandr xorg-xset xorg-xsetroot
```

- `ttf-joypixels` — цветные emoji в баре dwm и в меню. **Только AUR**, в
  репозиториях (включая chaotic-aur) его нет: `yay -S ttf-joypixels`.
  Установленная версия — 11.0.0-1, packager «Unknown», то есть собран локально.
- `picom` — композитор (замена старого xcompmgr). Нужен для полупрозрачности меню
  и st, И для плавной записи экрана: xcompmgr не перерисовывал GPU-окна (видео в
  браузере, mpv-камера) на полной частоте, из-за чего запись такого видео выходила
  рваной (~18 fps); picom с glx+vsync это чинит (~29 fps). Конфиг — в
  `.config/picom/picom.conf`, запускается из `.xinitrc`.
- Дальше по вкусу: `feh`, `dunst`, `xss-lock`, `clipmenu`, `maim`, `imagemagick`,
  `xdotool`, `xorg-xdpyinfo`.

## Шрифты

`SF Mono` в репозиториях Arch нет, он лежит в этом репозитории и ставится руками:

```
sudo mkdir -p /usr/share/fonts/local
sudo cp fonts/SF-Mono-Regular.otf /usr/share/fonts/local/
sudo fc-cache -fv
fc-match "SF Mono:pixelsize=24"     # должен вернуть SF-Mono-Regular.otf
```

**Ловушка.** Имя семейства в `config.h` должно совпадать с реально
установленным. Если fontconfig такого семейства не найдёт, он молча подставит
другой шрифт (так уже было: в конфиге стоял `SF Mono Powerline`, которого в
системе нет, и dmenu рисовался в `Noto Sans Mono`). После правки шрифта всегда
проверяйте через `fc-match`.

## Сборка

Каталог держим в `/usr/src`. Для каждого проекта одно и то же:

```sh
DF=~/Work/dotfiles          # этот репозиторий

# --- dmenu: меню по центру + полупрозрачное ---
sudo git clone https://git.suckless.org/dmenu /usr/src/dmenu
cd /usr/src/dmenu
sudo git checkout 7175c48
sudo git apply $DF/dmenu/dmenu-all-local-changes-20260903.diff
sudo cp $DF/dmenu/config.h .
sudo make install

# --- dwm ---
sudo git clone https://git.suckless.org/dwm /usr/src/dwm
cd /usr/src/dwm
sudo git checkout 44dbc68
sudo git apply $DF/dwm/dwm-sticky-20260910.diff
sudo cp $DF/dwm/config.h .
sudo make install

# --- st ---
sudo git clone https://git.suckless.org/st /usr/src/st
cd /usr/src/st
sudo git checkout 04ce0d6
sudo git apply $DF/st/st-local-patches-20260903.diff
sudo cp $DF/st/config.h .
sudo make install

# --- slock (ставится с suid) ---
sudo git clone https://git.suckless.org/slock /usr/src/slock
cd /usr/src/slock
sudo git checkout 1.7
sudo cp $DF/slock/config.h .
sudo make install

# --- scroll ---
sudo git clone https://git.suckless.org/scroll /usr/src/scroll
cd /usr/src/scroll && sudo make install

# --- pauzer (свой таймер перерывов) ---
sudo tar xzf $DF/pauzer/pauzer-src.tar.gz -C /usr/src
cd /usr/src/pauzer && sudo make install

# --- todo (свой список задач, Win+D) ---
sudo tar xzf $DF/todo/todo-src.tar.gz -C /usr/src
cd /usr/src/todo && sudo make install
mkdir -p ~/Work/SyncData/ToDo        # сам список, путь задан в config.h
```

`dmenu-all-local-changes-20260903.diff` содержит всё сразу: center + alpha +
lazy-width. Отдельные диффы (`dmenu-center-*`, `dmenu-alpha-*`,
`dmenu-lazy-width-*`) нужны только если придётся переносить правки на
**новую** версию dmenu — тогда накатывать в этом порядке, причём alpha даст
один конфликт в `config.def.h` (не хватит строки `static const unsigned int
alpha`), это нормально, строка уже есть в нашем `config.h`.

## Из чего состоит «меню по центру и полупрозрачное»

Всё в `dmenu/config.h`:

| Параметр | Значение | Смысл |
|----------|----------|-------|
| `centered` | `1` | меню по центру, а не полосой сверху |
| `min_width` | `700` | минимальная ширина; итоговая = по самой длинной строке |
| `menu_height_ratio` | `2.0` | по центру вертикали (`4.0` — на 1/4 сверху) |
| `alpha` | `0xd8` | ~85% непрозрачности, нужен запущенный композитор |
| `measure_max` / `measure_slack` | `32` / `2` | сколько строк мерить шрифтом при подборе ширины |

Последние два — своя правка (`dmenu-lazy-width-*.diff`). Без неё патч `center`
мерит шрифтом каждую строку, и большой список с emoji (1631 строка) открывается
на ~500 мс дольше.

Высота меню задаётся вызывающей стороной через `-l N`: в `scripts/connect.sh` и
`scripts/rdpconnect.sh` стоит `-l 15`, в `scripts/dmenuunicode` — `-l 30`.

## flameshot (скриншоты с рисованием, `Win+S`)

Пакет `flameshot`, конфиг — `.config/flameshot/flameshot.ini`, обёртка —
`scripts/screenshot-draw`.

**Обязательная опция** в `flameshot.ini`:

```ini
[General]
useX11LegacyScreenshot=true
```

Начиная с flameshot 14.0.0 на X11 снимок по умолчанию делается через
`xdg-desktop-portal`. На dwm это тупик: ни один установленный бэкенд портала не
реализует `org.freedesktop.impl.portal.Screenshot` (у `xdg-desktop-portal-gtk`
в `Interfaces=` его просто нет, а `-gnome`/`-kde`/`-wlr` требуют своих
окружений). Запрос уходит в никуда, и flameshot **зависает навсегда** в
`ScreenGrabber::freeDesktopPortal`. Опция возвращает прямой захват через X11.

Вторая деталь: `flameshot gui --clipboard` бесполезен сам по себе — процесс
после копирования завершается и вместе с ним теряется владение X-выделением,
буфер оказывается пустым. Поэтому `screenshot-draw` отдаёт картинку через
`flameshot gui --raw` и владельцем буфера делает `xclip`, который остаётся жить.

## RNNoise — шумоподавление микрофона (как в Windows)

Системный фильтр PipeWire: виртуальный источник «Noise Canceling Source»
прогоняет реальный микрофон через нейросетевой шумодав RNNoise и становится
микрофоном по умолчанию — чистится звук везде (запись экрана, звонки, встречи).
Замер: фоновый шум −68 → −91 дБ (−23 дБ).

```sh
sudo pacman -S --needed noise-suppression-for-voice   # даёт /usr/lib/ladspa/librnnoise_ladspa.so
mkdir -p ~/.config/pipewire/pipewire.conf.d
cp .config/pipewire/pipewire.conf.d/99-rnnoise-mic.conf ~/.config/pipewire/pipewire.conf.d/
systemctl --user restart pipewire pipewire-pulse wireplumber
wpctl set-default "$(wpctl status | awk '/Sources:/{f=1} f&&/Noise Canceling/{print $2+0; exit}')"
```

Проверка: `pactl get-default-source` → `rnnoise_source`. Вход фильтра должен идти
от железного микрофона (`pw-link -l | grep -A1 capture.rnnoise_source`), не
зациклен. Выбор по умолчанию персистится в `~/.local/state/wireplumber`.

`screencast` пишет микрофон через этот источник (default), поэтому свой шумодав
(afftdn) в скрипте убран — RNNoise делает это лучше и до ffmpeg.

## WireGuard дома: туннель, переживающий роуминг Wi-Fi

На ноуте постоянно поднят `wg-quick@wg-client0` — весь трафик идёт через сервер.
Дома (две точки доступа, RSSI ~−72 дБм на 5 ГГц) `iwd` регулярно роумится между
ними, и после каждого роуминга туннель умирал навсегда, до ручного
`systemctl restart wg-quick@wg-client0`.

Причина не в провайдере и не в `PersistentKeepalive`. Роуминг — это потеря
carrier на 1–2 секунды, а `systemd-networkd` по умолчанию
(`IgnoreCarrierLoss=no`) на любую потерю carrier **сносит адрес и маршруты** и
переполучает DHCP. WireGuard остаётся с протухшим кэшем исходящего адреса и
больше не отправляет ни одного пакета. `PersistentKeepalive` тут бессилен: он
держит открытым NAT, но не чинит оборванный сокет. В журнале это выглядит так:

```
iwd: event: state, old: connected, new: roaming
wlan0: Lost carrier / Gained carrier
wlan0: DHCPv4 address 192.168.2.100 acquired    ← конфигурация переполучена заново
```

**Лечение** — одна строка в секции `[Network]` файла
`etc/systemd/network/20-wlan.network`:

```ini
IgnoreCarrierLoss=10s
```

Блики короче 10 секунд больше не приводят к сносу конфигурации, и туннель
переживает роуминг вообще без вмешательства.

**Страховка** на случай настоящих обрывов (провайдер, сон/пробуждение) —
`scripts/wg-watchdog` + `etc/systemd/system/wg-watchdog.service`.

Разворачивание всего узла с нуля, из корня репозитория:

```sh
sudo pacman -S --needed wireguard-tools nftables
sudo install -m600 etc/wireguard/wg-client0.conf.example /etc/wireguard/wg-client0.conf
sudo vim /etc/wireguard/wg-client0.conf          # вписать PrivateKey, в репозиторий он не попадает
sudo systemctl enable --now wg-quick@wg-client0

sudo install -m644 etc/nftables.conf /etc/nftables.conf
sudo systemctl enable --now nftables

sudo cp etc/systemd/network/20-wlan.network /etc/systemd/network/
sudo networkctl reload
sudo install -m755 scripts/wg-watchdog /usr/local/bin/wg-watchdog
sudo cp etc/systemd/system/wg-watchdog.service /etc/systemd/system/
sudo systemctl enable --now wg-watchdog.service
```

Сторож пингует `10.100.10.1` раз в 10 секунд; на двух провалах подряд сначала
пробует дешёвый `wg set … endpoint` (маршруты и DNS не трогаются) и только потом
перезапускает `wg-quick`. Дальше — backoff 30 → 300 с, чтобы при реальном обрыве
у провайдера не долбить рестартами. Ничего не делает, если юнит остановлен
вручную или физического дефолтного маршрута нет вообще.

Две ловушки, на которые легко напороться при правке:

- `IgnoreCarrierLoss=` живёт в секции `[Network]`. Если дописать строку в конец
  файла, она попадёт в `[DHCPv4]` и networkd молча её проигнорирует —
  `journalctl -u systemd-networkd | grep "Unknown key"`.
- Ключ пира в base64 заканчивается на `=`, поэтому разбирать конфиг через
  `awk -F=` нельзя — хвостовой символ отрезается. Режем только по первому `=`:
  `awk '/^[[:space:]]*PublicKey[[:space:]]*=/{sub(/^[^=]*=[[:space:]]*/, ""); print; exit}'`.

Проверка сторожа — блокировкой endpoint, а не подменой его через `wg set`:
сервер сам шлёт пакеты и возвращает endpoint обратно, подмена не держится.

```sh
sudo iptables -I OUTPUT -d 5.44.252.67 -p udp --dport 55830 -j DROP
journalctl -u wg-watchdog -f      # ~20 c: сброс endpoint, затем рестарт, затем пауза 30 с
sudo iptables -D OUTPUT -d 5.44.252.67 -p udp --dport 55830 -j DROP
```

Что роуминг больше не рвёт конфигурацию, видно по отсутствию строки
`DHCPv4 address … acquired` после `Gained carrier`:
`journalctl -u systemd-networkd -u iwd | grep -E "roam|carrier|acquired"`.

### Конфиг туннеля

`etc/wireguard/wg-client0.conf.example` → `/etc/wireguard/wg-client0.conf`
(`chmod 600`, приватный ключ в репозиторий не кладётся):

```ini
[Interface]
PrivateKey = <приватный ключ клиента>
Address = 10.100.10.50/24
DNS = 10.100.10.1

[Peer]
PublicKey = 7bN0QHcm4Y1fisiWatei1NNM/QuzNKXZFHJHePQ2mG0=
Endpoint = 5.44.252.67:55830
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 20
```

`AllowedIPs = 0.0.0.0/0` — весь трафик в туннель. `wg-quick` реализует это не
заменой дефолтного маршрута, а политикой маршрутизации: помечает свои пакеты
fwmark и добавляет правила `not from all fwmark 0xca6c lookup 51820` и
`suppress_prefixlength 0`. Поэтому в `ip route` дефолт остаётся через Wi-Fi, а
весь трафик всё равно уходит в `wg-client0` — смотреть надо `ip rule` и
`ip route show table 51820`.

`DNS = 10.100.10.1` прописывается через `resolvconf`, который на этой машине —
шим к `systemd-resolved`. Проверка, что резолвинг ушёл в туннель, а не к роутеру:
`resolvectl status` → у `wg-client0` должно быть `DNS Domain: ~.` и
`Default Route: yes`.

`PersistentKeepalive = 20` держит открытым NAT на стороне провайдера. Он **не**
чинит оборванный сокет — именно поэтому нужны `IgnoreCarrierLoss` и сторож выше.

### Killswitch на nftables

`etc/nftables.conf` → `/etc/nftables.conf`, включается
`sudo systemctl enable --now nftables`. Суть — в цепочке `output` политика `drop`
и выпускается наружу только то, без чего туннель не поднимется:

```nft
define wg_if = "wg-client0"
define wg_endpoint = 5.44.252.67
define wg_port = 55830

  chain output {
    type filter hook output priority filter
    policy drop

    ct state invalid drop
    ct state {established, related} accept
    oifname lo accept
    fib daddr type local accept comment "allow local addresses"

    # единственная дырка наружу: сам WireGuard к своему серверу
    ip daddr $wg_endpoint udp dport $wg_port accept comment "allow wireguard endpoint"
    udp sport 68 udp dport 67 accept comment "allow dhcp requests"

    ip daddr 192.168.10.0/24 accept comment "allow LAN"

    oifname $wg_if accept comment "allow traffic through WireGuard"
    counter reject with icmpx type admin-prohibited comment "killswitch: block non-WireGuard output"
  }
```

Пока туннель жив — всё уходит через него; как только он падает, последнее
правило режет весь остальной исходящий трафик, и утечки мимо VPN не случается.
`reject` вместо `drop` выбран сознательно: приложения получают отказ сразу, а не
висят до таймаута.

Чего тут легко не заметить:

- Дырка наружу прибита к **конкретному IP и порту** (`define wg_endpoint`).
  Сменился сервер — правь `define` и перезагружай ruleset, иначе туннель не
  поднимется вообще, а выглядеть будет как «опять интернет пропал».
- Домашняя подсеть `192.168.2.0/24` в killswitch **не** открыта (открыта рабочая
  `192.168.10.0/24` и пара отдельных адресов). Поэтому роутер `192.168.2.1` с
  ноута не пингуется — это норма, а не поломка. Именно из-за этого `wg-watchdog`
  проверяет наличие физического линка по таблице маршрутов, а не пингом шлюза:
  пинг шлюза killswitch зарежет, и сторож решит, что линка нет.
- `nftables.service` — `Type=oneshot`, поэтому после успешной загрузки правил он
  показывает `inactive (dead)`. Это нормально; смотреть надо
  `sudo nft list ruleset`, а не `systemctl is-active`.
- Правила `ct state {established, related} accept` означают, что уже открытые
  соединения переживут падение туннеля. Полная герметичность — убрать `related`
  и явно ограничить `established` интерфейсом, но тогда ломается больше, чем
  защищается.

Проверка killswitch: при остановленном туннеле наружу не должно уходить ничего,
а счётчик последнего правила — расти.

```sh
sudo systemctl stop wg-quick@wg-client0
ping -c1 -W2 1.1.1.1                                    # From 192.168.2.100 icmp_seq=1 Packet filtered
sudo nft list chain inet filter output | grep killswitch # counter packets N ... - N растёт
sudo systemctl start wg-quick@wg-client0
```

## Проверка, что получилось то же самое

```sh
Xvfb :99 -screen 0 1920x1080x24 &
seq 1 15 | DISPLAY=:99 dmenu -i -l 15 &
DISPLAY=:99 xdotool search --sync --onlyvisible --class dmenu | \
  xargs -I{} env DISPLAY=:99 xdotool getwindowgeometry {}
kill %1
# ожидаемо на экране 1920x1080: Geometry 700x496, Position 610,292
```

Строк на входе должно быть не меньше, чем в `-l`: dmenu сжимает список до числа
элементов (`lines = MIN(lines, i)`), и на трёх строках получится `700x124`.

Требует `xorg-server-xvfb` и `xdotool`.
