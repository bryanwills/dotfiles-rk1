#!/usr/bin/env python3
# changewall-widget.py — Wallpaper switcher with GTK Layer Shell
# Thumbnails are cached to disk — instant startup after first run.

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import os, subprocess, glob, threading, hashlib
from concurrent.futures import ThreadPoolExecutor

WALLPAPER_DIR = os.path.expanduser("~/Pictures/Wallpapers")
CACHE_DIR     = os.path.expanduser("~/.cache/changewall-widget")
THUMB_SIZE    = 160
WIDGET_HEIGHT = 220
WIDGET_MARGIN = 335

# ── Colors ────────────────────────────────────────────────────────────────────
def get_wal_colors():
    try:
        with open(os.path.expanduser("~/.cache/wal/colors")) as f:
            return [l.strip() for l in f if l.strip()]
    except:
        return ["#1a1a2e","#16213e","#0f3460","#533483",
                "#e94560","#2d6a4f","#52b788","#a8dadc",
                "#457b9d","#1d3557","#2d6a4f","#52b788",
                "#a8dadc","#e9c46a","#f4a261","#ffffff"]

C   = get_wal_colors()
BG  = C[0]; BG2 = C[1]; ACC = C[2]
FG  = C[7]; FG2 = C[15] if len(C) > 15 else "#ffffff"
HIGH= C[4]

CSS = f"""
window {{ background-color: transparent; border: 2px solid {ACC}; border-radius: 12px; }}
.frame {{ background-color: alpha({BG}, 0.5); border-radius: 12px;
          border: 2px solid {ACC}; margin: 6px; }}
.bar   {{ background-color: transparent; padding: 6px 16px 4px 16px; }}
.title {{ color: {FG2}; font-family: "JetBrainsMono Nerd Font"; font-size: 12px; font-weight: bold; }}
.hint  {{ color: {FG};  font-family: "JetBrainsMono Nerd Font"; font-size: 10px; opacity: 0.5; }}
.applying {{ color: {ACC}; font-family: "JetBrainsMono Nerd Font"; font-size: 10px; }}
.gallery  {{ background-color: transparent; padding: 4px 12px 8px 12px; }}
.thumb-box {{
    background-color: {BG2}; border-radius: 10px;
    border: 2px solid transparent; margin: 2px 5px; padding: 4px;
}}
.thumb-box:hover {{ border-color: {ACC}; }}
.thumb-active {{
    background-color: {BG2}; border-radius: 10px;
    border: 2px solid {FG2}; margin: 2px 5px; padding: 4px;
}}
.thumb-name        {{ color: {FG};  font-family: "JetBrainsMono Nerd Font"; font-size: 9px; opacity: 0.7; }}
.thumb-name-active {{ color: {FG2}; font-family: "JetBrainsMono Nerd Font"; font-size: 9px; font-weight: bold; }}
"""

# ── Thumbnail cache ───────────────────────────────────────────────────────────
os.makedirs(CACHE_DIR, exist_ok=True)

def cache_path(wall_path):
    """Cache key = filename + mtime, so it auto-invalidates when file changes."""
    mtime = int(os.path.getmtime(wall_path))
    key   = hashlib.md5(f"{wall_path}{mtime}{THUMB_SIZE}".encode()).hexdigest()[:12]
    return os.path.join(CACHE_DIR, f"{key}.png")

def load_thumbnail(path):
    """Load from disk cache if available, otherwise scale and save."""
    cp = cache_path(path)
    if os.path.exists(cp):
        try:
            return GdkPixbuf.Pixbuf.new_from_file(cp)
        except:
            pass
    # Cache miss — decode full image, scale, save
    try:
        pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, THUMB_SIZE, THUMB_SIZE, True)
        w, h = pb.get_width(), pb.get_height()
        if w != h:
            sq = min(w, h)
            pb = pb.new_subpixbuf((w - sq) // 2, (h - sq) // 2, sq, sq)
            pb = pb.scale_simple(THUMB_SIZE, THUMB_SIZE, GdkPixbuf.InterpType.BILINEAR)
        pb.savev(cp, "png", [], [])
        return pb
    except:
        return None

def find_wallpapers():
    files = []
    for ext in ('*.jpg', '*.jpeg', '*.png', '*.webp'):
        files.extend(glob.glob(os.path.join(WALLPAPER_DIR, ext)))
        files.extend(glob.glob(os.path.join(WALLPAPER_DIR, '**', ext), recursive=True))
    seen, result = set(), []
    for f in sorted(files):
        if f not in seen:
            seen.add(f); result.append(f)
    return result

def get_current_wall():
    try:
        with open(os.path.expanduser("~/.cache/wal/wal")) as f:
            return f.read().strip()
    except:
        return ""

def apply_wallpaper(path, status_cb, done_cb):
    name = os.path.basename(path)
    GLib.idle_add(status_cb, f"󰐍  Applying {name}...")
    subprocess.run(['awww', 'img', path, '--transition-type', 'grow',
                    '--transition-pos', 'center'], capture_output=True)
    GLib.idle_add(status_cb, "󰸉  Generating colors...")
    subprocess.run(['wal', '-n', '-s', '-t', '-e', '-q', '-i', path, '--vte'], capture_output=True)
    subprocess.run(['wal', '-R', '--vte'], capture_output=True)
    GLib.idle_add(status_cb, "󰑓  Reloading Waybar...")
    subprocess.run(['killall', '-9', 'waybar'], capture_output=True)
    subprocess.Popen(['waybar'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.Popen(['notify-send', '-a', 'Wallpaper', 'Theme Synced Successfully', '-i', path])
    GLib.idle_add(status_cb, f"✓  {name}")
    GLib.idle_add(done_cb)

# ── Widget ────────────────────────────────────────────────────────────────────
class WallWidget(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("changewall-widget")

        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.connect("realize", self._position)

        self.set_decorated(False); self.set_resizable(False); self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        prov = Gtk.CssProvider()
        prov.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.connect("key-press-event", self._on_key)
        self.connect("destroy", Gtk.main_quit)

        self._current_wall = get_current_wall()
        self._applying     = False
        self._thumb_boxes  = {}

        # Layout
        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        frame.get_style_context().add_class('frame')
        self.add(frame)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        frame.pack_start(root, True, True, 0)

        bar = Gtk.Box(); bar.get_style_context().add_class('bar')
        title = Gtk.Label(label="󰸉  Wallpaper Switcher")
        title.get_style_context().add_class('title'); title.set_halign(Gtk.Align.START)
        self.status_lbl = Gtk.Label(label="")
        self.status_lbl.get_style_context().add_class('applying')
        self.status_lbl.set_halign(Gtk.Align.CENTER)
        hint = Gtk.Label(label="click to apply  •  ESC to close  •  scroll to browse")
        hint.get_style_context().add_class('hint'); hint.set_halign(Gtk.Align.END)
        bar.pack_start(title, False, False, 0)
        bar.pack_start(self.status_lbl, True, True, 0)
        bar.pack_end(hint, False, False, 0)
        root.pack_start(bar, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        scroll.get_style_context().add_class('gallery')
        self.gallery = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        scroll.add(self.gallery)
        root.pack_start(scroll, True, True, 0)
        scroll.connect("scroll-event", self._on_scroll)
        self._scroll = scroll

        self._start_loading()

    def _position(self, *_):
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        geo     = monitor.get_geometry()
        w       = geo.width - WIDGET_MARGIN * 2
        x       = geo.x + WIDGET_MARGIN
        y       = geo.y + geo.height - WIDGET_HEIGHT - 8
        self.set_default_size(w, WIDGET_HEIGHT)
        self.move(x, y)

    def _start_loading(self):
        walls = find_wallpapers()
        if not walls:
            lbl = Gtk.Label(label=f"No wallpapers found in {WALLPAPER_DIR}")
            lbl.get_style_context().add_class('hint')
            self.gallery.pack_start(lbl, True, True, 20)
            return

        cached, uncached = [], []
        for p in walls:
            (cached if os.path.exists(cache_path(p)) else uncached).append(p)

        # Cached hits: load synchronously right now — they're just small PNG reads,
        # takes <50ms total and means the window opens fully populated.
        for path in cached:
            pb = load_thumbnail(path)
            self._add_thumb(path, pb)

        # Cache misses: generate in background, stream in as they finish.
        if uncached:
            self.status_lbl.set_text(f"  Caching {len(uncached)} new wallpapers...")
            def worker():
                with ThreadPoolExecutor() as ex:
                    for path, pb in zip(uncached, ex.map(load_thumbnail, uncached)):
                        GLib.idle_add(self._add_thumb, path, pb)
                GLib.idle_add(self.status_lbl.set_text, "")
            threading.Thread(target=worker, daemon=True).start()

    def _add_thumb(self, path, pb):
        name     = os.path.splitext(os.path.basename(path))[0]
        active   = path == self._current_wall
        evbox    = Gtk.EventBox()
        evbox.get_style_context().add_class('thumb-active' if active else 'thumb-box')
        inner    = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        for m in (inner.set_margin_top, inner.set_margin_bottom,
                  inner.set_margin_start, inner.set_margin_end): m(5)
        img = Gtk.Image.new_from_pixbuf(pb) if pb else \
              Gtk.Image.new_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
        img.set_size_request(THUMB_SIZE, THUMB_SIZE)
        inner.pack_start(img, False, False, 0)
        name_lbl = Gtk.Label(label=name[:18] if len(name) <= 18 else name[:16] + "…")
        name_lbl.get_style_context().add_class('thumb-name-active' if active else 'thumb-name')
        name_lbl.set_halign(Gtk.Align.CENTER)
        inner.pack_start(name_lbl, False, False, 0)
        evbox.add(inner)
        evbox.connect("enter-notify-event", self._on_enter, evbox, path)
        evbox.connect("leave-notify-event", self._on_leave, evbox, path)
        evbox.connect("button-press-event", self._on_click, path)
        self.gallery.pack_start(evbox, False, False, 0)
        self._thumb_boxes[path] = (evbox, name_lbl)
        self.gallery.show_all()

    def _on_enter(self, w, e, evbox, path):
        if path != self._current_wall:
            evbox.get_style_context().remove_class('thumb-box')
            evbox.get_style_context().add_class('thumb-active')

    def _on_leave(self, w, e, evbox, path):
        if path != self._current_wall:
            evbox.get_style_context().remove_class('thumb-active')
            evbox.get_style_context().add_class('thumb-box')

    def _on_click(self, w, event, path):
        if self._applying or event.button != 1:
            return
        self._applying = True
        for p, (eb, nl) in self._thumb_boxes.items():
            is_sel = p == path
            eb.get_style_context().remove_class('thumb-active')
            eb.get_style_context().remove_class('thumb-box')
            nl.get_style_context().remove_class('thumb-name-active')
            nl.get_style_context().remove_class('thumb-name')
            eb.get_style_context().add_class('thumb-active' if is_sel else 'thumb-box')
            nl.get_style_context().add_class('thumb-name-active' if is_sel else 'thumb-name')
        self._current_wall = path
        threading.Thread(target=apply_wallpaper,
                         args=(path, self._set_status, self._done_applying),
                         daemon=True).start()

    def _set_status(self, msg):  self.status_lbl.set_text(msg)
    def _done_applying(self):
        self._applying = False
        GLib.timeout_add(3000, lambda: self.status_lbl.set_text("") or False)

    def _on_scroll(self, widget, event):
        adj  = self._scroll.get_hadjustment()
        step = 80
        if event.direction == Gdk.ScrollDirection.DOWN or \
           (event.direction == Gdk.ScrollDirection.SMOOTH and event.delta_y > 0):
            adj.set_value(adj.get_value() + step)
        elif event.direction == Gdk.ScrollDirection.UP or \
             (event.direction == Gdk.ScrollDirection.SMOOTH and event.delta_y < 0):
            adj.set_value(adj.get_value() - step)
        return True

    def _on_key(self, widget, event):
        adj = self._scroll.get_hadjustment()
        if event.keyval == Gdk.KEY_Escape:  Gtk.main_quit()
        elif event.keyval == Gdk.KEY_Right: adj.set_value(adj.get_value() + THUMB_SIZE + 20)
        elif event.keyval == Gdk.KEY_Left:  adj.set_value(adj.get_value() - THUMB_SIZE - 20)

if __name__ == "__main__":
    win = WallWidget()
    win.show_all()
    Gtk.main()
