# Football Manager 97/25 – v1.2  (console + GUI + prénom/nom coach)
# ---------------------------------------------------------------
# Python ≥ 3.9 — facultatif :  pip install rich  (console colorée)
from __future__ import annotations
import random
from dataclasses import dataclass
from typing import List, Optional

try:                         # joli tableau console si 'rich' installé
    from rich.console import Console
    from rich.table import Table
    console = Console()
except ImportError:
    console = None

# ---------- Modèles -------------------------------------------------
@dataclass
class Player:
    name: str
    position: str  # GK / DF / MF / FW
    attack: int
    defense: int

@dataclass
class Team:
    name: str
    players: List[Player]
    points: int = 0
    goals_for: int = 0
    goals_against: int = 0
    matches_played: int = 0
    lineup_indices: Optional[List[int]] = None   # indices titulaires

    @property
    def active(self) -> List[Player]:
        return [self.players[i] for i in (self.lineup_indices or range(11))]

    @property
    def attack_rating(self): return sum(p.attack for p in self.active)/11
    @property
    def defense_rating(self): return sum(p.defense for p in self.active)/11
    @property
    def diff(self): return self.goals_for - self.goals_against

# ---------- Génération équipes -------------------------------------
def create_team(name: str) -> Team:
    roles = ['GK'] + ['DF']*5 + ['MF']*5 + ['FW']*5
    pl = [Player(f"{name[:3]}P{i+1:02d}", r,
                 random.randint(50, 90), random.randint(50, 90))
          for i, r in enumerate(roles)]
    return Team(name, pl)

# ---------- Moteur de match ----------------------------------------
def simulate(h: Team, a: Team):
    h_atk = h.attack_rating + random.randint(-5, 5) + 3    # bonus domicile
    a_atk = a.attack_rating + random.randint(-5, 5)
    h_def = h.defense_rating + random.randint(-5, 5)
    a_def = a.defense_rating + random.randint(-5, 5)
    hg = max(0, int((h_atk - a_def)/10) + random.randint(0, 2))
    ag = max(0, int((a_atk - h_def)/10) + random.randint(0, 2))
    # mises à jour
    h.goals_for += hg; h.goals_against += ag
    a.goals_for += ag; a.goals_against += hg
    h.matches_played += 1; a.matches_played += 1
    if hg > ag: h.points += 3
    elif ag > hg: a.points += 3
    else: h.points += 1; a.points += 1
    return hg, ag

# ---------- Championnat --------------------------------------------
class Championship:
    def __init__(self, teams: List[Team]):
        self.teams = teams
        self.idx = 0
        self.log: List[str] = []
        self.fixtures = [(a, b) for i, a in enumerate(teams)
                         for b in teams[i+1:]] * 2  # aller + retour
        random.shuffle(self.fixtures)

    def has_next(self): return self.idx < len(self.fixtures)
    def peek(self): return self.fixtures[self.idx]
    def play(self):
        h, a = self.fixtures[self.idx]; self.idx += 1
        hg, ag = simulate(h, a)
        res = f"{h.name} {hg}-{ag} {a.name}"
        self.log.append(res); return res
    def table(self):
        return sorted(self.teams,
                      key=lambda t: (-t.points, t.diff, -t.goals_for))

# ---------- Aides console -----------------------------------------
def show_table(ch: Championship, user: Team):
    data = ch.table()
    if console:
        tab = Table(title="Classement"); tab.add_column("#"); tab.add_column("Équipe")
        for c in ("MJ", "Pts", "BP", "BC", "Diff"):
            tab.add_column(c, justify="right")
        for i, t in enumerate(data, 1):
            style = "bold yellow" if t is user else ""
            tab.add_row(str(i), t.name, str(t.matches_played), str(t.points),
                        str(t.goals_for), str(t.goals_against), str(t.diff),
                        style=style)
        console.print(tab)
    else:
        for i, t in enumerate(data, 1):
            star = "*" if t is user else " "
            print(f"{i}{star} {t.name:12} {t.points:3} "
                  f"{t.goals_for:2} {t.goals_against:2} {t.diff:3}")

def choose_lineup(team: Team):
    for i, p in enumerate(team.players, 1):
        print(f"{i:2}. {p.name:12} {p.position} A:{p.attack} D:{p.defense}")
    while True:
        idx = [int(n)-1 for n in input("11 numéros : ").split() if n.isdigit()]
        if len(idx) == 11 and any(team.players[i].position == 'GK' for i in idx):
            team.lineup_indices = idx; return
        print("❌  11 joueurs valides dont 1 GK requis.")

# ---------- Jeu console --------------------------------------------
def console_game():
    clubs = ["Paris FC", "Marseille 13", "Lyonnais", "Monaco"]
    teams = [create_team(c) for c in clubs]
    for i, c in enumerate(clubs, 1): print(i, c)
    user = teams[int(input("Votre club : ")) - 1]
    coach = input("Prénom entraîneur : ") + " " + input("Nom entraîneur : ")
    print(f"Bienvenue {coach.strip() or 'Coach'} !")
    champ = Championship(teams)
    while champ.has_next():
        h, a = champ.peek()
        if user in (h, a): choose_lineup(user)
        input(f"{h.name} vs {a.name} — Entrée")
        print("Résultat :", champ.play())
        show_table(champ, user); print("="*40)

# ---------- Jeu GUI (Tkinter) --------------------------------------
def gui_game():
    try:
        import tkinter as tk
        from tkinter import ttk, scrolledtext, messagebox
    except ImportError:
        print("Tkinter absent – bascule console"); console_game(); return

    clubs = ["Paris FC", "Marseille 13", "Lyonnais", "Monaco"]
    teams = [create_team(c) for c in clubs]
    champ = Championship(teams); user: Optional[Team] = None

    root = tk.Tk(); root.title("FM 97/25"); root.geometry("1000x700")
    start = ttk.Frame(root, padding=20); start.pack(fill="both", expand=True)

    ttk.Label(start, text="Club :").grid(row=0, column=0, sticky="e")
    club_var = tk.StringVar(value=clubs[0])
    ttk.Combobox(start, textvariable=club_var, values=clubs,
                 state="readonly").grid(row=0, column=1, sticky="w")

    ttk.Label(start, text="Prénom coach :").grid(row=1, column=0, sticky="e")
    e_first = ttk.Entry(start, width=20); e_first.grid(row=1, column=1, sticky="w")
    ttk.Label(start, text="Nom coach :").grid(row=2, column=0, sticky="e")
    e_last = ttk.Entry(start, width=20); e_last.grid(row=2, column=1, sticky="w")

    def launch():
        nonlocal user
        user = teams[clubs.index(club_var.get())]
        start.forget(); main.pack(fill="both", expand=True); refresh()

    ttk.Button(start, text="Commencer", command=launch
               ).grid(row=3, column=0, columnspan=2, pady=10)

    # ---- écran principal
    main = ttk.Frame(root, padding=20)
    lbl_next = ttk.Label(main, font=("Arial", 14))
    lbl_next.grid(row=0, column=0, sticky="w")
    btn_play = ttk.Button(main, text="Jouer"); btn_play.grid(row=0, column=1, padx=10)
    log = scrolledtext.ScrolledText(main, width=60, height=20)
    log.grid(row=1, column=0, columnspan=2, pady=10)
    lbl_table = ttk.Label(main, font=("Courier", 10), justify="left")
    lbl_table.grid(row=2, column=0, columnspan=2)

    def lineup_popup():
        pop = tk.Toplevel(root); pop.title("XI titulaire")
        vars = [tk.IntVar(value=1 if i < 11 else 0) for i in range(16)]
        for i, p in enumerate(user.players):
            ttk.Checkbutton(pop,
                            text=f"{i+1:02d} {p.name:12} {p.position}",
                            variable=vars[i]
                            ).grid(row=i, column=0, sticky="w")
        def ok():
            idx = [i for i, v in enumerate(vars) if v.get()==1]
            if len(idx)!=11 or not any(user.players[i].position=='GK' for i in idx):
                messagebox.showerror("Erreur","11 joueurs valides et 1 GK")
                return
            user.lineup
