# Small always-on-top window with the agent character. Started by the response_start handler, then driven by files in state\:
# mode says what the agent does (thinking = orange, tool running = red); when alive is deleted it turns green and closes.
# alive holds the agent PID; the window also vanishes if that process dies.
# Usage: pythonw -m handlers.character_window   (from the project folder, so its imports are found)

# =========================================
# Imports and defines
# =========================================
import json
import sys

import psutil
from PyQt6.QtCore import QFileSystemWatcher, QLockFile, QPoint, Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QLabel

from handlers.common_functions import ALIVE_PATH, MODE_PATH, MODE_TOOL_RUNNING, PROJECT_DIR, STATE_DIR, load_config

LOCK_PATH = STATE_DIR / ".lock"
POSITION_PATH = STATE_DIR / "position.json"

# =========================================
# Classes and functions
# =========================================
class CharacterWindow(QLabel):
    """Frameless, see-through, always-on-top character that follows the files in state\\.
    Left drag moves it, right click closes it."""

    def __init__(self, pixmaps, done_display_seconds, polling_seconds):
        super().__init__()
        self.pixmaps = pixmaps
        self.agent_pid = None
        self.drag_offset = None
        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.setInterval(int(done_display_seconds * 1000))
        self.close_timer.timeout.connect(self.close_if_still_done)
        self.agent_check_timer = QTimer(self)
        self.agent_check_timer.setInterval(int(polling_seconds * 1000))
        self.agent_check_timer.timeout.connect(self.check_agent_alive)
        self.agent_check_timer.start()
        # The folder watch sees alive created or deleted, the file watch sees mode writes
        self.watcher = QFileSystemWatcher(self)
        self.watcher.addPath(str(STATE_DIR))
        self.watcher.directoryChanged.connect(self.update_state)
        self.watcher.fileChanged.connect(self.update_state)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(pixmaps["thinking"].size())
        self.update_state()

    def update_state(self):
        """Re-reads the state files and shows the matching character; green and closing once the alive file is gone."""
        if not ALIVE_PATH.exists():
            self.setPixmap(self.pixmaps["done"])
            if not self.close_timer.isActive():
                self.close_timer.start()
            return
        self.close_timer.stop()
        agent_pid = read_agent_pid()
        if agent_pid is not None:
            self.agent_pid = agent_pid
        if MODE_PATH.exists() and str(MODE_PATH) not in self.watcher.files():
            self.watcher.addPath(str(MODE_PATH))
        if read_mode() == MODE_TOOL_RUNNING:
            self.setPixmap(self.pixmaps["tool_running"])
        else:
            self.setPixmap(self.pixmaps["thinking"])

    def close_if_still_done(self):
        """Quits when the done time is over, unless a new prompt created the alive file again meanwhile."""
        if not ALIVE_PATH.exists():
            QApplication.quit()

    def check_agent_alive(self):
        """Closes the app when the watched agent process is gone; skipped when no PID is known (manual runs)."""
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

def character_window(cfg):
    """Shows the character and follows the state files until the response ends or the agent dies."""
    character_cfg = cfg["character"]
    image_paths = {
        "thinking": PROJECT_DIR / character_cfg["image_thinking"],
        "tool_running": PROJECT_DIR / character_cfg["image_tool_running"],
        "done": PROJECT_DIR / character_cfg["image_done"],
    }
    done_display_seconds = float(character_cfg["done_display_seconds"])
    polling_seconds = float(character_cfg["polling_seconds"])
    height = int(character_cfg["height"])
    margin = int(character_cfg["margin"])

    STATE_DIR.mkdir(parents = True, exist_ok = True)
    # Every prompt starts a window; only the first one gets the lock, the others exit and the running one follows the files
    lock = QLockFile(str(LOCK_PATH))
    if not lock.tryLock(0):
        return
    app = QApplication(sys.argv)
    pixmaps = create_character_pixmaps(image_paths, height)
    window = CharacterWindow(pixmaps, done_display_seconds, polling_seconds)
    # Every way of closing (done timer, agent died, right click) goes through quit, so the last place is always saved
    app.aboutToQuit.connect(lambda: save_position(window.pos()))
    window.move(get_start_position(window.width(), margin))
    window.show()
    app.exec()

def read_agent_pid():
    """Returns the agent PID written in the alive file, or None if it is missing or half written."""
    try:
        with open(ALIVE_PATH, encoding = "utf-8") as alive_file:
            return int(alive_file.read())
    except (OSError, ValueError):
        return None

def read_mode():
    """Returns the MODE_ number in the mode file, or None if it is missing or half written."""
    try:
        with open(MODE_PATH, encoding = "utf-8") as mode_file:
            return int(mode_file.read())
    except (OSError, ValueError):
        return None

def create_character_pixmaps(image_paths, height):
    """Loads the image of every character state (already see-through, made by scripts\\create_character_images.py) at the wanted height."""
    pixmaps = {}
    for state, image_path in image_paths.items():
        # Fast (nearest pixel) scaling keeps the pixel art sharp
        pixmaps[state] = QPixmap(str(image_path)).scaledToHeight(height, Qt.TransformationMode.FastTransformation)
    return pixmaps

def get_start_position(width, margin):
    """Returns the last dragged-to position if it is still on a screen, else the top right corner."""
    saved_position = read_saved_position()
    if saved_position is not None and QApplication.screenAt(saved_position) is not None:
        return saved_position
    screen_area = QApplication.primaryScreen().availableGeometry()
    x = screen_area.right() - width - margin
    y = screen_area.top() + margin
    return QPoint(x, y)

def read_saved_position():
    """Returns the position saved on the last close, or None if the file is missing or broken (e.g. edited by hand)."""
    try:
        with open(POSITION_PATH, encoding = "utf-8") as position_file:
            saved = json.load(position_file)
        return QPoint(int(saved["x"]), int(saved["y"]))
    except (OSError, ValueError, KeyError, TypeError):
        return None

def save_position(position):
    """Saves the window position on close, so the character comes back where the user left it."""
    POSITION_PATH.parent.mkdir(parents = True, exist_ok = True)
    with open(POSITION_PATH, "w", encoding = "utf-8") as position_file:
        json.dump({"x": position.x(), "y": position.y()}, position_file)

# =========================================
# Main
# =========================================
def main():
    cfg = load_config()
    character_window(cfg)

if __name__ == "__main__":
    main()
