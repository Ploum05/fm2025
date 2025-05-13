# Football Manager 97/25 – v1.1 (coach + écran plus propre)
from __future__ import annotations
import random
from dataclasses import dataclass
from typing import List, Optional

try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
except ImportError:
    console = None

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
    pl=[Player(f"{name[:3]}P{i+1:02d}",r,random.randint(50,90),random.randint(50,90))
        for i,r in enumerate(roles)]
    return Team(name,pl)

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
    def table(self): return sorted(self.teams,key=lambda t:(-t.points,t.diff,-t.goals_for))

def show_table(ch,user):
    for i,t in enumerate(ch.table(),1):
        star="*" if t is user else " "
        print(f"{i}{star} {t.name:12} {t.points:3} {t.goals_for:2} {t.goals_against:2} {t.diff:3}")

def choose_lineup(team):
    for i,p in enumerate(team.players,1):
        print(f"{i:2}. {p.name:12} {p.position} A:{p.attack} D:{p.defense}")
    while True:
        nums=input("11 numéros : ").split()
        idx=[int(n)-1 for n in nums if n.isdigit()]
        if len(idx)==11 and any(team.players[i].position=='GK' for i in idx):
            team.lineup_indices=idx; return
        print("Il faut 11 joueurs dont 1 GK.")

def console_game():
    clubs=["Paris FC","Marseille 13","Lyonnais","Monaco"]
    teams=[create_team(c) for c in clubs]
    for i,c in enumerate(clubs,1): print(i,c)
    user=teams[int(input("Votre club : "))-1]
    coach=input("Prénom entraîneur : ")+" "+input("Nom entraîneur : ")
    print("Bienvenue",coach,"!")
    champ=Championship(teams)
    while champ.has_next():
        h,a=champ.peek()
        if user in (h,a): choose_lineup(user)
        input(f"{h.name} vs {a.name} – Entrée")
        print("Résultat :",champ.play())
        show_table(champ,user); print("="*40)

if __name__=="__main__":
    console_game()
