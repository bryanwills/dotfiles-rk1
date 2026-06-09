#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  launcher-widget.py — App launcher + file browser
#  Bottom-centre, slides from bottom, 800x600, Control Panel themed (List View)
# ─────────────────────────────────────────────────────────────────────────────

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, GtkLayerShell, Gio
import os, subprocess, threading, re

# --- Configuration ---
WIDGET_W      = 500
WIDGET_H      = 500
ICON_SIZE     = 42
HOME          = os.path.expanduser("~")
THEME_FILE    = os.path.expanduser("~/custom-scripts/Control-Panel/current-theme.css")

def load_control_panel_colors():
    """Extracts raw styling colors directly out of the generated current-theme.css structure."""
    defaults = {
        "bg": "#1d2021",
        "accent": "#9c7321",
        "fg": "#ffffff",
        "fg_dim": "#aaaaaa"
    }
    if os.path.exists(THEME_FILE):
        try:
            with open(THEME_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Robust extraction matching background properties across formatting types
            bg_match = re.search(r"QWidget#MainWidget\s*\{\s*background-color:\s*([^;}\n]+)", content)
            accent_match = re.search(r"border:\s*2px\s+solid\s+([^;}\n]+)", content)
            text_match = re.search(r"QLabel\s*\{\s*color:\s*([^;}\n]+)", content)
            hint_match = re.search(r"QLabel#DateLabel\s*\{\s*color:\s*([^;}\n]+)", content)
            
            if bg_match: defaults["bg"] = bg_match.group(1).strip()
            if accent_match: defaults["accent"] = accent_match.group(1).strip()
            if text_match: defaults["fg"] = text_match.group(1).strip()
            if hint_match: defaults["fg_dim"] = hint_match.group(1).strip()
        except Exception:
            pass
    return defaults

# --- Extract active colors prior to stylesheet compiling ---
THEME_PALETTE = load_control_panel_colors()
BG      = THEME_PALETTE["bg"]
BG_SEC  = "#050505"
BORDER  = "#222222"
ACC     = THEME_PALETTE["accent"]
FG      = THEME_PALETTE["fg"]
FG_DIM  = THEME_PALETTE["fg_dim"]

CSS = f"""
window {{
    background-color: {BG};
    border: 1px solid {ACC};
}}
.frame {{
    background-color: {BG};
    border-radius: 4px;
    border: 1px solid #333333;
    margin: 6px;
}}
.search-box {{
    background-color: {BG};
    border-radius: 4px;
    border: 2px solid {ACC};
    padding: 2px 8px;
    margin: 10px 12px 6px 12px;
}}
.search-entry {{
    background-color: transparent;
    color: {FG};
    font-family: "JetBrains Mono";
    font-size: 14px;
    border: 0px solid transparent;
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
    color: {FG};
    border-radius: 4px;
    border: none;
    padding: 4px 14px;
    font-family: "JetBrains Mono";
    font-size: 14px;
}}
.tab-btn:hover {{
    color: {FG};
}}
.tab-active {{
    background-color: {ACC};
    color: {BG_SEC};
    border-radius: 4px;
    border: none;
    padding: 4px 14px;
    font-family: "JetBrains Mono";
    font-size: 14px;
    font-weight: bold;
}}
.list-scroll {{
    background-color: transparent;
    padding: 4px 8px;
}}
.app-row {{
    background-color: {BG};
    border-radius: 4px;
    border: 1px solid {ACC};
    padding: 8px 12px;
    margin: 4px 8px;
}}
.app-row:hover {{
    background-color: {ACC};
    border-color: {ACC};
}}
.app-row:focus {{
    background-color: {ACC};
    border-color: {ACC};
}}
.app-name {{
    color: {FG};
    font-family: "JetBrains Mono";
    font-size: 14px;
}}
.file-row {{
    background-color: {BG};
    border-radius: 4px;
    border: 1px solid {ACC};
    padding: 16px 18px;
    margin: 10px 14px;
}}
.file-row:hover {{
    background-color: {ACC};
    border-color: {ACC};
}}
.file-row:focus {{
    background-color: {ACC};
    border-color: {ACC};
}}
.file-name {{
    color: {FG};
    font-family: "JetBrains Mono";
    font-size: 16px;
}}
.file-path {{
    color: {FG_DIM};
    font-family: "JetBrains Mono";
    font-size: 12px;
}}
.breadcrumb {{
    background-color: {BG};
    border-radius: 4px;
    padding: 4px 12px;
    margin: 0px 12px 6px 12px;
}}
.breadcrumb-lbl {{
    color: {FG_DIM};
    font-family: "JetBrains Mono";
    font-size: 10px;
}}
.breadcrumb-btn {{
    background-color: transparent;
    color: {ACC};
    border: none;
    border-radius: 4px;
    padding: 2px 6px;
    font-family: "JetBrains Mono";
    font-size: 10px;
}}
.breadcrumb-btn:hover {{
    color: {FG};
}}
.status-bar {{
    background-color: transparent;
    padding: 8px 14px;
    border-top: 1px solid {BORDER};
}}
.status-lbl {{
    color: {FG_DIM};
    font-family: "JetBrains Mono";
    font-size: 9px;
}}
"""

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

class Launcher(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("s-bar")

        # Layout allocation configurations targeting bottom layer setup parameters
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_keep_above(True)

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

        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        frame.get_style_context().add_class('frame')
        frame.set_size_request(WIDGET_W, WIDGET_H)
        frame.set_halign(Gtk.Align.CENTER)
        self.add(frame)

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

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(150)
        frame.pack_start(self.stack, True, True, 0)

        # ── Apps List Layout Section ──
        apps_scroll = Gtk.ScrolledWindow()
        apps_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        apps_scroll.get_style_context().add_class('list-scroll')
        self.apps_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        apps_scroll.add(self.apps_list)
        self.stack.add_named(apps_scroll, "apps")

        # ── Files List Layout Section ──
        files_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.breadcrumb_box = Gtk.Box(spacing=2)
        self.breadcrumb_box.get_style_context().add_class('breadcrumb')
        files_box.pack_start(self.breadcrumb_box, False, False, 0)

        files_scroll = Gtk.ScrolledWindow()
        files_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        files_scroll.get_style_context().add_class('list-scroll')
        self.files_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        files_scroll.add(self.files_list)
        files_box.pack_start(files_scroll, True, True, 0)
        self.stack.add_named(files_box, "files")

        status = Gtk.Box()
        status.get_style_context().add_class('status-bar')
        self.status_lbl = Gtk.Label(label="ESC to close  •  Enter to launch  •  ↑↓ to navigate")
        self.status_lbl.get_style_context().add_class('status-lbl')
        status.pack_start(self.status_lbl, True, True, 0)
        frame.pack_start(status, False, False, 0)

        self._switch_tab("apps")
        self._update_tab_styles()

        threading.Thread(target=self._load_apps, daemon=True).start()

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

    def _load_apps(self):
        apps = get_apps()
        self._all_apps = apps
        GLib.idle_add(self._populate_apps, apps)

    def _populate_apps(self, apps):
        for child in self.apps_list.get_children():
            self.apps_list.remove(child)

        for name, app in apps:
            row = self._make_app_row(name, app)
            self.apps_list.pack_start(row, False, False, 0)

        self.apps_list.show_all()
        self.app_count_lbl.set_text(f"{len(apps)} apps")

    def _make_app_row(self, name, app):
        evbox = Gtk.EventBox()
        evbox.get_style_context().add_class('app-row')
        evbox.set_can_focus(True)

        row = Gtk.Box(spacing=12)
        row.set_margin_top(2)
        row.set_margin_bottom(2)

        pb = get_icon_pixbuf(app, ICON_SIZE)
        if pb:
            img = Gtk.Image.new_from_pixbuf(pb)
        else:
            img = Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.MENU)
        img.set_halign(Gtk.Align.CENTER)

        lbl = Gtk.Label(label=name)
        lbl.get_style_context().add_class('app-name')
        lbl.set_halign(Gtk.Align.START)

        row.pack_start(img, False, False, 0)
        row.pack_start(lbl, True, True, 0)

        evbox.add(row)
        evbox._app = app
        evbox.connect("button-press-event", lambda w, e: self._launch_app(w))
        return evbox

    def _launch_app(self, box):
        if hasattr(box, '_app'):
            try:
                box._app.launch([], None)
            except:
                cmd = box._app.get_commandline()
                if cmd:
                    subprocess.Popen(cmd.split())
            Gtk.main_quit()

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
        evbox.set_can_focus(True)

        row = Gtk.Box(spacing=12)
        row.set_margin_top(2)
        row.set_margin_bottom(2)

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

    def _on_search_key(self, widget, event):
        key = event.keyval
        if key == Gdk.KEY_Down:
            if self._cur_tab == "apps":
                children = self.apps_list.get_children()
                if children:
                    children[0].grab_focus()
            elif self._cur_tab == "files":
                children = self.files_list.get_children()
                if children:
                    children[0].grab_focus()
            return True
        if key in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            if self._cur_tab == "apps":
                children = self.apps_list.get_children()
                if children:
                    self._launch_app(children[0])
            elif self._cur_tab == "files":
                children = self.files_list.get_children()
                if children:
                    path = os.path.join(self._cur_dir,
                                        children[0].get_child()
                                        .get_children()[1]
                                        .get_text())
                    self._on_file_click(path)
            return True
        return False

    def _on_key(self, widget, event):
        key = event.keyval
        
        # Linear row navigation logic matching shared framework requirements
        focused = self.get_focus()
        if focused and isinstance(focused, Gtk.EventBox):
            parent_box = focused.get_parent()
            children = parent_box.get_children()
            idx = children.index(focused)
            
            if key == Gdk.KEY_Down and idx < len(children) - 1:
                children[idx + 1].grab_focus()
                return True
            elif key == Gdk.KEY_Up:
                if idx > 0:
                    children[idx - 1].grab_focus()
                else:
                    self.search.grab_focus()
                return True
            elif key in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
                if self._cur_tab == "apps":
                    self._launch_app(focused)
                elif self._cur_tab == "files":
                    path = os.path.join(self._cur_dir, focused.get_child().get_children()[1].get_text())
                    self._on_file_click(path)
                return True

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
