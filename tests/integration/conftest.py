import pytest
from mysql.connector.pooling import MySQLConnectionPool
from app.persistence.connection import MySQLConnectionPoolBuilder, create_tables, drop_tables


@pytest.fixture(scope="session")
def test_database_pool() -> MySQLConnectionPool:
    """Create a test database connection pool for integration tests."""
    pool = MySQLConnectionPoolBuilder.builder().database("test_db").build()
    return pool


@pytest.fixture(scope="function")
def clean_database(test_database_pool: MySQLConnectionPool):
    """Ensure clean database state for each test."""
    # Setup: Create tables
    create_tables(test_database_pool)
    
    yield test_database_pool
    
    # Teardown: Drop tables
    drop_tables(test_database_pool)


@pytest.fixture
def sample_teams_data():
    """Sample team data for testing."""
    return [
        {"name": "Team A", "points": 10},
        {"name": "Team B", "points": 15},
        {"name": "Team C", "points": 8}
    ]


@pytest.fixture
def sample_players_data():
    """Sample player data for testing."""
    return [
        {"name": "Player 1", "goals": 5, "team_id": 1},
        {"name": "Player 2", "goals": 3, "team_id": 1},
        {"name": "Player 3", "goals": 7, "team_id": 2}
    ]
