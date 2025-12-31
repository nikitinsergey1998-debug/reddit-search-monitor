import sys
import json
import webbrowser
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import quote_plus

import requests
import feedparser
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QLabel, QComboBox, QHeaderView, QSpinBox,
    QTextEdit
)
from PyQt6.QtCore import QTimer

# ================= GLOBAL ERROR HANDLER =================
def global_exception_hook(exctype, value, tb):
    print("\n===== UNCAUGHT EXCEPTION =====")
    traceback.print_exception(exctype, value, tb)
    print("===== END EXCEPTION =====\n")

sys.excepthook = global_exception_hook

# ================= PATHS =================
BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "monitor_config.json"

# ================= HTTP =================
HEADERS = {
    "User-Agent": "Mozilla/5.0 reddit-monitor-no-api/2.0"
}

def safe_fetch_json(url, params=None):
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception:
        traceback.print_exc()
        return None

# ================= CONFIG =================
def load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            traceback.print_exc()
    return {}

def save_config(data: dict):
    CONFIG_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

# ================= APP =================
class RedditApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reddit Search + Monitor")
        self.resize(1150, 700)

        self.config = load_config()
        self.seen_ids = set()

        self.tabs = QTabWidget()
        self.init_search_tab()
        self.init_monitor_tab()
        self.init_blacklist_tab()

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run_monitor)

        self.load_settings()

    # ---------- BLACKLIST LOGIC ----------
    def is_blacklisted_post(self, post: dict):
        title = post.get("title", "")
        selftext = post.get("selftext", "")
        url = post.get("url", "")
        flair = post.get("link_flair_text", "")

        full_text = f"{title} {selftext} {url} {flair}".lower()

        base_blacklist = ("question", "вопрос", "discussion", "humor")
        user_blacklist = self.config.get("blacklist_words", [])

        if full_text.startswith("?"):
            return True

        for w in base_blacklist:
            if w in full_text:
                return True

        for w in user_blacklist:
            if w and w.lower() in full_text:
                return True

        return False

    # ---------- SEARCH TAB ----------
    def init_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        bar1 = QHBoxLayout()
        self.q_search = QLineEdit()
        self.q_search.setPlaceholderText("Ключевые слова")

        self.q_sub = QLineEdit()
        self.q_sub.setPlaceholderText("Сабреддиты через запятую")

        self.q_sub_limit = QSpinBox()
        self.q_sub_limit.setRange(1, 500)
        self.q_sub_limit.setValue(10)

        bar1.addWidget(self.q_search)
        bar1.addWidget(self.q_sub)
        bar1.addWidget(QLabel("Макс сабов:"))
        bar1.addWidget(self.q_sub_limit)

        bar2 = QHBoxLayout()
        self.time_value = QSpinBox()
        self.time_value.setRange(1, 1000)
        self.time_value.setValue(1)

        self.time_unit = QComboBox()
        self.time_unit.addItems(["hour", "day", "week", "month"])

        btn = QPushButton("Поиск")
        btn.clicked.connect(self.run_search)

        bar2.addWidget(QLabel("Период:"))
        bar2.addWidget(self.time_value)
        bar2.addWidget(self.time_unit)
        bar2.addStretch()
        bar2.addWidget(btn)

        self.search_table = self.make_table()

        layout.addLayout(bar1)
        layout.addLayout(bar2)
        layout.addWidget(self.search_table)
        self.tabs.addTab(tab, "Поиск")

    def run_search(self):
        self.search_table.setRowCount(0)

        query = self.q_search.text().strip()
        subs = [s.strip() for s in self.q_sub.text().split(",") if s.strip()]
        subs = list(dict.fromkeys(subs))[: self.q_sub_limit.value()]

        delta = {
            "hour": timedelta(hours=self.time_value.value()),
            "day": timedelta(days=self.time_value.value()),
            "week": timedelta(weeks=self.time_value.value()),
            "month": timedelta(days=30 * self.time_value.value())
        }[self.time_unit.currentText()]

        time_limit = datetime.now(timezone.utc) - delta

        for sub in subs:
            if query:
                url = f"https://www.reddit.com/r/{sub}/search.json"
                params = {
                    "q": query,
                    "restrict_sr": 1,
                    "sort": "new",
                    "t": self.time_unit.currentText(),
                    "limit": 100
                }
            else:
                url = f"https://www.reddit.com/r/{sub}/new.json"
                params = {"limit": 100}

            data = safe_fetch_json(url, params)
            if not data:
                continue

            for item in data["data"]["children"]:
                post = item["data"]

                post_time = datetime.fromtimestamp(
                    post["created_utc"], tz=timezone.utc
                )
                if post_time < time_limit:
                    continue

                if self.is_blacklisted_post(post):
                    continue

                self.add_row(
                    self.search_table,
                    post["title"],
                    post["subreddit"],
                    post_time,
                    "https://www.reddit.com" + post["permalink"]
                )

    # ---------- MONITOR TAB (DISCOVER SUBREDDITS) ----------
    def init_monitor_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        bar = QHBoxLayout()
        self.m_keys = QLineEdit()
        self.m_keys.setPlaceholderText("Ключевые слова (PiratedGames, piracy)")

        btn = QPushButton("Найти сабреддиты")
        btn.clicked.connect(self.run_monitor)

        bar.addWidget(self.m_keys)
        bar.addWidget(btn)

        self.monitor_table = self.make_table()

        layout.addLayout(bar)
        layout.addWidget(self.monitor_table)
        self.tabs.addTab(tab, "Поиск сабреддитов")

    def run_monitor(self):
        self.monitor_table.setRowCount(0)
        seen = set()

        keys = [k.strip() for k in self.m_keys.text().split(",") if k.strip()]

        for key in keys:
            url = "https://www.reddit.com/subreddits/search.json"
            params = {
                "q": key,
                "limit": 25,
                "sort": "new"
            }

            data = safe_fetch_json(url, params)
            if not data:
                continue

            for item in data["data"]["children"]:
                sub = item["data"]
                name = sub.get("display_name", "")
                if not name or name.lower() in seen:
                    continue

                seen.add(name.lower())

                self.add_row(
                    self.monitor_table,
                    f"r/{name}",
                    "subreddit",
                    datetime.now(timezone.utc),
                    "https://www.reddit.com/r/" + name
                )

    # ---------- BLACKLIST TAB ----------
    def init_blacklist_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.blacklist_edit = QTextEdit()
        self.blacklist_edit.setPlaceholderText("Одно слово или фраза на строку")

        btn_bar = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        clear_btn = QPushButton("Очистить")

        save_btn.clicked.connect(self.save_blacklist)
        clear_btn.clicked.connect(self.clear_blacklist)

        btn_bar.addWidget(save_btn)
        btn_bar.addWidget(clear_btn)

        layout.addWidget(QLabel("Чёрный список слов:"))
        layout.addWidget(self.blacklist_edit)
        layout.addLayout(btn_bar)

        self.tabs.addTab(tab, "Чёрный список")

    def save_blacklist(self):
        words = [
            w.strip().lower()
            for w in self.blacklist_edit.toPlainText().splitlines()
            if w.strip()
        ]
        self.config["blacklist_words"] = words
        save_config(self.config)

    def clear_blacklist(self):
        self.blacklist_edit.clear()
        self.config["blacklist_words"] = []
        save_config(self.config)

    # ---------- UTILS ----------
    def make_table(self):
        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(
            ["Заголовок", "Сабреддит", "Время", "Ссылка"]
        )
        h = table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        table.cellDoubleClicked.connect(
            lambda r, c: webbrowser.open(table.item(r, 3).text())
        )
        return table

    def add_row(self, table, title, sub, dt, link):
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(title))
        table.setItem(row, 1, QTableWidgetItem(sub))
        table.setItem(row, 2, QTableWidgetItem(dt.strftime("%Y-%m-%d %H:%M")))
        table.setItem(row, 3, QTableWidgetItem(link))

    # ---------- SETTINGS ----------
    def load_settings(self):
        self.blacklist_edit.setPlainText(
            "\n".join(self.config.get("blacklist_words", []))
        )

# ================= RUN =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RedditApp()
    win.show()
    sys.exit(app.exec())
