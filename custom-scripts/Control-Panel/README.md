## Control-Panel

[v0.1.0]

A unified, Waybar-free dashboard built with PyQt6 for Hyprland. It integrates workspace management, a taskbar, system monitoring, and a notification centre into a single process.

**Features**
- **Workspace Switcher**: Real-time Hyprland workspace tracking and switching.
- **Taskbar**: Direct window focus and task management via hyprctl.
- **App Launcher**: Robust application discovery using Gio.
- **System Stats**: Live CPU usage, temperature, and RAM (True Used memory).
- **Notification Centre*: Persistent history log with individual entry deletion and "Clear All" functionality.

### IMPORTANT: Custom Scripts Dependency

The **Tools Section** in this panel is hardcoded to launch specific custom scripts. If you are not using my personal custom made scripts, these buttons will not function without modification.

**The tools currently reference**:
- **RTM**: Task Manager (https://github.com/Rakosn1cek/RTM)
- **Budget-Buddy**: Financial Tracker (https://github.com/Rakosn1cek/Budget-Buddy)
- **Mirec**: Screen Recorder (https://github.com/Rakosn1cek/mirec)
- **Wifi/BT**: Custom TUI wrappers for nmcli and bluetoothctl. Both to be found in custom-scripts.
- **Clipbox**: Clipboard manager widget found in custom-scripts/Python-Widgets/clipbox-widget2.py
- **Aliases**: Custom scritpt to show all aliases included in ~/.zshrc and ~/.zsh.aliases. Script is in the custom-scripts/Show-Aliases.
- **Keybinds**: Custom script to show keybinds from ~/.config/hypr/configs/keybinds.conf found in custom-scripts/Shell-Widgets.

You can find these scripts in my dotfiles or remap the tools dictionary in the init_ui method to your preferred binaries.

Here is the Tools section that you can modify to fit your own purpose.

```zsh
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
            btn.clicked.connect(lambda chk, c=cmd: self.launch_app_manual(c))
            g_lay.addWidget(btn, i // 2, i % 2)
            self.tool_btns[tid] = btn
        left.addWidget(g_sec)
```
### Warning

> *NOTE: I will continue to work on the Control Panel and all updates will be posted on Discord. [You can join here!!](https://discord.gg/Yqxpzs8JHJ) and ask questions or request features.*


