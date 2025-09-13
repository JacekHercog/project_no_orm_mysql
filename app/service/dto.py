from dataclasses import dataclass

@dataclass
class CreatePlayerWithTeamDto:
    player_name: str
    player_goals: int
    team_name: str