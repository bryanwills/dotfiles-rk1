#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  changewall-widget.py — Wallpaper switcher with GTK Layer Shell
#  Anchored to bottom of screen, any size, no windowrules needed
# ─────────────────────────────────────────────────────────────────────────────

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, GtkLayerShell
import os, subprocess, glob, threading
from concurrent.futures import ThreadPoolExecutor

WALLPAPER_DIR = os.path.expanduser("~/Pictures/Wallpapers")
THUMB_SIZE    = 160
WIDGET_HEIGHT  = 220
WIDGET_MARGIN  = 335   # px from each side — increase to make narrower

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

C   = get_wal_colors()
BG  = C[0];  BG2 = C[1];  ACC = C[2]
FG  = C[7];  FG2 = C[15] if len(C) > 15 else "#ffffff"
HIGH= C[4]

# Parse hex to rgba for transparent background
def hex_to_rgba(h, a=0.92):
    h = h.lstrip('#')
    r, g, b = int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255
    return f"rgba({int(r*255)},{int(g*255)},{int(b*255)},{a})"

CSS = f"""
window {{
    background-color: transparent;
    border: 2px solid {ACC};
    border-radius: 12px;
}}
.frame {{
    background-color: alpha({BG}, 0.5);
    border-radius: 12px;
    border: 2px solid {ACC};
    margin: 6px;
}}
.bar {{
    background-color: transparent;
    padding: 6px 16px 4px 16px;
}}
.title {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 12px;
    font-weight: bold;
}}
.hint {{
    color: {FG};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 10px;
    opacity: 0.5;
}}
.applying {{
    color: {ACC};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 10px;
}}
.gallery {{
    background-color: transparent;
    padding: 4px 12px 8px 12px;
}}
.thumb-box {{
    background-color: {BG2};
    border-radius: 10px;
    border: 2px solid transparent;
    margin: 2px 5px;
    padding: 4px;
}}
.thumb-box:hover {{
    border-color: {ACC};
}}
.thumb-active {{
    background-color: {BG2};
    border-radius: 10px;
    border: 2px solid {FG2};
    margin: 2px 5px;
    padding: 4px;
}}
.thumb-name {{
    color: {FG};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 9px;
    opacity: 0.7;
}}
.thumb-name-active {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 9px;
    font-weight: bold;
}}
"""

# ── Wallpaper helpers ─────────────────────────────────────────────────────────
def find_wallpapers():
    files = []
    for ext in ('*.jpg','*.jpeg','*.png','*.webp'):
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

def load_thumbnail(path, size=THUMB_SIZE):
    try:
        pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, size, size, True)
        w, h = pb.get_width(), pb.get_height()
        if w != h:
            sq = min(w, h)
            pb = pb.new_subpixbuf((w-sq)//2, (h-sq)//2, sq, sq)
            pb = pb.scale_simple(size, size, GdkPixbuf.InterpType.BILINEAR)
        return pb
    except:
        return None

def apply_wallpaper(path, status_cb, done_cb):
    name = os.path.basename(path)
    GLib.idle_add(status_cb, f"󰐍  Applying {name}...")
    
    # 1. Update Wallpaper via awww
    subprocess.run(['awww', 'img', path, 
                    '--transition-type', 'grow', 
                    '--transition-pos', 'center'], capture_output=True)
    
    # 2. Generate new color scheme
    GLib.idle_add(status_cb, "󰸉  Generating colors...")
    subprocess.run(['wal', '-n', '-s', '-t', '-e', '-q', '-i', path, '--vte'], capture_output=True)
    
    # 3. Reload pywal colors into the environment
    subprocess.run(['wal', '-R', '--vte'], capture_output=True)

    # 4. Clean Waybar Restart
    # Using killall -9 to ensure no ghost processes remain during the reload
    GLib.idle_add(status_cb, "󰑓  Reloading Waybar...")
    subprocess.run(['killall', '-9', 'waybar'], capture_output=True)
    
    # Critical "settle" time: allows filesystem I/O to finish and 
    # portals to stabilize before Waybar requests a surface.
    # import time
    # time.sleep(0.4) 
    
    # Launch standard Waybar instance
    subprocess.Popen(['waybar'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5. Notify and Finalize
    subprocess.Popen(['notify-send', '-a', 'Wallpaper', 'Theme Synced Successfully', '-i', path])
    GLib.idle_add(status_cb, f"✓  {name}")
    GLib.idle_add(done_cb)
    
# ── Widget ────────────────────────────────────────────────────────────────────
class WallWidget(Gtk.Window):
    def __init__(self, preloaded=None):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("changewall-widget")
        self._preloaded = preloaded or []

        # ── GTK Layer Shell setup ─────────────────────────────────────────────
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT,   True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT,  True)
        GtkLayerShell.set_exclusive_zone(self, WIDGET_HEIGHT)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, 0)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT,   WIDGET_MARGIN)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT,  WIDGET_MARGIN)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)
        # ─────────────────────────────────────────────────────────────────────

        self.set_decorated(False)
        self.set_resizable(False)
        self.set_app_paintable(True)

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

        self._current_wall = get_current_wall()
        self._applying     = False
        self._thumb_boxes  = {}

        # ── Layout ────────────────────────────────────────────────────────────
        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        frame.get_style_context().add_class('frame')
        self.add(frame)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        frame.pack_start(root, True, True, 0)

        # Top bar
        bar = Gtk.Box()
        bar.get_style_context().add_class('bar')
        title = Gtk.Label(label="󰸉  Wallpaper Switcher")
        title.get_style_context().add_class('title')
        title.set_halign(Gtk.Align.START)
        self.status_lbl = Gtk.Label(label="")
        self.status_lbl.get_style_context().add_class('applying')
        self.status_lbl.set_halign(Gtk.Align.CENTER)
        hint = Gtk.Label(label="click to apply  •  ESC to close  •  scroll to browse")
        hint.get_style_context().add_class('hint')
        hint.set_halign(Gtk.Align.END)
        bar.pack_start(title, False, False, 0)
        bar.pack_start(self.status_lbl, True, True, 0)
        bar.pack_end(hint, False, False, 0)
        root.pack_start(bar, False, False, 0)

        # Scrolled gallery
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        scroll.get_style_context().add_class('gallery')
        self.gallery = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        scroll.add(self.gallery)
        root.pack_start(scroll, True, True, 0)
        scroll.connect("scroll-event", self._on_scroll)
        self._scroll = scroll

        self._load_thumbnails()

    def _load_thumbnails(self):
        if self._preloaded:
            # Already loaded — add instantly, no flash
            for path, pb in self._preloaded:
                self._add_thumb(path, pb)
            return
        walls = find_wallpapers()
        if not walls:
            lbl = Gtk.Label(label=f"No wallpapers found in {WALLPAPER_DIR}")
            lbl.get_style_context().add_class('hint')
            self.gallery.pack_start(lbl, True, True, 20)
            return
        def loader():
            for path in walls:
                pb = load_thumbnail(path)
                GLib.idle_add(self._add_thumb, path, pb)
        threading.Thread(target=loader, daemon=True).start()

    def _add_thumb(self, path, pb):
        name = os.path.splitext(os.path.basename(path))[0]
        is_active = (path == self._current_wall)

        evbox = Gtk.EventBox()
        evbox.get_style_context().add_class('thumb-active' if is_active else 'thumb-box')

        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        inner.set_margin_top(5); inner.set_margin_bottom(5)
        inner.set_margin_start(5); inner.set_margin_end(5)

        img = Gtk.Image.new_from_pixbuf(pb) if pb else \
              Gtk.Image.new_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
        img.set_size_request(THUMB_SIZE, THUMB_SIZE)
        inner.pack_start(img, False, False, 0)

        display_name = name if len(name) <= 18 else name[:16] + "…"
        name_lbl = Gtk.Label(label=display_name)
        name_lbl.get_style_context().add_class(
            'thumb-name-active' if is_active else 'thumb-name')
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
            ctx = evbox.get_style_context()
            ctx.remove_class('thumb-box')
            ctx.add_class('thumb-active')

    def _on_leave(self, w, e, evbox, path):
        if path != self._current_wall:
            ctx = evbox.get_style_context()
            ctx.remove_class('thumb-active')
            ctx.add_class('thumb-box')

    def _on_click(self, w, event, path):
        if self._applying or event.button != 1:
            return
        self._applying = True
        for p, (eb, nl) in self._thumb_boxes.items():
            eb.get_style_context().remove_class('thumb-active')
            eb.get_style_context().remove_class('thumb-box')
            nl.get_style_context().remove_class('thumb-name-active')
            nl.get_style_context().remove_class('thumb-name')
            if p == path:
                eb.get_style_context().add_class('thumb-active')
                nl.get_style_context().add_class('thumb-name-active')
            else:
                eb.get_style_context().add_class('thumb-box')
                nl.get_style_context().add_class('thumb-name')
        self._current_wall = path
        threading.Thread(
            target=apply_wallpaper,
            args=(path, self._set_status, self._done_applying),
            daemon=True).start()

    def _set_status(self, msg):
        self.status_lbl.set_text(msg)

    def _done_applying(self):
        self._applying = False
        GLib.timeout_add(3000, lambda: self.status_lbl.set_text("") or False)

    def _on_scroll(self, widget, event):
        adj = self._scroll.get_hadjustment()
        step = 80
        if event.direction in (Gdk.ScrollDirection.DOWN,) or \
           (event.direction == Gdk.ScrollDirection.SMOOTH and event.delta_y > 0):
            adj.set_value(adj.get_value() + step)
        elif event.direction in (Gdk.ScrollDirection.UP,) or \
             (event.direction == Gdk.ScrollDirection.SMOOTH and event.delta_y < 0):
            adj.set_value(adj.get_value() - step)
        return True

    def _on_key(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()
        adj = self._scroll.get_hadjustment()
        if event.keyval == Gdk.KEY_Right:
            adj.set_value(adj.get_value() + THUMB_SIZE + 20)
        elif event.keyval == Gdk.KEY_Left:
            adj.set_value(adj.get_value() - THUMB_SIZE - 20)

def _preload():
    walls = find_wallpapers()
    # Use all CPU cores to scale 10 images at once
    with ThreadPoolExecutor() as executor:
        # map handles the loading in parallel
        results = list(executor.map(lambda p: (p, load_thumbnail(p)), walls))
        for path, pb in results:
            _preloaded.append((path, pb))
    _preload_done.set()

if __name__ == "__main__":
    _preloaded = []
    _preload_done = threading.Event()

    t = threading.Thread(target=_preload, daemon=True)
    t.start()
    
    # With parallel loading, 10 thumbs take < 0.1s. 
    # This wait ensures they are in memory before the window maps.
    _preload_done.wait(timeout=1.0)

    win = WallWidget(_preloaded)
    win.show_all()
    Gtk.main()
