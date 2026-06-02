#!/usr/bin/env python3
import sys
import os
import json
import re
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QHBoxLayout, QScrollArea, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt

CONFIG_PATH = os.path.expanduser("~/.config/project-spaces.json")
THEME_FILE  = os.path.expanduser("~/custom-scripts/Control-Panel/current_theme.css")

def get_control_panel_theme():
    """Parses current_theme.css to pull active Control Panel color variables."""
    # Robust fallbacks matching original Tokyonight styling bounds
    theme = {
        "bg": "#1d2021",
        "panel_bg": "#24283b",
        "border": "#414868",
        "accent": "#7aa2f7",
        "text": "#c0caf5",
        "text_dim": "#a9b1d6",
        "danger": "#f7768e",
        "danger_bg": "#382c36",
        "warning": "#e0af68"
    }
    
    if os.path.exists(THEME_FILE):
        try:
            with open(THEME_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Extract raw parameters cleanly from theme-widget output blocks
            bg_match = re.search(r"QWidget#MainWidget\s*\{\s*background-color:\s*([^;]+);", content)
            accent_match = re.search(r"border:\s*2px\s*solid\s*([^;]+);", content)
            text_match = re.search(r"QLabel\s*\{\s*color:\s*([^;]+);", content)
            hint_match = re.search(r"QLabel#DateLabel\s*\{\s*color:\s*([^;]+);", content)
            
            if bg_match:
                theme["bg"] = bg_match.group(1).strip()
            if accent_match:
                theme["accent"] = accent_match.group(1).strip()
            if text_match:
                theme["text"] = text_match.group(1).strip()
                theme["text_dim"] = text_match.group(1).strip()
            if hint_match:
                theme["border"] = hint_match.group(1).strip()
                
        except Exception:
            pass
            
    return theme

class WorkspaceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.editing_profile_name = None
        # Load the dynamic color profile prior to UI building loops
        self.colors = get_control_panel_theme()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(450, 560)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QWidget()
        self.container.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['bg']};
                border: 0px solid {self.colors['accent']};
                border-radius: 5px;
            }}
            QLabel {{
                color: {self.colors['text']};
                font-size: 15px;
                font-weight: bold;
                border: none;
                padding: 5px;
            }}
        """)
        self.container_layout = QVBoxLayout(self.container)
        
        title = QLabel("Workspace Profiles")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.container_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent; border: none;")
        self.list_layout = QVBoxLayout(scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.load_profiles()
        scroll.setWidget(scroll_content)
        self.container_layout.addWidget(scroll)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("+ New Workspace")
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['panel_bg']};
                color: {self.colors['accent']};
                border: 1px solid {self.colors['accent']};
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.colors['accent']};
                color: {self.colors['bg']};
            }}
        """)
        self.add_btn.clicked.connect(self.open_creator_for_new)
        btn_layout.addWidget(self.add_btn)
        
        self.container_layout.addLayout(btn_layout)
        self.main_layout.addWidget(self.container)

        self.creator = QWidget()
        self.creator.setVisible(False)
        self.creator.setStyleSheet(self.container.styleSheet())
        self.creator_layout = QVBoxLayout(self.creator)
        
        self.c_title = QLabel("Create Profile")
        self.c_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.creator_layout.addWidget(self.c_title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Workspace Name")
        self.style_input(self.name_input)
        self.creator_layout.addWidget(self.name_input)

        dir_row = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Project Directory Path")
        self.style_input(self.dir_input)
        dir_row.addWidget(self.dir_input)
        
        dir_btn = QPushButton("...")
        dir_btn.setFixedWidth(40)
        dir_btn.setStyleSheet(self.add_btn.styleSheet())
        dir_btn.clicked.connect(self.browse_directory)
        dir_row.addWidget(dir_btn)
        self.creator_layout.addLayout(dir_row)

        self.files_input = QLineEdit()
        self.files_input.setPlaceholderText("Files (comma separated)")
        self.style_input(self.files_input)
        self.creator_layout.addWidget(self.files_input)

        form_actions_layout = QHBoxLayout()
        form_actions_layout.setSpacing(8)

        self.save_btn = QPushButton("Save Workspace")
        self.save_btn.setStyleSheet(self.add_btn.styleSheet())
        self.save_btn.clicked.connect(self.save_profile)
        form_actions_layout.addWidget(self.save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['danger_bg']};
                color: {self.colors['danger']};
                border: 1px solid {self.colors['danger']};
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.colors['danger']};
                color: {self.colors['bg']};
            }}
        """)
        cancel_btn.clicked.connect(self.close_creator_panel)
        form_actions_layout.addWidget(cancel_btn)

        self.creator_layout.addLayout(form_actions_layout)
        self.main_layout.addWidget(self.creator)

    def style_input(self, widget):
        widget.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.colors['panel_bg']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 8px;
            }}
        """)

    def open_creator_for_new(self):
        self.editing_profile_name = None
        self.c_title.setText("Create Profile")
        self.name_input.setEnabled(True)
        self.name_input.clear()
        self.dir_input.clear()
        self.files_input.clear()
        
        if not self.creator.isVisible():
            self.setFixedSize(900, 560)
            self.creator.setVisible(True)

    def open_creator_for_edit(self, name, data):
        self.editing_profile_name = name
        self.c_title.setText(f"Edit Profile: {name}")
        self.name_input.setText(name)
        self.name_input.setEnabled(False)
        self.dir_input.setText(data.get("directory", ""))
        
        files_list = [t["file"] for t in data.get("targets", [])]
        self.files_input.setText(", ".join(files_list))
        
        if not self.creator.isVisible():
            self.setFixedSize(900, 560)
            self.creator.setVisible(True)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if directory:
            self.dir_input.setText(directory)

    def load_profiles(self):
        # ... (Preserve original clean layout wipe and JSON reading logic exactly) ...
        if not os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "w") as f:
                json.dump({}, f)

        with open(CONFIG_PATH, "r") as f:
            profiles = json.load(f)

        for name, data in profiles.items():
            row = QHBoxLayout()
            row.setSpacing(4)
            
            btn = QPushButton(name)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.colors['panel_bg']};
                    color: {self.colors['text_dim']};
                    border: 1px solid {self.colors['border']};
                    border-radius: 6px;
                    padding: 12px;
                    font-size: 13px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['border']};
                    color: {self.colors['accent']};
                    border: 1px solid {self.colors['accent']};
                }}
            """)
            btn.clicked.connect(lambda checked, n=name, d=data: self.launch_space(n, d))
            row.addWidget(btn, stretch=4)

            edit_btn = QPushButton("✎")
            edit_btn.setFixedWidth(36)
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.colors['panel_bg']};
                    color: {self.colors['warning']};
                    border: 1px solid {self.colors['border']};
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['warning']};
                    color: {self.colors['bg']};
                    border: 1px solid {self.colors['warning']};
                }}
            """)
            edit_btn.clicked.connect(lambda checked, n=name, d=data: self.open_creator_for_edit(n, d))
            row.addWidget(edit_btn)

            del_btn = QPushButton("🗙")
            del_btn.setFixedWidth(36)
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.colors['panel_bg']};
                    color: {self.colors['danger']};
                    border: 1px solid {self.colors['border']};
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['danger']};
                    color: {self.colors['bg']};
                    border: 1px solid {self.colors['danger']};
                }}
            """)
            del_btn.clicked.connect(lambda checked, n=name: self.delete_profile(n))
            row.addWidget(del_btn)

            self.list_layout.addLayout(row)

    def delete_profile(self, name):
        with open(CONFIG_PATH, "r") as f:
            profiles = json.load(f)
            
        if name in profiles:
            del profiles[name]
            
        with open(CONFIG_PATH, "w") as f:
            json.dump(profiles, f, indent=4)
            
        if self.editing_profile_name == name:
            self.creator.setVisible(False)
            self.setFixedSize(450, 560)
            
        self.load_profiles()

    def close_creator_panel(self):
        self.name_input.clear()
        self.dir_input.clear()
        self.files_input.clear()
        self.editing_profile_name = None
        
        self.creator.setVisible(False)
        self.setFixedSize(450, 560)

    def save_profile(self):
        name = self.name_input.text().strip()
        directory = self.dir_input.text().strip()
        files_raw = self.files_input.text().split(",")

        if not name or not directory:
            return

        targets = []
        for f in files_raw:
            f_clean = f.strip()
            if f_clean:
                ext = os.path.splitext(f_clean)[1].lower()
                t_type = "editor" if ext in [".py", ".lua", ".conf", ".sh", ".txt", ".json", ".toml", ".lock", ".md", ".bash", ".fish", ".zsh", ".yaml", ".yml", ".ini", ".theme", ".rules", ".desktop", ".service", ".awk", ".sed"] else "manager"
                targets.append({"type": t_type, "file": f_clean})

        if not targets:
            targets.append({"type": "manager", "file": "yazi"})

        with open(CONFIG_PATH, "r") as f:
            profiles = json.load(f)

        profiles[name] = {
            "directory": directory,
            "targets": targets
        }

        with open(CONFIG_PATH, "w") as f:
            json.dump(profiles, f, indent=4)

        self.name_input.clear()
        self.dir_input.clear()
        self.files_input.clear()
        
        self.creator.setVisible(False)
        self.setFixedSize(450, 560)
        self.load_profiles()

    def launch_space(self, name, data):
        self.hide()
        QApplication.processEvents()
        
        project_dir = os.path.expanduser(data["directory"])
        socket_name = name.replace(" ", "_")
        socket_path = f"/tmp/kitty-{socket_name}.sock"
        
        if os.path.exists(socket_path):
            try:
                os.remove(socket_path)
            except OSError:
                pass

        env_config = os.environ.copy()
        env_config["KITTY_ALLOW_REMOTE_CONTROL"] = "yes"

        subprocess.Popen([
            "kitty",
            "--listen-on", f"unix:{socket_path}",
            "--directory", project_dir,
            "--title", name
        ], env=env_config, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        import time
        socket_ready = False
        for _ in range(40):
            if os.path.exists(socket_path):
                socket_ready = True
                break
            time.sleep(0.1)

        if not socket_ready:
            print(f"Error: Timing out waiting for socket allocation at {socket_path}")
            return

        time.sleep(0.2)
        
        first = True
        for target in data["targets"]:
            if target["type"] == "editor":
                cmd_args = ["/usr/bin/micro", target["file"]]
            else:
                cmd_args = ["/usr/bin/yazi"]
            
            if first:
                full_cmd = " ".join(cmd_args)
                subprocess.run(["kitty", "@", "--to", f"unix:{socket_path}", "send-text", f"clear && {full_cmd}\n"])
                subprocess.run(["kitty", "@", "--to", f"unix:{socket_path}", "set-tab-title", target["file"]])
                first = False
            else:
                subprocess.run([
                    "kitty", "@", "--to", f"unix:{socket_path}",
                    "launch", "--type=tab", "--cwd", project_dir,
                    "--tab-title", target["file"]
                ] + cmd_args)
        
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = WorkspaceWidget()
    widget.show()
    sys.exit(app.exec())
