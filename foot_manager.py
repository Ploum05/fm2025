# Football Manager 97/25 – v1.2  (console + GUI + prénom/nom coach)
from __future__ import annotations
import random
from dataclasses import dataclass
from typing import List, Optional

# Optionnel : 'pip install rich' pour de jolies tables en console
try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
except ImportError:
    console = None

# ---------- modèles de données ----------
@dataclass
class Player:
    name: str; position: str; attack: int; defense: int

@dataclass
class Team:
    name: str; players: List[Player]
    points: int = 0; goals_for: int = 0; goals_against: int = 0
    matches_played: int = 0; lineup_indices: Optional[List[int]] = None
    @property
    def active(self): return [self.players[i] for i in (self.lineup_indices or range(11))]
    @property
    def attack_rating(self): return sum(p.attack for p in self.active)/11
    @property
    def defense_rating(self): return sum(p.defense for p in self.active)/11
    @property
    def diff(self): return self.goals_for - self.goals_against

def create_team(name:str)->Team:
    roles=['GK']+['DF']*5+['MF']*5+['FW']*5
    return Team(name,[Player(f"{name[:3]}P{i+1:02d}",r,
                             random.randint(50,90),random.randint(50,90))
                      for i,r in enumerate(roles)])

# ---------- moteur de match ----------
def simulate(h:Team,a:Team):
    h_atk=h.attack_rating+random.randint(-5,5)+3
    a_atk=a.attack_rating+random.randint(-5,5)
    h_def=h.defense_rating+random.randint(-5,5)
    a_def=a.defense_rating+random.randint(-5,5)
    hg=max(0,int((h_atk-a_def)/10)+random.randint(0,2))
    ag=max(0,int((a_atk-h_def)/10)+random.randint(0,2))
    h.goals_for+=hg; h.goals_against+=ag
    a.goals_for+=ag; a.goals_against+=hg
    h.matches_played+=1; a.matches_played+=1
    if hg>ag: h.points+=3
    elif ag>hg: a.points+=3
    else: h.points+=1; a.points+=1
    return hg,ag

# ---------- championnat ----------
class Championship:
    def __init__(self,teams:List[Team]):
        self.teams=teams; self.idx=0; self.log=[]
        self.fixtures=[(a,b) for i,a in enumerate(teams) for b in teams[i+1:]]*2
        random.shuffle(self.fixtures)
    def has_next(self): return self.idx<len(self.fixtures)
    def peek(self): return self.fixtures[self.idx]
    def play(self):
        h,a=self.fixtures[self.idx]; self.idx+=1
        hg,ag=simulate(h,a)
        res=f"{h.name} {hg}-{ag} {a.name}"
        self.log.append(res); return res
    def table(self): return sorted(self.teams,
                                   key=lambda t:(-t.points,t.diff,-t.goals_for))

# ---------- helpers console ----------
def show_table(champ: Championship, user: Team):
    if console:
        t=Table(title="Classement"); t.add_column("#"); t.add_column("Équipe")
        for c in("MJ","Pts","BP","BC","Diff"): t.add_column(c,justify="right")
        for i,tim in enumerate(champ.table(),1):
            style="bold yellow" if tim is user else ""
            t.add_row(str(i),tim.name,str(tim.matches_played),str(tim.points),
                      str(tim.goals_for),str(tim.goals_against),str(tim.diff),style=style)
        console.print(t)
    else:
        for i,tim in enumerate(champ.table(),1):
            star="*" if tim is user else " "
            print(i,star,tim.name,tim.points,tim.goals_for,
                  tim.goals_against,tim.diff)

def choose_lineup(team: Team):
    for i,p in enumerate(team.players,1):
        print(f"{i:2}. {p.name:12} {p.position} A:{p.attack} D:{p.defense}")
    while True:
        idx=[int(n)-1 for n in input("11 numéros : ").split() if n.isdigit()]
        if len(idx)==11 and any(team.players[i].position=='GK' for i in idx):
            team.lineup_indices=idx; return
        print("❌ 11 joueurs valides, dont 1 GK requis.")

# ---------- jeu console ----------
def console_game():
    clubs=["Paris FC","Marseille 13","Lyonnais","Monaco"]
    teams=[create_team(c) for c in clubs]
    for i,c in enumerate(clubs,1): print(i,c)
    user=teams[int(input("Votre club : "))-1]
    coach=input("Prénom entraîneur : ")+" "+input("Nom entraîneur : ")
    champ=Championship(teams)
    while champ.has_next():
        h,a=champ.peek()
        if user in(h,a): choose_lineup(user)
        input(f"{h.name} vs {a.name} – Entrée")
        print("Résultat :",champ.play())
        show_table(champ,user); print("="*40)

# ---------- jeu GUI ----------
def gui_game():
    try:
        import tkinter as tk
        from tkinter import ttk, scrolledtext, messagebox
    except ImportError:
        print("Tkinter absent – bascule console"); console_game(); return

    clubs=["Paris FC","Marseille 13","Lyonnais","Monaco"]
    teams=[create_team(c) for c in clubs]
    champ=Championship(teams); user:Optional[Team]=None

    root=tk.Tk(); root.title("FM 97/25"); root.geometry("1000x700")
    start=ttk.Frame(root,padding=20); start.pack(fill="both",expand=True)
    ttk.Label(start,text="Club :").grid(row=0,column=0,sticky="e")
    club=tk.StringVar(value=clubs[0])
    ttk.Combobox(start,textvariable=club,values=clubs,
                 state="readonly").grid(row=0,column=1,sticky="w")
    ttk.Label(start,text="Prénom coach :").grid(row=1,column=0,sticky="e")
    e_first=ttk.Entry(start,width=20); e_first.grid(row=1,column=1,sticky="w")
    ttk.Label(start,text="Nom coach :").grid(row=2,column=0,sticky="e")
    e_last=ttk.Entry(start,width=20); e_last.grid(row=2,column=1,sticky="w")

    def launch():
        nonlocal user
