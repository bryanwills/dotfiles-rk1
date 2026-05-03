import sys
import os
import psutil
import datetime
import subprocess
import glob
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QGridLayout, QProgressBar, 
                             QPushButton, QFrame, QSlider, QListWidget, QListWidgetItem)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon, QFontDatabase

# Path to battery info
BAT = "/sys/class/power_supply/BAT0"

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(700, 680)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setObjectName("MainWidget")
        self.setWindowTitle("control-panel.py")
        self.home = os.path.expanduser("~")
        
        # Load custom Nerd Font if available
        font_path = os.path.expanduser("~/.local/share/fonts/OpenDyslexicMNerdFontMono-Regular.otf")
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            print(f"DEBUG: Font families loaded: {QFontDatabase.applicationFontFamilies(font_id)}")
            self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            self.font_family = "JetBrains Mono"

        # Verified stylesheet using standard hyphenated properties only
        self.setStyleSheet(f"""
            QWidget#MainWidget {{ background-color: #000000; border: 1px solid #333333; }}
            QFrame#Section {{ border: 1px solid #222222; border-radius: 4px; background-color: #050505; }}
            QLabel {{ color: #ffffff; font-family: 'JetBrains Mono'; font-size: 11px; }}
            QLineEdit {{ background-color: #111111; border: 1px solid #333333; color: #ffffff; padding: 5px; border-radius: 4px; }}
            QListWidget {{ background-color: #000000; border: 1px solid #222222; color: #ffffff; outline: none; border-radius: 4px; }}
            QListWidget::item {{ padding: 8px; border-bottom: 1px solid #111111; }}
            QListWidget::item:selected {{ background-color: #111111; color: #52fa69; }}
            QProgressBar {{ border: none; background-color: #111111; height: 8px; border-radius: 4px; color: transparent; }}
            QProgressBar::chunk {{ background-color: #52fa69; border-radius: 4px; }}
            QScrollBar:vertical {{ border: none; background: #000000; width: 8px; margin: 0px; }}
            QScrollBar::handle:vertical {{ background: #333333; min-height: 20px; border-radius: 4px; }}
            QScrollBar::handle:vertical:hover {{ background: #52fa69; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ border: none; background: none; height: 0px; }}
            QSlider::groove:horizontal {{ border: none; height: 2px; background: #333333; }}
            QSlider::handle:horizontal {{ background: #52fa69; border: 1px solid #ffffff; width: 4px; height: 14px; margin: -7px 0; }}
            QPushButton {{ background-color: #111111; border: 1px solid #222222; color: #ffffff; padding: 8px; font-family: 'JetBrains Mono'; border-radius: 4px; }}
            QPushButton:hover {{ background-color: #222222; border-color: #52fa69; }}
            QPushButton#ActiveProfile {{ background-color: #52fa69; color: #000000; font-weight: bold; border: 1px solid #ffffff; }}
        """)

        self.apps_list = self.get_installed_apps()
        self.init_ui()
        self.sync_hardware_sliders()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_live_data)
        self.timer.start(1500)

    def get_installed_apps(self):
        apps = []
        for file in glob.glob('/usr/share/applications/*.desktop'):
            try:
                with open(file, 'r') as f:
                    name, cmd, icon = "", "", "application-x-executable"
                    for line in f:
                        if line.startswith('Name='): name = line.split('=')[1].strip()
                        if line.startswith('Exec='): cmd = line.split('=')[1].split('%')[0].strip()
                        if line.startswith('Icon='): icon = line.split('=')[1].strip()
                    if name and cmd: apps.append({'name': name, 'exec': cmd, 'icon': icon})
            except: continue
        return sorted(apps, key=lambda x: x['name'].lower())

    def create_section(self):
        frame = QFrame()
        frame.setObjectName("Section")
        return frame

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header
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

        body = QHBoxLayout()
        
        # --- LEFT COLUMN ---
        left = QVBoxLayout()
        
        # Search
        s_sec = self.create_section()
        s_lay = QVBoxLayout(s_sec)
        s_lay.setContentsMargins(10, 10, 10, 5)
        s_lay.setSpacing(5) # Reduce space between title and bar

        # Search
        s_sec = self.create_section()
        s_lay = QVBoxLayout(s_sec)
        s_lay.setContentsMargins(15, 12, 15, 12)
        s_lay.setSpacing(8)  # Tight spacing between title and bar

        # Add Title
        search_title = QLabel("󰀻  APP LAUNCHER")
        search_title.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
        s_lay.addWidget(search_title)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")
        self.search.textChanged.connect(self.filter_apps)
        s_lay.addWidget(self.search)

        self.results = QListWidget()
        self.results.setFixedHeight(110)
        self.results.hide()
        self.results.itemDoubleClicked.connect(self.launch_app)
        s_lay.addWidget(self.results)

        # This pushes everything above it to the top
        s_lay.addStretch()
        
        left.addWidget(s_sec)

        # Tools Grid
        g_sec = self.create_section()
        g_lay = QGridLayout(g_sec)
        tools = {
            "  ": f"kitty --class rtm -e python3 {self.home}/arch-projects/RTM/rtm.py", 
            " 󱀇 ": f"kitty --class budget-buddy -e python3 {self.home}/arch-projects/Budget-Buddy/budget-buddy.py",
            "  ": f"kitty --title Mirec -e {self.home}/arch-projects/MIREC/mirec",
            " 󰖩 ": f"kitty --class floating_wifi -e {self.home}/custom-scripts/wifi/wwifi",
            "  ": f"kitty --class bt-menu -e {self.home}/custom-scripts/bluetooth/bt",
            " 󰌌 ": f"bash {self.home}/custom-scripts/keybinds.sh",
            " 󰬈 ": f"bash {self.home}/custom-scripts/Show-Aliases/show-aliases.sh",
            " 󱫉 ": f"python3 {self.home}/custom-scripts/clipbox-widget2.py"
        }
        for i, (name, cmd) in enumerate(tools.items()):
            btn = QPushButton(name)
            btn.setStyleSheet("font-size: 16px; padding: 10px;")
            btn.clicked.connect(lambda chk, c=cmd: self.launch_app_manual(c))
            g_lay.addWidget(btn, i // 2, i % 2)
        left.addWidget(g_sec)

        # Power Acts
        p_sec = self.create_section()
        p_lay = QGridLayout(p_sec)
        p_acts = {"󰐥": "shutdown now", "󰑐": "reboot", "󰤄": "systemctl suspend", "󰈆": "hyprctl dispatch exit", "󰖔": f"bash {self.home}/.local/bin/nightlight"}
        for i, (icon, cmd) in enumerate(p_acts.items()):
            pb = QPushButton(icon)
            pb.setStyleSheet("font-size: 16px; padding: 10px;")
            pb.clicked.connect(lambda chk, c=cmd: self.run_cmd(c))
            p_lay.addWidget(pb, i // 3, i % 3)
        left.addWidget(p_sec)
        
        body.addLayout(left, 1)

        # --- RIGHT COLUMN ---
        right = QVBoxLayout()
        
        # Detailed Resources & Battery
        r_sec = self.create_section()
        r_lay = QVBoxLayout(r_sec)
        r_lay.addWidget(QLabel("SYSTEM & BATTERY"))
        self.cpu = QProgressBar()
        self.cpu.setFixedHeight(9)
        self.ram = QProgressBar()
        self.ram.setFixedHeight(9)
        r_lay.addWidget(QLabel("CPU Usage"))
        r_lay.addWidget(self.cpu)
        r_lay.addWidget(QLabel("RAM Usage"))
        r_lay.addWidget(self.ram)
        
        self.bat_stats = QLabel("Checking battery...")
        self.bat_stats.setStyleSheet("color: #888888; font-size: 12px;")
        self.bat_stats.setWordWrap(True)
        r_lay.addWidget(self.bat_stats)
        right.addWidget(r_sec)

        # Volume & Brightness
        t_sec = self.create_section()
        t_lay = QVBoxLayout(t_sec)
        t_lay.addWidget(QLabel("VOLUME"))
        self.vol = QSlider(Qt.Orientation.Horizontal)
        self.vol.setRange(0, 100)
        self.vol.valueChanged.connect(self.set_volume)
        t_lay.addWidget(self.vol)
        t_lay.addWidget(QLabel("BRIGHTNESS"))
        self.bright = QSlider(Qt.Orientation.Horizontal)
        self.bright.setRange(1, 100)
        self.bright.valueChanged.connect(self.set_brightness)
        t_lay.addWidget(self.bright)
        right.addWidget(t_sec)

        # CPU Power Profiles Section
        cp_sec = self.create_section()
        cp_lay = QVBoxLayout(cp_sec)
        cp_lay.addWidget(QLabel("CPU POWER PROFILE"))
        self.prof_btns = {}
        
        profiles = [
            ("⚡ Performance", "performance"), 
            ("󰌪  Power Saver", "powersave")
        ]
        
        for label, gov_val in profiles:
            btn = QPushButton(label)
            btn.clicked.connect(lambda chk, g=gov_val: self.set_governor(g))
            cp_lay.addWidget(btn)
            self.prof_btns[gov_val] = btn
            
        right.addWidget(cp_sec)
        body.addLayout(right, 1)

        # CRITICAL FIX: Add the body layout back to the main layout
        main_layout.addLayout(body)

    def get_battery_info(self):
        def read_sys(file):
            try:
                with open(f"{BAT}/{file}", 'r') as f:
                    return int(f.read().strip())
            except:
                return 0

        cap = read_sys("capacity")
        pwr_mw = read_sys("power_now")
        pwr = pwr_mw / 1_000_000
        vlt = read_sys("voltage_now") / 1_000_000
        
        full = read_sys("energy_full") or read_sys("charge_full")
        now = read_sys("energy_now") or read_sys("charge_now")
        design = read_sys("energy_full_design") or read_sys("charge_full_design")
        health = int(100 * full / design) if design > 0 else 0

        try:
            status = open(f"{BAT}/status").read().strip()
        except:
            status = "Unknown"
        
        # Calculate time remaining
        time_info = "Calculating..."
        if pwr_mw > 0:
            if status == "Discharging":
                # Remaining hours = Current energy / Power draw
                hours = now / pwr_mw
                time_info = f"{int(hours)}h {int((hours % 1) * 60)}m left"
            elif status == "Charging":
                # Time to full = (Full capacity - Current energy) / Power draw
                hours = (full - now) / pwr_mw
                time_info = f"{int(hours)}h {int((hours % 1) * 60)}m to full"
        elif status == "Full":
            time_info = "Battery Full"

        icon = "󱐋" if status == "Charging" else "󰁹"

        return f"{icon} {cap}% | 󱐋 {pwr:.1f}W | 󱔣  {vlt:.1f}V | 󰑐 Health: {health}% | 󱎫 {time_info}"

    def set_governor(self, gov):
        try:
            subprocess.Popen(['pkexec', '/usr/local/bin/set-governor.sh', gov])
        except Exception as e:
            print(f"Governor error: {e}")

    def update_live_data(self):
        now = datetime.datetime.now()
        self.clock_lbl.setText(now.strftime("%H:%M:%S"))
        self.date_lbl.setText(now.strftime("%A, %d %B %Y").upper())
        self.cpu.setValue(int(psutil.cpu_percent()))
        self.ram.setValue(int(psutil.virtual_memory().percent))
        self.bat_stats.setText(self.get_battery_info())
        self.highlight_active_profile()

    def sync_hardware_sliders(self):
        try:
            vol_out = subprocess.check_output("wpctl get-volume @DEFAULT_AUDIO_SINK@", shell=True).decode()
            self.vol.setValue(int(float(vol_out.split(":")[1].strip()) * 100))
            bright_out = subprocess.check_output("brightnessctl g", shell=True).decode()
            bright_max = subprocess.check_output("brightnessctl m", shell=True).decode()
            self.bright.setValue(int((int(bright_out) / int(bright_max)) * 100))
        except: pass

    def highlight_active_profile(self):
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor", "r") as f:
                current_gov = f.read().strip()
            
            for gov_key, btn in self.prof_btns.items():
                if gov_key == current_gov:
                    btn.setObjectName("ActiveProfile")
                else:
                    btn.setObjectName("")
                btn.style().unpolish(btn)
                btn.style().polish(btn)
        except: pass
    
    def set_volume(self, val):
        subprocess.run(f"wpctl set-volume @DEFAULT_AUDIO_SINK@ {val/100:.2f}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def set_brightness(self, val):
        subprocess.run(f"brightnessctl set {val}%", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def filter_apps(self, text):
        self.results.clear()
        if not text: self.results.hide(); return
        matches = [a for a in self.apps_list if text.lower() in a['name'].lower()][:5]
        for a in matches:
            item = QListWidgetItem(QIcon.fromTheme(a['icon']), a['name'])
            item.setData(Qt.ItemDataRole.UserRole, a['exec'])
            self.results.addItem(item)
        self.results.show() if matches else self.results.hide()

    def launch_app(self, item):
        self.run_cmd(item.data(Qt.ItemDataRole.UserRole))
        self.close()

    def launch_app_manual(self, cmd):
        self.run_cmd(cmd)
        self.close()

    def run_cmd(self, cmd):
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cleanup_and_exit()

    def cleanup_and_exit(self):
        self.timer.stop() # Stop the background hardware polling
        QApplication.quit()
        sys.exit(0) # Force the terminal process to end

if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = ControlPanel()
    panel.show()
    sys.exit(app.exec())
