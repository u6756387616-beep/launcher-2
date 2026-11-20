import threading
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from PIL import Image, ImageTk, ImageEnhance

from .config import load_config, save_config
from .hardware import scan_hardware
from .optimizer import recommend
from .core import LOADERS, list_versions, installed_versions, install_version

BG = "#0b0b0e"
PANEL = "#151519"
PANEL_2 = "#1d1d23"
RED = "#ed2638"
RED_HOVER = "#ff4352"
TEXT = "#f5f5f7"
MUTED = "#96969f"
GREEN = "#54d68b"


class LauncherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LOK LAUNCHER")
        self.geometry("1080x720")
        self.minsize(900, 650)
        self.configure(bg=BG)
        self.cfg = load_config()
        self.hw = None
        self.versions = []
        self.recommendation = None
        self._hero_photo = None
        self._style()
        self._build()
        self.after(80, self.first_run_setup)
        self.after(120, self.refresh_hardware)
        self.after(220, self.refresh_versions)

    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TCombobox", fieldbackground="#24242b", background="#24242b",
                    foreground=TEXT, arrowcolor=TEXT, bordercolor="#33333b",
                    lightcolor="#33333b", darkcolor="#33333b", padding=8)
        s.map("TCombobox", fieldbackground=[("readonly", "#24242b")],
              foreground=[("readonly", TEXT)])
        s.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                    foreground=TEXT, rowheight=26, borderwidth=0)
        s.configure("Treeview.Heading", background="#292930", foreground=TEXT)

    def _label(self, parent, text, size=10, color=TEXT, bold=False, bg=None):
        return tk.Label(parent, text=text, bg=bg or parent.cget("bg"), fg=color,
                        font=("Segoe UI", size, "bold" if bold else "normal"))

    def _button(self, parent, text, command, primary=False, width=None):
        return tk.Button(
            parent, text=text, command=command,
            bg=RED if primary else "#292930", fg="white",
            activebackground=RED_HOVER, activeforeground="white",
            relief="flat", bd=0, padx=18, pady=11, width=width,
            font=("Segoe UI", 10, "bold"), cursor="hand2",
            highlightthickness=0
        )

    def _card(self, parent, padx=15, pady=14):
        return tk.Frame(parent, bg=PANEL, padx=padx, pady=pady,
                        highlightthickness=1, highlightbackground="#24242b")

    def _build(self):
        # Top navigation
        top = tk.Frame(self, bg=BG, height=68)
        top.pack(fill="x", padx=28, pady=(18, 12))
        top.pack_propagate(False)

        logo = tk.Frame(top, bg=BG)
        logo.pack(side="left", anchor="center")
        tk.Label(logo, text="LOK", bg=BG, fg=RED,
                 font=("Segoe UI Black", 25, "bold")).pack(side="left")
        tk.Label(logo, text=" LAUNCHER", bg=BG, fg=TEXT,
                 font=("Segoe UI", 19, "bold")).pack(side="left", pady=(5, 0))
        tk.Label(top, text="MINECRAFT JAVA EDITION  /  DESKTOP",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(side="right", pady=22)

        # Hero artwork
        hero_wrap = tk.Frame(self, bg=BG)
        hero_wrap.pack(fill="x", padx=28)
        self.hero = tk.Canvas(hero_wrap, height=244, bg="#171014",
                              bd=0, highlightthickness=0)
        self.hero.pack(fill="x")
        self._draw_hero()
        self.bind("<Configure>", self._resize_hero)

        # Main content
        content = tk.Frame(self, bg=BG)
        content.pack(fill="both", expand=True, padx=28, pady=16)

        left = tk.Frame(content, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 14))
        right = tk.Frame(content, bg=BG, width=300)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        settings = self._card(left, 18, 16)
        settings.pack(fill="x")
        head = tk.Frame(settings, bg=PANEL)
        head.pack(fill="x", pady=(0, 12))
        self._label(head, "PRZYGOTUJ ROZGRYWKĘ", 12, TEXT, True).pack(side="left")
        self._label(head, "QUICK PLAY", 8, RED, True).pack(side="right")

        fields = tk.Frame(settings, bg=PANEL)
        fields.pack(fill="x")
        for col in range(3):
            fields.grid_columnconfigure(col, weight=1, uniform="fields")

        self._label(fields, "WERSJA GRY", 8, MUTED, True).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self._label(fields, "MODLOADER", 8, MUTED, True).grid(row=0, column=1, sticky="w", padx=5)
        self._label(fields, "PAMIĘĆ RAM", 8, MUTED, True).grid(row=0, column=2, sticky="w", padx=(10, 0))

        self.version_var = tk.StringVar(value=self.cfg.get("version", "release"))
        self.version_box = ttk.Combobox(fields, textvariable=self.version_var, state="normal")
        self.version_box.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(6, 0), ipady=2)

        self.loader_var = tk.StringVar(value=self.cfg.get("loader", "Vanilla"))
        ttk.Combobox(fields, textvariable=self.loader_var, values=LOADERS,
                     state="readonly").grid(row=1, column=1, sticky="ew", padx=5, pady=(6, 0), ipady=2)

        self.ram_var = tk.StringVar(value=str(self.cfg.get("ram_gb", 2)))
        ttk.Combobox(fields, textvariable=self.ram_var,
                     values=[str(x) for x in range(1, 33)], state="readonly").grid(
                         row=1, column=2, sticky="ew", padx=(10, 0), pady=(6, 0), ipady=2)

        actions = tk.Frame(settings, bg=PANEL)
        actions.pack(fill="x", pady=(17, 0))
        self._button(actions, "⬇  INSTALUJ / NAPRAW", self.install_selected).pack(side="left")
        self._button(actions, "▶  PLAY", self.launch_game, True, 15).pack(side="right")

        # Installed versions and status
        installed_card = self._card(left, 18, 14)
        installed_card.pack(fill="both", expand=True, pady=(13, 0))
        row = tk.Frame(installed_card, bg=PANEL)
        row.pack(fill="x", pady=(0, 8))
        self._label(row, "TWOJE INSTANCJE", 10, TEXT, True).pack(side="left")
        self._label(row, "LOCAL LIBRARY", 8, MUTED, True).pack(side="right")
        self.installed = tk.Listbox(installed_card, bg="#101014", fg="#e9e9ed",
                                    selectbackground=RED, selectforeground="white",
                                    relief="flat", height=5, bd=0,
                                    font=("Segoe UI", 9), activestyle="none")
        self.installed.pack(fill="both", expand=True)
        self.status = tk.StringVar(value="Uruchamianie LOK Launcher…")
        tk.Label(installed_card, textvariable=self.status, bg=PANEL, fg=MUTED,
                 wraplength=620, justify="left", font=("Segoe UI", 8)).pack(anchor="w", pady=(9, 0))

        # Hardware panel
        system = self._card(right, 16, 15)
        system.pack(fill="x")
        self._label(system, "SYSTEM OVERVIEW", 11, TEXT, True).pack(anchor="w")
        self._label(system, "WYKRYTE PODZESPOŁY", 8, MUTED, True).pack(anchor="w", pady=(3, 12))
        self.hw_text = tk.Label(system, text="Skanowanie sprzętu…", bg=PANEL, fg=TEXT,
                                justify="left", anchor="nw", font=("Segoe UI", 8),
                                wraplength=255)
        self.hw_text.pack(fill="x")

        optimizer = self._card(right, 16, 15)
        optimizer.pack(fill="x", pady=(12, 0))
        self._label(optimizer, "SMART OPTIMIZER", 11, RED, True).pack(anchor="w")
        self.profile_title = tk.Label(optimizer, text="ANALIZA W TOKU", bg=PANEL,
                                      fg=TEXT, font=("Segoe UI", 10, "bold"), anchor="w")
        self.profile_title.pack(fill="x", pady=(10, 4))
        self.profile_text = tk.Label(optimizer, text="Czekam na dane komputera…",
                                     bg=PANEL, fg=MUTED, justify="left", anchor="nw",
                                     font=("Segoe UI", 8), wraplength=255)
        self.profile_text.pack(fill="x", pady=(0, 10))
        self._button(optimizer, "✦  ZASTOSUJ AUTO RAM", self.apply_auto).pack(fill="x")
        self._button(optimizer, "ODŚWIEŻ SPRZĘT", self.refresh_hardware).pack(fill="x", pady=(7, 0))

        footer = tk.Frame(self, bg=BG)
        footer.pack(fill="x", padx=28, pady=(0, 12))
        tk.Label(footer, text="LOK LAUNCHER  •  DEV BUILD 0.2.0",
                 bg=BG, fg="#66666f", font=("Segoe UI", 8)).pack(side="left")
        self._button(footer, "⚙  FOLDER .MINECRAFT", self.choose_folder).pack(side="right")

    def _draw_hero(self):
        self.hero.delete("all")
        w = max(self.hero.winfo_width(), 900)
        h = 244
        base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
        img_path = base_dir / "assets" / "lok_hero.png"
        if img_path.exists():
            try:
                im = Image.open(img_path).convert("RGB")
                ratio = max(w / im.width, h / im.height)
                im = im.resize((int(im.width * ratio), int(im.height * ratio)), Image.Resampling.LANCZOS)
                x0 = max(0, (im.width - w) // 2)
                y0 = max(0, (im.height - h) // 2)
                im = im.crop((x0, y0, x0 + w, y0 + h))
                im = ImageEnhance.Brightness(im).enhance(0.62)
                self._hero_photo = ImageTk.PhotoImage(im)
                self.hero.create_image(0, 0, image=self._hero_photo, anchor="nw")
            except Exception:
                self.hero.create_rectangle(0, 0, w, h, fill="#260d12", outline="")
        else:
            self.hero.create_rectangle(0, 0, w, h, fill="#260d12", outline="")
        # Dark left gradient-like overlay using translucent-looking solid bands
        self.hero.create_rectangle(0, 0, int(w * .64), h, fill="#100d10", stipple="gray50", outline="")
        self.hero.create_text(30, 34, text="YOUR WORLD. YOUR RULES.",
                              anchor="nw", fill="#ff6975",
                              font=("Segoe UI", 9, "bold"))
        self.hero.create_text(27, 68, text="WEJDŹ DO GRY",
                              anchor="nw", fill="white",
                              font=("Segoe UI Black", 27, "bold"))
        self.hero.create_text(30, 116, text="Wybierz wersję, dopasuj ustawienia i graj.",
                              anchor="nw", fill="#dedee3",
                              font=("Segoe UI", 10))
        self.hero.create_rectangle(30, 164, 168, 204, fill=RED, outline="")
        self.hero.create_text(99, 184, text="LOK  /  READY",
                              fill="white", font=("Segoe UI", 9, "bold"))

    def _resize_hero(self, event):
        if event.widget is self and hasattr(self, "hero"):
            self.after_idle(self._draw_hero)

    def _background(self, fn, on_done=None):
        def worker():
            try:
                result, error = fn(), None
            except Exception as exc:
                result, error = None, str(exc)
            self.after(0, lambda: on_done(result, error) if on_done else self._show_result(result, error))
        threading.Thread(target=worker, daemon=True).start()

    def _show_result(self, result, error):
        if error:
            self.status.set("Błąd: " + error)
            messagebox.showerror("LOK LAUNCHER", error)
        else:
            self.status.set("Operacja zakończona.")

    def refresh_hardware(self):
        self.status.set("Skanowanie podzespołów…")
        def done(hw, error):
            if error:
                self.status.set("Nie udało się odczytać sprzętu: " + error)
                return
            self.hw = hw
            self.hw_text.config(text=(
                f"CPU\\n{hw['cpu']}\\n\\n"
                f"RAM\\n{hw['ram_total']} GB  •  wolne {hw['ram_available']} GB\\n\\n"
                f"GPU\\n{hw['gpu']}\\n\\n"
                f"RDZENIE / WĄTKI\\n{hw['cores']} / {hw['threads']}\\n\\n"
                f"DYSK WOLNE\\n{hw['disk_free']} GB"
            ))
            self._update_optimizer()
            self.status.set("Skanowanie zakończone. Możesz przygotować grę.")
        self._background(scan_hardware, done)

    def _update_optimizer(self):
        if not self.hw:
            return
        rec = recommend(self.hw)
        self.recommendation = rec
        self.profile_title.config(text=f"PROFIL  /  {rec['profile']}")
        self.profile_text.config(text=(
            f"Rekomendowany RAM: {rec['ram_gb']} GB\\n"
            f"Render distance: {rec['render_distance']} chunks\\n\\n{rec['note']}"
        ))

    def apply_auto(self):
        if not self.hw:
            messagebox.showinfo("Smart Optimizer", "Najpierw poczekaj na skanowanie sprzętu.")
            return
        self._update_optimizer()
        self.ram_var.set(str(self.recommendation["ram_gb"]))
        self.status.set("Zastosowano rekomendowaną ilość RAM.")

    def refresh_versions(self):
        self.status.set("Pobieranie listy wersji Minecraft…")
        def done(versions, error):
            if error:
                self.status.set("Nie udało się pobrać wersji: " + error)
                return
            self.versions = versions
            ids = [v["id"] for v in versions]
            self.version_box["values"] = ids
            if self.version_var.get() not in ids:
                latest = next((v["id"] for v in versions if v.get("type") == "release"),
                              ids[0] if ids else "")
                self.version_var.set(latest)
            self.status.set(f"Załadowano {len(ids)} wersji Minecraft.")
            self.refresh_installed()
        self._background(list_versions, done)

    def refresh_installed(self):
        def done(items, error):
            self.installed.delete(0, "end")
            if error:
                self.installed.insert("end", "Błąd odczytu: " + error)
                return
            for item in items:
                self.installed.insert("end", "  •  " + item.get("id", str(item)))
            if not items:
                self.installed.insert("end", "  Brak zainstalowanych wersji.")
        self._background(lambda: installed_versions(self.cfg["game_dir"]), done)

    def install_selected(self):
        version = self.version_var.get().strip()
        loader = self.loader_var.get()
        if not version:
            messagebox.showwarning("LOK", "Wybierz wersję Minecraft.")
            return
        try:
            ram = int(self.ram_var.get())
        except ValueError:
            messagebox.showwarning("LOK", "Nieprawidłowa ilość RAM.")
            return
        self.cfg.update(version=version, loader=loader, ram_gb=ram)
        save_config(self.cfg)
        self.status.set(f"Instalowanie {version} ({loader})…")
        def done(result, error):
            if error:
                self.status.set("Instalacja nie powiodła się.")
                messagebox.showerror("Błąd instalacji", error)
            else:
                self.status.set(f"Zainstalowano {version} ({loader}).")
                self.refresh_installed()
        self._background(lambda: install_version(version, loader, self.cfg["game_dir"]), done)

    def launch_game(self):
        messagebox.showinfo(
            "LOK LAUNCHER",
            "Interfejs PLAY jest gotowy, ale bezpieczne logowanie Microsoft OAuth "
            "i przekazanie tokenu do gry to kolejny etap. W tej wersji nie ma "
            "logowania crack/offline."
        )


    def first_run_setup(self):
        """First-run wizard: choose an existing .minecraft or use the standard one."""
        if self.cfg.get("first_run_setup_done"):
            return
        standard = Path.home() / "AppData" / "Roaming" / ".minecraft"
        # Prefer APPDATA when available (Windows).
        import os
        standard = Path(os.getenv("APPDATA", str(Path.home()))) / ".minecraft"
        current = Path(self.cfg.get("game_dir", standard))
        if current.exists() and (current / "versions").exists():
            self.cfg["game_dir"] = str(current)
            self.cfg["first_run_setup_done"] = True
            save_config(self.cfg)
            self.status.set("Podłączono istniejący folder Minecraft: " + str(current))
            return

        win = tk.Toplevel(self)
        win.title("Pierwsze uruchomienie — LOK LAUNCHER")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        win.geometry("560x330")
        win.update_idletasks()
        x = self.winfo_rootx() + max(20, (self.winfo_width() - 560) // 2)
        y = self.winfo_rooty() + max(20, (self.winfo_height() - 330) // 2)
        win.geometry(f"+{x}+{y}")

        tk.Label(win, text="KONFIGURACJA FOLDERU GRY", bg=BG, fg=RED,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=24, pady=(22, 8))
        tk.Label(win, text="Gdzie znajduje się Minecraft?", bg=BG, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=24)
        tk.Label(
            win,
            text="LOK Launcher może użyć standardowego folderu .minecraft albo podłączyć istniejący folder z innego dysku. Twoje światy i mody nie będą przenoszone ani kasowane.",
            bg=BG, fg=MUTED, justify="left", wraplength=505,
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=24, pady=(7, 16))

        path_var = tk.StringVar(value=str(standard))
        path_entry = tk.Entry(win, textvariable=path_var, bg="#202027", fg=TEXT,
                              insertbackground=TEXT, relief="flat",
                              font=("Segoe UI", 9))
        path_entry.pack(fill="x", padx=24, ipady=9)

        def browse():
            selected = filedialog.askdirectory(parent=win, title="Wybierz folder .minecraft")
            if selected:
                path_var.set(selected)

        row = tk.Frame(win, bg=BG)
        row.pack(fill="x", padx=24, pady=12)
        self._button(row, "PRZEGLĄDAJ…", browse).pack(side="left")

        def finish(use_path):
            selected = Path(use_path).expanduser()
            if not selected.exists():
                try:
                    selected.mkdir(parents=True, exist_ok=True)
                except Exception as exc:
                    messagebox.showerror("Folder gry", f"Nie można utworzyć folderu:\\n{exc}", parent=win)
                    return
            self.cfg["game_dir"] = str(selected)
            self.cfg["first_run_setup_done"] = True
            save_config(self.cfg)
            win.grab_release()
            win.destroy()
            self.status.set("Folder Minecraft: " + str(selected))
            self.refresh_installed()

        actions = tk.Frame(win, bg=BG)
        actions.pack(fill="x", padx=24, pady=(12, 22))
        self._button(actions, "UŻYJ TEGO FOLDERU", lambda: finish(path_var.get()), True).pack(side="right")
        self._button(actions, "UŻYJ STANDARDOWEGO", lambda: finish(str(standard))).pack(side="left")

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Wybierz katalog Minecraft")
        if folder:
            self.cfg["game_dir"] = folder
            self.cfg["first_run_setup_done"] = True
            save_config(self.cfg)
            self.status.set("Zmieniono katalog gry.")
            self.refresh_installed()
