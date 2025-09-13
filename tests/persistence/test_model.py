import pytest
from app.persistence.model import Team, Player, PlayerWithTeamView


class TestTeam:
    """Tests for Team model."""
    
    def test_team_creation_with_defaults(self):
        """Test creating a team with default values."""
        team = Team()
        assert team.id_ is None
        assert team.name is None
        assert team.points == 0
    
    def test_team_creation_with_values(self):
        """Test creating a team with specific values."""
        team = Team(id_=1, name="Test Team", points=15)
        assert team.id_ == 1
        assert team.name == "Test Team"
        assert team.points == 15
    
    def test_team_has_points_between_valid_range(self):
        """Test has_points_between method with valid points."""
        team = Team(points=10)
        assert team.has_points_between(5, 15) is True
        assert team.has_points_between(10, 10) is True
        assert team.has_points_between(0, 20) is True
    
    def test_team_has_points_between_invalid_range(self):
        """Test has_points_between method outside valid range."""
        team = Team(points=10)
        assert team.has_points_between(15, 20) is False
        assert team.has_points_between(0, 5) is False
    
    def test_team_has_points_between_none_points(self):
        """Test has_points_between method with None points."""
        team = Team(points=None)
        assert team.has_points_between(0, 10) is False
    
    def test_team_has_points_between_edge_cases(self):
        """Test has_points_between method edge cases."""
        team = Team(points=10)
        assert team.has_points_between(10, 10) is True  # Exact match
        assert team.has_points_between(9, 11) is True   # Within range
        assert team.has_points_between(11, 15) is False # Above range
        assert team.has_points_between(0, 9) is False   # Below range


class TestPlayer:
    """Tests for Player model."""
    
    def test_player_creation_with_defaults(self):
        """Test creating a player with default values."""
        player = Player()
        assert player.id_ is None
        assert player.name is None
        assert player.goals == 0
        assert player.team_id is None
    
    def test_player_creation_with_values(self):
        """Test creating a player with specific values."""
        player = Player(id_=1, name="Test Player", goals=5, team_id=2)
        assert player.id_ == 1
        assert player.name == "Test Player"
        assert player.goals == 5
        assert player.team_id == 2
    
    def test_player_creation_partial_values(self):
        """Test creating a player with some values."""
        player = Player(name="Partial Player", team_id=3)
        assert player.id_ is None
        assert player.name == "Partial Player"
        assert player.goals == 0  # Default value
        assert player.team_id == 3


class TestPlayerWithTeamView:
    """Tests for PlayerWithTeamView model."""
    
    def test_player_with_team_view_creation(self):
        """Test creating a PlayerWithTeamView."""
        view = PlayerWithTeamView(
            player_id=1,
            player_name="John Doe",
            player_goals=5,
            team_id=2,
            team_name="Test Team"
        )
        assert view.player_id == 1
        assert view.player_name == "John Doe"
        assert view.player_goals == 5
        assert view.team_id == 2
        assert view.team_name == "Test Team"
    
    def test_player_with_team_view_all_required(self):
        """Test that all fields are required for PlayerWithTeamView."""
        # This should work without raising an exception
        view = PlayerWithTeamView(
            player_id=1,
            player_name="Jane Doe",
            player_goals=3,
            team_id=1,
            team_name="Another Team"
        )
        assert view is not None
    
    def test_player_with_team_view_dataclass_equality(self):
        """Test dataclass equality for PlayerWithTeamView."""
        view1 = PlayerWithTeamView(
            player_id=1,
            player_name="John Doe",
            player_goals=5,
            team_id=2,
            team_name="Test Team"
        )
        view2 = PlayerWithTeamView(
            player_id=1,
            player_name="John Doe",
            player_goals=5,
            team_id=2,
            team_name="Test Team"
        )
        view3 = PlayerWithTeamView(
            player_id=2,
            player_name="Jane Doe",
            player_goals=3,
            team_id=1,
            team_name="Another Team"
        )
        
        assert view1 == view2
        assert view1 != view3


class TestModelIntegration:
    """Integration tests for model interactions."""
    
    def test_team_and_player_relationship(self):
        """Test the logical relationship between Team and Player."""
        team = Team(id_=1, name="Test Team", points=20)
        player1 = Player(id_=1, name="Player 1", goals=5, team_id=team.id_)
        player2 = Player(id_=2, name="Player 2", goals=3, team_id=team.id_)
        
        # Verify relationship
        assert player1.team_id == team.id_
        assert player2.team_id == team.id_
        
        # Test team points filtering with players
        assert team.has_points_between(15, 25) is True
    
    def test_view_creation_from_models(self):
        """Test creating a view from Team and Player models."""
        team = Team(id_=1, name="Test Team", points=20)
        player = Player(id_=1, name="Test Player", goals=5, team_id=team.id_)
        
        # Create view (simulating what would happen in repository)
        view = PlayerWithTeamView(
            player_id=player.id_,
            player_name=player.name,
            player_goals=player.goals,
            team_id=team.id_,
            team_name=team.name
        )
        
        assert view.player_id == player.id_
        assert view.player_name == player.name
        assert view.player_goals == player.goals
        assert view.team_id == team.id_
        assert view.team_name == team.name
