from app.persistence.configuration import player_repository, team_repository
from app.persistence.connection import create_tables, drop_tables, connection_pool
from app.service.players_with_teams import PlayersWithTeamsService
from app.service.dto import CreatePlayerWithTeamDto
import logging

logging.basicConfig(level=logging.INFO)

def main() -> None:
    # create_tables(connection_pool)
    player_with_teams_service = PlayersWithTeamsService(player_repository, team_repository)
    player_with_teams_service.add_player_with_team(CreatePlayerWithTeamDto(
        player_name='B',
        player_goals=12,
        team_name='A'
    ))
    # drop_tables(connection_pool)

if __name__ == '__main__':
    main()