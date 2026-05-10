#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  sysmon-widget.py — Floating system monitor for Hyprland/Wayland
#  Fixed: positioning, CPU flicker, wlan0 network stats
# ─────────────────────────────────────────────────────────────────────────────

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess, os, time, glob

# ── Read pywal colors ─────────────────────────────────────────────────────────
def get_wal_colors():
    try:
        with open(os.path.expanduser("~/.cache/wal/colors")) as f:
            return [l.strip() for l in f if l.strip()]
    except:
        return ["#1a1a2e","#16213e","#0f3460","#533483",
                "#e94560","#2d6a4f","#52b788","#a8dadc",
                "#457b9d","#1d3557","#2d6a4f","#52b788",
                "#a8dadc","#e9c46a","#f4a261","#ffffff"]

C = get_wal_colors()
BG   = C[0];  BG2 = C[1];  ACC = C[2]
FG   = C[7];  FG2 = C[15] if len(C) > 15 else "#ffffff"
HIGH = C[4]

CSS = f"""
window {{
    background-color: {BG};
    border-radius: 12px;
    border: 2px solid {ACC};
}}
.header {{
    background-color: {BG2};
    border-radius: 8px;
    padding: 8px 14px;
    margin-bottom: 8px;
}}
.header-label {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 13px;
    font-weight: bold;
}}
.card {{
    background-color: {BG2};
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 4px;
}}
.lbl {{ color: {FG}; font-family: "JetBrainsMono Nerd Font"; font-size: 12px; opacity: 0.8; }}
.val {{ color: {FG2}; font-family: "JetBrainsMono Nerd Font"; font-size: 12px; font-weight: bold; }}
.sub {{ color: {FG2};  font-family: "JetBrainsMono Nerd Font"; font-size: 12px; opacity: 0.8; }}
.bar-track {{ background-color: {BG}; border-radius: 4px; min-height: 6px; }}
.bar-low  {{ background-color: {ACC};  border-radius: 4px; min-height: 6px; }}
.bar-mid  {{ background-color: {C[3]}; border-radius: 4px; min-height: 6px; }}
.bar-high {{ background-color: {HIGH}; border-radius: 4px; min-height: 6px; }}
.btn {{
    background-color: {BG2};
    color: {FG};
    border-radius: 8px;
    border: none;
    padding: 8px 14px;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 11px;
}}
.btn:hover {{ background-color: {ACC}; color: {FG2}; }}
"""

# ── CPU ───────────────────────────────────────────────────────────────────────
_cpu_prev = None

def read_cpu_stat():
    with open('/proc/stat') as f:
        vals = list(map(int, f.readline().split()[1:9]))
    idle  = vals[3] + vals[4]
    total = sum(vals)
    return idle, total

def get_cpu():
    global _cpu_prev
    idle, total = read_cpu_stat()
    if _cpu_prev is None:
        _cpu_prev = (idle, total)
        return None   # not ready yet — caller handles None
    pi, pt = _cpu_prev
    _cpu_prev = (idle, total)
    dt = total - pt
    di = idle  - pi
    return int(100 * (dt - di) / dt) if dt > 0 else 0

# ── RAM ───────────────────────────────────────────────────────────────────────
def get_ram():
    info = {}
    with open('/proc/meminfo') as f:
        for line in f:
            k, v = line.split(':', 1)
            info[k.strip()] = int(v.split()[0])
    used  = (info['MemTotal'] - info['MemAvailable']) // 1024
    total = info['MemTotal'] // 1024
    return used, total

# ── Temp ──────────────────────────────────────────────────────────────────────
def get_temp():
    for f in glob.glob('/sys/class/hwmon/hwmon*/temp1_input'):
        try: return int(open(f).read()) // 1000
        except: pass
    try:
        return int(open('/sys/class/thermal/thermal_zone0/temp').read()) // 1000
    except:
        return None

# ── Network ───────────────────────────────────────────────────────────────────
_net_prev = None
_net_time  = None
NET_IFACE  = 'wlan0'

def get_net_bytes(iface):
    rx_path = f'/sys/class/net/{iface}/statistics/rx_bytes'
    tx_path = f'/sys/class/net/{iface}/statistics/tx_bytes'
    try:
        rx = int(open(rx_path).read())
        tx = int(open(tx_path).read())
        return rx, tx
    except:
        return 0, 0

def get_net_speed():
    global _net_prev, _net_time
    now = time.monotonic()
    rx, tx = get_net_bytes(NET_IFACE)
    if _net_prev is None:
        _net_prev = (rx, tx)
        _net_time  = now
        return 0.0, 0.0
    dt = now - _net_time
    if dt < 0.1:
        return 0.0, 0.0
    rx_spd = (rx - _net_prev[0]) / dt / 1024
    tx_spd = (tx - _net_prev[1]) / dt / 1024
    _net_prev = (rx, tx)
    _net_time  = now
    return max(0.0, rx_spd), max(0.0, tx_spd)

def fmt_speed(kbs):
    if kbs >= 1024: return f"{kbs/1024:.1f} MB/s"
    return f"{kbs:.0f} KB/s"

# ── Progress bar ──────────────────────────────────────────────────────────────
def make_bar():
    track = Gtk.Box(); track.get_style_context().add_class('bar-track')
    fill  = Gtk.Box(); fill.set_size_request(0, 6)
    track.pack_start(fill, False, False, 0)
    return track, fill

def update_bar(track, fill, pct):
    ctx = fill.get_style_context()
    for c in ('bar-low','bar-mid','bar-high'): ctx.remove_class(c)
    ctx.add_class('bar-low' if pct < 60 else ('bar-mid' if pct < 85 else 'bar-high'))
    w = track.get_allocation().width
    if w > 1:
        fill.set_size_request(max(1, int(w * pct / 100)), 6)

# ── Widget ────────────────────────────────────────────────────────────────────
class SysMon(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)   # POPUP avoids WM placement
        self.set_title("sysmon")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_app_paintable(True)
        self.set_default_size(380, -1)

        # Apply CSS
        prov = Gtk.CssProvider()
        prov.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), prov,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.connect("key-press-event", lambda w, e:
            Gtk.main_quit() if e.keyval == Gdk.KEY_Escape else None)
        self.connect("destroy", Gtk.main_quit)

        # ── Layout ────────────────────────────────────────────────────────────
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root.set_margin_top(10); root.set_margin_bottom(10)
        root.set_margin_start(10); root.set_margin_end(10)
        self.add(root)

        # Header
        hdr = Gtk.Box(); hdr.get_style_context().add_class('header')
        hl  = Gtk.Label(label="  System Monitor")
        hl.get_style_context().add_class('header-label')
        hl.set_halign(Gtk.Align.START)
        hdr.pack_start(hl, True, True, 0)
        root.pack_start(hdr, False, False, 0)

        # CPU card
        self.cpu_val, self.temp_val, self.cpu_track, self.cpu_fill = \
            self._stat_card(root, "󰻠  CPU", right2=True)

        # RAM card
        self.ram_val, self.ram_sub, self.ram_track, self.ram_fill = \
            self._stat_card(root, "󰍛  RAM", right2=True)

        # Net card
        net_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        net_card.get_style_context().add_class('card')
        net_row = Gtk.Box()
        self.net_lbl = Gtk.Label(label=f"󰖩  {NET_IFACE}")
        self.net_lbl.get_style_context().add_class('lbl')
        self.net_lbl.set_halign(Gtk.Align.START)
        speeds = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.net_rx = Gtk.Label(label="↓  --")
        self.net_rx.get_style_context().add_class('val')
        self.net_rx.set_halign(Gtk.Align.END)
        self.net_tx = Gtk.Label(label="↑  --")
        self.net_tx.get_style_context().add_class('val')
        self.net_tx.set_halign(Gtk.Align.END)
        speeds.pack_start(self.net_rx, False, False, 0)
        speeds.pack_start(self.net_tx, False, False, 0)
        net_row.pack_start(self.net_lbl, True, True, 0)
        net_row.pack_end(speeds, False, False, 0)
        net_card.pack_start(net_row, False, False, 0)
        root.pack_start(net_card, False, False, 0)

        # Buttons
        btn_row = Gtk.Box(spacing=8); btn_row.set_margin_top(8)
        for label, cmd in [("󰑓  btop", "kitty -e btop"), ("  htop", "kitty -e htop")]:
            b = Gtk.Button(label=label)
            b.get_style_context().add_class('btn')
            b.connect("clicked", lambda _, c=cmd: self._launch(c))
            btn_row.pack_start(b, True, True, 0)
        root.pack_start(btn_row, False, False, 0)

        # Position after window is realized
        self.connect("realize", self._position)

        # Warm up CPU baseline then start ticking
        read_cpu_stat()   # set _cpu_prev baseline immediately
        _cpu_prev_init = read_cpu_stat  # just to be safe
        GLib.timeout_add(1000, self._update)

    def _stat_card(self, root, icon, right2=False):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        card.get_style_context().add_class('card')
        row  = Gtk.Box()
        lbl  = Gtk.Label(label=icon)
        lbl.get_style_context().add_class('lbl')
        lbl.set_halign(Gtk.Align.START)
        val  = Gtk.Label(label="--")
        val.get_style_context().add_class('val')
        val.set_halign(Gtk.Align.END)
        sub  = Gtk.Label(label="")
        sub.get_style_context().add_class('sub')
        sub.set_halign(Gtk.Align.END)
        row.pack_start(lbl, True, True, 0)
        if right2:
            row.pack_end(sub, False, False, 8)
            row.pack_end(val, False, False, 0)
        card.pack_start(row, False, False, 0)
        track, fill = make_bar()
        card.pack_start(track, False, False, 2)
        root.pack_start(card, False, False, 0)
        return val, sub, track, fill

    def _position(self, *_):
        # Use Gdk monitor geometry for reliable Wayland positioning
        display  = Gdk.Display.get_default()
        monitor  = display.get_primary_monitor() or display.get_monitor(0)
        geo      = monitor.get_geometry()
        # top-right, 8px from edge, 8px from top (below waybar ~35px)
        wx, wy   = self.get_size()
        x = geo.x + geo.width  - 380 - 8
        y = geo.y + 40           # adjust if waybar is taller
        self.move(x, y)

    def _update(self):
        # CPU
        cpu = get_cpu()
        if cpu is not None:
            self.cpu_val.set_text(f"{cpu}%")
            update_bar(self.cpu_track, self.cpu_fill, cpu)
            temp = get_temp()
            self.temp_val.set_text(f"  {temp}°C" if temp else "")

        # RAM
        used, total = get_ram()
        pct = int(100 * used / total) if total else 0
        self.ram_val.set_text(f"{pct}%")
        self.ram_sub.set_text(f"{used} / {total} MB")
        update_bar(self.ram_track, self.ram_fill, pct)

        # Net
        rx, tx = get_net_speed()
        self.net_rx.set_text(f"↓  {fmt_speed(rx)}")
        self.net_tx.set_text(f"↑  {fmt_speed(tx)}")

        return True  # keep ticking

    def _launch(self, cmd):
        subprocess.Popen(cmd.split())
        Gtk.main_quit()

if __name__ == "__main__":
    # Seed CPU baseline before window appears so first reading is valid
    read_cpu_stat()
    time.sleep(0.3)

    win = SysMon()
    win.show_all()
    Gtk.main()
