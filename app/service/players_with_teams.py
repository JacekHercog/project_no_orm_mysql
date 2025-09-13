import logging

from app.persistence.model import Player, Team
from app.persistence.repository import PlayerRepository, TeamRepository
from app.service.dto import CreatePlayerWithTeamDto
from dataclasses import dataclass

@dataclass
class PlayersWithTeamsService:
    player_repository: PlayerRepository
    team_repository: TeamRepository

    def add_player_with_team(self, createPlayerWithTeamDto: CreatePlayerWithTeamDto) -> int:
        team = self.team_repository.find_by_name(createPlayerWithTeamDto.team_name)
        if not team:
            raise ValueError('Team name not found')
        player = Player(
            name=createPlayerWithTeamDto.player_name,
            goals=createPlayerWithTeamDto.player_goals,
            team_id=team.id_
        )
        return self.player_repository.insert(player)
