from libqtile import bar, layout, widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
import os
import subprocess

from libqtile import hook

import psutil

# Window Swallowing
@hook.subscribe.client_new
def _swallow(window):
    pid = window.window.get_net_wm_pid()
    ppid = psutil.Process(pid).ppid()
    cpids = {c.window.get_net_wm_pid(): wid for wid, c in window.qtile.windows_map.items()}
    for i in range(5):
        if not ppid:
            return
        if ppid in cpids:
            parent = window.qtile.windows_map.get(cpids[ppid])
            parent.minimized = True
            window.parent = parent
            return
        ppid = psutil.Process(ppid).ppid()

@hook.subscribe.client_killed
def _unswallow(window):
    if hasattr(window, 'parent'):
        window.parent.minimized = False

# Startup Hook
@hook.subscribe.startup_once
def autostart():
    home = os.path.expanduser('~/Scripts/autostart.sh')
    subprocess.Popen([home])

# Default Apps
mod = "mod4"
terminal = "kitty"
launcher = "rofi -show drun"
files = "kitty ranger"
web = "brave"
music = "kitty -T music spt"

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    
    # Resize windows
    Key([mod], "l", lazy.layout.grow()),
    Key([mod], "h", lazy.layout.shrink()),

    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),

    Key([mod], "t", lazy.window.disable_floating(), desc="Tile floating window"),
    Key([mod], "m", lazy.window.toggle_fullscreen(), desc="Toggle fullscreen"),

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    
    # Qtile session
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),

    # App launchers
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key([mod], "r", lazy.spawn(launcher), desc="Launcher"),
    Key([mod], "f", lazy.spawn(files), desc="Launch file manager"),
    Key([mod], "b", lazy.spawn(web), desc="Launch web browser"),
    Key([mod, "shift"], "b", lazy.spawn(web + " --incognito"), desc="Launch web in incognito mode"),
    Key([mod], "s", lazy.spawn(music), desc="Launch music player"),
    
    # Volume Control
    Key([], "XF86AudioRaiseVolume", lazy.spawn("amixer -D pulse set Master 5%+"), desc="Raise Volume"),
    Key([], "XF86AudioLowerVolume", lazy.spawn("amixer -D pulse set Master 5%-"), desc="Lower Volume"),
    Key([], "XF86AudioMute",        lazy.spawn("amixer -D pulse set Master 1+ toggle"), desc="Lower Volume"),

    # Media Control
    Key([], "XF86AudioNext",        lazy.spawn("playerctl next"), desc="Next Track"),
    Key([], "XF86AudioPrev",        lazy.spawn("playerctl previous"), desc="Previous Track"),
    Key([], "XF86AudioStop",        lazy.spawn("playerctl stop"), desc="Stop Track"),
    Key([], "XF86AudioPlay",        lazy.spawn("playerctl play-pause"), desc="Play / Pause Track"),

    # Screenshot
    Key([], "Print",               lazy.spawn("xfce4-screenshooter"), desc="screenshot"),
    
    # Lockscreen
    Key([mod, "control"], "p",     lazy.spawn(os.path.expanduser("~/Scripts/lock.sh"))),
]


# Switch Screen Functions
def to_previous_screen(qtile, switch_group=False, switch_screen=True):
    i = qtile.screens.index(qtile.current_screen)
    if i != 0:
        qtile.cmd_to_screen(i - 1)

def to_next_screen(qtile, switch_group=False, switch_screen=True):
    i = qtile.screens.index(qtile.current_screen)
    if i + 1 != len(qtile.screens):
        qtile.cmd_to_screen(i + 1)

def window_to_previous_screen(qtile, switch_group=False, switch_screen=False):
    i = qtile.screens.index(qtile.current_screen)
    if i != 0:
        group = qtile.screens[i - 1].group.name
        qtile.current_window.togroup(group, switch_group=switch_group)
        if switch_screen == True:
            qtile.cmd_to_screen(i - 1)

def window_to_next_screen(qtile, switch_group=False, switch_screen=False):
    i = qtile.screens.index(qtile.current_screen)
    if i + 1 != len(qtile.screens):
        group = qtile.screens[i + 1].group.name
        qtile.current_window.togroup(group, switch_group=switch_group)
        if switch_screen == True:
            qtile.cmd_to_screen(i + 1)

# Switch Screen Keybinds
keys.extend([
    Key([mod], "w", lazy.function(to_previous_screen)),
    Key([mod], "e", lazy.function(to_next_screen)),
    Key([mod,"shift"],"e", lazy.function(window_to_next_screen, switch_screen=True)),
    Key([mod,"shift"],"w", lazy.function(window_to_previous_screen, switch_screen=True)),
    # Key([mod], "w", lazy.to_screen(0)),
    # Key([mod], "e", lazy.to_screen(1)),
])


# Groups
groups = [Group(i) for i in "123456789"]

for i in groups:
    keys.extend(
        [
            # mod1 + letter of group = switch to group
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name),
                desc="move focused window to group {}".format(i.name)
            ),
        ]
    )

# Theme
colors = []
cache='/home/mx3/.cache/wal/colors'
def load_colors(cache):
    with open(cache, 'r') as file:
        for i in range(8):
            colors.append(file.readline().strip())
    colors.append('#ffffff')
    lazy.reload()
load_colors(cache)

layout_theme = {
    "border_width": 4,
    "margin": 24,
    "border_focus": colors[1],
    "border_normal": colors[0],
}

# Layouts
layouts = [
    layout.MonadTall(**layout_theme),
    layout.MonadThreeCol(**layout_theme),
]

widget_defaults = dict(
    font="SAGA Heavy",
    fontsize=12,
    padding=5,
)
extension_defaults = widget_defaults.copy()

# Bar
screens = [
    Screen(
        bottom=bar.Bar(
            [
                widget.TextBox(
                    text="",
                    fontsize=20,
                    mouse_callbacks={'Button1': lazy.spawn("rofi -show drun")},
                    padding=8,
                    foreground=colors[7],
                ),
                
                widget.GroupBox(
                    active=colors[7],
                    # inactive=colors[2]
                    highlight_method="line",
                    highlight_color=colors[0],
                    this_screen_border=colors[1],
                    this_current_screen_border=colors[1],
                    other_screen_border=colors[3],
                    other_current_screen_border=colors[3],

                ),
                widget.WindowName(
                    max_chars=50,
                    padding=8,
                    foreground=colors[7],
                ),
                widget.Systray(
                    padding=4,
                    icon_size=20,
                ),
                widget.CurrentLayoutIcon(
                    scale=0.55,
                    foreground=colors[7],
                ),
                widget.Volume(foreground=colors[7]),
                widget.Clock(format=" %a %H:%M %d/%m/%y", foreground=colors[7]),
                widget.Spacer(length=8)
            ],
            32,
            background=colors[0],
        ),
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

# Rules
dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(
    **layout_theme,
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

wmname = "qtile"
