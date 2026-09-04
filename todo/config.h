/* See LICENSE file for copyright and license details. */

/* where the list lives; a leading ~/ is expanded to $HOME */
static const char *todofile = "~/Work/SyncData/ToDo/todo.md";

/* the header written when the file is created from scratch */
static const char *filehead = "# ToDo";

/* appearance; first font wins, the rest cover glyphs it lacks (emoji) */
static const char *fontnames[] = {
	"SF Mono:pixelsize=20:antialias=true:autohint=true",
	"JoyPixels:pixelsize=20:antialias=true:autohint=true",
};

static const char *colbg     = "#282828"; /* same gruvbox palette as dwm */
static const char *colfg     = "#ebdbb2";
static const char *colaccent = "#8ec07c"; /* cursor line */
static const char *colmuted  = "#928374"; /* done items, headings, hints */

static const double opacity  = 0.95; /* 1.0 = opaque; needs a compositor */

/* geometry */
static const int winwidth    = 720; /* window width in pixels */
static const int padding     = 14;  /* inner margin */
static const int lineheight  = 28;  /* one item row */
static const int maxrows     = 20;  /* grow no taller than this many rows */
static const int strikedone  = 1;   /* 1 draws a line through finished items */

/* texts */
static const char *wintitle  = "todo";
static const char *hint      = "Space отметить · a добавить · e править · "
                               "D удалить · J/K перенести · q выход";
static const char *inputadd  = "новая задача: ";
static const char *inputedit = "правка: ";
static const char *emptyhint = "список пуст — a добавит первую задачу";
