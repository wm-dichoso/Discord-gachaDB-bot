import sqlite3
import os


class DatabaseManager:
    def __init__(self, db_path="data.db"):
        self.db_path = db_path
        self.connection = None

    def connect_db(self):
        try:
            file_exists = os.path.exists(self.db_path)
            # this is the database connection !!
            self.connection = sqlite3.connect(self.db_path)

            if file_exists:
                print(f"Connected to the database: {self.db_path}")
            else:
                print(f"New database created in: {self.db_path}")

            return True

        except sqlite3.Error as e:
            print("Failed to connect to database")
            print(e)
            return False

    def is_connected(self):
        return self.connection is not None
        
    def create_tables(self):
        if not self.is_connected():
            print("Database is not connected")
            return False
        
        cur = self.connection.cursor()
        # tables for games, banner_name, pull_history, sessions, settings
        # me go ask ai, can you make me a query of this table with this columns and these pk and fk, ty !
        try:
            cur.executescript("""
                PRAGMA foreign_keys = ON;
                -- Meta table
                CREATE TABLE IF NOT EXISTS meta (
                    version TEXT DEFAULT '1.0.0',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_modified TEXT
                );

                -- Games table
                CREATE TABLE IF NOT EXISTS games (
                    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_name TEXT NOT NULL,
                    channel_id TEXT
                );

                -- Banners table
                CREATE TABLE IF NOT EXISTS banners (
                    banner_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER,
                    banner_name TEXT NOT NULL,
                    current_pity INTEGER DEFAULT 0,
                    last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES games(game_id)
                );

                -- Pull history table
                CREATE TABLE IF NOT EXISTS pull_history (
                    pull_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    banner_id INTEGER,
                    game_id INTEGER,
                    entry_name TEXT NOT NULL,
                    pity INTEGER DEFAULT 0,
                    notes TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (banner_id) REFERENCES banners(banner_id),
                    FOREIGN KEY (game_id) REFERENCES games(game_id)
                );

                -- Sessions table
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL,
                    start_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    end_time TEXT
                );

                -- Session breaks table
                CREATE TABLE IF NOT EXISTS session_breaks (
                    break_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    break_start TEXT DEFAULT CURRENT_TIMESTAMP,
                    break_end TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                );

                -- Settings table
                CREATE TABLE IF NOT EXISTS settings (
                    pagination_size INTEGER DEFAULT 10,
                    features_enabled TEXT DEFAULT '{}'
                );
                """)
        except sqlite3.OperationalError as e:
            print(f"SQLite error occurred: {e}")
            return False
        
        self.connection.commit()
        self.connection.close()
        return True
    

    # EXISTENCE CHECKS

    def game_exists(self):
        pass

    def banner_exists(self):
        pass

    def session_exists(self):
        pass

    # STATS HELPER

    def get_current_pity(self):
        pass

    def increment_pity(self):
        pass

    def reset_pity(self):
        pass 

    # crud operations for the tables apparently

    # for the meta table !!

    def get_meta(self):
        pass

    def update_meta(self):
        pass

    # for the games !!
    # should be able to: add new games, list all the games on the table, get a particular game 
    # and display some info, update a game info, delete the game from the table.
    def add_games(self):
        pass

    def get_game(self):
        pass

    def list_games(self):
        pass

    def update_game(self):
        pass

    def delete_game(self):
        pass

    # for the banners !!
    # add new banner/ banner name to the table, get a banner for a particular game,
    # update a banner's information.
    def add_banners(self):
        pass

    def get_banner(self):
        pass

    def get_game_banners(self):
        pass

    def update_banner_info(self):
        pass

    def delete_banner(self):
        pass

    # for the pull history !!
    # browse a list history of a particular banner, delete an entry
    def add_pull(self):
        pass

    def get_pulls_by_banner(self):
        pass

    def delete_pull(self):
        pass

    # for the session history !!
    # add new session, browse history of sessions, delete session
    def add_session(self):
        pass

    def end_session(self):
        pass

    def browse_sessions(self):
        pass

    def add_session_break(self):
        pass

    def end_session_break(self):
        pass

    def get_breaks_for_session(self):
        pass

    def delete_sessions(self):
        pass

    # for the settings table !!

    def get_settings(self):
        pass

    def update_settings(self):
        pass