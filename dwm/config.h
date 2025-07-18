/* See LICENSE file for copyright and license details. */

/* appearance */
static const unsigned int borderpx  = 3;        /* border pixel of windows */
static const unsigned int snap      = 32;       /* snap pixel */
static const int showbar            = 1;        /* 0 means no bar */
static const int topbar             = 1;        /* 0 means bottom bar */
static const char *fonts[]          = { "SF Mono Powerline:pixelsize=24:antialias=true:autohint=true", "JoyPixels:pixelsize=24:antialias=true:autohint=true" };
static const char dmenufont[]       = "SF Mono Powerline:pixelsize=24:antialias=true:autohint=true";
static const char col_gray1[]       = "#282828";
static const char col_gray2[]       = "#444444";
static const char col_gray3[]       = "#ebdbb2";
static const char col_gray4[]       = "#eeeeee";
static const char col_cyan[]        = "#928374";
static const char *colors[][3]      = {
	/*               fg         bg         border   */
	[SchemeNorm] = { col_gray3, col_gray1, col_gray2 },
	[SchemeSel]  = { col_gray4, col_cyan,  col_cyan  },
};

/* tagging */
static const char *tags[] = { "1", "2", "3", "4", "5", "6", "7", "8", "9" };

static const Rule rules[] = {
	/* xprop(1):
	 *	WM_CLASS(STRING) = instance, class
	 *	WM_NAME(STRING) = title
	 */
	/* class      instance    title       tags mask     isfloating   monitor */
	{ "Gimp",     NULL,       NULL,       0,            1,           -1 },
	{ "Galculator",     NULL,       NULL,       0,            1,           -1 },
	{ "Firefox",  NULL,       NULL,       1 << 8,       0,           -1 },
};

/* layout(s) */
static const float mfact     = 0.55; /* factor of master area size [0.05..0.95] */
static const int nmaster     = 1;    /* number of clients in master area */
static const int resizehints = 0;    /* 1 means respect size hints in tiled resizals */
static const int lockfullscreen = 1; /* 1 will force focus on the fullscreen window */

static const Layout layouts[] = {
	/* symbol     arrange function */
	{ "[M]",      monocle },
	{ "[]=",      tile },    /* first entry is default */
	{ "><>",      NULL },    /* no layout function means floating behavior */

};

/* key definitions */
#define XF86MonBrightnessDown           0x1008ff03
#define XF86MonBrightnessUp                     0x1008ff02
#define XF86AudioMute                           0x1008ff12
#define XF86AudioLowerVolume            0x1008ff11
#define XF86AudioRaiseVolume            0x1008ff13
#define MODKEY Mod1Mask
#define WINKEY Mod4Mask
#define TAGKEYS(KEY,TAG) \
	{ MODKEY,                       KEY,      view,           {.ui = 1 << TAG} }, \
	{ MODKEY|ControlMask,           KEY,      toggleview,     {.ui = 1 << TAG} }, \
	{ MODKEY|ShiftMask,             KEY,      tag,            {.ui = 1 << TAG} }, \
	{ MODKEY|ControlMask|ShiftMask, KEY,      toggletag,      {.ui = 1 << TAG} },

/* helper for spawning shell commands in the pre dwm-5.0 fashion */
#define SHCMD(cmd) { .v = (const char*[]){ "/bin/sh", "-c", cmd, NULL } }

/* commands */
static char dmenumon[2] = "0"; /* component of dmenucmd, manipulated in spawn() */
static const char *dmenucmd[] = { "dmenu_run", "-m", dmenumon, "-fn", dmenufont, "-nb", col_gray1, "-nf", col_gray3, "-sb", col_cyan, "-sf", col_gray4, NULL };
static const char *termcmd[]  = { "st", NULL };

static const char *urlcmd[] = { "clipmenu-url", NULL  };
static const char *clipcmd[] = { "clipmenu", "-i", "-fn", dmenufont, NULL  };

static const char *cmdbrightnessup[]  = { "brightness", "up", NULL };
static const char *cmdbrightnessdown[]  = { "brightness", "down", NULL };
static const char *cmdsoundup[]  = { "volumecontrol", "up", NULL };
static const char *cmdsounddown[]  = { "volumecontrol", "down", NULL };
static const char *cmdsoundtoggle[]  = { "volumecontrol", "mute", NULL };
static const char *cmdlock[]  = { "slock", NULL };
static const char *scrshot[] = { "flameshot", "gui", "--clipboard", "-p", "/tmp", NULL };


static const Key keys[] = {
	/* modifier                     key        function        argument */
        { MODKEY,                       XK_Insert, spawn,          {.v = clipcmd } },
        { MODKEY,                       XK_o,      spawn,          {.v = urlcmd } },

        { MODKEY,                       XK_c,      spawn,          SHCMD("st -e connect.sh") },
        { MODKEY,                       XK_r,      spawn,          SHCMD("st -e rdpconnect.sh") },
        { MODKEY,                       XK_s,      spawn,          SHCMD("st -e sega.sh") },
        { MODKEY|ShiftMask,             XK_x,      spawn,          SHCMD("st -e moonkill.sh") },
        { WINKEY,                       XK_b,      spawn,          SHCMD("chromium") },
        { WINKEY,                           XK_s,      spawn,          SHCMD("screenshot") },
        { WINKEY,                               XK_c,      spawn,          SHCMD("galculator") },
        { WINKEY,                               XK_z,      spawn,          SHCMD("brnorm") },
        { WINKEY,                               XK_p,      spawn,          SHCMD("pass.sh") },
        { WINKEY,                               XK_w,      spawn,          SHCMD("screencast") },
        { WINKEY,                               XK_q,      spawn,          SHCMD("webcamtoggle") },
        { WINKEY,                                               XK_m,           spawn,                        SHCMD("st -e sudo mc") },
        { WINKEY,                                               XK_grave,       spawn,                        SHCMD("dmenuunicode") },
        { WINKEY,                                               XK_space,       spawn,                        SHCMD("swlayout") },
        { MODKEY|ShiftMask,                             XK_w,           spawn,
                SHCMD("st -e sudo nmtui") },
        { MODKEY|ShiftMask,                             XK_q,           spawn,
                SHCMD("sysact") },
        { MODKEY,                                               XK_F9,          spawn,                        SHCMD("dmenumount") },
        { MODKEY,                                               XK_F10,         spawn,                        SHCMD("dmenuumount") },
        { MODKEY,                                               XK_F11,         spawn,                        SHCMD("dmenumountcifs") },
	{ MODKEY,                       XK_p,      spawn,          {.v = dmenucmd } },
	{ MODKEY|ShiftMask,             XK_Return, spawn,          {.v = termcmd } },
	{ MODKEY,                       XK_b,      togglebar,      {0} },
        { WINKEY,                       XK_l,      spawn,          {.v = cmdlock } },
        { 0,                                                    XK_Print,
                                spawn,                  {.v = scrshot } },
        { 0,                            XF86MonBrightnessDown,     spawn,         {.v
= cmdbrightnessdown } },
        { 0,                            XF86MonBrightnessUp,       spawn,         {.v
= cmdbrightnessup } },
        { 0,                            XF86AudioMute,             spawn,          {.v = cmdsoundtoggle } },
        { 0,                            XF86AudioRaiseVolume,      spawn,          {.v = cmdsoundup } },
        { 0,                            XF86AudioLowerVolume,      spawn,          {.v = cmdsounddown } },
	{ MODKEY,                       XK_j,      focusstack,     {.i = +1 } },
	{ MODKEY,                       XK_k,      focusstack,     {.i = -1 } },
	{ MODKEY,                       XK_i,      incnmaster,     {.i = +1 } },
	{ MODKEY,                       XK_d,      incnmaster,     {.i = -1 } },
	{ MODKEY,                       XK_h,      setmfact,       {.f = -0.05} },
	{ MODKEY,                       XK_l,      setmfact,       {.f = +0.05} },
	{ MODKEY,                       XK_Return, zoom,           {0} },
	{ MODKEY,                       XK_Tab,    view,           {0} },
	{ MODKEY|ShiftMask,             XK_c,      killclient,     {0} },
	{ MODKEY,                       XK_t,      setlayout,      {.v = &layouts[0]} },
	{ MODKEY,                       XK_f,      setlayout,      {.v = &layouts[1]} },
	{ MODKEY,                       XK_m,      setlayout,      {.v = &layouts[2]} },
	{ MODKEY,                       XK_space,  setlayout,      {0} },
	{ MODKEY|ShiftMask,             XK_space,  togglefloating, {0} },
	{ MODKEY,                       XK_0,      view,           {.ui = ~0 } },
	{ MODKEY|ShiftMask,             XK_0,      tag,            {.ui = ~0 } },
	{ MODKEY,                       XK_comma,  focusmon,       {.i = -1 } },
	{ MODKEY,                       XK_period, focusmon,       {.i = +1 } },
	{ MODKEY|ShiftMask,             XK_comma,  tagmon,         {.i = -1 } },
	{ MODKEY|ShiftMask,             XK_period, tagmon,         {.i = +1 } },
	TAGKEYS(                        XK_1,                      0)
	TAGKEYS(                        XK_2,                      1)
	TAGKEYS(                        XK_3,                      2)
	TAGKEYS(                        XK_4,                      3)
	TAGKEYS(                        XK_5,                      4)
	TAGKEYS(                        XK_6,                      5)
	TAGKEYS(                        XK_7,                      6)
	TAGKEYS(                        XK_8,                      7)
	TAGKEYS(                        XK_9,                      8)
};

/* button definitions */
/* click can be ClkTagBar, ClkLtSymbol, ClkStatusText, ClkWinTitle, ClkClientWin, or ClkRootWin */
static const Button buttons[] = {
	/* click                event mask      button          function        argument */
	{ ClkLtSymbol,          0,              Button1,        setlayout,      {0} },
	{ ClkLtSymbol,          0,              Button3,        setlayout,      {.v = &layouts[2]} },
	{ ClkWinTitle,          0,              Button2,        zoom,           {0} },
	{ ClkStatusText,        0,              Button2,        spawn,          {.v = termcmd } },
	{ ClkClientWin,         MODKEY,         Button1,        movemouse,      {0} },
	{ ClkClientWin,         MODKEY,         Button2,        togglefloating, {0} },
	{ ClkClientWin,         MODKEY,         Button3,        resizemouse,    {0} },
	{ ClkTagBar,            0,              Button1,        view,           {0} },
	{ ClkTagBar,            0,              Button3,        toggleview,     {0} },
	{ ClkTagBar,            MODKEY,         Button1,        tag,            {0} },
	{ ClkTagBar,            MODKEY,         Button3,        toggletag,      {0} },
};

