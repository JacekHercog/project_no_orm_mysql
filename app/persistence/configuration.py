
from app.persistence.connection import connection_pool
from app.persistence.repository import TeamRepository, PlayerRepository, PlayerWithTeamRepository   

team_repository = TeamRepository(connection_pool)
player_repository = PlayerRepository(connection_pool)
player_with_team_repository = PlayerWithTeamRepository(connection_pool)