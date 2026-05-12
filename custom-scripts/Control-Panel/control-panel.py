#!/usr/bin/env python3

#----------------------------------------------------------------------------------
# CONTROL PANEL
# Author: Lukas Grumlik - Rakosn1cek
# Created: 2026-05-04
# Version: 0.1.0
# Descriptions: 
# A unified, Waybar-free dashboard built with PyQt6 for Hyprland.
#----------------------------------------------------------------------------------

import sys
import os
import psutil
import datetime
import subprocess
import glob
import re
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QGridLayout, QProgressBar, 
                             QPushButton, QFrame, QSlider, QListWidget, QListWidgetItem,
                             QMenu, QScrollArea)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon, QFontDatabase

BAT = "/sys/class/power_supply/BAT0"
LOG_FILE = os.path.expanduser("~/.cache/notification_history.log")

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        # Adjust height for better vertical distribution
        self.setFixedSize(700, 750) 
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setObjectName("MainWidget")
        self.home = os.path.expanduser("~")
        
        font_path = os.path.expanduser("~/.local/share/fonts/OpenDyslexicMNerdFontMono-Regular.otf")
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            self.font_family = "JetBrains Mono"

        self.setStyleSheet(f"""
            QWidget#MainWidget {{ background-color: #1d2021; border: 1px solid #050505; }}
            QFrame#Section {{ border: 1px solid #9c7321; border-radius: 4px; background-color: #1d2021; }}
            QLabel {{ color: #ffffff; font-family: 'JetBrains Mono'; font-size: 11px; }}
            QLineEdit {{ background-color: #1d2021; border: 1px solid #9c7321; color: #ffffff; padding: 5px; border-radius: 4px; }}
            QListWidget {{ background-color: #1d2021; border: 1px solid #222222; color: #ffffff; outline: none; border-radius: 4px; }}
            QListWidget::item {{ padding: 8px; border-bottom: 1px solid #111111; }}
            QListWidget::item:selected {{ background-color: #111111; color: #9c7321; }}
            QProgressBar {{ border: none; background-color: #111111; height: 4px; border-radius: 5px; color: transparent; }}
            QProgressBar::chunk {{ background-color: #52fa69; border-radius: 5px; }}
            QScrollBar {{ border: none; background: #000000; width: 8px; height: 8px; margin: 0px; }}
            QScrollBar::handle {{ background: #333333; min-height: 20px; min-width: 20px; border-radius: 4px; }}
            QScrollBar::handle:hover {{ background: #287b34; }}
            QPushButton {{ background-color: #1d2021; border: 1px solid #9c7321; color: #ffffff; padding: 8px; font-family: 'JetBrains Mono'; border-radius: 4px; }}
            QSlider::groove:horizontal {{ border: none; height: 2px; background: #333333; }}
            QSlider::handle:horizontal {{ background: #52fa69; border: 1px solid #ffffff; width: 4px; height: 14px; margin: -7px 0; }}
            QPushButton:hover {{ background-color: #222222; border-color: #287b34; }}
            QPushButton:focus {{ background-color: #222222; border: 1px solid #ffffff; outline: none; }}
            QPushButton#ActiveProfile, QPushButton#ActiveWorkspace {{ background-color: #9c7321; color: #000000; font-weight: bold; border: 1px solid #ffffff; }}
            QPushButton#TaskItem {{ font-size: 10px; padding: 4px 6px; min-width: 70px; background-color: #1d2021; border-color: #9c7321; }}
        """)

        self.apps_list = self.get_installed_apps()
        self.init_ui()
        self.sync_hardware_sliders()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_live_data)
        self.timer.start(1500)

    def get_installed_apps(self):
        import gi
        gi.require_version('Gio', '2.0')
        from gi.repository import Gio
        apps = []
        seen_names = set()
        search_dirs = ['/usr/share/applications', '/usr/local/share/applications', os.path.expanduser('~/.local/share/applications')]
        for d in search_dirs:
            if not os.path.isdir(d): continue
            for f in sorted(os.listdir(d)):
                if not f.endswith('.desktop'): continue
                try:
                    app_info = Gio.DesktopAppInfo.new_from_filename(os.path.join(d, f))
                    if app_info and app_info.should_show():
                        name = app_info.get_name()
                        cmd = app_info.get_commandline()
                        if cmd: cmd = re.sub(r'%[fFuUicein]', '', cmd).strip().replace('"', '')
                        icon = "application-x-executable"
                        gicon = app_info.get_icon()
                        if gicon: icon = gicon.to_string()
                        if name and cmd and name not in seen_names:
                            apps.append({'name': name, 'exec': cmd, 'icon': icon})
                            seen_names.add(name)
                except: continue
        return sorted(apps, key=lambda x: x['name'].lower())

    def create_section(self):
        frame = QFrame()
        frame.setObjectName("Section")
        return frame

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Header Section
        top_sec = self.create_section()
        top_sec.setFixedHeight(90)
        top_lay = QVBoxLayout(top_sec)
        self.clock_lbl = QLabel()
        self.clock_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clock_lbl.setStyleSheet(f"font-size: 36px; font-family: '{self.font_family}'; font-weight: 900;")
        self.date_lbl = QLabel()
        self.date_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_lbl.setStyleSheet("font-size: 12px; color: #aaaaaa; letter-spacing: 1px;")
        top_lay.addWidget(self.clock_lbl)
        top_lay.addWidget(self.date_lbl)
        main_layout.addWidget(top_sec)

        # Workspaces Row
        ws_sec = self.create_section()
        ws_lay = QHBoxLayout(ws_sec)
        self.ws_btns = {}
        for i in range(1, 11):
            btn = QPushButton(str(i))
            btn.setFixedSize(32, 32)
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.clicked.connect(lambda chk, w=i: self.run_cmd(f"hyprctl dispatch workspace {w}"))
            # btn.clicked.connect(lambda chk, w=i: self.run_cmd(f"hyprctl dispatch 'hl.dsp.workspace(\"{w}\")'")) # Lua transition
            ws_lay.addWidget(btn)
            self.ws_btns[i] = btn
        main_layout.addWidget(ws_sec)

        body = QHBoxLayout()
        left = QVBoxLayout()
        
        # Tasks Section
        task_sec = self.create_section()
        task_lay = QVBoxLayout(task_sec)
        task_lay.addWidget(QLabel("󰖯  OPEN TASKS"))
        self.task_grid = QGridLayout()
        self.task_grid.setSpacing(5)
        task_lay.addLayout(self.task_grid)
        task_lay.addStretch()
        left.addWidget(task_sec)

        # App Launcher
        s_sec = self.create_section()
        s_lay = QVBoxLayout(s_sec)
        s_lay.addWidget(QLabel("󰀻  APP LAUNCHER"))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")
        self.search.textChanged.connect(self.filter_apps)
        s_lay.addWidget(self.search)
        self.results = QListWidget()
        self.results.setFixedHeight(90)
        self.results.hide()
        self.results.itemDoubleClicked.connect(self.launch_app)
        s_lay.addWidget(self.results)
        left.addWidget(s_sec)

        # Tools Grid with ID tracking
        g_sec = self.create_section()
        g_lay = QGridLayout(g_sec)
        self.tool_btns = {}
        tools = [
            ("  ", "rtm", f"kitty --class rtm -e python3 {self.home}/arch-projects/RTM/rtm.py"),
            (" 󱀇 ", "budget", f"kitty --class budget-buddy -e python3 {self.home}/arch-projects/Budget-Buddy/budget-buddy.py"),
            ("  ", "mirec", f"kitty --title Mirec -e {self.home}/arch-projects/MIREC/mirec"),
            (" 󰖩 ", "wifi", f"kitty --class floating_wifi -e {self.home}/custom-scripts/wifi/wwifi"),
            ("  ", "bt", f"kitty --class bt-menu -e {self.home}/custom-scripts/bluetooth/bt"),
            (" 󰌌 ", "keys", f"kitty --class keybinds -e {self.home}/custom-scripts/keybinds.sh"),
            (" 󰬈 ", "alias", f"kitty --class show-aliases -e {self.home}/custom-scripts/Show-Aliases/show-aliases.sh"),
            (" 󱫉 ", "clip", f"python3 {self.home}/custom-scripts/Python-Widgets/clipbox-widget2.py")
        ]
        for i, (icon, tid, cmd) in enumerate(tools):
            btn = QPushButton(icon)
            btn.setStyleSheet("font-size: 16px; padding: 10px;")
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.clicked.connect(lambda chk, c=cmd: self.launch_app_manual(c))
            g_lay.addWidget(btn, i // 2, i % 2)
            self.tool_btns[tid] = btn
        left.addWidget(g_sec)

        # CPU Profiles
        cp_sec = self.create_section()
        cp_lay = QHBoxLayout(cp_sec)
        self.prof_btns = {}
        for label, gov in [("⚡ Performance", "performance"), ("󰌪  Power Saver", "powersave")]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda chk, g=gov: self.set_governor(g))
            cp_lay.addWidget(btn)
            self.prof_btns[gov] = btn
        left.addWidget(cp_sec)
        body.addLayout(left, 1)

        # Right Column
        right = QVBoxLayout()
        r_sec = self.create_section()
        r_lay = QVBoxLayout(r_sec)
        r_lay.setContentsMargins(15, 15, 15, 15)
        
        temp_lay = QHBoxLayout()
        temp_lay.addWidget(QLabel("SYSTEM RESOURCES"))
        self.temp_lbl = QLabel("󰔏 0°C")
        self.temp_lbl.setStyleSheet("color: #52fa69; font-weight: bold; font-size: 13px;")
        temp_lay.addWidget(self.temp_lbl, 0, Qt.AlignmentFlag.AlignRight)
        r_lay.addLayout(temp_lay)

        self.cpu = QProgressBar(); self.cpu.setFixedHeight(4)
        self.ram = QProgressBar(); self.ram.setFixedHeight(4)
        self.cpu_label = QLabel("CPU Usage")
        r_lay.addWidget(self.cpu_label)
        r_lay.addWidget(self.cpu)
        r_lay.addSpacing(5)
        self.ram_label = QLabel("RAM Usage")
        r_lay.addWidget(self.ram_label)
        r_lay.addWidget(self.ram)
        r_lay.addSpacing(10)
        r_lay.addWidget(QLabel("BATTERY"))
        self.bat_stats = QLabel("Checking battery...")
        self.bat_stats.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        self.bat_stats.setWordWrap(True)
        r_lay.addWidget(self.bat_stats)
        right.addWidget(r_sec)

        # Volume & Brightness
        t_sec = self.create_section()
        t_lay = QVBoxLayout(t_sec)
        t_lay.setContentsMargins(15, 15, 15, 15)
        t_lay.addWidget(QLabel("VOLUME"))
        self.vol = QSlider(Qt.Orientation.Horizontal)
        self.vol.setRange(0, 100)
        self.vol.valueChanged.connect(self.set_volume)
        t_lay.addWidget(self.vol)
        t_lay.addSpacing(10)
        t_lay.addWidget(QLabel("BRIGHTNESS"))
        self.bright = QSlider(Qt.Orientation.Horizontal)
        self.bright.setRange(1, 100)
        self.bright.valueChanged.connect(self.set_brightness)
        t_lay.addWidget(self.bright)
        right.addWidget(t_sec)

        # Notification Centre
        notif_sec = self.create_section()
        notif_lay = QVBoxLayout(notif_sec)
        nh_lay = QHBoxLayout()
        nh_lay.addWidget(QLabel("RECENT NOTIFICATIONS"))
        cb = QPushButton("󰆴"); cb.setFixedWidth(30)
        cb.clicked.connect(self.clear_all_notifications)
        nh_lay.addWidget(cb)
        notif_lay.addLayout(nh_lay)
        self.notif_list = QListWidget()
        self.notif_list.setObjectName("NotifList")
        self.notif_list.setFixedHeight(160)
        self.notif_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.notif_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.notif_list.customContextMenuRequested.connect(self.show_notif_menu)
        notif_lay.addWidget(self.notif_list)
        right.addWidget(notif_sec)
        
        body.addLayout(right, 1)
        main_layout.addLayout(body)

        # Bottom Power Action Row
        p_sec_bottom = self.create_section()
        p_lay_bottom = QHBoxLayout(p_sec_bottom)
        p_clrs = {"󰐥": "#ff5555", "󰑐": "#f1fa8c", "󰤄": "#bd93f9", "󰈆": "#8be9fd", "󰖔": "#ffb86c"}
        p_acts = {"󰐥": "shutdown now", "󰑐": "reboot", "󰤄": "systemctl suspend", "󰈆": "hyprctl dispatch exit", "󰖔": f"bash {self.home}/.local/bin/nightlight"}
        for icon, cmd in p_acts.items():
            pb = QPushButton(icon)
            pb.setStyleSheet(f"font-size: 16px; color: {p_clrs.get(icon, '#ffffff')};")
            pb.clicked.connect(lambda chk, c=cmd: self.run_cmd(c))
            p_lay_bottom.addWidget(pb)
        main_layout.addWidget(p_sec_bottom)

    def update_live_data(self):
        now = datetime.datetime.now()
        self.clock_lbl.setText(now.strftime("%H:%M:%S"))
        self.date_lbl.setText(now.strftime("%A, %d %B %Y").upper())
    
        # Fetch fresh hardware stats
        cpu_percent = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        
        # Calculate Gigabytes (1024^3)
        true_used_bytes = mem.total - mem.available
        used_gb = mem.used / 1073741824
        total_gb = mem.total / 1073741824
    
        self.cpu.setValue(int(cpu_percent))
        self.ram.setValue(int(mem.percent))
    
        self.cpu_label.setText(f"CPU: {cpu_percent}%")
        self.ram_label.setText(f"RAM: {used_gb:.2f}GB / {total_gb:.1f}GB ({mem.percent}%)")
    
        self.bat_stats.setText(self.get_battery_info())
        try:
            temps = psutil.sensors_temperatures()
            core_temp = temps.get('coretemp', temps.get('cpu_thermal', []))[0].current
            self.temp_lbl.setText(f"󰔏 {int(core_temp)}°C")
        except: pass

        # Connection status sensing for WiFi and Bluetooth
        try:
            wifi_con = subprocess.run("nmcli -t -f TYPE,STATE dev | grep -q '^wifi:connected'", shell=True).returncode == 0
            w_col = "#52fa69" if wifi_con else "#ffffff"
            self.tool_btns["wifi"].setStyleSheet(f"font-size: 16px; padding: 10px; color: {w_col};")
            
            bt_con = subprocess.run("bluetoothctl devices Connected | grep -q '.'", shell=True).returncode == 0
            b_col = "#3b82f6" if bt_con else "#ffffff"
            self.tool_btns["bt"].setStyleSheet(f"font-size: 16px; padding: 10px; color: {b_col};")
        except: pass

        self.update_workspaces()
        self.update_taskbar()
        self.highlight_active_profile()
        self.refresh_notifications()

    # --- Workspace and Taskbar Syncing ---
    def update_workspaces(self):
        try:
            res = subprocess.check_output(["hyprctl", "activeworkspace", "-j"])
            active = json.loads(res).get("id")
            for i, btn in self.ws_btns.items():
                btn.setObjectName("ActiveWorkspace" if i == active else "")
                btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                btn.style().unpolish(btn); btn.style().polish(btn)
        except: pass

    def update_taskbar(self):
        while self.task_grid.count():
            child = self.task_grid.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        try:
            res = subprocess.check_output(["hyprctl", "clients", "-j"])
            clients = json.loads(res)
            valid_tasks = [c for c in clients if c.get("title")]
            for i, c in enumerate(valid_tasks):
                btn = QPushButton(c.get("class")[:10])
                btn.setObjectName("TaskItem")
                btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                btn.setToolTip(c.get("title"))
                btn.clicked.connect(lambda chk, a=c.get("address"): self.run_cmd(f"hyprctl dispatch focuswindow address:{a}"))
                # btn.clicked.connect(lambda chk, a=c.get("address"): self.run_cmd(f"hyprctl dispatch 'hl.dsp.focus({{ window = \"address:{a}\" }})'")) # Transition to Lua
                self.task_grid.addWidget(btn, i // 3, i % 3)
        except: pass

    # --- Notification Handling ---
    def show_notif_menu(self, pos):
        if not self.notif_list.itemAt(pos): return
        menu = QMenu()
        menu.setStyleSheet("QMenu { background: #000; border: 1px solid #333; color: #fff; } QMenu::item:selected { background: #52fa69; color: #000; }")
        del_act = menu.addAction("Delete Entry")
        action = menu.exec(self.notif_list.viewport().mapToGlobal(pos))
        if action == del_act: self.delete_selected_notification()

    def delete_selected_notification(self):
        row = self.notif_list.currentRow()
        if row < 0: return
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f: lines = f.readlines()
            lines.reverse()
            if row < len(lines): lines.pop(row)
            lines.reverse()
            with open(LOG_FILE, 'w', encoding='utf-8') as f: f.writelines(lines)
        except: pass
        self.refresh_notifications()

    def get_notifications(self):
        pattern = re.compile(r'^\[(\d{2}:\d{2})\]\s+(.+)$')
        entries = []
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in reversed(lines):
                        m = pattern.match(line.strip())
                        if m: entries.append(f"{m.group(1)}  {m.group(2)}")
                        if len(entries) >= 5: break
        except: pass
        return entries

    def refresh_notifications(self):
        self.notif_list.clear()
        for n in self.get_notifications(): self.notif_list.addItem(n)

    # --- System State Sensing ---
    def get_battery_info(self):
        def read_sys(file):
            try:
                with open(f"{BAT}/{file}", 'r') as f:
                    return int(f.read().strip())
            except: return 0
        cap = read_sys("capacity")
        pwr_mw = read_sys("power_now")
        pwr = pwr_mw / 1_000_000
        vlt = read_sys("voltage_now") / 1_000_000
        full = read_sys("energy_full") or read_sys("charge_full")
        now = read_sys("energy_now") or read_sys("charge_now")
        design = read_sys("energy_full_design") or read_sys("charge_full_design")
        health = int(100 * full / design) if design > 0 else 0
        try: status = open(f"{BAT}/status").read().strip()
        except: status = "Unknown"
        time_info = "Calculating..."
        if pwr_mw > 0:
            if status == "Discharging":
                hours = now / pwr_mw
                time_info = f"{int(hours)}h {int((hours % 1) * 60)}m left"
            elif status == "Charging":
                hours = (full - now) / pwr_mw
                time_info = f"{int(hours)}h {int((hours % 1) * 60)}m to full"
        elif status == "Full": time_info = "Battery Full"
        icon = "󱐋" if status == "Charging" else "󰁹"
        return f"{icon} {cap}% | 󱐋 {pwr:.1f}W | 󱔣  {vlt:.1f}V | 󰑐 Health: {health}% | 󱎫 {time_info}"

    def set_governor(self, gov):
        subprocess.Popen(['pkexec', '/usr/local/bin/set-governor.sh', gov])

    def sync_hardware_sliders(self):
        try:
            v = subprocess.check_output("wpctl get-volume @DEFAULT_AUDIO_SINK@", shell=True).decode()
            self.vol.setValue(int(float(v.split(":")[1].strip()) * 100))
            b_now = subprocess.check_output("brightnessctl g", shell=True).decode()
            b_max = subprocess.check_output("brightnessctl m", shell=True).decode()
            self.bright.setValue(int((int(b_now)/int(b_max)) * 100))
        except: pass

    def highlight_active_profile(self):
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor", "r", encoding='utf-8') as f:
                cur = f.read().strip()
            for k, btn in self.prof_btns.items():
                btn.setObjectName("ActiveProfile" if k == cur else "")
                btn.style().unpolish(btn); btn.style().polish(btn)
        except: pass
    
    def set_volume(self, val): subprocess.run(f"wpctl set-volume @DEFAULT_AUDIO_SINK@ {val/100:.2f}", shell=True, check=False)
    def set_brightness(self, val): subprocess.run(f"brightnessctl set {val}%", shell=True, check=False)
    def filter_apps(self, t):
        self.results.clear()
        if not t: self.results.hide(); return
        m = [a for a in self.apps_list if t.lower() in a['name'].lower()][:5]
        for a in m:
            item = QListWidgetItem(QIcon.fromTheme(a['icon']), a['name'])
            item.setData(Qt.ItemDataRole.UserRole, a['exec'])
            self.results.addItem(item)
        self.results.show() if m else self.results.hide()

    def launch_app(self, i):
            cmd = i.data(Qt.ItemDataRole.UserRole)
            self.smart_launch(cmd)
    
    def launch_app_manual(self, c):
        self.smart_launch(c)

    def smart_launch(self, cmd):
        # List of apps that must run in kitty/terminal
        tui_apps = ["btop", "htop", "nvtop", "top", "vim", "nvim", "micro"]
        
        # Check if the command is a TUI app and not already wrapped in kitty/terminal
        if any(app in cmd.lower() for app in tui_apps) and "kitty" not in cmd:
            cmd = f"kitty {cmd}"
            
        self.run_cmd(cmd)
        self.close()
    def run_cmd(self, c): subprocess.Popen(c, shell=True, start_new_session=True)
    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.cleanup_and_exit()
            
        elif e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            focused_widget = self.focusWidget()
            if isinstance(focused_widget, QPushButton):
                focused_widget.click()
            elif isinstance(focused_widget, QListWidget):
                item = focused_widget.currentItem()
                if item:
                    self.launch_app(item)
        
        else:
            super().keyPressEvent(e)
    def cleanup_and_exit(self):
        self.timer.stop(); QApplication.quit(); sys.exit(0)
    def clear_all_notifications(self):
        if os.path.exists(LOG_FILE): open(LOG_FILE, 'w', encoding='utf-8').close()
        self.refresh_notifications()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = ControlPanel()
    panel.show()
    sys.exit(app.exec())
