import pytest
from unittest.mock import Mock, MagicMock
from app.service.players_with_teams import PlayersWithTeamsService
from app.service.dto import CreatePlayerWithTeamDto
from app.persistence.model import Player, Team
from app.persistence.repository import PlayerRepository, TeamRepository


class TestPlayersWithTeamsService:
    """Tests for PlayersWithTeamsService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_player_repository = Mock(spec=PlayerRepository)
        self.mock_team_repository = Mock(spec=TeamRepository)
        
        self.service = PlayersWithTeamsService(
            player_repository=self.mock_player_repository,
            team_repository=self.mock_team_repository
        )
    
    def test_service_initialization(self):
        """Test that service initializes correctly."""
        assert self.service.player_repository == self.mock_player_repository
        assert self.service.team_repository == self.mock_team_repository
    
    def test_add_player_with_team_success(self):
        """Test successful addition of player with existing team."""
        # Arrange
        dto = CreatePlayerWithTeamDto(
            player_name="John Doe",
            player_goals=5,
            team_name="Test Team"
        )
        
        # Mock team found in repository
        mock_team = Team(id_=1, name="Test Team", points=10)
        self.mock_team_repository.find_by_name.return_value = mock_team
        
        # Mock player insertion returning ID
        self.mock_player_repository.insert.return_value = 123
        
        # Act
        result = self.service.add_player_with_team(dto)
        
        # Assert
        assert result == 123
        
        # Verify team lookup
        self.mock_team_repository.find_by_name.assert_called_once_with("Test Team")
        
        # Verify player insertion
        self.mock_player_repository.insert.assert_called_once()
        inserted_player = self.mock_player_repository.insert.call_args[0][0]
        assert isinstance(inserted_player, Player)
        assert inserted_player.name == "John Doe"
        assert inserted_player.goals == 5
        assert inserted_player.team_id == 1
    
    def test_add_player_with_team_team_not_found(self):
        """Test adding player when team doesn't exist."""
        # Arrange
        dto = CreatePlayerWithTeamDto(
            player_name="Jane Doe",
            player_goals=3,
            team_name="Nonexistent Team"
        )
        
        # Mock team not found
        self.mock_team_repository.find_by_name.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Team name not found"):
            self.service.add_player_with_team(dto)
        
        # Verify team lookup was attempted
        self.mock_team_repository.find_by_name.assert_called_once_with("Nonexistent Team")
        
        # Verify player insertion was not attempted
        self.mock_player_repository.insert.assert_not_called()
    
    def test_add_player_with_team_empty_team_result(self):
        """Test adding player when team lookup returns falsy value."""
        # Arrange
        dto = CreatePlayerWithTeamDto(
            player_name="Bob Smith",
            player_goals=2,
            team_name="Empty Team"
        )
        
        # Mock team returns empty/falsy result (could be empty list, None, etc.)
        self.mock_team_repository.find_by_name.return_value = []
        
        # Act & Assert
        with pytest.raises(ValueError, match="Team name not found"):
            self.service.add_player_with_team(dto)
    
    def test_add_player_with_team_zero_goals(self):
        """Test adding player with zero goals."""
        # Arrange
        dto = CreatePlayerWithTeamDto(
            player_name="Zero Goals Player",
            player_goals=0,
            team_name="Test Team"
        )
        
        # Mock team found
        mock_team = Team(id_=2, name="Test Team", points=15)
        self.mock_team_repository.find_by_name.return_value = mock_team
        
        # Mock player insertion
        self.mock_player_repository.insert.return_value = 456
        
        # Act
        result = self.service.add_player_with_team(dto)
        
        # Assert
        assert result == 456
        inserted_player = self.mock_player_repository.insert.call_args[0][0]
        assert inserted_player.goals == 0
    
    def test_add_player_with_team_high_goals(self):
        """Test adding player with high number of goals."""
        # Arrange
        dto = CreatePlayerWithTeamDto(
            player_name="Goal Machine",
            player_goals=50,
            team_name="Champions"
        )
        
        # Mock team found
        mock_team = Team(id_=3, name="Champions", points=100)
        self.mock_team_repository.find_by_name.return_value = mock_team
        
        # Mock player insertion
        self.mock_player_repository.insert.return_value = 789
        
        # Act
        result = self.service.add_player_with_team(dto)
        
        # Assert
        assert result == 789
        inserted_player = self.mock_player_repository.insert.call_args[0][0]
        assert inserted_player.goals == 50
    
    def test_add_player_with_team_repository_exception(self):
        """Test handling repository exceptions."""
        # Arrange
        dto = CreatePlayerWithTeamDto(
            player_name="Exception Player",
            player_goals=1,
            team_name="Test Team"
        )
        
        # Mock team found
        mock_team = Team(id_=1, name="Test Team", points=10)
        self.mock_team_repository.find_by_name.return_value = mock_team
        
        # Mock player repository raising exception
        self.mock_player_repository.insert.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            self.service.add_player_with_team(dto)
    
    def test_add_player_with_team_team_lookup_exception(self):
        """Test handling team repository exceptions."""
        # Arrange
        dto = CreatePlayerWithTeamDto(
            player_name="Team Lookup Error",
            player_goals=1,
            team_name="Error Team"
        )
        
        # Mock team repository raising exception
        self.mock_team_repository.find_by_name.side_effect = Exception("Team lookup error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Team lookup error"):
            self.service.add_player_with_team(dto)
        
        # Verify player insertion was not attempted
        self.mock_player_repository.insert.assert_not_called()


class TestPlayersWithTeamsServiceIntegration:
    """Integration-style tests for PlayersWithTeamsService."""
    
    def test_dto_parameter_validation(self):
        """Test that DTO parameters are properly used."""
        # Arrange
        mock_player_repository = Mock(spec=PlayerRepository)
        mock_team_repository = Mock(spec=TeamRepository)
        service = PlayersWithTeamsService(mock_player_repository, mock_team_repository)
        
        dto = CreatePlayerWithTeamDto(
            player_name="Integration Test Player",
            player_goals=7,
            team_name="Integration Team"
        )
        
        # Mock successful flow
        mock_team = Team(id_=99, name="Integration Team", points=25)
        mock_team_repository.find_by_name.return_value = mock_team
        mock_player_repository.insert.return_value = 999
        
        # Act
        result = service.add_player_with_team(dto)
        
        # Assert
        assert result == 999
        
        # Verify all DTO fields were used correctly
        mock_team_repository.find_by_name.assert_called_once_with("Integration Team")
        
        call_args = mock_player_repository.insert.call_args[0][0]
        assert call_args.name == "Integration Test Player"
        assert call_args.goals == 7
        assert call_args.team_id == 99
    
    def test_service_workflow_complete(self):
        """Test complete workflow from DTO to player creation."""
        # Arrange
        mock_player_repository = Mock(spec=PlayerRepository)
        mock_team_repository = Mock(spec=TeamRepository)
        service = PlayersWithTeamsService(mock_player_repository, mock_team_repository)
        
        # Multiple DTOs to test
        dtos = [
            CreatePlayerWithTeamDto("Player 1", 3, "Team A"),
            CreatePlayerWithTeamDto("Player 2", 5, "Team B"),
            CreatePlayerWithTeamDto("Player 3", 1, "Team A")  # Same team as first
        ]
        
        # Mock teams
        team_a = Team(id_=1, name="Team A", points=20)
        team_b = Team(id_=2, name="Team B", points=15)
        
        mock_team_repository.find_by_name.side_effect = [team_a, team_b, team_a]
        mock_player_repository.insert.side_effect = [101, 102, 103]
        
        # Act
        results = [service.add_player_with_team(dto) for dto in dtos]
        
        # Assert
        assert results == [101, 102, 103]
        assert mock_team_repository.find_by_name.call_count == 3
        assert mock_player_repository.insert.call_count == 3
        
        # Verify team assignments
        player_calls = mock_player_repository.insert.call_args_list
        assert player_calls[0][0][0].team_id == 1  # Team A
        assert player_calls[1][0][0].team_id == 2  # Team B
        assert player_calls[2][0][0].team_id == 1  # Team A again
