# Small always-on-top window with the agent character. Started by the response_start handler, then driven by
# short commands on a localhost port: start <agent_pid> (orange), tool_start (red), tool_end (orange), end (green, then close).
# It also vanishes by itself if the agent process dies (e.g. its terminal is closed mid-response).
# Usage: pythonw character_window.py [--agent-pid PID]

# =========================================
# Imports and defines
# =========================================
import argparse
import json
import sys

import psutil
from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtGui import QColor, QImage, QPixmap
from PyQt6.QtNetwork import QHostAddress, QTcpServer
from PyQt6.QtWidgets import QApplication, QLabel

from lib.common_functions import PROJECT_DIR, load_config

BACKGROUND_THRESHOLD = 235

# =========================================
# Classes and functions
# =========================================
class CharacterWindow(QLabel):
    """Frameless, see-through, always-on-top character that changes color with the agent's state.
    Left drag moves it, right click closes it."""

    def __init__(self, pixmaps, done_seconds, agent_check_seconds, agent_pid):
        super().__init__()
        self.pixmaps = pixmaps
        self.agent_pid = agent_pid
        self.drag_offset = None
        self.running_tools = 0
        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.setInterval(int(done_seconds * 1000))
        self.close_timer.timeout.connect(QApplication.quit)
        self.agent_check_timer = QTimer(self)
        self.agent_check_timer.setInterval(int(agent_check_seconds * 1000))
        self.agent_check_timer.timeout.connect(self.check_agent_alive)
        self.agent_check_timer.start()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setPixmap(pixmaps["thinking"])
        self.resize(pixmaps["thinking"].size())

    def apply_command(self, command):
        """Updates the character for one command. Counts running tools, so parallel commands keep it red until all finish."""
        words = command.split()
        command = words[0] if words else ""
        if command == "start":
            self.close_timer.stop()
            self.running_tools = 0
            # A new prompt may come from another agent session, so watch the one that sent it
            if len(words) > 1:
                self.agent_pid = int(words[1])
        elif command == "tool_start":
            self.running_tools += 1
        elif command == "tool_end":
            self.running_tools = max(self.running_tools - 1, 0)
        elif command == "end":
            self.running_tools = 0
            self.setPixmap(self.pixmaps["done"])
            self.close_timer.start()
            return
        if self.running_tools > 0:
            self.setPixmap(self.pixmaps["tool_running"])
        else:
            self.setPixmap(self.pixmaps["thinking"])

    def check_agent_alive(self):
        """Closes the app when the watched agent process is gone; skipped when no PID was given (manual runs)."""
        if self.agent_pid is not None and not psutil.pid_exists(self.agent_pid):
            QApplication.quit()

    def mousePressEvent(self, event):
        """Starts a drag on left click, closes the app on right click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            QApplication.quit()

    def mouseMoveEvent(self, event):
        """Moves the window with the mouse while dragging."""
        if self.drag_offset is not None:
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event):
        """Ends the drag."""
        self.drag_offset = None

def character_window(cfg, agent_pid):
    """Shows the character and follows the commands sent by the hook handlers until the response ends or the agent dies."""
    character_cfg = cfg["character"]
    image_paths = {
        "thinking": PROJECT_DIR / character_cfg["image_thinking"],
        "tool_running": PROJECT_DIR / character_cfg["image_tool_running"],
        "done": PROJECT_DIR / character_cfg["image_done"],
    }
    done_seconds = float(character_cfg["done_seconds"])
    agent_check_seconds = float(character_cfg["agent_check_seconds"])
    height = int(character_cfg["height"])
    margin = int(character_cfg["margin"])
    port = int(character_cfg["port"])
    position_path = PROJECT_DIR / character_cfg["position_file"]

    app = QApplication(sys.argv)
    command_server = create_command_server(app, port)
    if command_server is None:
        return
    pixmaps = create_character_pixmaps(image_paths, height)
    window = CharacterWindow(pixmaps, done_seconds, agent_check_seconds, agent_pid)
    command_server.newConnection.connect(lambda: window.apply_command(read_command(command_server)))
    # Every way of closing (done timer, agent died, right click) goes through quit, so the last place is always saved
    app.aboutToQuit.connect(lambda: save_position(position_path, window.pos()))
    window.move(get_start_position(position_path, window.width(), window.height(), margin))
    window.show()
    app.exec()

def create_command_server(app, port):
    """Listens for handler commands on a localhost port. Returns None if a window is already running there."""
    command_server = QTcpServer(app)
    if not command_server.listen(QHostAddress.SpecialAddress.LocalHost, port):
        return None
    return command_server

def read_command(command_server):
    """Reads the one-word command from a new handler connection."""
    connection = command_server.nextPendingConnection()
    connection.waitForReadyRead(500)
    command = bytes(connection.readAll()).decode("utf-8").strip()
    connection.close()
    return command

def create_character_pixmaps(image_paths, height):
    """Builds a scaled, see-through pixmap for every character state."""
    pixmaps = {}
    for state, image_path in image_paths.items():
        pixmaps[state] = create_character_pixmap(image_path, height)
    return pixmaps

def create_character_pixmap(image_path, height):
    """Scales the image to the wanted height and makes its light background transparent."""
    image = QImage(str(image_path))
    width = round(image.width() * height / image.height())
    # Fast (nearest pixel) scaling keeps the pixel art sharp and the background a clean single color
    image = image.scaled(width, height, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)
    image = image.convertToFormat(QImage.Format.Format_ARGB32)
    transparent = QColor(0, 0, 0, 0)
    for y in range(image.height()):
        for x in range(image.width()):
            color = image.pixelColor(x, y)
            if color.red() > BACKGROUND_THRESHOLD and color.green() > BACKGROUND_THRESHOLD and color.blue() > BACKGROUND_THRESHOLD:
                image.setPixelColor(x, y, transparent)
    return QPixmap.fromImage(image)

def get_start_position(position_path, width, height, margin):
    """Returns the last dragged-to position if it is still on a screen, else the bottom right corner."""
    if position_path.exists():
        with open(position_path, encoding = "utf-8") as position_file:
            saved = json.load(position_file)
        position = QPoint(saved["x"], saved["y"])
        if QApplication.screenAt(position) is not None:
            return position
    screen_area = QApplication.primaryScreen().availableGeometry()
    x = screen_area.right() - width - margin
    y = screen_area.bottom() - height - margin
    return QPoint(x, y)

def save_position(position_path, position):
    """Saves the window position on close, so the character comes back where the user left it."""
    position_path.parent.mkdir(parents = True, exist_ok = True)
    with open(position_path, "w", encoding = "utf-8") as position_file:
        json.dump({"x": position.x(), "y": position.y()}, position_file)

# =========================================
# Main
# =========================================
def main():
    parser = argparse.ArgumentParser(description = "Show the agent character window.")
    parser.add_argument("--agent-pid", type = int, default = None, help = "agent process to watch; the window closes when it dies")
    args = parser.parse_args()
    cfg = load_config()
    character_window(cfg, args.agent_pid)

if __name__ == "__main__":
    main()
