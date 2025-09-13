from dataclasses import dataclass

# --------------------------------------------------
# ENTITIES
# --------------------------------------------------
@dataclass
class Team:
    id_: int | None = None
    name: str | None = None
    points: int | None = 0

    def has_points_between(self, points_from: int, points_to: int) -> bool:
        if self.points is None:
            return False
        return points_from <= self.points <= points_to


@dataclass
class Player:
    id_: int | None = None
    name: str | None = None
    goals: int | None = 0
    team_id: int | None = None


# --------------------------------------------------
# VIEWS
# --------------------------------------------------
@dataclass
class PlayerWithTeamView:
    player_id: int
    player_name: str
    player_goals: int
    team_id: int
    team_name: str