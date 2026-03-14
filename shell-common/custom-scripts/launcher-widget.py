#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  launcher-widget.py — App launcher + file browser
#  Bottom-centre, slides from bottom, 800x600, pywal themed
# ─────────────────────────────────────────────────────────────────────────────

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, GtkLayerShell, Gio
import os, subprocess, threading

WIDGET_W      = 800
WIDGET_H      = 580
ICON_SIZE     = 48
GRID_COLS     = 6
HOME          = os.path.expanduser("~")

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

CSS = f"""
window {{
    background-color: transparent;
}}
.frame {{
    background-color: alpha({BG}, 0.97);
    border-radius: 16px 16px 16px 16px;
    border: 2px solid {ACC};
    border-bottom: none;
}}
.search-box {{
    background-color: {BG2};
    border-radius: 10px;
    border: 1px solid {ACC};
    padding: 2px 8px;
    margin: 10px 12px 6px 12px;
}}
.search-entry {{
    background-color: transparent;
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 13px;
    border: none;
    box-shadow: none;
    padding: 6px 4px;
    min-width: 200px;
}}
.search-entry:focus {{
    outline: none;
    box-shadow: none;
}}
.tab-bar {{
    background-color: transparent;
    padding: 0px 12px 6px 12px;
}}
.tab-btn {{
    background-color: transparent;
    color: {FG2};
    border-radius: 8px;
    border: none;
    padding: 5px 18px;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 11px;
    opacity: 0.8;
}}
.tab-btn:hover {{
    opacity: 1.0;
    color: {FG2};
}}
.tab-active {{
    background-color: {ACC};
    color: {FG2};
    border-radius: 8px;
    border: none;
    padding: 5px 18px;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 11px;
    font-weight: bold;
    opacity: 1.0;
}}
.grid-scroll {{
    background-color: transparent;
    padding: 4px 8px;
}}
.app-tile {{
    background-color: {BG2};
    border-radius: 10px;
    border: 2px solid transparent;
    padding: 10px 6px 8px 6px;
    margin: 4px;
}}
.app-tile:hover {{
    background-color: {ACC};
    border-color: {FG2};
}}
flowboxchild:selected .app-tile {{
    background-color: {ACC};
    border-color: {FG2};
}}
flowboxchild:selected {{
    background-color: transparent;
    border: none;
    outline: none;
    box-shadow: none;
}}
.app-name {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 10px;
    margin-top: 4px;
}}
.file-row {{
    background-color: transparent;
    border-radius: 8px;
    border: 4px solid transparent;
    padding: 8px 12px;
    margin: 10px 8px;
}}
.file-row:hover {{
    background-color: {ACC};
    border-color: {FG2};
}}
.file-name {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 15px;
}}
.file-path {{
    color: {FG};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 9px;
    opacity: 0.8;
}}
.breadcrumb {{
    background-color: {BG2};
    border-radius: 8px;
    padding: 4px 12px;
    margin: 0px 12px 6px 12px;
}}
.breadcrumb-lbl {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 10px;
    opacity: 0.7;
}}
.breadcrumb-btn {{
    background-color: transparent;
    color: {ACC};
    border: none;
    border-radius: 4px;
    padding: 2px 6px;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 10px;
}}
.breadcrumb-btn:hover {{
    color: {FG2};
}}
.status-bar {{
    background-color: transparent;
    padding: 4px 16px;
    border-top: 1px solid alpha({ACC}, 0.3);
}}
.status-lbl {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 9px;
    opacity: 0.5;
}}
"""

# ── App discovery ─────────────────────────────────────────────────────────────
def get_apps():
    apps = []
    seen = set()
    dirs = [
        '/usr/share/applications',
        '/usr/local/share/applications',
        os.path.expanduser('~/.local/share/applications'),
    ]
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith('.desktop'):
                continue
            path = os.path.join(d, f)
            try:
                app = Gio.DesktopAppInfo.new_from_filename(path)
                if app and app.should_show():
                    name = app.get_name() or f[:-8]
                    if name not in seen:
                        seen.add(name)
                        apps.append((name, app))
            except:
                pass
    return sorted(apps, key=lambda x: x[0].lower())

def get_icon_pixbuf(app, size=ICON_SIZE):
    try:
        icon = app.get_icon()
        if icon:
            theme = Gtk.IconTheme.get_default()
            if isinstance(icon, Gio.ThemedIcon):
                names = icon.get_names()
                for name in names:
                    try:
                        pb = theme.load_icon(name, size, 0)
                        if pb:
                            return pb
                    except:
                        pass
            elif isinstance(icon, Gio.FileIcon):
                path = icon.get_file().get_path()
                return GdkPixbuf.Pixbuf.new_from_file_at_scale(path, size, size, True)
        return theme.load_icon("application-x-executable", size, 0)
    except:
        return None

# ── File helpers ──────────────────────────────────────────────────────────────
def list_dir(path):
    try:
        entries = os.listdir(path)
        dirs  = sorted([e for e in entries if os.path.isdir(os.path.join(path, e))
                        and not e.startswith('.')],  key=str.lower)
        files = sorted([e for e in entries if os.path.isfile(os.path.join(path, e))
                        and not e.startswith('.')], key=str.lower)
        return dirs + files
    except PermissionError:
        return []

def get_file_icon(path):
    if os.path.isdir(path):
        return "󰉋"
    ext = os.path.splitext(path)[1].lower()
    icons = {
        '.py':'.py', '.sh':'', '.js':'', '.ts':'',
        '.jpg':'󰋩', '.jpeg':'󰋩', '.png':'󰋩', '.webp':'󰋩', '.gif':'󰋩',
        '.mp4':'󰎁', '.mkv':'󰎁', '.avi':'󰎁',
        '.mp3':'󰎆', '.flac':'󰎆', '.wav':'󰎆',
        '.pdf':'󰈦', '.doc':'󰈙', '.docx':'󰈙',
        '.zip':'󰛫', '.tar':'󰛫', '.gz':'󰛫',
        '.txt':'󰈙', '.md':'󰈙', '.conf':'󰈙',
    }
    return icons.get(ext, "󰈔")

def open_file(path):
    try:
        subprocess.Popen(['xdg-open', path],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

# ── Widget ────────────────────────────────────────────────────────────────────
class Launcher(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("launcher-widget")

        # ── Layer Shell ───────────────────────────────────────────────────────
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_exclusive_zone(self, -1)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, 17)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.EXCLUSIVE)

        self.set_decorated(False)
        self.set_resizable(False)
        self.set_app_paintable(True)
        self.set_size_request(WIDGET_W, WIDGET_H)

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

        self._all_apps   = []
        self._cur_dir    = HOME
        self._cur_tab    = "apps"

        # ── Outer frame ───────────────────────────────────────────────────────
        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        frame.get_style_context().add_class('frame')
        frame.set_size_request(WIDGET_W, WIDGET_H)
        frame.set_halign(Gtk.Align.CENTER)
        self.add(frame)

        # Search bar
        search_wrap = Gtk.Box()
        search_wrap.get_style_context().add_class('search-box')
        search_icon = Gtk.Label(label="  ")
        search_icon.get_style_context().add_class('search-entry')
        self.search = Gtk.Entry()
        self.search.get_style_context().add_class('search-entry')
        self.search.set_placeholder_text("Search apps or files...")
        self.search.connect("changed", self._on_search)
        self.search.connect("key-press-event", self._on_search_key)
        search_wrap.pack_start(search_icon, False, False, 0)
        search_wrap.pack_start(self.search, True, True, 0)
        frame.pack_start(search_wrap, False, False, 0)

        # Tab bar
        tab_bar = Gtk.Box(spacing=6)
        tab_bar.get_style_context().add_class('tab-bar')
        self.tab_apps  = Gtk.Button(label="󰀻  Apps")
        self.tab_files = Gtk.Button(label="󰉋  Files")
        for btn, name in [(self.tab_apps, "apps"), (self.tab_files, "files")]:
            btn.connect("clicked", lambda _, n=name: self._switch_tab(n))
            tab_bar.pack_start(btn, False, False, 0)
        self.app_count_lbl = Gtk.Label(label="")
        self.app_count_lbl.get_style_context().add_class('status-lbl')
        self.app_count_lbl.set_halign(Gtk.Align.END)
        tab_bar.pack_end(self.app_count_lbl, False, False, 0)
        frame.pack_start(tab_bar, False, False, 0)

        # Stack
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(150)
        frame.pack_start(self.stack, True, True, 0)

        # ── Apps page ─────────────────────────────────────────────────────────
        apps_scroll = Gtk.ScrolledWindow()
        apps_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        apps_scroll.get_style_context().add_class('grid-scroll')
        self.apps_grid = Gtk.FlowBox()
        self.apps_grid.set_max_children_per_line(GRID_COLS)
        self.apps_grid.set_min_children_per_line(GRID_COLS)
        self.apps_grid.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.apps_grid.set_homogeneous(True)
        self.apps_grid.connect("child-activated", self._on_app_activate)
        self.apps_grid.connect("key-press-event", self._on_grid_key)
        apps_scroll.add(self.apps_grid)
        self.stack.add_named(apps_scroll, "apps")

        # ── Files page ────────────────────────────────────────────────────────
        files_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Breadcrumb
        self.breadcrumb_box = Gtk.Box(spacing=2)
        self.breadcrumb_box.get_style_context().add_class('breadcrumb')
        files_box.pack_start(self.breadcrumb_box, False, False, 0)

        files_scroll = Gtk.ScrolledWindow()
        files_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        files_scroll.get_style_context().add_class('grid-scroll')
        self.files_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        files_scroll.add(self.files_list)
        files_box.pack_start(files_scroll, True, True, 0)
        self.stack.add_named(files_box, "files")

        # Status bar
        status = Gtk.Box()
        status.get_style_context().add_class('status-bar')
        self.status_lbl = Gtk.Label(label="ESC to close  •  Enter to launch  •  ↑↓ to navigate")
        self.status_lbl.get_style_context().add_class('status-lbl')
        status.pack_start(self.status_lbl, True, True, 0)
        frame.pack_start(status, False, False, 0)

        self._switch_tab("apps")
        self._update_tab_styles()

        # Load apps in background
        threading.Thread(target=self._load_apps, daemon=True).start()

    # ── Tab switching ─────────────────────────────────────────────────────────
    def _switch_tab(self, name):
        self._cur_tab = name
        self.stack.set_visible_child_name(name)
        self._update_tab_styles()
        if name == "files":
            self._load_files(self._cur_dir)
        GLib.idle_add(self.search.grab_focus)

    def _update_tab_styles(self):
        for btn, name in [(self.tab_apps, "apps"), (self.tab_files, "files")]:
            ctx = btn.get_style_context()
            ctx.remove_class('tab-btn')
            ctx.remove_class('tab-active')
            ctx.add_class('tab-active' if self._cur_tab == name else 'tab-btn')

    # ── App loading ───────────────────────────────────────────────────────────
    def _load_apps(self):
        apps = get_apps()
        self._all_apps = apps
        GLib.idle_add(self._populate_apps, apps)

    def _populate_apps(self, apps):
        for child in self.apps_grid.get_children():
            self.apps_grid.remove(child)

        for name, app in apps:
            tile = self._make_app_tile(name, app)
            self.apps_grid.add(tile)

        self.apps_grid.show_all()
        self.app_count_lbl.set_text(f"{len(apps)} apps")

    def _make_app_tile(self, name, app):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.get_style_context().add_class('app-tile')
        box.set_size_request(100, 90)

        pb = get_icon_pixbuf(app, ICON_SIZE)
        if pb:
            img = Gtk.Image.new_from_pixbuf(pb)
        else:
            img = Gtk.Image.new_from_icon_name("application-x-executable",
                                               Gtk.IconSize.DIALOG)
        img.set_halign(Gtk.Align.CENTER)
        box.pack_start(img, False, False, 0)

        lbl = Gtk.Label(label=name if len(name) <= 12 else name[:11] + "…")
        lbl.get_style_context().add_class('app-name')
        lbl.set_halign(Gtk.Align.CENTER)
        lbl.set_tooltip_text(name)
        box.pack_start(lbl, False, False, 0)

        # Store app ref
        box._app = app
        return box

    def _on_app_activate(self, flowbox, child):
        box = child.get_child()
        if hasattr(box, '_app'):
            try:
                box._app.launch([], None)
            except:
                cmd = box._app.get_commandline()
                if cmd:
                    subprocess.Popen(cmd.split())
            Gtk.main_quit()

    # ── File loading ──────────────────────────────────────────────────────────
    def _load_files(self, path):
        self._cur_dir = path
        self._update_breadcrumb(path)

        for child in self.files_list.get_children():
            self.files_list.remove(child)

        entries = list_dir(path)
        for name in entries:
            full = os.path.join(path, name)
            row  = self._make_file_row(name, full)
            self.files_list.pack_start(row, False, False, 0)

        self.files_list.show_all()
        self.status_lbl.set_text(f"{len(entries)} items in {path}")

    def _make_file_row(self, name, full_path):
        evbox = Gtk.EventBox()
        evbox.get_style_context().add_class('file-row')

        row = Gtk.Box(spacing=12)
        row.set_margin_top(2); row.set_margin_bottom(2)

        icon_lbl = Gtk.Label(label=get_file_icon(full_path))
        icon_lbl.get_style_context().add_class('file-name')
        icon_lbl.set_size_request(28, -1)

        name_lbl = Gtk.Label(label=name)
        name_lbl.get_style_context().add_class('file-name')
        name_lbl.set_halign(Gtk.Align.START)
        name_lbl.set_ellipsize(3)
        name_lbl.set_max_width_chars(60)

        row.pack_start(icon_lbl, False, False, 0)
        row.pack_start(name_lbl, True, True, 0)

        if os.path.isdir(full_path):
            arr = Gtk.Label(label="›")
            arr.get_style_context().add_class('file-path')
            row.pack_end(arr, False, False, 0)

        evbox.add(row)
        evbox.connect("button-press-event",
                      lambda w, e, p=full_path: self._on_file_click(p))
        return evbox

    def _on_file_click(self, path):
        if os.path.isdir(path):
            self._load_files(path)
        else:
            open_file(path)
            Gtk.main_quit()

    def _update_breadcrumb(self, path):
        for child in self.breadcrumb_box.get_children():
            self.breadcrumb_box.remove(child)

        parts = path.replace(HOME, "~").split('/')
        parts = [p for p in parts if p]
        if not parts:
            parts = ['~']

        # Build clickable breadcrumb segments
        built = HOME
        for i, part in enumerate(parts):
            if i > 0:
                sep = Gtk.Label(label=" › ")
                sep.get_style_context().add_class('breadcrumb-lbl')
                self.breadcrumb_box.pack_start(sep, False, False, 0)
                built = os.path.join(built, part) if part != '~' else HOME
            else:
                built = HOME

            btn = Gtk.Button(label=part)
            btn.get_style_context().add_class('breadcrumb-btn')
            target = built if i > 0 else HOME
            btn.connect("clicked", lambda _, p=target: self._load_files(p))
            self.breadcrumb_box.pack_start(btn, False, False, 0)

        self.breadcrumb_box.show_all()

    # ── Search ────────────────────────────────────────────────────────────────
    def _on_search(self, entry):
        query = entry.get_text().lower().strip()

        if self._cur_tab == "apps":
            filtered = [(n, a) for n, a in self._all_apps
                        if query in n.lower()] if query else self._all_apps
            self._populate_apps(filtered)

        elif self._cur_tab == "files":
            if not query:
                self._load_files(self._cur_dir)
                return
            for child in self.files_list.get_children():
                self.files_list.remove(child)
            entries = [e for e in list_dir(self._cur_dir) if query in e.lower()]
            for name in entries:
                full = os.path.join(self._cur_dir, name)
                self.files_list.pack_start(self._make_file_row(name, full), False, False, 0)
            self.files_list.show_all()

    # ── Keyboard ──────────────────────────────────────────────────────────────
    def _on_grid_key(self, widget, event):
        key = event.keyval
        # Enter activates selected child
        if key in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            selected = self.apps_grid.get_selected_children()
            if selected:
                self.apps_grid.emit("child-activated", selected[0])
            return True
        # Escape returns focus to search
        if key == Gdk.KEY_Escape:
            self.apps_grid.unselect_all()
            self.search.grab_focus()
            return True
        # Any printable character → jump back to search and type
        if event.string and event.string.isprintable():
            self.search.grab_focus()
            self.search.set_text(self.search.get_text() + event.string)
            self.search.set_position(-1)
            return True
        return False

    def _on_search_key(self, widget, event):
        key = event.keyval
        # Arrow down from search → focus the grid
        if key == Gdk.KEY_Down:
            if self._cur_tab == "apps":
                children = self.apps_grid.get_children()
                if children:
                    self.apps_grid.select_child(children[0])
                    children[0].grab_focus()
            elif self._cur_tab == "files":
                children = self.files_list.get_children()
                if children:
                    children[0].grab_focus()
            return True
        # Enter from search → activate first result
        if key in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            if self._cur_tab == "apps":
                children = self.apps_grid.get_children()
                if children:
                    self.apps_grid.emit("child-activated", children[0])
            elif self._cur_tab == "files":
                children = self.files_list.get_children()
                if children:
                    path = os.path.join(self._cur_dir,
                                        children[0].get_child()
                                        .get_children()[0]  # row box
                                        .get_children()[1]  # name label
                                        .get_text())
                    self._on_file_click(path)
            return True
        return False

    def _on_key(self, widget, event):
        key = event.keyval
        if key == Gdk.KEY_Escape:
            if self._cur_dir != HOME and self._cur_tab == "files":
                self._load_files(os.path.dirname(self._cur_dir))
            else:
                Gtk.main_quit()
        elif key == Gdk.KEY_Tab:
            self._switch_tab("files" if self._cur_tab == "apps" else "apps")
        elif key == Gdk.KEY_BackSpace and self._cur_tab == "files":
            if not self.search.get_text():
                parent = os.path.dirname(self._cur_dir)
                if parent != self._cur_dir:
                    self._load_files(parent)

if __name__ == "__main__":
    win = Launcher()
    win.show_all()
    GLib.idle_add(win.search.grab_focus)
    Gtk.main()
