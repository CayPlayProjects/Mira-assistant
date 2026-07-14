#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIRA v2.0 — AI Assistant
Premium dark UI, multi-provider AI, voice, scripts, system monitor.
(c) CayPlay 2026
"""

import os, sys, json, logging, subprocess, threading, time
import urllib.request, urllib.parse, urllib.error, webbrowser
import shutil, psutil, platform, re, winreg, math, difflib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

import pyttsx3
import speech_recognition as sr
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFrame,
    QSystemTrayIcon, QMenu, QDialog, QPlainTextEdit, QScrollArea,
    QStackedWidget, QToolButton, QProgressBar, QListWidget, QListWidgetItem,
    QComboBox, QSplitter,
)
from PyQt6.QtGui import (
    QAction, QFont, QIcon, QColor, QPainter, QPixmap, QRadialGradient, QBrush,
    QDesktopServices, QShortcut, QKeySequence,
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QUrl, QSize,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("mira.log", encoding="utf-8")],
)
log = logging.getLogger("MIRA")

CONFIG_PATH = Path("mira_config.json")

DEFAULT_CONFIG = {
    "ai_provider": "openrouter",
    "openrouter": {"api_key": "", "base_url": "https://openrouter.ai/api/v1/chat/completions", "model": "google/gemini-2.0-flash-001"},
    "polza": {"api_key": "", "base_url": "https://api.polza.ai/v1/chat/completions", "model": "gpt-4o"},
    "router": {"api_key": "", "base_url": "https://api.router.ai/v1/chat/completions", "model": "gpt-4o"},
    "custom": {"api_key": "", "base_url": "", "model": ""},
    "ollama": {"base_url": "http://localhost:11434", "model": "qwen3:1.7b"},
    "commands": [
        {"trigger": "выключи компьютер", "action": "shutdown /s /t 30", "type": "system"},
        {"trigger": "перезагрузи компьютер", "action": "shutdown /r /t 30", "type": "system"},
        {"trigger": "заблокируй компьютер", "action": "rundll32.exe user32.dll,LockWorkStation", "type": "system"},
        {"trigger": "спящий режим", "action": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0", "type": "system"},
    ],
    "aliases": {
        "калькулятор": "calc.exe", "блокнот": "notepad.exe", "проводник": "explorer.exe",
        "диспетчер задач": "taskmgr.exe", "реестр": "regedit.exe", "командная строка": "cmd.exe",
        "терминал": "wt.exe", "powershell": "powershell.exe", "браузер": "msedge.exe",
        "хром": "chrome.exe", "стим": "steam.exe", "обс": "obs64.exe",
        "дискорд": "discord.exe", "телеграм": "Telegram.exe", "вк": "VK.exe",
        "вконтакте": "https://vk.com", "визуал студио": "code.exe", "пайчарм": "pycharm64.exe",
        "майнкрафт": "minecraft.exe", "ютуб": "https://youtube.com", "гитхаб": "https://github.com",
        "яндекс": "https://yandex.ru", "гугл": "https://google.com",
        "steam": "steam.exe", "calc": "calc.exe", "notepad": "notepad.exe",
        "explorer": "explorer.exe", "cmd": "cmd.exe", "terminal": "wt.exe",
        "browser": "msedge.exe", "edge": "msedge.exe", "chrome": "chrome.exe",
        "firefox": "firefox.exe", "opera": "opera.exe", "obs": "obs64.exe",
        "discord": "discord.exe", "telegram": "Telegram.exe", "vk": "VK.exe",
        "vscode": "code.exe", "pycharm": "pycharm64.exe", "minecraft": "minecraft.exe",
        "spotify": "Spotify.exe", "photoshop": "Photoshop.exe",
        "youtube": "https://youtube.com", "github": "https://github.com",
        "google": "https://google.com", "yandex": "https://yandex.ru",
    },
    "search_engines": {
        "google": "https://www.google.com/search?q=",
        "yandex": "https://yandex.ru/search/?text=",
        "duckduckgo": "https://duckduckgo.com/?q=",
        "youtube": "https://www.youtube.com/results?search_query=",
    },
    "default_search": "yandex",
    "voice": {"language": "ru-RU", "speed": 150},
    "contacts": {"telegram": "@CayPlay78", "vk": "https://m.vk.com/cayplay"},
    "notes": [],
    "scripts": {},
    "hotkey": "ctrl+shift+m",
}


def load_config() -> Dict:
    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        return json.loads(json.dumps(DEFAULT_CONFIG))
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            if k not in cfg:
                cfg[k] = v
            elif isinstance(v, dict) and isinstance(cfg[k], dict):
                for sk, sv in v.items():
                    if sk not in cfg[k]:
                        cfg[k][sk] = sv
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        return cfg
    except Exception as e:
        log.error(f"Config: {e}")
        return json.loads(json.dumps(DEFAULT_CONFIG))


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
    except Exception as e:
        log.error(f"Save config: {e}")


# ══════════════════════════════════════════════════════════════
# THEME
# ══════════════════════════════════════════════════════════════


class T:
    A  = "#6c5ce7"
    AH = "#a29bfe"
    AD = "#5a4bd1"
    BG = "#0e0e18"
    SF = "#151520"
    CD = "#1e1e30"
    CH = "#282845"
    IN = "#12121c"
    BD = "#2a2a42"
    BF = "#6c5ce7"
    TX = "#eeeef2"
    TD = "#9595b0"
    TM = "#5e5e7a"
    OK = "#00d2a0"
    ER = "#ff6b81"
    WR = "#ffc048"
    IF = "#74b9ff"


# ══════════════════════════════════════════════════════════════
# UI WIDGETS
# ══════════════════════════════════════════════════════════════


class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(f"#card{{background:{T.CD};border:1px solid {T.BD};border-radius:12px;}}")

    def enterEvent(self, e):
        if self.cursor().shape() == Qt.CursorShape.PointingHandCursor:
            self.setStyleSheet(f"#card{{background:{T.CH};border:1px solid {T.A}40;border-radius:12px;}}")

    def leaveEvent(self, e):
        self.setStyleSheet(f"#card{{background:{T.CD};border:1px solid {T.BD};border-radius:12px;}}")


class Btn(QPushButton):
    def __init__(self, text="", accent=False, parent=None):
        super().__init__(text, parent)
        self.accent = accent
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        if accent:
            self.setStyleSheet(f"QPushButton{{background:{T.A};color:white;border:none;border-radius:10px;padding:10px 22px;}}QPushButton:hover{{background:{T.AH};}}QPushButton:pressed{{background:{T.AD};}}")
        else:
            self.setStyleSheet(f"QPushButton{{background:{T.CH};color:{T.TX};border:1px solid {T.BD};border-radius:10px;padding:10px 22px;}}QPushButton:hover{{background:{T.BD};}}QPushButton:pressed{{background:{T.CD};}}")


class Dot(QPushButton):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.setFixedSize(38, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._color = color
        self.setStyleSheet(f"QPushButton{{background:transparent;color:{color};border:none;font-size:16px;border-radius:8px;}}QPushButton:hover{{background:{T.CH};}}")

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QColor(self._color)
        if self.underMouse():
            c = QColor(T.CH)
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, self.width(), self.height(), 8, 8)
        p.setPen(QColor("white") if self._color != T.CH else QColor(T.TX))
        p.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())


class Pulse(QWidget):
    def __init__(self, size=12, color=None, parent=None):
        super().__init__(parent)
        self._s = size
        self.setFixedSize(size * 2, size)
        self._ph = 0
        self._c = QColor(color or T.OK)
        self._on = False
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(80)

    def set_on(self, v):
        self._on = v
        self.update()

    def _tick(self):
        if self._on:
            self._ph = (self._ph + 0.3) % (2 * math.pi)
            self.update()

    def paintEvent(self, e):
        if not self._on:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        a = math.sin(self._ph) * 0.5 + 0.5
        r = int(a * (self._s // 2)) + 2
        c = QColor(self._c)
        c.setAlpha(int(150 + a * 100))
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(self.width() // 2 - r, self.height() // 2 - r, r * 2, r * 2)


# ══════════════════════════════════════════════════════════════
# NLP
# ══════════════════════════════════════════════════════════════

STOP = {"пожалуйста", "будь", "добр", "мне", "тебе", "очень", "просто", "сейчас", "только", "же", "то", "ли", "а", "и", "но"}
VERBS_OPEN = ["открой", "запусти", "включи", "покажи", "открыть", "запустить"]
VERBS_SEARCH = ["найди", "поищи", "погугли", "загугли"]
VERBS_GREET = ["привет", "здравствуй", "добрый день", "хай"]
VERBS_BYE = ["пока", "до свидания", "прощай"]
VERBS_THANKS = ["спасибо", "благодарю"]


class NLP:
    def __init__(self, cfg):
        self.cmds = cfg.get("commands", [])
        self.aliases = {k.lower(): v for k, v in cfg.get("aliases", {}).items()}

    def _norm(self, t):
        return " ".join(w for w in t.lower().strip(".,!?;:- \"'").split() if w not in STOP)

    def _fuzzy(self, target, cands, th=0.7):
        best, br = None, 0.0
        tl = target.lower()
        for c in cands:
            cl = c.lower()
            if tl == cl:
                return c
            if tl in cl or cl in tl:
                return c
            r = difflib.SequenceMatcher(None, tl, cl).ratio()
            if r > br and r >= th:
                best, br = c, r
        return best

    def _extract(self, text):
        for v in VERBS_OPEN + VERBS_SEARCH:
            text = re.sub(rf"\b{v}\b", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(в|на|из|по|для|с|к|о|у|в\s+браузере|в\s+интернете|онлайн)\b", "", text, flags=re.IGNORECASE)
        return " ".join(text.split()).strip()

    def classify(self, text):
        orig = text.lower().strip()
        clean = self._norm(text)

        m = re.search(r"(https?://\S+)", orig)
        if m:
            return "open_url", {"url": m.group(1)}

        for cmd in self.cmds:
            if cmd.get("trigger") and cmd["trigger"] in orig:
                return "system_cmd", {"action": cmd["action"], "type": cmd.get("type", "app"), "trigger": cmd["trigger"]}

        for v in VERBS_SEARCH:
            if orig.startswith(v + " ") or f" {v} " in orig:
                q = self._extract(orig)
                if q:
                    eng = "google" if ("гугл" in orig or "google" in orig) else "yandex"
                    return "search_web", {"query": q, "engine": eng}

        m = re.search(r"(найди|поищи|погугли|загугли)\s+(.+)", orig)
        if m:
            return "search_web", {"query": m.group(2), "engine": "yandex"}
        m = re.search(r"что\s+такое\s+(.+)", orig)
        if m:
            return "search_web", {"query": m.group(1), "engine": "yandex"}
        m = re.search(r"кто\s+такой\s+(.+)", orig)
        if m:
            return "search_web", {"query": m.group(1), "engine": "yandex"}

        m = re.search(r"создай\s+сценарий\s*[:\-]?\s*(.+)", orig)
        if m:
            return "create_script", {"match": m.group(1).strip()}
        m = re.search(r"запусти\s+сценарий\s*[:\-]?\s*(.+)", orig)
        if m:
            return "run_script", {"match": m.group(1).strip()}
        m = re.search(r"(покажи|список)\s+сценари", orig)
        if m:
            return "list_scripts", {}

        m = re.search(r"(сколько\s+будет|посчитай|вычисли)\s+(.+)", orig)
        if m:
            return "calc", {"expr": m.group(2).strip()}
        m = re.search(r"\d+\s*[+\-*/]\s*\d+", orig)
        if m:
            return "calc", {"expr": m}

        if any(w in orig for w in ["время", "час", "который час"]):
            return "time_query", {}
        if any(w in orig for w in ["дата", "число", "какое сегодня"]):
            return "date_query", {}

        m = re.search(r"(запомни|запиши)\s+(.+)", orig)
        if m:
            return "note_save", {"text": m.group(2).strip()}
        if any(w in orig for w in ["заметк", "покажи заметки"]):
            return "note_list", {}

        for v in VERBS_OPEN:
            if v in orig:
                target = self._extract(orig)
                if target:
                    if target in self.aliases:
                        return "open_app", {"target": self.aliases[target], "display": target}
                    fuzzy = self._fuzzy(target, list(self.aliases.keys()))
                    if fuzzy:
                        return "open_app", {"target": self.aliases[fuzzy], "display": fuzzy}
                    return "open_app", {"target": target, "display": target}

        for alias, exe in self.aliases.items():
            if alias in orig and len(alias) >= 3:
                return "open_app", {"target": exe, "display": alias}

        if any(w in orig for w in VERBS_GREET):
            return "chat", {"response": "Привет! Чем могу помочь?"}
        if any(w in orig for w in VERBS_BYE):
            return "chat", {"response": "До свидания!"}
        if any(w in orig for w in VERBS_THANKS):
            return "chat", {"response": "Пожалуйста!"}
        if "как дела" in orig:
            return "chat", {"response": "Отлично, готов помочь!"}
        if "что ты умеешь" in orig:
            return "chat", {"response": "Я умею запускать приложения, искать в интернете, отвечать на вопросы, работать со сценариями и заметками, и многое другое."}

        return "ai_chat", {"prompt": text}


# ══════════════════════════════════════════════════════════════
# SYSTEM EXECUTOR
# ══════════════════════════════════════════════════════════════


class Executor:
    def __init__(self, cfg):
        self.aliases = {k.lower(): v for k, v in cfg.get("aliases", DEFAULT_CONFIG["aliases"]).items()}
        self.search = cfg.get("search_engines", DEFAULT_CONFIG["search_engines"])
        self.default_search = cfg.get("default_search", "yandex")
        self.steam = self._find_steam()
        self._cache = {}
        threading.Thread(target=self._scan_steam, daemon=True).start()

    def _find_steam(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
                return winreg.QueryValueEx(k, "SteamPath")[0]
        except Exception:
            pass
        for p in ["C:\\Program Files (x86)\\Steam", "D:\\Games\\Steam"]:
            if os.path.exists(os.path.join(p, "steam.exe")):
                return p
        return None

    def _scan_steam(self):
        if not self.steam:
            return
        vdf = os.path.join(self.steam_path, "steamapps", "libraryfolders.vdf") if hasattr(self, 'steam_path') else None
        libs = [os.path.join(self.steam, "steamapps", "common")]
        skip = {"uninstall", "setup", "install", "redist", "steamwebhelper", "steamservice"}
        for lib in libs:
            if not os.path.isdir(lib):
                continue
            try:
                for folder in os.listdir(lib):
                    fp = os.path.join(lib, folder)
                    if not os.path.isdir(fp):
                        continue
                    for e in os.listdir(fp):
                        if e.lower().endswith(".exe") and e.lower().replace(".exe", "") not in skip:
                            self._cache[folder.lower()] = os.path.join(fp, e)
                            break
            except Exception:
                pass

    def _resolve(self, cmd):
        if not cmd:
            return None
        cl = cmd.lower().strip(".,!?;:- \"'")
        if cl in self._cache:
            return self._cache[cl]
        if cl in self.aliases:
            r = self._resolve_exe(self.aliases[cl])
            self._cache[cl] = r
            return r
        words = set(re.findall(r"\w+", cl))
        for alias, exe in self.aliases.items():
            if alias in words or alias == cl:
                r = self._resolve_exe(exe)
                self._cache[cl] = r
                return r
        clean = re.sub(r"\b(найди|открой|запусти|включи|покажи|поищи)\b", "", cl).strip()
        if clean:
            m = self._fuzzy(clean, list(self.aliases.keys()))
            if m:
                r = self._resolve_exe(self.aliases[m])
                self._cache[cl] = r
                return r
        if self.steam:
            for gn, ep in self._cache.items():
                if gn in cl or cl in gn:
                    if os.path.exists(ep):
                        return ep
        return shutil.which(cl) or shutil.which(cl + ".exe") or cmd

    def _fuzzy(self, target, cands, th=0.7):
        best, br = None, 0.0
        for c in cands:
            r = difflib.SequenceMatcher(None, target.lower(), c.lower()).ratio()
            if r > br and r >= th:
                best, br = c, r
        return best

    def _resolve_exe(self, exe):
        if os.path.isabs(exe) and os.path.exists(exe):
            return exe
        found = shutil.which(exe)
        if found:
            return found
        if not exe.lower().endswith(".exe"):
            found = shutil.which(exe + ".exe")
            if found:
                return found
        return exe

    def search_web(self, query, engine=None):
        engine = engine or self.default_search
        url = self.search.get(engine, self.search["yandex"]) + urllib.parse.quote(query)
        try:
            webbrowser.open(url)
            return f"Поиск: {query}"
        except Exception as e:
            return f"Ошибка поиска: {e}"

    def open_url(self, url):
        if not url.startswith("http"):
            url = "https://" + url
        try:
            webbrowser.open(url)
            return f"Открываю: {url}"
        except Exception as e:
            return f"Ошибка: {e}"

    def execute(self, command, ctype="auto"):
        try:
            if command.startswith("SEARCH:"):
                return self.search_web(command.replace("SEARCH:", "").strip())
            if command.startswith("URL:"):
                return self.open_url(command.replace("URL:", "").strip())
            if command.startswith("steam://"):
                os.startfile(command)
                return f"Steam: {command}"
            if ctype == "auto":
                cl = command.lower()
                if cl.startswith(("shutdown", "restart", "lock", "rundll32", "powershell")):
                    ctype = "system"
                elif Path(command).exists() or command.startswith("ms-"):
                    ctype = "file"
                else:
                    ctype = "app"
            if ctype == "system":
                r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
                return r.stdout.strip() or r.stderr.strip() or "Готово"
            if ctype == "file":
                os.startfile(command)
                return f"Открыто: {Path(command).name}"
            resolved = self._resolve(command)
            if resolved and os.path.isabs(resolved) and os.path.exists(resolved):
                subprocess.Popen(f'"{resolved}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return f"Запущено: {Path(resolved).name}"
            if resolved and resolved.startswith(("http://", "https://")):
                return self.open_url(resolved)
            if resolved and resolved.lower().endswith((".exe", ".bat", ".cmd")):
                subprocess.Popen(f'"{resolved}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return f"Запущено: {resolved}"
            return f"Не найдено: {command}"
        except Exception as e:
            return f"Ошибка: {e}"


# ══════════════════════════════════════════════════════════════
# AI MANAGER
# ══════════════════════════════════════════════════════════════


class AI:
    def __init__(self, cfg):
        self.cfg = cfg
        self.provider = cfg.get("ai_provider", "openrouter")
        self.history = [{"role": "system", "content": "Ты МИРА — умный ИИ-ассистент. Отвечай кратко, по-делу, на русском."}]
        self._lock = threading.Lock()

    def ask(self, prompt):
        self.history.append({"role": "user", "content": prompt})
        if len(self.history) > 11:
            self.history = [self.history[0]] + self.history[-9:]
        if self.provider == "ollama":
            return self._ask_ollama()
        return self._ask_cloud()

    def _ask_cloud(self):
        pc = self.cfg.get(self.provider, {})
        key = pc.get("api_key", "")
        url = pc.get("base_url", "")
        model = pc.get("model", "")
        if not key or not url or not model:
            return f"Настройте {self.provider}: нужен API Key, Base URL и Model."
        try:
            payload = json.dumps({"model": model, "messages": self.history}).encode()
            req = urllib.request.Request(url, data=payload, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read())
                ans = data["choices"][0]["message"]["content"]
                self.history.append({"role": "assistant", "content": ans})
                return ans.strip()
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                return "Неверный API-ключ. Проверьте настройки."
            if e.code == 429:
                return "Превышен лимит запросов. Подождите."
            return f"Ошибка {self.provider} ({e.code}): {e.reason}"
        except Exception as e:
            return f"Ошибка подключения к {self.provider}: {e}"

    def _ask_ollama(self):
        pc = self.cfg.get("ollama", {})
        url = pc.get("base_url", "http://localhost:11434")
        model = pc.get("model", "qwen3:1.7b")
        try:
            payload = json.dumps({"model": model, "messages": self.history, "stream": False}).encode()
            req = urllib.request.Request(f"{url}/api/chat", data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                ans = json.loads(r.read())["message"]["content"]
                self.history.append({"role": "assistant", "content": ans})
                return ans.strip()
        except Exception as e:
            return f"Ollama Error: {e}"

    def clear(self):
        self.history = [self.history[0]]


# ══════════════════════════════════════════════════════════════
# VOICE
# ══════════════════════════════════════════════════════════════


class Voice:
    def __init__(self, cfg):
        vc = cfg.get("voice", DEFAULT_CONFIG["voice"])
        self.rec = sr.Recognizer()
        self.rec.energy_threshold = 300
        self.rec.dynamic_energy_threshold = True
        self.mic = None
        self.engine = None
        self._lock = threading.Lock()
        try:
            self.mic = sr.Microphone()
            with self.mic as s:
                self.rec.adjust_for_ambient_noise(s, duration=0.5)
        except Exception:
            pass
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", vc.get("speed", 150))
            for v in self.engine.getProperty("voices"):
                if "ru" in v.id.lower():
                    self.engine.setProperty("voice", v.id)
                    break
        except Exception:
            pass

    def recognize(self, audio):
        try:
            return self.rec.recognize_google(audio, language="ru-RU").strip()
        except Exception:
            return None

    def speak(self, text):
        if not self.engine or not text:
            return
        def _t():
            with self._lock:
                try:
                    self.engine.say(text[:200])
                    self.engine.runAndWait()
                except Exception:
                    pass
        threading.Thread(target=_t, daemon=True).start()


# ══════════════════════════════════════════════════════════════
# WORKERS
# ══════════════════════════════════════════════════════════════


class AIWorker(QThread):
    result = pyqtSignal(str)
    def __init__(self, ai, prompt):
        super().__init__()
        self.ai, self.prompt = ai, prompt
    def run(self):
        self.result.emit(self.ai.ask(self.prompt))


class CmdWorker(QThread):
    result = pyqtSignal(str)
    def __init__(self, executor, command, ctype):
        super().__init__()
        self.executor, self.command, self.ctype = executor, command, ctype
    def run(self):
        self.result.emit(self.executor.execute(self.command, self.ctype))


class ScriptWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(str)
    def __init__(self, executor, name, commands):
        super().__init__()
        self.executor, self.name, self.commands = executor, name, commands
        self._stop = False
    def stop(self):
        self._stop = True
    def run(self):
        for i, cmd in enumerate(self.commands):
            if self._stop:
                break
            cmd = cmd.strip()
            if not cmd:
                continue
            self.progress.emit(i + 1, len(self.commands), cmd)
            self.executor.execute(cmd, "auto")
            time.sleep(1.2)
        self.finished.emit(self.name)


# ══════════════════════════════════════════════════════════════
# PANELS
# ══════════════════════════════════════════════════════════════


class ChatPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet(f"""
            QTextEdit{{background:transparent;border:none;color:{T.TX};font-family:'Segoe UI';font-size:14px;padding:28px 36px;}}
            QScrollBar:vertical{{background:transparent;width:8px;}}
            QScrollBar::handle:vertical{{background:{T.CH};border-radius:4px;min-height:40px;}}
            QScrollBar::handle:vertical:hover{{background:{T.A}60;}}
            QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}
        """)
        lay.addWidget(self.chat, 1)

        self.status_bar = QHBoxLayout()
        self.status_bar.setContentsMargins(36, 4, 36, 4)
        self.indicator = Pulse(size=10, color=T.AH)
        self.status_bar.addWidget(self.indicator)
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet(f"color:{T.TM};font-size:11px;background:transparent;")
        self.status_bar.addWidget(self.status_lbl)
        self.status_bar.addStretch()
        sw = QWidget()
        sw.setLayout(self.status_bar)
        lay.addWidget(sw)

        inp_frame = QFrame()
        inp_frame.setStyleSheet(f"QFrame{{background:{T.SF};border-top:1px solid {T.BD};padding:16px 28px;}}")
        inp_lay = QHBoxLayout(inp_frame)
        inp_lay.setContentsMargins(0, 0, 0, 0)
        inp_lay.setSpacing(10)

        self.inp = QLineEdit()
        self.inp.setPlaceholderText("Напишите сообщение...")
        inp_lay.addWidget(self.inp, 1)

        self.voice_btn = Btn("🎤")
        self.voice_btn.setFixedWidth(48)
        inp_lay.addWidget(self.voice_btn)

        self.send_btn = Btn("➤", accent=True)
        self.send_btn.setFixedWidth(48)
        inp_lay.addWidget(self.send_btn)

        lay.addWidget(inp_frame)

    def set_status(self, text, active=True):
        self.indicator.set_on(active)
        self.status_lbl.setText(text)


class SettingsPanel(QFrame):
    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self._parent = parent

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}QScrollBar:vertical{background:transparent;width:8px;}QScrollBar::handle:vertical{background:#282845;border-radius:4px;min-height:30px;}QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}")
        container = QWidget()
        container.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(40, 32, 40, 32)
        lay.setSpacing(20)

        title = QLabel("Настройки")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{T.TX};background:transparent;")
        lay.addWidget(title)

        card1 = Card()
        c1 = QVBoxLayout(card1)
        c1.setContentsMargins(24, 20, 24, 20)
        c1.setSpacing(12)
        lbl = QLabel("Провайдер ИИ")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color:{T.AH};background:transparent;")
        c1.addWidget(lbl)
        self.prov_combo = QComboBox()
        self.prov_combo.addItems(["openrouter", "polza", "router", "custom", "ollama"])
        self.prov_combo.setCurrentText(cfg.get("ai_provider", "openrouter"))
        self.prov_combo.currentTextChanged.connect(self._on_prov)
        c1.addWidget(self.prov_combo)
        lay.addWidget(card1)

        card2 = Card()
        c2 = QVBoxLayout(card2)
        c2.setContentsMargins(24, 20, 24, 20)
        c2.setSpacing(12)
        lbl2 = QLabel("API Key")
        lbl2.setStyleSheet(f"color:{T.TD};font-size:12px;font-weight:500;background:transparent;")
        c2.addWidget(lbl2)
        api_row = QHBoxLayout()
        api_row.setSpacing(8)
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("sk-...")
        self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_input.textChanged.connect(self._on_field)
        api_row.addWidget(self.api_input, 1)
        self.show_btn = QPushButton("Показать")
        self.show_btn.setFixedWidth(90)
        self.show_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_btn.clicked.connect(self._toggle_key)
        api_row.addWidget(self.show_btn)
        c2.addLayout(api_row)
        self.status_lbl = QLabel("")
        self.status_lbl.setFont(QFont("Consolas", 11))
        c2.addWidget(self.status_lbl)
        lay.addWidget(card2)

        card3 = Card()
        c3 = QVBoxLayout(card3)
        c3.setContentsMargins(24, 20, 24, 20)
        c3.setSpacing(12)
        lbl3 = QLabel("Base URL")
        lbl3.setStyleSheet(f"color:{T.TD};font-size:12px;font-weight:500;background:transparent;")
        c3.addWidget(lbl3)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://api.example.com/v1/chat/completions")
        self.url_input.textChanged.connect(self._on_field)
        c3.addWidget(self.url_input)
        lay.addWidget(card3)

        card4 = Card()
        c4 = QVBoxLayout(card4)
        c4.setContentsMargins(24, 20, 24, 20)
        c4.setSpacing(12)
        lbl4 = QLabel("Модель")
        lbl4.setStyleSheet(f"color:{T.TD};font-size:12px;font-weight:500;background:transparent;")
        c4.addWidget(lbl4)
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("gpt-4o, deepseek-chat, qwen3:1.7b ...")
        self.model_input.textChanged.connect(self._on_field)
        c4.addWidget(self.model_input)
        lay.addWidget(card4)

        act_card = Card()
        ac = QVBoxLayout(act_card)
        ac.setContentsMargins(24, 20, 24, 20)
        ac.setSpacing(12)
        lbl5 = QLabel("Действия")
        lbl5.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl5.setStyleSheet(f"color:{T.AH};background:transparent;")
        ac.addWidget(lbl5)
        br = QHBoxLayout()
        br.setSpacing(10)
        r1 = Btn("Обновить статус")
        r1.clicked.connect(self._refresh)
        br.addWidget(r1)
        r2 = Btn("Очистить историю ИИ")
        r2.clicked.connect(self._clear)
        br.addWidget(r2)
        br.addStretch()
        ac.addLayout(br)
        lay.addWidget(act_card)

        lay.addStretch()
        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        self._sync(self.prov_combo.currentText())

    def _on_prov(self, p):
        self.cfg["ai_provider"] = p
        save_config(self.cfg)
        if hasattr(self._parent, "_ai"):
            self._parent._ai.provider = p
        self._sync(p)

    def _sync(self, p):
        pc = self.cfg.get(p, {})
        self.api_input.blockSignals(True)
        self.url_input.blockSignals(True)
        self.model_input.blockSignals(True)
        self.api_input.setText(pc.get("api_key", ""))
        self.url_input.setText(pc.get("base_url", ""))
        self.model_input.setText(pc.get("model", ""))
        self.api_input.blockSignals(False)
        self.url_input.blockSignals(False)
        self.model_input.blockSignals(False)
        self.api_input.setVisible(p != "ollama")
        self._upd_status()

    def _on_field(self):
        p = self.prov_combo.currentText()
        self.cfg.setdefault(p, {})["api_key"] = self.api_input.text().strip()
        self.cfg.setdefault(p, {})["base_url"] = self.url_input.text().strip()
        self.cfg.setdefault(p, {})["model"] = self.model_input.text().strip()
        save_config(self.cfg)
        self._upd_status()

    def _toggle_key(self):
        if self.api_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_btn.setText("Скрыть")
        else:
            self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_btn.setText("Показать")

    def _upd_status(self):
        p = self.prov_combo.currentText()
        if p == "ollama":
            self.status_lbl.setText("Локальный Ollama")
            self.status_lbl.setStyleSheet(f"color:{T.WR};font-family:Consolas;font-size:11px;background:transparent;")
        else:
            has = all([self.api_input.text().strip(), self.url_input.text().strip(), self.model_input.text().strip()])
            if has:
                self.status_lbl.setText("✓ Конфигурация готова")
                self.status_lbl.setStyleSheet(f"color:{T.OK};font-family:Consolas;font-size:11px;background:transparent;")
            else:
                miss = []
                if not self.api_input.text().strip(): miss.append("API Key")
                if not self.url_input.text().strip(): miss.append("URL")
                if not self.model_input.text().strip(): miss.append("Model")
                self.status_lbl.setText(f"Не хватает: {', '.join(miss)}")
                self.status_lbl.setStyleSheet(f"color:{T.WR};font-family:Consolas;font-size:11px;background:transparent;")

    def _refresh(self):
        self._upd_status()

    def _clear(self):
        if hasattr(self._parent, "_ai"):
            self._parent._ai.clear()


class NotesPanel(QFrame):
    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self._suspend = False
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 32, 40, 32)
        lay.setSpacing(16)
        hdr = QHBoxLayout()
        t = QLabel("Заметки")
        t.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{T.TX};background:transparent;")
        hdr.addWidget(t)
        hdr.addStretch()
        add = Btn("+ Новая", accent=True)
        add.clicked.connect(self._new)
        hdr.addWidget(add)
        lay.addLayout(hdr)

        content = QHBoxLayout()
        content.setSpacing(14)
        self.list_w = QListWidget()
        self.list_w.setStyleSheet(f"""
            QListWidget{{background:{T.SF};border:1px solid {T.BD};border-radius:12px;padding:6px;color:{T.TX};font-size:13px;}}
            QListWidget::item{{padding:12px 14px;border-radius:8px;margin:2px 0;}}
            QListWidget::item:hover{{background:{T.CH};}}
            QListWidget::item:selected{{background:{T.A};color:white;}}
        """)
        self.list_w.currentItemChanged.connect(self._on_select)
        self.list_w.setMaximumWidth(260)
        content.addWidget(self.list_w, 1)

        right = QVBoxLayout()
        right.setSpacing(8)
        self.date_lbl = QLabel("")
        self.date_lbl.setStyleSheet(f"color:{T.TM};font-size:11px;background:transparent;")
        right.addWidget(self.date_lbl)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Заголовок...")
        self.title_edit.textChanged.connect(self._auto_save)
        right.addWidget(self.title_edit)
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText("Текст заметки...")
        self.text_edit.textChanged.connect(self._auto_save)
        right.addWidget(self.text_edit, 1)
        del_btn = Btn("Удалить")
        del_btn.setStyleSheet(f"QPushButton{{background:{T.CH};color:{T.ER};border:1px solid {T.ER}40;border-radius:8px;padding:10px 16px;font-size:12px;}}QPushButton:hover{{background:{T.ER}20;border:1px solid {T.ER}80;}}")
        del_btn.clicked.connect(self._delete)
        right.addWidget(del_btn)
        content.addLayout(right, 3)
        lay.addLayout(content, 1)
        self.refresh()

    def refresh(self):
        self.list_w.clear()
        for i, n in enumerate(self.cfg.get("notes", [])):
            t = n.get("title", "Без названия") or "Без названия"
            d = n.get("date", "")
            item = QListWidgetItem(f"{t}\n{d}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.list_w.addItem(item)

    def _new(self):
        notes = self.cfg.setdefault("notes", [])
        notes.insert(0, {"title": "Новая заметка", "text": "", "date": datetime.now().strftime("%d.%m.%Y %H:%M")})
        save_config(self.cfg)
        self.refresh()
        self.list_w.setCurrentRow(0)

    def _on_select(self, cur, _prev):
        if not cur:
            return
        idx = cur.data(Qt.ItemDataRole.UserRole)
        notes = self.cfg.get("notes", [])
        if 0 <= idx < len(notes):
            self._suspend = True
            self.title_edit.setText(notes[idx].get("title", ""))
            self.text_edit.setPlainText(notes[idx].get("text", ""))
            self.date_lbl.setText(notes[idx].get("date", ""))
            self._suspend = False

    def _auto_save(self):
        if self._suspend:
            return
        cur = self.list_w.currentItem()
        if not cur:
            return
        idx = cur.data(Qt.ItemDataRole.UserRole)
        notes = self.cfg.get("notes", [])
        if 0 <= idx < len(notes):
            notes[idx]["title"] = self.title_edit.text() or "Без названия"
            notes[idx]["text"] = self.text_edit.toPlainText()
            notes[idx]["date"] = datetime.now().strftime("%d.%m.%Y %H:%M")
            save_config(self.cfg)
            cur.setText(f"{notes[idx]['title']}\n{notes[idx]['date']}")

    def _delete(self):
        cur = self.list_w.currentItem()
        if not cur:
            return
        idx = cur.data(Qt.ItemDataRole.UserRole)
        notes = self.cfg.get("notes", [])
        if 0 <= idx < len(notes):
            notes.pop(idx)
            save_config(self.cfg)
            self.refresh()
            self.title_edit.clear()
            self.text_edit.clear()


class ScriptsPanel(QFrame):
    run_signal = pyqtSignal(str)
    create_signal = pyqtSignal()
    edit_signal = pyqtSignal(str)

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 32, 40, 32)
        lay.setSpacing(16)
        t = QLabel("Сценарии")
        t.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{T.TX};background:transparent;")
        lay.addWidget(t)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}QScrollBar:vertical{background:transparent;width:8px;}QScrollBar::handle:vertical{background:#282845;border-radius:4px;min-height:30px;}QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}")
        self.content = QWidget()
        self.content.setStyleSheet("background:transparent;")
        self.scroll.setWidget(self.content)
        self.cl = QVBoxLayout(self.content)
        self.cl.setContentsMargins(0, 0, 0, 0)
        self.cl.setSpacing(10)
        self.cl.addStretch()
        lay.addWidget(self.scroll, 1)
        add = Btn("+ Новый сценарий", accent=True)
        add.clicked.connect(self.create_signal.emit)
        lay.addWidget(add)
        self.refresh()

    def refresh(self):
        while self.cl.count():
            item = self.cl.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        scripts = self.cfg.get("scripts", {})
        if not scripts:
            e = QLabel("Нет сценариев. Создайте первый!")
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            e.setStyleSheet(f"color:{T.TM};padding:60px;font-size:14px;background:transparent;")
            self.cl.addWidget(e)
        else:
            for name, cmds in scripts.items():
                self.cl.addWidget(self._card(name, cmds))
        self.cl.addStretch()

    def _card(self, name, cmds):
        card = Card()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(8)
        hdr = QHBoxLayout()
        h = QLabel(name)
        h.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        h.setStyleSheet(f"color:{T.TX};background:transparent;")
        hdr.addWidget(h)
        hdr.addStretch()
        run = Btn("▶", accent=True)
        run.setFixedWidth(50)
        run.clicked.connect(lambda: self.run_signal.emit(name))
        hdr.addWidget(run)
        edit = Btn("✎")
        edit.setFixedWidth(40)
        edit.clicked.connect(lambda: self.edit_signal.emit(name))
        hdr.addWidget(edit)
        delete = Btn("✕")
        delete.setFixedWidth(40)
        delete.setStyleSheet(f"QPushButton{{background:{T.CH};color:{T.ER};border:1px solid {T.ER}40;border-radius:8px;padding:6px;font-size:14px;}}QPushButton:hover{{background:{T.ER}20;}}")
        delete.clicked.connect(lambda: self._delete(name))
        hdr.addWidget(delete)
        cl.addLayout(hdr)
        meta = QLabel(f"{len(cmds)} шагов ~{len(cmds) * 1.2:.0f}с")
        meta.setStyleSheet(f"color:{T.TM};font-size:11px;background:transparent;")
        cl.addWidget(meta)
        return card

    def _delete(self, name):
        if name in self.cfg.get("scripts", {}):
            del self.cfg["scripts"][name]
            save_config(self.cfg)
            self.refresh()


class SystemPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 32, 40, 32)
        lay.setSpacing(20)

        t = QLabel("Системный монитор")
        t.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{T.TX};background:transparent;")
        lay.addWidget(t)

        grid = QGridLayout()
        grid.setSpacing(16)
        self.cpu_v, self.cpu_bar, self.cpu_d = self._m("CPU")
        grid.addWidget(self.cpu_v[0], 0, 0)
        self.ram_v, self.ram_bar, self.ram_d = self._m("RAM")
        grid.addWidget(self.ram_v[0], 0, 1)
        self.disk_v, self.disk_bar, self.disk_d = self._m("Диск")
        grid.addWidget(self.disk_v[0], 0, 2)

        info_card = Card()
        il = QVBoxLayout(info_card)
        il.setContentsMargins(24, 20, 24, 20)
        il.setSpacing(12)
        it = QLabel("Информация о системе")
        it.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        it.setStyleSheet(f"color:{T.AH};background:transparent;")
        il.addWidget(it)
        self.info_lbl = QLabel()
        self.info_lbl.setStyleSheet(f"color:{T.TD};font-family:'Consolas',monospace;font-size:12px;background:transparent;")
        self.info_lbl.setWordWrap(True)
        il.addWidget(self.info_lbl)
        grid.addWidget(info_card, 1, 0, 1, 3)
        lay.addLayout(grid)
        lay.addStretch()

        self._last_info = 0
        t = QTimer(self)
        t.timeout.connect(self._upd)
        t.start(1500)
        self._upd()

    def _m(self, name):
        card = Card()
        card.setMinimumHeight(140)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(2)
        nm = QLabel(name)
        nm.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        nm.setStyleSheet(f"color:{T.TM};background:transparent;")
        cl.addWidget(nm)
        v = QLabel("0%")
        v.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        v.setStyleSheet(f"color:{T.AH};background:transparent;")
        cl.addWidget(v)
        d = QLabel("")
        d.setStyleSheet(f"color:{T.TD};font-size:11px;background:transparent;")
        cl.addWidget(d)
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setTextVisible(False)
        bar.setFixedHeight(6)
        bar.setStyleSheet(f"QProgressBar{{background:{T.CD};border:none;border-radius:3px;}}QProgressBar::chunk{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {T.A},stop:1 {T.AH});border-radius:3px;}}")
        cl.addWidget(bar)
        return (card, v, d), bar, d

    def _upd(self):
        try:
            cpu = psutil.cpu_percent(interval=0)
            self.cpu_v[1].setText(f"{cpu:.0f}%")
            self.cpu_bar.setValue(int(cpu))
            self.cpu_d.setText(f"{psutil.cpu_count(logical=True)} потоков")

            ram = psutil.virtual_memory()
            self.ram_v[1].setText(f"{ram.percent:.0f}%")
            self.ram_bar.setValue(int(ram.percent))
            self.ram_d.setText(f"{(ram.total - ram.available) / 1024**3:.1f} / {ram.total / 1024**3:.1f} GB")

            disk = psutil.disk_usage("C:\\")
            self.disk_v[1].setText(f"{disk.percent:.0f}%")
            self.disk_bar.setValue(int(disk.percent))
            self.disk_d.setText(f"{disk.used / 1024**3:.0f} / {disk.total / 1024**3:.0f} GB")

            now = time.time()
            if now - self._last_info > 30:
                self._last_info = now
                u = platform.uname()
                freq = psutil.cpu_freq()
                freq_s = f" @ {freq.current:.0f} MHz" if freq else ""
                info = [
                    f"OS:       {u.system} {u.release}",
                    f"Машина:   {u.machine}",
                    f"CPU:      {(u.processor or 'N/A')[:55]}{freq_s}",
                    f"Ядра:     {psutil.cpu_count(logical=False)} физ / {psutil.cpu_count(logical=True)} лог",
                    f"RAM:      {ram.total / 1024**3:.1f} GB",
                    f"Swap:     {psutil.swap_memory().total / 1024**3:.1f} GB",
                    f"Диск C:\\: {disk.total / 1024**3:.0f} GB",
                    f"Python:   {platform.python_version()}",
                ]
                self.info_lbl.setText("\n".join(info))
        except Exception:
            pass


class ContactsPanel(QFrame):
    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        contacts = cfg.get("contacts", {})
        lay = QVBoxLayout(self)
        lay.setContentsMargins(50, 40, 50, 40)
        lay.setSpacing(16)
        t = QLabel("Контакты")
        t.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{T.TX};background:transparent;")
        lay.addWidget(t)
        for icon, name, val, url in [
            ("✈", "Telegram", contacts.get("telegram", "@CayPlay78"), f"https://t.me/{contacts.get('telegram', '@CayPlay78').lstrip('@')}"),
            ("●", "VKontakte", contacts.get("vk", "https://m.vk.com/cayplay"), contacts.get("vk", "https://m.vk.com/cayplay")),
        ]:
            card = Card()
            card.setFixedHeight(80)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(22, 16, 22, 16)
            ic = QLabel(icon)
            ic.setFont(QFont("Segoe UI Emoji", 24))
            ic.setStyleSheet("background:transparent;")
            cl.addWidget(ic)
            info = QVBoxLayout()
            info.setSpacing(2)
            lbl = QLabel(name)
            lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color:{T.TX};background:transparent;")
            info.addWidget(lbl)
            vl = QLabel(val)
            vl.setFont(QFont("Consolas", 11))
            vl.setStyleSheet(f"color:{T.AH};background:transparent;")
            info.addWidget(vl)
            cl.addLayout(info)
            cl.addStretch()
            copy = Btn("Копировать")
            copy.setFixedWidth(100)
            copy.clicked.connect(lambda v=val: QApplication.clipboard().setText(v))
            cl.addWidget(copy)
            open_ = Btn("Открыть", accent=True)
            open_.setFixedWidth(100)
            open_.clicked.connect(lambda u=url: QDesktopServices.openUrl(QUrl(u)))
            cl.addWidget(open_)
            lay.addWidget(card)
        lay.addStretch()


class AboutPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card = Card()
        card.setMaximumWidth(520)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(44, 36, 44, 36)
        cl.setSpacing(12)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo = QLabel("M")
        logo.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        logo.setStyleSheet(f"color:{T.A};background:transparent;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(logo)
        v = QLabel("MIRA v2.0")
        v.setFont(QFont("Consolas", 13))
        v.setStyleSheet(f"color:{T.AH};background:transparent;")
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(v)
        d = QLabel("ИИ-ассистент для вашего ПК.\nГолос, текст, сценарии, поиск, мониторинг системы.")
        d.setFont(QFont("Segoe UI", 13))
        d.setStyleSheet(f"color:{T.TD};background:transparent;")
        d.setAlignment(Qt.AlignmentFlag.AlignCenter)
        d.setWordWrap(True)
        cl.addWidget(d)
        cl.addSpacing(8)
        c = QLabel("(c) CayPlay 2026")
        c.setFont(QFont("Segoe UI", 11))
        c.setStyleSheet(f"color:{T.TM};background:transparent;")
        c.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(c)
        btns = QHBoxLayout()
        btns.setSpacing(10)
        btns.addStretch()
        gh = Btn("GitHub")
        gh.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com")))
        btns.addWidget(gh)
        tg = Btn("Telegram", accent=True)
        tg.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/CayPlay78")))
        btns.addWidget(tg)
        btns.addStretch()
        cl.addLayout(btns)
        wrap = QHBoxLayout()
        wrap.addStretch()
        wrap.addWidget(card)
        wrap.addStretch()
        lay.addLayout(wrap)


# ══════════════════════════════════════════════════════════════
# MAIN WINDOW
# ══════════════════════════════════════════════════════════════


class MIRAWindow(QMainWindow):
    voice_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self._exec = Executor(self.cfg)
        self._ai = AI(self.cfg)
        self._voice = Voice(self.cfg)
        self._nlp = NLP(self.cfg)
        self.voice_signal.connect(self._on_voice)
        self.active_threads = []
        self._script_worker = None
        self._setup_ui()
        self._setup_hotkeys()
        self._init_tray()
        QTimer.singleShot(100, self._boot)

    def _setup_ui(self):
        self.setWindowTitle("MIRA v2.0")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet(f"background:{T.BG};")
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.title_bar = self._make_titlebar()
        root.addWidget(self.title_bar)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        self.sidebar = self._make_sidebar()
        content.addWidget(self.sidebar)

        self.stacked = QStackedWidget()
        self.stacked.setStyleSheet(f"background:{T.BG};")

        self.chat_panel = ChatPanel()
        self.chat_panel.send_btn.clicked.connect(self._process)
        self.chat_panel.inp.returnPressed.connect(self._process)
        self.chat_panel.voice_btn.clicked.connect(self._toggle_voice)
        self.stacked.addWidget(self.chat_panel)

        self.scripts_panel = ScriptsPanel(self.cfg)
        self.scripts_panel.run_signal.connect(self._run_script)
        self.scripts_panel.create_signal.connect(lambda: self._edit_script(None))
        self.scripts_panel.edit_signal.connect(self._edit_script)
        self.stacked.addWidget(self.scripts_panel)

        self.notes_panel = NotesPanel(self.cfg)
        self.stacked.addWidget(self.notes_panel)

        self.sys_panel = SystemPanel()
        self.stacked.addWidget(self.sys_panel)

        self.contacts_panel = ContactsPanel(self.cfg)
        self.stacked.addWidget(self.contacts_panel)

        self.settings_panel = SettingsPanel(self.cfg, self)
        self.stacked.addWidget(self.settings_panel)

        self.about_panel = AboutPanel()
        self.stacked.addWidget(self.about_panel)

        content.addWidget(self.stacked, 1)
        cw = QWidget()
        cw.setLayout(content)
        root.addWidget(cw, 1)

    def _make_titlebar(self):
        tb = QFrame()
        tb.setFixedHeight(44)
        tb.setStyleSheet(f"QFrame{{background:{T.SF};border-bottom:1px solid {T.BD};}}")
        lay = QHBoxLayout(tb)
        lay.setContentsMargins(240, 0, 12, 0)
        lay.setSpacing(12)
        self.page_icon = QLabel("💬")
        self.page_icon.setStyleSheet("background:transparent;")
        lay.addWidget(self.page_icon)
        self.page_lbl = QLabel("Чат")
        self.page_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        self.page_lbl.setStyleSheet(f"color:{T.TX};background:transparent;")
        lay.addWidget(self.page_lbl)
        lay.addStretch()
        for txt, func, color in [("—", self.showMinimized, T.TD), ("□", self._toggle_max, T.TD), ("✕", self.close, T.ER)]:
            b = QPushButton(txt)
            b.setFixedSize(36, 30)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(f"QPushButton{{background:transparent;color:{color};border:none;font-size:14px;border-radius:6px;}}QPushButton:hover{{background:{T.CH};}}")
            b.clicked.connect(func)
            lay.addWidget(b)
        return tb

    def _make_sidebar(self):
        sb = QFrame()
        sb.setObjectName("sidebar")
        sb.setFixedWidth(220)
        sb.setStyleSheet(f"#sidebar{{background:{T.SF};border-right:1px solid {T.BD};}}")
        lay = QVBoxLayout(sb)
        lay.setContentsMargins(12, 16, 12, 12)
        lay.setSpacing(0)

        logo_row = QHBoxLayout()
        logo_row.setContentsMargins(12, 8, 12, 24)
        logo_row.setSpacing(10)
        dot = QLabel()
        dot.setFixedSize(32, 32)
        dot.setStyleSheet(f"QLabel{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {T.A},stop:1 {T.AH});border-radius:8px;}}")
        dot_t = QLabel("M")
        dot_t.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        dot_t.setStyleSheet("color:white;background:transparent;")
        dot_t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dl = QVBoxLayout(dot)
        dl.setContentsMargins(0, 0, 0, 0)
        dl.addWidget(dot_t)
        logo_row.addWidget(dot)
        nm = QLabel("MIRA")
        nm.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        nm.setStyleSheet(f"color:{T.TX};background:transparent;")
        logo_row.addWidget(nm)
        logo_row.addStretch()
        lay.addLayout(logo_row)

        self.nav_btns = {}
        items = [
            ("chat",     "💬", "Чат"),
            ("scripts",  "🎬", "Сценарии"),
            ("notes",    "📝", "Заметки"),
            ("system",   "📊", "Система"),
            ("contacts", "📌", "Контакты"),
            ("settings", "⚙", "Настройки"),
            ("about",    "ℹ", "О приложении"),
        ]
        for nid, icon, label in items:
            btn = QToolButton()
            btn.setText(f"  {icon}  {label}")
            btn.setProperty("nav_id", nid)
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QToolButton{{background:transparent;color:{T.TD};border:none;border-radius:8px;font-size:13px;font-family:'Segoe UI';text-align:left;padding:0px 12px;}}
                QToolButton:hover{{background:{T.CH};color:{T.TX};}}
                QToolButton:checked{{background:{T.A};color:white;font-weight:600;}}
            """)
            btn.setCheckable(True)
            btn.clicked.connect(self._on_nav)
            lay.addWidget(btn)
            self.nav_btns[nid] = btn

        self.nav_btns["chat"].setChecked(True)
        lay.addStretch()

        sr = QHBoxLayout()
        sr.setContentsMargins(14, 0, 14, 4)
        sr.setSpacing(6)
        self.sidebar_dot = Pulse(size=6, color=T.OK)
        self.sidebar_dot.set_on(True)
        sr.addWidget(self.sidebar_dot)
        sl = QLabel("Online")
        sl.setStyleSheet(f"color:{T.OK};font-size:11px;font-weight:500;background:transparent;")
        sr.addWidget(sl)
        sr.addStretch()
        lay.addLayout(sr)
        return sb

    def _on_nav(self):
        btn = self.sender()
        nid = btn.property("nav_id")
        pages = {
            "chat": (self.chat_panel, "Чат", "💬"),
            "scripts": (self.scripts_panel, "Сценарии", "🎬"),
            "notes": (self.notes_panel, "Заметки", "📝"),
            "system": (self.sys_panel, "Система", "📊"),
            "contacts": (self.contacts_panel, "Контакты", "📌"),
            "settings": (self.settings_panel, "Настройки", "⚙"),
            "about": (self.about_panel, "О приложении", "ℹ"),
        }
        for k, b in self.nav_btns.items():
            b.setChecked(k == nid)
        if nid in pages:
            panel, title, icon = pages[nid]
            self.stacked.setCurrentWidget(panel)
            self.page_lbl.setText(title)
            self.page_icon.setText(icon)

    def _setup_hotkeys(self):
        def _ghk():
            try:
                import keyboard
                keyboard.add_hotkey(self.cfg.get("hotkey", "ctrl+shift+m"), self._restore)
            except Exception:
                pass
        threading.Thread(target=_ghk, daemon=True).start()
        for i, p in enumerate(["chat", "scripts", "notes", "system", "contacts", "settings", "about"], 1):
            QShortcut(QKeySequence(f"Ctrl+{i}"), self, lambda p=p: self.nav_btns[p].click())
        QShortcut(QKeySequence("Ctrl+Q"), self, self._full_exit)
        QShortcut(QKeySequence("Ctrl+L"), self, self._clear_chat)
        QShortcut(QKeySequence("Ctrl+Space"), self, self._toggle_voice)
        QShortcut(QKeySequence("F11"), self, self._toggle_max)

    def _init_tray(self):
        px = QPixmap(64, 64)
        px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        g = QRadialGradient(32, 32, 32)
        g.setColorAt(0, QColor(108, 92, 231))
        g.setColorAt(1, QColor(90, 75, 209))
        p.setBrush(QBrush(g))
        p.drawRoundedRect(2, 2, 60, 60, 14, 14)
        p.setPen(Qt.GlobalColor.white)
        p.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "M")
        p.end()
        self.tray = QSystemTrayIcon(QIcon(px), self)
        self.tray.setToolTip("MIRA v2.0")
        m = QMenu()
        m.setStyleSheet(f"QMenu{{background:{T.SF};color:{T.TX};border:1px solid {T.BD};border-radius:8px;padding:6px;}}QMenu::item{{padding:8px 24px;border-radius:6px;}}QMenu::item:selected{{background:{T.A};color:white;}}")
        a1 = QAction("Открыть MIRA", self)
        a1.triggered.connect(self._restore)
        m.addAction(a1)
        m.addSeparator()
        a3 = QAction("Выход", self)
        a3.triggered.connect(self._full_exit)
        m.addAction(a3)
        self.tray.setContextMenu(m)
        self.tray.activated.connect(lambda r: self._restore() if r == QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.show()

    def _restore(self):
        if self.isMinimized():
            self.showNormal()
        if not self.isVisible():
            self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.activateWindow()
        self.raise_()

    def _full_exit(self):
        self.tray.hide()
        for t in self.active_threads:
            try:
                if t.isRunning():
                    t.terminate()
            except Exception:
                pass
        QApplication.quit()
        sys.exit(0)

    def _toggle_max(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _boot(self):
        self._add("ai", "MIRA v2.0 готова к работе.\n\nЧем могу помочь?")

    def _clear_chat(self):
        self.chat_panel.chat.clear()
        self._add("ai", "Чат очищен.")

    def _cleanup(self, t):
        if t in self.active_threads:
            self.active_threads.remove(t)
        t.deleteLater()

    def _start(self, w):
        w.finished.connect(lambda: self._cleanup(w))
        self.active_threads.append(w)
        w.start()

    def _add(self, role, text):
        colors = {"user": T.IF, "ai": T.OK, "sys": T.WR, "success": T.OK, "error": T.ER}
        bg_map = {"user": f"{T.A}15", "ai": f"{T.OK}10", "sys": f"{T.WR}10", "success": f"{T.OK}18", "error": f"{T.ER}18"}
        bg = bg_map.get(role, bg_map["ai"])
        c = colors.get(role, T.OK)
        safe = text.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        ts = datetime.now().strftime("%H:%M")
        if role == "user":
            html = f'<div style="text-align:right;margin:12px 0;"><div style="background:{T.A}12;padding:14px 18px;border-radius:16px 16px 4px 16px;display:inline-block;max-width:75%;border:1px solid {T.A}30;"><div style="color:{T.TX};font-size:14px;line-height:1.5;">{safe}</div><div style="color:{T.TM};font-size:10px;margin-top:6px;">{ts}</div></div></div>'
        else:
            html = f'<div style="text-align:left;margin:12px 0;"><div style="background:{bg};padding:14px 18px;border-radius:16px 16px 16px 4px;display:inline-block;max-width:75%;border:1px solid {c}25;"><div style="font-size:10px;color:{c};font-weight:600;letter-spacing:1px;margin-bottom:6px;">{role.upper()}</div><div style="color:{T.TX};font-size:14px;line-height:1.5;">{safe}</div><div style="color:{T.TM};font-size:10px;margin-top:6px;">{ts}</div></div></div>'
        self.chat_panel.chat.append(html)
        sb = self.chat_panel.chat.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _process(self):
        txt = self.chat_panel.inp.text().strip()
        if not txt:
            return
        self.chat_panel.inp.clear()
        self._add("user", txt)
        QTimer.singleShot(10, lambda: self._route(txt))

    def _route(self, text):
        try:
            intent, data = self._nlp.classify(text)
            if intent == "system_cmd":
                self._add("sys", f"Выполняю: {data['trigger']}")
                self._exec_cmd(data["action"], data["type"])
            elif intent == "search_web":
                q = re.sub(r"\b(в\s+браузере|в\s+интернете|онлайн)\b", "", data.get("query", ""), flags=re.IGNORECASE)
                q = " ".join(q.split()).strip()
                self._add("sys", f"Ищу: {q}")
                self._exec_cmd(f"SEARCH:{q}", "search")
            elif intent == "open_url":
                self._add("sys", f"Открываю: {data['url']}")
                self._exec_cmd(f"URL:{data['url']}", "url")
            elif intent == "open_app":
                self._add("sys", f"Запускаю: {data.get('display', data['target'])}")
                self._exec_cmd(data["target"], "auto")
            elif intent == "create_script":
                self._edit_script(None, data.get("match", ""))
            elif intent == "run_script":
                self._run_script(data.get("match", ""))
            elif intent == "list_scripts":
                scripts = self.cfg.get("scripts", {})
                msg = "Сценарии:\n" + "\n".join(f"  {n} ({len(c)} шагов)" for n, c in scripts.items()) if scripts else "Сценариев пока нет."
                self._add("ai", msg)
            elif intent == "time_query":
                self._add("ai", f"Сейчас {datetime.now().strftime('%H:%M:%S')}")
            elif intent == "date_query":
                months = ["", "января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
                n = datetime.now()
                self._add("ai", f"Сегодня {n.day} {months[n.month]} {n.year}")
            elif intent == "calc":
                try:
                    expr = data.get("expr", "")
                    safe = re.sub(r"[^0-9+\-*/().,\s]", "", str(expr)).replace(",", ".")
                    result = eval(safe, {"__builtins__": {}}, {})
                    self._add("success", f"{expr} = {result}")
                except Exception:
                    self._add("error", f"Не могу посчитать: {expr}")
            elif intent == "note_save":
                notes = self.cfg.setdefault("notes", [])
                notes.insert(0, {"title": data["text"][:40], "text": data["text"], "date": datetime.now().strftime("%d.%m.%Y %H:%M")})
                save_config(self.cfg)
                self.notes_panel.refresh()
                self._add("success", f"Заметка сохранена: {data['text']}")
            elif intent == "note_list":
                self.nav_btns["notes"].click()
            elif intent == "chat":
                self._add("ai", data.get("response", ""))
            elif intent == "ai_chat":
                self._add("ai", "Думаю...")
                w = AIWorker(self._ai, data.get("prompt", text))
                w.result.connect(self._on_ai)
                self._start(w)
        except Exception as e:
            self._add("error", f"Ошибка: {e}")

    def _on_cmd(self, result):
        self.chat_panel.set_status("", False)
        role = "success" if any(w in result for w in ["Запущено", "Открыто", "Готово", "Открываю", "Поиск"]) else ("error" if "Ошибка" in result or "Не найдено" in result else "sys")
        self._add(role, result)

    def _on_ai(self, result):
        self.chat_panel.set_status("", False)
        self._add("ai", result)

    def _exec_cmd(self, cmd, ctype):
        self.chat_panel.set_status("Выполняю...", True)
        w = CmdWorker(self._exec, cmd, ctype)
        w.result.connect(self._on_cmd)
        self._start(w)

    def _run_script(self, name):
        scripts = self.cfg.get("scripts", {})
        if name not in scripts:
            self._add("error", f"Сценарий '{name}' не найден")
            return
        cmds = scripts[name]
        self._add("ai", f"Запускаю '{name}' ({len(cmds)} шагов)...")
        self._script_worker = ScriptWorker(self._exec, name, cmds)
        self._script_worker.progress.connect(lambda i, t, c: self._add("sys", f"Шаг {i}/{t}: {c}"))
        self._script_worker.finished.connect(lambda n: self._add("success", f"Сценарий '{n}' выполнен!"))
        self._start(self._script_worker)

    def _edit_script(self, name=None, pre_name=""):
        dlg = QDialog(self)
        dlg.setWindowTitle("Редактор сценария")
        dlg.resize(580, 440)
        dlg.setStyleSheet(f"QDialog{{background:{T.SF};color:{T.TX};}}QLabel{{color:{T.TX};font-weight:bold;}}")
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)
        lay.addWidget(QLabel("Название:"))
        name_in = QLineEdit(pre_name)
        if name and name in self.cfg.get("scripts", {}):
            name_in.setText(name)
        lay.addWidget(name_in)
        lay.addWidget(QLabel("Команды (по одной на строку):"))
        cmd_in = QPlainTextEdit()
        if name and name in self.cfg.get("scripts", {}):
            cmd_in.setPlainText("\n".join(self.cfg["scripts"][name]))
        lay.addWidget(cmd_in)
        btns = QHBoxLayout()
        btns.addStretch()
        cancel = Btn("Отмена")
        cancel.clicked.connect(dlg.reject)
        btns.addWidget(cancel)
        save = Btn("Сохранить", accent=True)
        save.clicked.connect(dlg.accept)
        btns.addWidget(save)
        lay.addLayout(btns)
        if dlg.exec():
            nm = name_in.text().strip()
            cmds = [l.strip() for l in cmd_in.toPlainText().split("\n") if l.strip()]
            if not nm:
                return
            if name and name in self.cfg.get("scripts", {}):
                del self.cfg["scripts"][name]
            self.cfg.setdefault("scripts", {})[nm] = cmds
            save_config(self.cfg)
            self.scripts_panel.refresh()

    def _on_voice(self, txt):
        if not txt:
            self.chat_panel.set_status("", False)
            return
        self._add("user", txt)
        QTimer.singleShot(10, lambda: self._route(txt))
        self.chat_panel.set_status("", False)

    def _toggle_voice(self):
        if not self._voice.mic:
            self._add("error", "Микрофон не найден")
            return
        self.chat_panel.set_status("Слушаю...", True)
        def listen():
            try:
                with self._voice.mic as source:
                    self._voice.rec.adjust_for_ambient_noise(source, duration=0.3)
                    audio = self._voice.rec.listen(source, timeout=6, phrase_time_limit=10)
                    txt = self._voice.recognize(audio)
                    self.voice_signal.emit(txt or "")
            except Exception:
                self.voice_signal.emit("")
        threading.Thread(target=listen, daemon=True).start()

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def closeEvent(self, event):
        self.hide()
        self.tray.showMessage("MIRA", "Свернуто в трей.", QSystemTrayIcon.MessageIcon.Information, 2000)
        event.ignore()


# ══════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("MIRA")
    app.setApplicationVersion("2.0")
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))

    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(T.BG))
    palette.setColor(palette.ColorRole.WindowText, QColor(T.TX))
    palette.setColor(palette.ColorRole.Base, QColor(T.CD))
    palette.setColor(palette.ColorRole.Text, QColor(T.TX))
    palette.setColor(palette.ColorRole.Button, QColor(T.CH))
    palette.setColor(palette.ColorRole.ButtonText, QColor(T.TX))
    palette.setColor(palette.ColorRole.Highlight, QColor(T.A))
    palette.setColor(palette.ColorRole.HighlightedText, QColor("white"))
    app.setPalette(palette)

    app.setStyleSheet(f"""
        QLineEdit, QPlainTextEdit, QTextEdit {{
            background-color: {T.IN};
            border: 2px solid {T.BD};
            border-radius: 10px;
            padding: 12px 16px;
            color: {T.TX};
            font-size: 14px;
            selection-background-color: {T.A};
        }}
        QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
            border: 2px solid {T.BF};
            background-color: {T.SF};
        }}
        QComboBox {{
            background-color: {T.IN};
            border: 2px solid {T.BD};
            border-radius: 10px;
            padding: 12px 16px;
            color: {T.TX};
            font-size: 14px;
            min-height: 20px;
        }}
        QComboBox:focus {{
            border: 2px solid {T.BF};
        }}
        QComboBox:hover {{
            border: 2px solid {T.TM};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {T.TD};
            margin-right: 10px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {T.SF};
            color: {T.TX};
            border: 2px solid {T.BD};
            selection-background-color: {T.A};
            selection-color: white;
            border-radius: 8px;
            padding: 4px;
        }}
        QProgressBar {{
            background-color: {T.CD};
            border: none;
            border-radius: 4px;
            height: 8px;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {T.A},stop:1 {T.AH});
            border-radius: 4px;
        }}
        QToolTip {{
            background-color: {T.SF};
            color: {T.TX};
            border: 1px solid {T.BD};
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 12px;
        }}
    """)

    win = MIRAWindow()
    win.resize(1400, 900)
    win.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
