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
        if user in (h, a): choose_line_
