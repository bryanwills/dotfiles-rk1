#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  battery-widget.py — Battery monitor + power profile switcher
#  Matches sysmon/notif-widget style. Close with Escape.
# ─────────────────────────────────────────────────────────────────────────────

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import os, subprocess, glob, time

BAT = "/sys/class/power_supply/BAT0"

# ── Pywal colors ──────────────────────────────────────────────────────────────
def get_wal_colors():
    try:
        with open(os.path.expanduser("~/.cache/wal/colors")) as f:
            return [l.strip() for l in f if l.strip()]
    except:
        return ["#1a1a2e","#16213e","#0f3460","#533483",
                "#e94560","#2d6a4f","#52b788","#a8dadc",
                "#457b9d","#1d3557","#2d6a4f","#52b788",
                "#a8dadc","#e9c46a","#f4a261","#ffffff"]

C    = get_wal_colors()
BG   = C[0];  BG2 = C[1];  ACC = C[2]
FG   = C[7];  FG2 = C[15] if len(C) > 15 else "#ffffff"
HIGH = C[4];  GRN = C[6] if len(C) > 6 else "#52b788"

CSS = f"""
window {{
    background-color: {BG};
    border-radius: 12px;
    border: 2px solid {ACC};
}}
.header {{
    background-color: {BG2};
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 10px;
}}
.header-label {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 13px;
    font-weight: bold;
}}
.card {{
    background-color: {BG2};
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 6px;
}}
.lbl  {{ color: {FG2};  font-family: "JetBrainsMono Nerd Font"; font-size: 13px; opacity: 0.8; }}
.val  {{ color: {FG2}; font-family: "JetBrainsMono Nerd Font"; font-size: 13px; font-weight: bold; }}
.sub  {{ color: {FG2};  font-family: "JetBrainsMono Nerd Font"; font-size: 13px; opacity: 0.8; }}
.time {{ color: {GRN}; font-family: "JetBrainsMono Nerd Font"; font-size: 11px; font-weight: bold; }}
.bar-track  {{ background-color: {BG};  border-radius: 4px; min-height: 8px; }}
.bar-high   {{ background-color: {GRN}; border-radius: 4px; min-height: 8px; }}
.bar-mid    {{ background-color: {C[3] if len(C)>3 else "#e9c46a"}; border-radius: 4px; min-height: 8px; }}
.bar-low    {{ background-color: {HIGH}; border-radius: 4px; min-height: 8px; }}
.section-title {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 13px;
    opacity: 0.8;
    margin-bottom: 4px;
    margin-top: 6px;
}}
/* Profile buttons */
.profile-btn {{
    background-color: {BG2};
    color: {FG2};
    border-radius: 10px;
    border: 1px solid {BG};
    padding: 10px 8px;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 13px;
}}
.profile-btn:hover {{
    border-color: {ACC};
    color: {FG2};
}}
.profile-active {{
    background-color: {ACC};
    color: {FG2};
    border-radius: 10px;
    border: 1px solid {FG2};
    padding: 10px 8px;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 13px;
    font-weight: bold;
}}
.brightness-scale trough {{
    background-color: {BG};
    border-radius: 4px;
    min-height: 6px;
}}
.brightness-scale highlight {{
    background-color: {ACC};
    border-radius: 4px;
}}
.brightness-scale slider {{
    background-color: {FG2};
    border-radius: 50%;
    min-width: 16px;
    min-height: 16px;
    border: none;
}}
"""

# ── Battery data ──────────────────────────────────────────────────────────────
def read(path):
    try: return int(open(path).read().strip())
    except: return 0

def get_battery():
    capacity = read(f"{BAT}/capacity")
    try:
        status = open(f"{BAT}/status").read().strip()
    except:
        status = "Unknown"

    energy_now  = read(f"{BAT}/energy_now")
    power_now   = read(f"{BAT}/power_now")
    energy_full = read(f"{BAT}/energy_full")

    time_str = ""
    if status == "Discharging" and power_now > 0:
        mins = energy_now * 60 // power_now
        time_str = f"{mins//60}h {mins%60:02d}m remaining"
    elif status == "Charging" and power_now > 0:
        needed = energy_full - energy_now
        mins = needed * 60 // power_now
        time_str = f"{mins//60}h {mins%60:02d}m until full"
    else:
        time_str = status

    health = int(100 * energy_full / read(f"{BAT}/energy_full_design")) \
             if read(f"{BAT}/energy_full_design") > 0 else 0
    cycles = read(f"{BAT}/cycle_count")

    return {
        "capacity": capacity,
        "status":   status,
        "time":     time_str,
        "health":   health,
        "cycles":   cycles,
        "power_w":  power_now / 1_000_000,
        "voltage":  read(f"{BAT}/voltage_now") / 1_000_000,
    }

def get_governor():
    try:
        return open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor").read().strip()
    except:
        return "unknown"

def get_brightness():
    try:
        cur = int(subprocess.check_output(['brightnessctl', 'get']).strip())
        mx  = int(subprocess.check_output(['brightnessctl', 'max']).strip())
        return int(100 * cur / mx) if mx else 0
    except:
        return 0

def set_governor(gov):
    try:
        subprocess.Popen(['pkexec', '/usr/local/bin/set-governor.sh', gov])
    except Exception as e:
        print(f"Governor error: {e}")

def set_brightness(pct):
    try:
        subprocess.Popen(['brightnessctl', 'set', f'{pct}%'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Brightness error: {e}")

# ── Progress bar ──────────────────────────────────────────────────────────────
def make_bar():
    track = Gtk.Box(); track.get_style_context().add_class('bar-track')
    fill  = Gtk.Box(); fill.set_size_request(0, 8)
    track.pack_start(fill, False, False, 0)
    return track, fill

def update_bar(track, fill, pct, invert=False):
    ctx = fill.get_style_context()
    for c in ('bar-high','bar-mid','bar-low'): ctx.remove_class(c)
    if invert:
        cls = 'bar-low' if pct > 85 else ('bar-mid' if pct > 50 else 'bar-high')
    else:
        cls = 'bar-high' if pct > 50 else ('bar-mid' if pct > 20 else 'bar-low')
    ctx.add_class(cls)
    w = track.get_allocation().width
    if w > 1:
        fill.set_size_request(max(1, int(w * pct / 100)), 8)

# ── Widget ────────────────────────────────────────────────────────────────────
class BatteryWidget(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("battery-widget")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_app_paintable(True)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_default_size(380, -1)

        # RGBA visual for xray support
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        prov = Gtk.CssProvider()
        prov.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), prov,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.connect("key-press-event", self._on_key)
        self.connect("destroy", Gtk.main_quit)

        # ── Layout ────────────────────────────────────────────────────────────
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root.set_margin_top(12); root.set_margin_bottom(12)
        root.set_margin_start(12); root.set_margin_end(12)
        self.add(root)

        # Header
        hdr = Gtk.Box()
        hdr.get_style_context().add_class('header')
        hl = Gtk.Label(label="󰁹  Battery & Power")
        hl.get_style_context().add_class('header-label')
        hl.set_halign(Gtk.Align.START)
        self.status_lbl = Gtk.Label(label="")
        self.status_lbl.get_style_context().add_class('sub')
        self.status_lbl.set_halign(Gtk.Align.END)
        hdr.pack_start(hl, True, True, 0)
        hdr.pack_end(self.status_lbl, False, False, 0)
        root.pack_start(hdr, False, False, 0)

        # ── Battery card ──────────────────────────────────────────────────────
        bat_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        bat_card.get_style_context().add_class('card')

        # Capacity row
        cap_row = Gtk.Box()
        cap_icon = Gtk.Label(label="󰁹  Charge")
        cap_icon.get_style_context().add_class('lbl')
        cap_icon.set_halign(Gtk.Align.START)
        self.cap_val = Gtk.Label(label="--")
        self.cap_val.get_style_context().add_class('val')
        self.cap_val.set_halign(Gtk.Align.END)
        self.time_lbl = Gtk.Label(label="")
        self.time_lbl.get_style_context().add_class('time')
        self.time_lbl.set_halign(Gtk.Align.END)
        cap_row.pack_start(cap_icon, True, True, 0)
        cap_row.pack_end(self.time_lbl, False, False, 8)
        cap_row.pack_end(self.cap_val, False, False, 0)
        bat_card.pack_start(cap_row, False, False, 0)
        self.bat_track, self.bat_fill = make_bar()
        bat_card.pack_start(self.bat_track, False, False, 0)

        # Stats row
        stats_row = Gtk.Box(spacing=16)
        stats_row.set_margin_top(6)
        for attr in ['power_lbl', 'volt_lbl', 'health_lbl', 'cycles_lbl']:
            lbl = Gtk.Label(label="--")
            lbl.get_style_context().add_class('sub')
            lbl.set_halign(Gtk.Align.START)
            setattr(self, attr, lbl)
            stats_row.pack_start(lbl, True, True, 0)
        bat_card.pack_start(stats_row, False, False, 0)
        root.pack_start(bat_card, False, False, 0)

        # ── Brightness card ───────────────────────────────────────────────────
        bright_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        bright_card.get_style_context().add_class('card')
        bright_row = Gtk.Box()
        bright_lbl = Gtk.Label(label="󰃟  Brightness")
        bright_lbl.get_style_context().add_class('lbl')
        bright_lbl.set_halign(Gtk.Align.START)
        self.bright_val = Gtk.Label(label="--")
        self.bright_val.get_style_context().add_class('val')
        self.bright_val.set_halign(Gtk.Align.END)
        bright_row.pack_start(bright_lbl, True, True, 0)
        bright_row.pack_end(self.bright_val, False, False, 0)
        bright_card.pack_start(bright_row, False, False, 0)

        self._updating_slider = False
        self.bright_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 5, 100, 1)
        self.bright_scale.set_draw_value(False)
        self.bright_scale.get_style_context().add_class('brightness-scale')
        self.bright_scale.set_value(get_brightness())
        self.bright_scale.connect("value-changed", self._on_brightness)
        bright_card.pack_start(self.bright_scale, False, False, 0)
        root.pack_start(bright_card, False, False, 0)

        # ── Power profiles card ───────────────────────────────────────────────
        prof_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        prof_card.get_style_context().add_class('card')
        prof_title = Gtk.Label(label="  CPU POWER PROFILE")
        prof_title.get_style_context().add_class('section-title')
        prof_title.set_halign(Gtk.Align.START)
        prof_card.pack_start(prof_title, False, False, 0)

        self.prof_btns = {}
        btn_row = Gtk.Box(spacing=6)
        profiles = [
            ("⚡ Performance", "performance",  "performance"),
            ("󰾅  Balanced",    "balanced",      "powersave"),
            ("󰌪  Power Saver", "powersave",     "powersave"),
        ]
        self._profiles = profiles
        for label, name, gov in profiles:
            btn = Gtk.Button(label=label)
            btn.get_style_context().add_class('profile-btn')
            btn.connect("clicked", lambda _, n=name, g=gov: self._set_profile(n, g))
            self.prof_btns[name] = btn
            btn_row.pack_start(btn, True, True, 0)
        prof_card.pack_start(btn_row, False, False, 0)

        # Current profile indicator
        self.prof_lbl = Gtk.Label(label="")
        self.prof_lbl.get_style_context().add_class('sub')
        self.prof_lbl.set_halign(Gtk.Align.CENTER)
        self.prof_lbl.set_margin_top(4)
        prof_card.pack_start(self.prof_lbl, False, False, 0)
        root.pack_start(prof_card, False, False, 0)

        self._current_profile = None
        self._update()
        GLib.timeout_add(3000, self._update)

    def _update(self):
        bat = get_battery()

        # Header status
        icon = "󰂄" if bat['status'] == "Charging" else "󰁹"
        self.status_lbl.set_text(bat['status'])

        # Battery
        cap = bat['capacity']
        self.cap_val.set_text(f"{icon} {cap}%")
        self.time_lbl.set_text(bat['time'])
        update_bar(self.bat_track, self.bat_fill, cap)

        self.power_lbl.set_text(f"󱐋 {bat['power_w']:.1f}W")
        self.volt_lbl.set_text(f"󱔣 {bat['voltage']:.2f}V")
        self.health_lbl.set_text(f"󰑐 Health {bat['health']}%")
        self.cycles_lbl.set_text(f"󰑞 {bat['cycles']} cycles")

        # Brightness
        bri = get_brightness()
        self.bright_val.set_text(f"{bri}%")
        self._updating_slider = True
        self.bright_scale.set_value(bri)
        self._updating_slider = False

        # Governor → profile
        gov = get_governor()
        self._update_profile_buttons(gov)

        return True

    def _update_profile_buttons(self, gov):
        for label, name, pgov in self._profiles:
            btn = self.prof_btns[name]
            ctx = btn.get_style_context()
            ctx.remove_class('profile-btn')
            ctx.remove_class('profile-active')
            # Highlight: performance=performance gov, balanced/powersave=powersave gov
            if (name == "performance" and gov == "performance") or \
               (name != "performance" and gov == "powersave" and
                self._current_profile in (None, name)):
                ctx.add_class('profile-active')
                self.prof_lbl.set_text(f"Active: {label.strip()}")
            else:
                ctx.add_class('profile-btn')

    def _set_profile(self, name, gov):
        self._current_profile = name
        # Brightness presets per profile
        presets = {"performance": None, "balanced": None, "powersave": 30}
        preset_bri = presets.get(name)

        set_governor(gov)

        if preset_bri is not None:
            self._updating_slider = True
            self.bright_scale.set_value(preset_bri)
            self._updating_slider = False
            set_brightness(preset_bri)

        # Update buttons immediately
        self._update_profile_buttons(gov)
        self.prof_lbl.set_text(f"Switching to {name}...")
        GLib.timeout_add(1500, self._update)

    def _on_brightness(self, scale):
        if self._updating_slider:
            return
        pct = int(scale.get_value())
        self.bright_val.set_text(f"{pct}%")
        set_brightness(pct)

    def _on_key(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()

if __name__ == "__main__":
    win = BatteryWidget()
    win.show_all()
    Gtk.main()
