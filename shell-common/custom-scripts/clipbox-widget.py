#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  clipbox-widget.py — Fast clipboard manager using cliphist
#  Lazy loading, 100 entry display limit, full search across all 750
# ─────────────────────────────────────────────────────────────────────────────

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GLib, Pango, GtkLayerShell
import os, subprocess, json, threading

WIDGET_W    = 860
WIDGET_H    = 580
PINS_FILE   = os.path.expanduser("~/.cache/clipbox-pins.json")
DISPLAY_MAX = 100   # rows shown before searching

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
HIGH= C[4];  GRN = C[6] if len(C) > 6 else "#52b788"

CSS = f"""
window {{ background-color: transparent; }}
.frame {{
    background-color: alpha({BG}, 0.97);
    border-radius: 14px;
    border: 2px solid {ACC};
    margin: 6px;
}}
.header {{
    background-color: {BG2};
    border-radius: 10px 10px 0px 0px;
    padding: 10px 14px;
    margin-bottom: 6px;
}}
.header-label {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 13px; font-weight: bold;
}}
.count-lbl {{
    color: {FG};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 10px; opacity: 0.5;
}}
.search-box {{
    background-color: {BG2};
    border-radius: 8px;
    border: 1px solid {ACC};
    padding: 2px 8px;
    margin: 0px 12px 6px 12px;
}}
.search-entry {{
    background-color: transparent;
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 12px;
    border: none; box-shadow: none; padding: 6px 4px;
}}
.tab-bar {{ background-color: transparent; padding: 0px 12px 6px 12px; }}
.tab-btn {{
    background-color: transparent; color: {FG};
    border-radius: 8px; border: none; padding: 4px 14px;
    font-family: "JetBrainsMono Nerd Font"; font-size: 11px; opacity: 0.6;
}}
.tab-btn:hover {{ opacity: 1.0; color: {FG2}; }}
.tab-active {{
    background-color: {ACC}; color: {FG2};
    border-radius: 8px; border: none; padding: 4px 14px;
    font-family: "JetBrainsMono Nerd Font"; font-size: 11px; font-weight: bold;
}}
.clip-row {{
    background-color: {BG2}; border-radius: 8px;
    border: 2px solid transparent; padding: 8px 10px; margin: 2px 8px;
}}
.clip-row:hover {{ border-color: {ACC}; background-color: alpha({ACC}, 0.15); }}
.clip-row-selected {{
    background-color: alpha({ACC}, 0.25); border-radius: 8px;
    border: 2px solid {ACC}; padding: 8px 10px; margin: 2px 8px;
}}
.clip-row-pinned {{
    background-color: alpha({GRN}, 0.12); border-radius: 8px;
    border: 2px solid alpha({GRN}, 0.4); padding: 8px 10px; margin: 2px 8px;
}}
.clip-row-pinned:hover {{ border-color: {GRN}; }}
.clip-text {{
    color: {FG2}; font-family: "JetBrainsMono Nerd Font"; font-size: 11px;
}}
.clip-id {{
    color: {FG}; font-family: "JetBrainsMono Nerd Font";
    font-size: 9px; opacity: 0.4; min-width: 32px;
}}
.pin-icon {{ color: {GRN}; font-family: "JetBrainsMono Nerd Font"; font-size: 12px; }}
.action-btn {{
    background-color: transparent; color: {FG};
    border: none; border-radius: 6px; padding: 2px 6px;
    font-family: "JetBrainsMono Nerd Font"; font-size: 11px; opacity: 0.5;
}}
.action-btn:hover {{ opacity: 1.0; color: {FG2}; background-color: alpha({ACC}, 0.3); }}
.del-btn {{
    background-color: transparent; color: {FG};
    border: none; border-radius: 6px; padding: 2px 6px;
    font-family: "JetBrainsMono Nerd Font"; font-size: 11px; opacity: 0.3;
}}
.del-btn:hover {{ opacity: 1.0; color: {HIGH}; background-color: alpha({HIGH}, 0.2); }}
.preview-box {{
    background-color: {BG2}; border-radius: 8px;
    border: 1px solid alpha({ACC}, 0.4);
    padding: 8px 12px; margin: 0px 12px 6px 12px;
}}
.preview-text {{
    color: {FG}; font-family: "JetBrainsMono Nerd Font";
    font-size: 10px; opacity: 0.8;
}}
.btn {{
    background-color: {BG2}; color: {FG};
    border-radius: 8px; border: none; padding: 7px 14px;
    font-family: "JetBrainsMono Nerd Font"; font-size: 11px;
}}
.btn:hover {{ background-color: {ACC}; color: {FG2}; }}
.btn-danger {{
    background-color: {BG2}; color: {HIGH};
    border-radius: 8px; border: none; padding: 7px 14px;
    font-family: "JetBrainsMono Nerd Font"; font-size: 11px;
}}
.btn-danger:hover {{ background-color: {HIGH}; color: {FG2}; }}
.status-bar {{ padding: 4px 14px; border-top: 1px solid alpha({ACC}, 0.2); }}
.status-lbl {{
    color: {FG}; font-family: "JetBrainsMono Nerd Font";
    font-size: 9px; opacity: 0.4;
}}
.loading-lbl {{
    color: {FG}; font-family: "JetBrainsMono Nerd Font";
    font-size: 11px; opacity: 0.5; padding: 20px;
}}
"""

STATUS_HINT = "Enter: copy  •  Ctrl+P: pin  •  Ctrl+D: delete  •  Ctrl+T: paste  •  Tab: switch  •  ESC: close"

# ── Cliphist helpers ──────────────────────────────────────────────────────────
def cliphist_list():
    try:
        out = subprocess.check_output(['cliphist', 'list'],
                                      stderr=subprocess.DEVNULL).decode(errors='replace')
        entries = []
        for line in out.splitlines():
            if '\t' in line:
                cid, text = line.split('\t', 1)
                entries.append((cid.strip(), text.strip()))
        return entries
    except:
        return []

def cliphist_decode(cid, text):
    try:
        result = subprocess.run(['cliphist', 'decode'],
                                input=f"{cid}\t{text}".encode(),
                                capture_output=True)
        return result.stdout
    except:
        return text.encode()

def cliphist_delete(cid, text):
    try:
        subprocess.run(['cliphist', 'delete'],
                       input=f"{cid}\t{text}".encode(), capture_output=True)
    except:
        pass

def wl_copy(data):
    try:
        subprocess.run(['wl-copy'], input=data, capture_output=True)
        return True
    except:
        return False

def paste_to_terminal(data):
    wl_copy(data)
    for cmd in [
        ['wtype', '-M', 'ctrl', '-M', 'shift', '-k', 'v', '-m', 'ctrl', '-m', 'shift'],
        ['ydotool', 'key', 'ctrl+shift+v'],
    ]:
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except:
            continue

def load_pins():
    try:
        with open(PINS_FILE) as f:
            return set(json.load(f))
    except:
        return set()

def save_pins(pins):
    try:
        with open(PINS_FILE, 'w') as f:
            json.dump(list(pins), f)
    except:
        pass

# ── Widget ────────────────────────────────────────────────────────────────────
class ClipBox(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("clipbox-widget")

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_exclusive_zone(self, -1)
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

        self._pins        = load_pins()
        self._all_entries = []      # full 750 list, loaded in background
        self._filtered    = []      # current visible subset
        self._selected    = None    # (cid, text)
        self._cur_tab     = "all"
        self._row_widgets = []
        self._loading     = True

        # ── Frame ─────────────────────────────────────────────────────────────
        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        frame.get_style_context().add_class('frame')
        frame.set_size_request(WIDGET_W, WIDGET_H)
        self.add(frame)

        # Header
        hdr = Gtk.Box()
        hdr.get_style_context().add_class('header')
        hl = Gtk.Label(label="󰅇  Clipboard")
        hl.get_style_context().add_class('header-label')
        hl.set_halign(Gtk.Align.START)
        self.count_lbl = Gtk.Label(label="Loading...")
        self.count_lbl.get_style_context().add_class('count-lbl')
        hdr.pack_start(hl, True, True, 0)
        hdr.pack_end(self.count_lbl, False, False, 0)
        frame.pack_start(hdr, False, False, 0)

        # Search
        sw = Gtk.Box(); sw.get_style_context().add_class('search-box')
        si = Gtk.Label(label="  "); si.get_style_context().add_class('search-entry')
        self.search = Gtk.Entry()
        self.search.get_style_context().add_class('search-entry')
        self.search.set_placeholder_text("Search clipboard...")
        self.search.connect("changed", self._on_search)
        self.search.connect("key-press-event", self._on_search_key)
        sw.pack_start(si, False, False, 0)
        sw.pack_start(self.search, True, True, 0)
        frame.pack_start(sw, False, False, 0)

        # Tabs
        tab_bar = Gtk.Box(spacing=6)
        tab_bar.get_style_context().add_class('tab-bar')
        self.tab_all    = Gtk.Button(label="󰉿  All")
        self.tab_pinned = Gtk.Button(label="  Pinned")
        for btn, name in [(self.tab_all, "all"), (self.tab_pinned, "pinned")]:
            btn.connect("clicked", lambda _, n=name: self._switch_tab(n))
            tab_bar.pack_start(btn, False, False, 0)
        frame.pack_start(tab_bar, False, False, 0)

        # Preview
        pbox = Gtk.Box(); pbox.get_style_context().add_class('preview-box')
        self.preview_lbl = Gtk.Label(label="Select an entry to preview")
        self.preview_lbl.get_style_context().add_class('preview-text')
        self.preview_lbl.set_halign(Gtk.Align.START)
        self.preview_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        self.preview_lbl.set_max_width_chars(100)
        self.preview_lbl.set_xalign(0)
        pbox.pack_start(self.preview_lbl, True, True, 0)
        frame.pack_start(pbox, False, False, 0)

        # Scrolled list
        self._scroll = Gtk.ScrolledWindow()
        self._scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.clip_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._scroll.add(self.clip_list)
        frame.pack_start(self._scroll, True, True, 0)

        # Show loading spinner immediately
        self._loading_lbl = Gtk.Label(label="󰑓  Loading clipboard history...")
        self._loading_lbl.get_style_context().add_class('loading-lbl')
        self._loading_lbl.set_halign(Gtk.Align.CENTER)
        self.clip_list.pack_start(self._loading_lbl, False, False, 0)
        self.clip_list.show_all()

        # Buttons
        btn_row = Gtk.Box(spacing=8)
        btn_row.set_margin_top(8); btn_row.set_margin_bottom(8)
        btn_row.set_margin_start(12); btn_row.set_margin_end(12)
        for label, style, cb in [
            ("󰑓  Refresh",   'btn',        lambda _: self._start_load()),
            ("󰆴  Clear All", 'btn-danger', lambda _: self._clear_all()),
        ]:
            b = Gtk.Button(label=label)
            b.get_style_context().add_class(style)
            b.connect("clicked", cb)
            btn_row.pack_start(b, True, True, 0)
        frame.pack_start(btn_row, False, False, 0)

        # Status
        status = Gtk.Box(); status.get_style_context().add_class('status-bar')
        self.status_lbl = Gtk.Label(label=STATUS_HINT)
        self.status_lbl.get_style_context().add_class('status-lbl')
        status.pack_start(self.status_lbl, True, True, 0)
        frame.pack_start(status, False, False, 0)

        self._update_tab_styles()

        # Load data in background — window appears instantly
        self._start_load()
        GLib.idle_add(self.search.grab_focus)

    # ── Loading ───────────────────────────────────────────────────────────────
    def _start_load(self):
        self._loading = True
        self._all_entries = []
        self._show_loading()
        threading.Thread(target=self._bg_load, daemon=True).start()

    def _bg_load(self):
        entries = cliphist_list()
        GLib.idle_add(self._on_loaded, entries)

    def _on_loaded(self, entries):
        self._all_entries = entries
        self._loading = False
        self._rebuild_list()

    def _show_loading(self):
        for child in self.clip_list.get_children():
            self.clip_list.remove(child)
        lbl = Gtk.Label(label="󰑓  Loading clipboard history...")
        lbl.get_style_context().add_class('loading-lbl')
        lbl.set_halign(Gtk.Align.CENTER)
        self.clip_list.pack_start(lbl, False, False, 0)
        self.clip_list.show_all()
        self.count_lbl.set_text("Loading...")

    # ── Tab ───────────────────────────────────────────────────────────────────
    def _switch_tab(self, name):
        self._cur_tab = name
        self._selected = None
        self._update_tab_styles()
        self._rebuild_list()

    def _update_tab_styles(self):
        for btn, n in [(self.tab_all,"all"),(self.tab_pinned,"pinned")]:
            ctx = btn.get_style_context()
            ctx.remove_class('tab-btn'); ctx.remove_class('tab-active')
            ctx.add_class('tab-active' if self._cur_tab == n else 'tab-btn')

    # ── List building ─────────────────────────────────────────────────────────
    def _rebuild_list(self):
        if self._loading:
            return

        for child in self.clip_list.get_children():
            self.clip_list.remove(child)
        self._row_widgets = []

        query   = self.search.get_text().lower().strip()
        entries = self._all_entries

        # Tab filter
        if self._cur_tab == "pinned":
            entries = [(c, t) for c, t in entries if t in self._pins]

        # Search filter — searches all 750 when query present
        if query:
            entries = [(c, t) for c, t in entries if query in t.lower()]
        else:
            # No search — show pinned first then cap at DISPLAY_MAX
            pinned   = [(c, t) for c, t in entries if t in self._pins]
            unpinned = [(c, t) for c, t in entries if t not in self._pins]
            entries  = pinned + unpinned[:DISPLAY_MAX - len(pinned)]

        self._filtered = entries
        total = len(self._all_entries)
        shown = len(entries)

        if not entries:
            lbl = Gtk.Label(label="No entries found")
            lbl.get_style_context().add_class('loading-lbl')
            lbl.set_halign(Gtk.Align.CENTER)
            self.clip_list.pack_start(lbl, False, False, 0)
        else:
            # Build rows lazily via idle_add batches
            self._lazy_add(entries, 0)

        suffix = f" (showing {shown} of {total})" if not query and shown < total else ""
        self.count_lbl.set_text(f"{shown} entries{suffix}")
        self.clip_list.show_all()

    def _lazy_add(self, entries, start, batch=30):
        """Add rows in batches so UI stays responsive."""
        end = min(start + batch, len(entries))
        for cid, text in entries[start:end]:
            row = self._make_row(cid, text)
            self.clip_list.pack_start(row, False, False, 0)
            self._row_widgets.append((row, cid, text))
        self.clip_list.show_all()
        if end < len(entries):
            GLib.idle_add(self._lazy_add, entries, end, batch)

    def _make_row(self, cid, text):
        is_pinned = text in self._pins
        evbox = Gtk.EventBox()
        evbox.get_style_context().add_class(
            'clip-row-pinned' if is_pinned else 'clip-row')

        row = Gtk.Box(spacing=8)
        row.set_margin_top(3); row.set_margin_bottom(3)
        row.set_margin_start(4); row.set_margin_end(4)

        pin_lbl = Gtk.Label(label="" if is_pinned else "")
        pin_lbl.get_style_context().add_class('pin-icon' if is_pinned else 'clip-id')
        pin_lbl.set_size_request(20, -1)
        row.pack_start(pin_lbl, False, False, 0)

        id_lbl = Gtk.Label(label=cid)
        id_lbl.get_style_context().add_class('clip-id')
        id_lbl.set_size_request(36, -1)
        row.pack_start(id_lbl, False, False, 0)

        sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        sep.set_margin_top(4); sep.set_margin_bottom(4)
        row.pack_start(sep, False, False, 0)

        txt_lbl = Gtk.Label(label=text)
        txt_lbl.get_style_context().add_class('clip-text')
        txt_lbl.set_halign(Gtk.Align.START)
        txt_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        txt_lbl.set_max_width_chars(80)
        txt_lbl.set_xalign(0)
        row.pack_start(txt_lbl, True, True, 0)

        for icon, style, tip, cb in [
            ("", 'action-btn', "Paste to terminal", lambda _, c=cid, t=text: self._do_paste(c, t)),
            ("󰐃" if not is_pinned else "󰐄", 'action-btn', "Pin/Unpin", lambda _, t=text: self._toggle_pin(t)),
            ("󰆴", 'del-btn', "Delete", lambda _, c=cid, t=text: self._delete_entry(c, t)),
        ]:
            btn = Gtk.Button(label=icon)
            btn.get_style_context().add_class(style)
            btn.set_tooltip_text(tip)
            btn.connect("clicked", cb)
            row.pack_end(btn, False, False, 0)

        evbox.add(row)
        evbox.connect("button-press-event",
                      lambda w, e, c=cid, t=text, ev=evbox: self._on_row_click(e, c, t, ev))
        return evbox

    # ── Actions ───────────────────────────────────────────────────────────────
    def _select_row(self, evbox, cid, text):
        if self._selected:
            pc, pt = self._selected
            for ev, c, t in self._row_widgets:
                if c == pc and t == pt:
                    ctx = ev.get_style_context()
                    ctx.remove_class('clip-row-selected')
                    ctx.add_class('clip-row-pinned' if t in self._pins else 'clip-row')
        self._selected = (cid, text)
        ctx = evbox.get_style_context()
        for cls in ('clip-row','clip-row-pinned'): ctx.remove_class(cls)
        ctx.add_class('clip-row-selected')
        self.preview_lbl.set_text(text[:200] + ("…" if len(text) > 200 else ""))

    def _on_row_click(self, event, cid, text, evbox):
        self._select_row(evbox, cid, text)
        if event.type.value_name == 'GDK_2BUTTON_PRESS':
            self._do_copy(cid, text)

    def _do_copy(self, cid, text):
        wl_copy(cliphist_decode(cid, text))
        self._flash_status(f"✓  Copied: {text[:60]}")
        Gtk.main_quit()

    def _do_paste(self, cid, text):
        paste_to_terminal(cliphist_decode(cid, text))
        self._flash_status("✓  Pasted to terminal")
        GLib.timeout_add(800, Gtk.main_quit)

    def _toggle_pin(self, text):
        if text in self._pins: self._pins.discard(text)
        else: self._pins.add(text)
        save_pins(self._pins)
        self._rebuild_list()

    def _delete_entry(self, cid, text):
        # Fire delete in background so UI doesn't freeze
        threading.Thread(
            target=cliphist_delete, args=(cid, text), daemon=True).start()
        self._pins.discard(text)
        save_pins(self._pins)
        # Remove from local list immediately — no need to re-query
        self._all_entries = [(c, t) for c, t in self._all_entries
                             if not (c == cid and t == text)]
        self._selected = None
        self._rebuild_list()

    def _clear_all(self):
        # First press: ask for confirmation inline
        if not getattr(self, '_confirm_clear', False):
            self._confirm_clear = True
            self._flash_status("󰆴  Press Clear All again to confirm — this cannot be undone")
            return
        # Second press: do it
        self._confirm_clear = False
        subprocess.run(['cliphist', 'wipe'], capture_output=True)
        self._pins.clear()
        save_pins(self._pins)
        self._start_load()

    def _flash_status(self, msg):
        self.status_lbl.set_text(msg)
        GLib.timeout_add(2000, lambda: self.status_lbl.set_text(STATUS_HINT) or False)

    # ── Keyboard ──────────────────────────────────────────────────────────────
    def _on_search(self, entry):
        self._selected = None
        self._rebuild_list()

    def _on_search_key(self, widget, event):
        key = event.keyval
        if key == Gdk.KEY_Down:
            if self._row_widgets:
                ev, cid, text = self._row_widgets[0]
                self._select_row(ev, cid, text)
                ev.grab_focus()
            return True
        if key in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            if self._row_widgets:
                ev, cid, text = self._row_widgets[0]
                self._do_copy(cid, text)
            return True
        return False

    def _on_key(self, widget, event):
        key  = event.keyval
        ctrl = event.state & Gdk.ModifierType.CONTROL_MASK

        if key == Gdk.KEY_Escape:
            Gtk.main_quit()
        elif key in (Gdk.KEY_Return, Gdk.KEY_KP_Enter) and self._selected:
            self._do_copy(*self._selected)
        elif ctrl and key == Gdk.KEY_p and self._selected:
            self._toggle_pin(self._selected[1])
        elif ctrl and key == Gdk.KEY_d and self._selected:
            self._delete_entry(*self._selected)
        elif ctrl and key == Gdk.KEY_t and self._selected:
            self._do_paste(*self._selected)
        elif ctrl and key == Gdk.KEY_r:
            self._start_load()
        elif key == Gdk.KEY_Down:
            self._move_selection(1)
        elif key == Gdk.KEY_Up:
            self._move_selection(-1)
        elif key == Gdk.KEY_Tab:
            self._switch_tab("pinned" if self._cur_tab == "all" else "all")

    def _move_selection(self, direction):
        rows = self._row_widgets
        if not rows:
            return
        if self._selected is None:
            idx = 0 if direction > 0 else len(rows) - 1
        else:
            cur_c, cur_t = self._selected
            idx = next((i for i, (ev, c, t) in enumerate(rows)
                        if c == cur_c and t == cur_t), 0)
            idx = max(0, min(len(rows) - 1, idx + direction))
        ev, cid, text = rows[idx]
        self._select_row(ev, cid, text)
        GLib.idle_add(ev.grab_focus)

if __name__ == "__main__":
    win = ClipBox()
    win.show_all()
    GLib.idle_add(win.search.grab_focus)
    Gtk.main()
