import pytest
from unittest.mock import Mock, MagicMock, patch
from mysql.connector.pooling import MySQLConnectionPool
from app.persistence.repository import CrudRepository, TeamRepository, PlayerRepository, PlayerWithTeamRepository
from app.persistence.model import Team, Player, PlayerWithTeamView


class TestCrudRepository:
    """Tests for CrudRepository base class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_pool = Mock(spec=MySQLConnectionPool)
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        
        # Configure the mock chain properly for context manager
        context_manager = MagicMock()
        context_manager.__enter__.return_value = self.mock_connection
        context_manager.__exit__.return_value = None
        self.mock_pool.get_connection.return_value = context_manager
        self.mock_connection.cursor.return_value = self.mock_cursor
    
    def test_crud_repository_initialization(self):
        """Test CrudRepository initialization."""
        repo = TeamRepository(self.mock_pool)
        
        assert repo._connection_pool == self.mock_pool
        assert repo._entity == Team
        assert repo._entity_type == Team
    
    def test_insert_method(self):
        """Test insert method."""
        repo = TeamRepository(self.mock_pool)
        team = Team(name="Test Team", points=10)
        
        # Mock the lastrowid
        self.mock_cursor.lastrowid = 123
        
        result = repo.insert(team)
        
        assert result == 123
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()
    
    def test_insert_many_method(self):
        """Test insert_many method."""
        repo = TeamRepository(self.mock_pool)
        teams = [
            Team(name="Team A", points=10),
            Team(name="Team B", points=15)
        ]
        
        # Mock the lastrowid
        self.mock_cursor.lastrowid = 456
        
        result = repo.insert_many(teams)
        
        assert result == 456
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()
    
    def test_find_all_method(self):
        """Test find_all method."""
        repo = TeamRepository(self.mock_pool)
        
        # Mock fetchall return value
        self.mock_cursor.fetchall.return_value = [
            (1, "Team A", 10),
            (2, "Team B", 15)
        ]
        
        result = repo.find_all()
        
        assert len(result) == 2
        assert isinstance(result[0], Team)
        assert result[0].name == "Team A"
        assert result[0].points == 10
        self.mock_cursor.execute.assert_called_once()
    
    def test_find_by_id_method(self):
        """Test find_by_id method."""
        repo = TeamRepository(self.mock_pool)
        
        # Mock fetchone return value
        self.mock_cursor.fetchone.return_value = (1, "Test Team", 10)
        
        result = repo.find_by_id(1)
        
        assert result == (1, "Test Team", 10)
        self.mock_cursor.execute.assert_called_once()
    
    def test_find_by_id_not_found(self):
        """Test find_by_id when record not found."""
        repo = TeamRepository(self.mock_pool)
        
        # Mock fetchone return value for not found
        self.mock_cursor.fetchone.return_value = None
        
        result = repo.find_by_id(999)
        
        assert result is None
        self.mock_cursor.execute.assert_called_once()
    
    def test_update_method(self):
        """Test update method."""
        repo = TeamRepository(self.mock_pool)
        team = Team(id_=1, name="Updated Team", points=20)
        
        result = repo.update(1, team)
        
        assert result == 1
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()
    
    def test_delete_method(self):
        """Test delete method."""
        repo = TeamRepository(self.mock_pool)
        
        result = repo.delete(1)
        
        assert result == 1
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()
    
    def test_delete_all_method(self):
        """Test delete_all method."""
        repo = TeamRepository(self.mock_pool)
        
        repo.delete_all()
        
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()
    
    def test_table_name_generation(self):
        """Test table name generation."""
        repo = TeamRepository(self.mock_pool)
        table_name = repo._table_name()
        
        # inflection.tableize("Team") should return "teams"
        assert table_name == "teams"
    
    def test_field_names_extraction(self):
        """Test field names extraction."""
        repo = TeamRepository(self.mock_pool)
        field_names = repo._field_names()
        
        expected_fields = ['id_', 'name', 'points']
        assert set(field_names) == set(expected_fields)


class TestTeamRepository:
    """Tests for TeamRepository specific functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_pool = Mock(spec=MySQLConnectionPool)
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        
        # Configure the mock chain properly for context manager
        context_manager = MagicMock()
        context_manager.__enter__.return_value = self.mock_connection
        context_manager.__exit__.return_value = None
        self.mock_pool.get_connection.return_value = context_manager
        self.mock_connection.cursor.return_value = self.mock_cursor
    
    def test_find_by_name_found(self):
        """Test find_by_name when team is found."""
        repo = TeamRepository(self.mock_pool)
        
        # Mock fetchone return value
        self.mock_cursor.fetchone.return_value = (1, "Test Team", 10)
        
        result = repo.find_by_name("Test Team")
        
        assert isinstance(result, Team)
        assert result.name == "Test Team"
        assert result.points == 10
        self.mock_cursor.execute.assert_called_once()
    
    def test_find_by_name_not_found(self):
        """Test find_by_name when team is not found."""
        repo = TeamRepository(self.mock_pool)
        
        # Mock fetchone return value for not found
        self.mock_cursor.fetchone.return_value = None
        
        result = repo.find_by_name("Nonexistent Team")
        
        assert result is None
        self.mock_cursor.execute.assert_called_once()
    
    def test_find_all_by_points_between(self):
        """Test find_all_by_points_between method."""
        repo = TeamRepository(self.mock_pool)
        
        # Mock fetchall return value
        self.mock_cursor.fetchall.return_value = [
            (1, "Team A", 15),
            (2, "Team B", 18)
        ]
        
        result = repo.find_all_by_points_between(10, 20)
        
        assert len(result) == 2
        assert isinstance(result[0], Team)
        assert result[0].points == 15
        self.mock_cursor.execute.assert_called_once()


class TestPlayerRepository:
    """Tests for PlayerRepository functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_pool = Mock(spec=MySQLConnectionPool)
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        
        # Configure the mock chain properly for context manager
        context_manager = MagicMock()
        context_manager.__enter__.return_value = self.mock_connection
        context_manager.__exit__.return_value = None
        self.mock_pool.get_connection.return_value = context_manager
        self.mock_connection.cursor.return_value = self.mock_cursor
    
    def test_player_repository_initialization(self):
        """Test PlayerRepository initialization."""
        repo = PlayerRepository(self.mock_pool)
        
        assert repo._connection_pool == self.mock_pool
        assert repo._entity == Player
        assert repo._entity_type == Player
    
    def test_player_table_name_generation(self):
        """Test table name generation for players."""
        repo = PlayerRepository(self.mock_pool)
        table_name = repo._table_name()
        
        # inflection.tableize("Player") should return "players"
        assert table_name == "players"
    
    def test_player_insert(self):
        """Test inserting a player."""
        repo = PlayerRepository(self.mock_pool)
        player = Player(name="Test Player", goals=5, team_id=1)
        
        # Mock the lastrowid
        self.mock_cursor.lastrowid = 456
        
        result = repo.insert(player)
        
        assert result == 456
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()


class TestPlayerWithTeamRepository:
    """Tests for PlayerWithTeamRepository functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_pool = Mock(spec=MySQLConnectionPool)
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        
        # Configure the mock chain properly for context manager
        context_manager = MagicMock()
        context_manager.__enter__.return_value = self.mock_connection
        context_manager.__exit__.return_value = None
        self.mock_pool.get_connection.return_value = context_manager
        self.mock_connection.cursor.return_value = self.mock_cursor
    
    def test_player_with_team_repository_initialization(self):
        """Test PlayerWithTeamRepository initialization."""
        repo = PlayerWithTeamRepository(self.mock_pool)
        
        assert repo.connection_pool == self.mock_pool
    
    def test_find_all_players_with_teams_empty_implementation(self):
        """Test find_all_players_with_teams method (currently returns empty list)."""
        repo = PlayerWithTeamRepository(self.mock_pool)
        
        result = repo.find_all_players_with_teams(10, 20)
        
        # Current implementation returns empty list
        assert result == []
        assert isinstance(result, list)


class TestRepositoryIntegration:
    """Integration tests for repository interactions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_pool = Mock(spec=MySQLConnectionPool)
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        
        # Configure the mock chain properly for context manager
        context_manager = MagicMock()
        context_manager.__enter__.return_value = self.mock_connection
        context_manager.__exit__.return_value = None
        self.mock_pool.get_connection.return_value = context_manager
        self.mock_connection.cursor.return_value = self.mock_cursor
    
    def test_team_and_player_repository_interaction(self):
        """Test interaction between team and player repositories."""
        team_repo = TeamRepository(self.mock_pool)
        player_repo = PlayerRepository(self.mock_pool)
        
        # Mock team insertion
        self.mock_cursor.lastrowid = 1
        team = Team(name="Test Team", points=10)
        team_id = team_repo.insert(team)
        
        # Mock player insertion
        self.mock_cursor.lastrowid = 1
        player = Player(name="Test Player", goals=5, team_id=team_id)
        player_id = player_repo.insert(player)
        
        assert team_id == 1
        assert player_id == 1
        assert player.team_id == team_id
