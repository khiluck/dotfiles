# Восстановление suckless-сборки после переустановки системы

Проверено 2026-09-03: по этой инструкции все четыре бинарника собираются
**бит-в-бит** такими же, как установленные.

## Зафиксированные коммиты upstream

Диффы и конфиги в этом репозитории применяются именно к этим версиям.
Если брать `master`, патчи могут не наложиться.

| Проект | Коммит / тег      | Что своё |
|--------|-------------------|----------|
| dmenu  | `7175c48` (5.4+3) | `config.h` + 3 диффа (center, alpha, lazy-width) |
| dwm    | `44dbc68` (6.8+5) | только `config.h`, исходники чистые |
| st     | `04ce0d6` (0.9.3+1) | `config.h` + `st-local-patches-20260903.diff` (alpha + scrollback-reflow + clipboard) |
| slock  | тег `1.7`         | только `config.h`, исходники чистые |
| scroll | `51ee387` (0.1)   | ничего, конфиг по умолчанию |

## Пакеты

```
pacman -S --needed base-devel git libx11 libxft libxinerama libxrandr libxext \
                   fontconfig freetype2 xcompmgr xorg-xrandr xorg-xset xorg-xsetroot
```

- `ttf-joypixels` — цветные emoji в баре dwm и в меню. **Только AUR**, в
  репозиториях (включая chaotic-aur) его нет: `yay -S ttf-joypixels`.
  Установленная версия — 11.0.0-1, packager «Unknown», то есть собран локально.
- `xcompmgr` — **обязателен для полупрозрачности** меню и st. Без композитора
  ничего не ломается, но меню просто станет непрозрачным.
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
