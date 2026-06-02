#!/usr/bin/env python3
import sys
import os
import json
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QHBoxLayout, QScrollArea, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt

CONFIG_PATH = os.path.expanduser("~/.config/project-spaces.json")

class WorkspaceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.editing_profile_name = None
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(450, 560)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: #1d2021;
                border: 0px solid #7aa2f7;
                border-radius: 5px;
            }
            QLabel {
                color: #c0caf5;
                font-size: 15px;
                font-weight: bold;
                border: none;
                padding: 5px;
            }
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
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2e3c56;
                color: #7aa2f7;
                border: 1px solid #7aa2f7;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7aa2f7;
                color: #1a1a24;
            }
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

        self.save_btn = QPushButton("Save Workspace")
        self.save_btn.setStyleSheet(self.add_btn.styleSheet())
        self.save_btn.clicked.connect(self.save_profile)
        self.creator_layout.addWidget(self.save_btn)
        
        self.main_layout.addWidget(self.creator)

    def style_input(self, widget):
        widget.setStyleSheet("""
            QLineEdit {
                background-color: #24283b;
                color: #c0caf5;
                border: 1px solid #414868;
                border-radius: 6px;
                padding: 8px;
            }
        """)

    def open_creator_for_new(self):
        self.editing_profile_name = None
        self.c_title.setText("Create Profile")
        self.name_input.setEnabled(True)
        self.name_input.clear()
        self.dir_input.clear()
        self.files_input.clear()
        
        if not self.creator.isVisible():
            self.setFixedSize(680, 520)
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
            self.setFixedSize(680, 520)
            self.creator.setVisible(True)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if directory:
            self.dir_input.setText(directory)

    def load_profiles(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Clean out nested button row layouts recursively
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                item.layout().deleteLater()

        if not os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "w") as f:
                json.dump({}, f)

        with open(CONFIG_PATH, "r") as f:
            profiles = json.load(f)

        for name, data in profiles.items():
            row = QHBoxLayout()
            row.setSpacing(4)
            
            # Main launch button
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #24283b;
                    color: #a9b1d6;
                    border: 1px solid #414868;
                    border-radius: 6px;
                    padding: 12px;
                    font-size: 13px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #414868;
                    color: #7aa2f7;
                    border: 1px solid #7aa2f7;
                }
            """)
            btn.clicked.connect(lambda checked, n=name, d=data: self.launch_space(n, d))
            row.addWidget(btn, stretch=4)

            # Quick action button layout configuration
            edit_btn = QPushButton("✎")
            edit_btn.setFixedWidth(36)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #24283b;
                    color: #e0af68;
                    border: 1px solid #414868;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e0af68;
                    color: #1a1a24;
                    border: 1px solid #e0af68;
                }
            """)
            edit_btn.clicked.connect(lambda checked, n=name, d=data: self.open_creator_for_edit(n, d))
            row.addWidget(edit_btn)

            del_btn = QPushButton("🗙")
            del_btn.setFixedWidth(36)
            del_btn.setStyleSheet("""
                QPushButton {
                    background-color: #24283b;
                    color: #f7768e;
                    border: 1px solid #414868;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #f7768e;
                    color: #1a1a24;
                    border: 1px solid #f7768e;
                }
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
            
        # Hide the editing panel if the profile being modified was deleted
        if self.editing_profile_name == name:
            self.creator.setVisible(False)
            self.setFixedSize(340, 520)
            
        self.load_profiles()

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
        self.setFixedSize(340, 520)
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

        # Capture the current system environment variables safely
        env_config = os.environ.copy()
        # Force Kitty to accept remote commands for this specific instance
        env_config["KITTY_ALLOW_REMOTE_CONTROL"] = "yes"

        # Spawn the isolated terminal boundary without breaking on invalid flags
        subprocess.Popen([
            "kitty",
            "--listen-on", f"unix:{socket_path}",
            "--directory", project_dir,
            "--title", name
        ], env=env_config, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Dynamic connection check: wait up to 4 seconds for the socket file to become available
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

        # Give the window server an extra moment to bind operational parameters
        time.sleep(0.2)
        
        first = True
        for target in data["targets"]:
            if target["type"] == "editor":
                cmd_args = ["/usr/bin/micro", target["file"]]
            else:
                cmd_args = ["/usr/bin/yazi"]
            
            if first:
                # Dispatch the command to the default shell layer spawned on startup
                full_cmd = " ".join(cmd_args)
                subprocess.run(["kitty", "@", "--to", f"unix:{socket_path}", "send-text", f"clear && {full_cmd}\n"])
                subprocess.run(["kitty", "@", "--to", f"unix:{socket_path}", "set-tab-title", target["file"]])
                first = False
            else:
                # Open subsequent targets natively inside fresh workspace tabs
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
