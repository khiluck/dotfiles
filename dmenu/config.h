/* See LICENSE file for copyright and license details. */
/* Default settings; can be overriden by command line. */

static int topbar = 1;                      /* -b  option; if 0, dmenu appears at bottom     */

/* --- patch: center --- */
static int centered = 1;                    /* -c option; меню по центру экрана */
static int min_width = 700;                 /* минимальная ширина в центрированном режиме */
/* Сколько строк реально измерять шрифтом при подборе ширины (см. max_textw).
 * measure_slack — насколько короче самой длинной строки ещё стоит мерить. */
static const unsigned int measure_max   = 32;
static const unsigned int measure_slack = 2;
static const float menu_height_ratio = 2.0f; /* 2.0 = по центру вертикали, 4.0 = на 1/4 сверху */

/* --- patch: alpha --- */
static const unsigned int alpha = 0xd8;     /* прозрачность окна; 0xff = непрозрачно */

/* -fn option overrides fonts[0]; default X11 font or font set */
static const char *fonts[] = {
	"SF Mono:pixelsize=24:antialias=true:autohint=true",
	"JoyPixels:pixelsize=24:antialias=true:autohint=true"
};
static const char *prompt      = NULL;      /* -p  option; prompt to the left of input field */

static const char *colors[SchemeLast][2] = {
    /*     fg         bg       */
//  [SchemeNorm] = { "#bbbbbb", "#222222" },
    [SchemeNorm] = { "#ebdbb2", "#282828" },
//  [SchemeSel] = { "#eeeeee", "#005577" },
    [SchemeSel] = { "#eeeeee", "#928374" },
    [SchemeOut] = { "#000000", "#00ffff" },
};

static const unsigned int alphas[SchemeLast][2] = {
	/*               fg      bg    */
	[SchemeNorm] = { OPAQUE, alpha },
	[SchemeSel]  = { OPAQUE, alpha },
	[SchemeOut]  = { OPAQUE, alpha },
};

/* -l option; if nonzero, dmenu uses vertical list with given number of lines */
static unsigned int lines      = 0;

/*
 * Characters not considered part of a word while deleting words
 * for example: " /?\"&[]"
 */
static const char worddelimiters[] = " ";
