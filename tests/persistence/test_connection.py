import pytest
from unittest.mock import Mock, MagicMock
from mysql.connector.pooling import MySQLConnectionPool
from app.persistence.connection import MySQLConnectionPoolBuilder, create_tables, drop_tables


class TestConnection:
    """Tests for database connection functionality."""
    
    def test_connection_pool_builder_default_values(self):
        """Test that connection pool builder has correct default values."""
        builder = MySQLConnectionPoolBuilder()
        config = builder._pool_config
        
        assert config['pool_name'] == 'my_pool'
        assert config['pool_size'] == 5
        assert config['host'] == 'localhost'
        assert config['database'] == 'db'  # Fixed: should be 'db', not 'db_1'
        assert config['user'] == 'user'
        assert config['password'] == 'user1234'
        assert config['port'] == 3306
    
    def test_connection_pool_builder_fluent_interface(self):
        """Test that builder methods return self for fluent interface."""
        builder = MySQLConnectionPoolBuilder()
        
        result = builder.pool_size(10)
        assert result is builder
        
        result = builder.user('test_user')
        assert result is builder
        
        result = builder.password('test_pass')
        assert result is builder
        
        result = builder.database('test_db')
        assert result is builder
        
        result = builder.port(3308)
        assert result is builder
    
    def test_connection_pool_builder_configuration_updates(self):
        """Test that builder methods update configuration correctly."""
        builder = MySQLConnectionPoolBuilder()
        
        builder.pool_size(10).user('test_user').password('test_pass').database('test_db').port(3308)
        
        config = builder._pool_config
        assert config['pool_size'] == 10
        assert config['user'] == 'test_user'
        assert config['password'] == 'test_pass'
        assert config['database'] == 'test_db'
        assert config['port'] == 3308
    
    def test_connection_pool_builder_class_method(self):
        """Test that builder class method returns instance."""
        builder = MySQLConnectionPoolBuilder.builder()
        assert isinstance(builder, MySQLConnectionPoolBuilder)
    
    @pytest.mark.skip(reason="Requires actual MySQL server connection")
    def test_connection_pool_build(self):
        """Test that build method returns MySQLConnectionPool."""
        builder = MySQLConnectionPoolBuilder.builder().database('test_db')
        pool = builder.build()
        assert isinstance(pool, MySQLConnectionPool)
    
    def test_create_tables_with_mock(self):
        """Test create_tables function with mocked connection."""
        # Create mock connection pool
        mock_pool = Mock(spec=MySQLConnectionPool)
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        
        # Configure mock chain
        context_manager = MagicMock()
        context_manager.__enter__.return_value = mock_connection
        context_manager.__exit__.return_value = None
        mock_pool.get_connection.return_value = context_manager
        mock_connection.cursor.return_value = mock_cursor
        
        # Call function
        create_tables(mock_pool)
        
        # Verify calls
        mock_pool.get_connection.assert_called_once()
        mock_connection.cursor.assert_called_once()
        assert mock_cursor.execute.call_count == 2  # Should execute 2 SQL statements
    
    def test_drop_tables_with_mock(self):
        """Test drop_tables function with mocked connection."""
        # Create mock connection pool
        mock_pool = Mock(spec=MySQLConnectionPool)
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        
        # Configure mock chain
        context_manager = MagicMock()
        context_manager.__enter__.return_value = mock_connection
        context_manager.__exit__.return_value = None
        mock_pool.get_connection.return_value = context_manager
        mock_connection.cursor.return_value = mock_cursor
        
        # Call function
        drop_tables(mock_pool)
        
        # Verify calls
        mock_pool.get_connection.assert_called_once()
        mock_connection.cursor.assert_called_once()
        assert mock_cursor.execute.call_count == 2  # Should execute 2 SQL statements
    
    @pytest.mark.skip(reason="Requires actual MySQL server connection")
    @pytest.mark.integration
    def test_create_tables(self):
        """Test table creation functionality."""
        # This test requires actual database connection
        # Should be run with integration test database
        test_pool = MySQLConnectionPoolBuilder.builder().database('test_db').build()
        
        # Should not raise exception
        create_tables(test_pool)
        
        # Verify tables exist by trying to query them
        with test_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check teams table
            cursor.execute("SHOW TABLES LIKE 'teams'")
            teams_table = cursor.fetchone()
            assert teams_table is not None
            
            # Check players table
            cursor.execute("SHOW TABLES LIKE 'players'")
            players_table = cursor.fetchone()
            assert players_table is not None
        
        # Cleanup
        drop_tables(test_pool)
    
    @pytest.mark.skip(reason="Requires actual MySQL server connection")
    @pytest.mark.integration
    def test_drop_tables(self):
        """Test table dropping functionality."""
        # This test requires actual database connection
        test_pool = MySQLConnectionPoolBuilder.builder().database('test_db').build()
        
        # First create tables
        create_tables(test_pool)
        
        # Then drop them
        drop_tables(test_pool)
        
        # Verify tables don't exist
        with test_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check teams table doesn't exist
            cursor.execute("SHOW TABLES LIKE 'teams'")
            teams_table = cursor.fetchone()
            assert teams_table is None
            
            # Check players table doesn't exist
            cursor.execute("SHOW TABLES LIKE 'players'")
            players_table = cursor.fetchone()
            assert players_table is None
