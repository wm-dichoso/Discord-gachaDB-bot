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
   
    def game_exists(self, game_id):
        if not self.is_connected():
            print("Database is not connected")
            return False
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM games WHERE game_id = ?", (game_id,))

        return cur.fetchone() is not None
    
    def game_exists_with_name(self, game_name):
        if not self.is_connected():
            print("Database is not connected")
            return False
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM games WHERE game_name = ?", (game_name,))

        return cur.fetchone() is not None

    def game_exists_with_channel_ID(self, channel_id):        
        if not self.is_connected():
            print("Database is not connected")
            return False
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM games WHERE game_name = ?", (channel_id,))

        return cur.fetchone() is not None

    def banner_exists(self, banner_id):
        if not self.is_connected():
            print("Database is not connected")
            return False
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM banners WHERE banner_id = ?", (banner_id,))

        return cur.fetchone() is not None
    
    def banner_name_exists(self, game_id, banner_name):
        if not self.is_connected():
            print("Database is not connected")
            return False
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM banners WHERE banner_name = ? AND game_id = ?", (banner_name, game_id,))

        return cur.fetchone() is not None

    def pull_entry_exists(self, pull_id):
        if not self.is_connected():
            print("Database is not connected")
            return False
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM pull_history WHERE pull_id = ?",(pull_id,))

        return cur.fetchone() is not None
    
    def session_exists(self, session_id):
        if not self.is_connected():
            print("Database is not connected")
            return False
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))

        return cur.fetchone() is not None

    # STATS HELPER

    def get_current_pity(self, banner_id):
        if not self.is_connected():
            print("Database is not connected")
            return 
        
        cur = self.connection.cursor()
        cur.execute("SELECT current_pity FROM banners WHERE banner_id = ?", (banner_id,))
        res = cur.fetchone()
        return res[0]

    def increment_pity(self, banner_id, pity: int):
        if not self.is_connected():
            print("Database is not connected")
            return 
        
        if not self.banner_exists(banner_id):
            print("banner does not exists")
            return
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("SELECT current_pity FROM banners WHERE banner_id = ?", (banner_id,))
            res = cur.fetchone()
            print(f"current pity is {res[0]}")

            new_pity = int(res[0]) + pity

            cur.execute("UPDATE banners SET current_pity = ? WHERE banner_id = ?", (new_pity, banner_id,))
            print(f"pity updated from {res[0]} to {new_pity}")
            return cur.rowcount > 0

    def reset_pity(self, banner_id, pity):
        if not self.is_connected():
            print("Database is not connected")
            return 
        
        if not self.banner_exists(banner_id):
            print("banner does not exists")
            return
        
        with self.connection:
            cur = self.connection.cursor()
            cur.execute("UPDATE banners SET current_pity = ? WHERE banner_id = ?", (pity, banner_id,))
            return cur.rowcount > 0
 

    # crud operations for the tables apparently

    #region for the meta table !!

    def get_meta_version(self):
        if not self.is_connected():
            print("Database is not connected")
            return 
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM meta")
        res = cur.fetchone()
        return res[0]
    
    def add_version(self, version):
        if not self.is_connected():
            print("Database is not connected")
            return 
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("INSERT INTO meta (version, created_at, last_modified) VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)", (version,))
            print(f"version {version} is added to the meta")

    def update_version(self, version):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        cur = self.connection.cursor()
        cur.execute("UPDATE meta SET last_modified = CURRENT_TIMESTAMP WHERE version = ?", (version,))
        self.connection.commit()

        return cur.rowcount > 0
    
    # endregion

    #region for the games !!
    # should be able to: add new games, list all the games on the table, get a particular game 
    # and display some info, update a game info, delete the game from the table.
    def add_games(self, game, ch_id):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        # check if game already exists 
        if self.game_exists_with_name(game):
            print(f"Game {game} already exists")
            return False
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("INSERT INTO games (game_name, channel_id) VALUES (?, ?)", (game, ch_id,))
            print(f"Game {game} is added to the games table")
            return cur.rowcount > 0

    def get_game_by_id(self, game_id):
        if not self.is_connected():
            print("Database is not connected")
            return 
        
        if not self.game_exists():
            print(f"game with game id: {game_id} does not exists.")
            return
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM games WHERE game_id = ?",(game_id,))
        return cur.fetchone()
        
    def list_games(self):
        if not self.is_connected():
            print("Database is not connected")
            return 
        
        cur = self.connection.cursor()
        cur.execute("SELECT game_name FROM games")
        return cur.fetchall()

    def update_game_name(self, game_id, game_name):        
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        if not self.game_exists():
            print(f"game with game id: {game_id} does not exists.")
            return False
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("UPDATE games SET game_name = ? WHERE game_id = ?", (game_name, game_id,))
            return cur.rowcount > 0

    def update_game_channel(self, game_id, channel_id):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        if not self.game_exists():
            print(f"game with game id: {game_id} does not exists.")
            return False
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("UPDATE games SET channel_id = ? WHERE game_id = ?", (channel_id, game_id,))
            return cur.rowcount > 0

    def delete_game(self, game_id):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        if not self.game_exists():
            print(f"game with game id: {game_id} does not exists.")
            return False
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("DELETE FROM games WHERE game_id = ?", (game_id,))
            return cur.rowcount > 0
        
    # endregion

    #region for the banners !!
    # add new banner/ banner name to the table, get a banner for a particular game,
    # update a banner's information.

    def add_banner(self, game_id, banner_name, current_pity, max_pity):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        # check if banner already exists first 
        if self.banner_name_exists(game_id, banner_name):
            print(f"Banner: {banner_name} already exists on the game id: {game_id}")
            return False
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("INSERT INTO banners (game_id, banner_name, current_pity, max_pity) VALUES (?, ?, ?, ?)", (game_id, banner_name,current_pity, max_pity,))
            print(f"Banner: {banner_name} is added to db")
            return cur.rowcount > 0

    def get_banner(self, banner_id):
        if not self.is_connected():
            print("Database is not connected")
            return 
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM banners WHERE banner_id = ?", (banner_id,))
        res = cur.fetchone()
        return res

    def get_game_banners(self, game_id):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        if not self.game_exists(game_id):
            print(f"Game id: {game_id} does not exists")
            return False
        
        cur = self.connection.cursor()
        cur.execute("SELECT banner_name, current_pity, last_updated FROM banners WHERE game_id = ?", (game_id,))
        return cur.fetchall()

    def update_banner_name(self, banner_id, new_banner_name):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        if not self.banner_exists():
            print(f"Banner with banner id: {banner_id} does not exists.")
            return False
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("UPDATE banners SET banner_name = ? WHERE banner_id = ?", (new_banner_name, banner_id,))
            return cur.rowcount > 0

    def update_banner_pity(self, banner_id, new_pity):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        if not self.banner_exists():
            print(f"Banner with banner id: {banner_id} does not exists.")
            return False
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("UPDATE banners SET current_pity = ? WHERE banner_id = ?", (new_pity, banner_id,))
            return cur.rowcount > 0
    
    def update_banner_max_pity(self, banner_id, new_max_pity):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        if not self.banner_exists():
            print(f"Banner with banner id: {banner_id} does not exists.")
            return False
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("UPDATE banners SET max_pity = ? WHERE banner_id = ?", (new_max_pity, banner_id,))
            return cur.rowcount > 0

    def delete_banner(self, banner_id):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        if not self.banner_exists(banner_id):
            print(f"Cannot be deleted. Banner with banner id: {banner_id} does not exists.")
            return False
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("DELETE FROM banners WHERE banner_id = ?", (banner_id,))
            return cur.rowcount > 0
        
    # endregion

    # for the pull history !!
    # browse a list history of a particular banner, delete an entry

    def add_pull(self, entry_name, banner_id, pity, notes):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        # check if banner for this pull actually xists 
        if not self.banner_exists(banner_id):
            print(f"Banner id: {banner_id} does not exists")
            return False
        
        with self.connection:        
            cur = self.connection.cursor()            
            cur.execute("""
                INSERT INTO pull_history (banner_id, game_id, entry_name, pity, notes)
                SELECT
                    b.banner_id, b.game_id, ?, ?, ?
                FROM banners b
                WHERE b.banner_id = ?
            """, (entry_name, pity, notes, banner_id))
            print(f"Added new unit")
            return cur.rowcount > 0

    def get_pulls_by_banner(self, banner_id):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        if not self.banner_exists(banner_id):
            print(f"banner id: {banner_id} does not exists")
            return False
        
        cur = self.connection.cursor()
        cur.execute("SELECT entry_name, pity, notes, timestamp FROM pull_history WHERE banner_id = ?", (banner_id,))
        return cur.fetchall()
        
    def delete_pull(self, pull_id):
        if not self.is_connected():
            print("Database is not connected")
            return False
        
        if not self.pull_entry_exists(pull_id):
            print(f"Cannot be deleted. pull entry id: {pull_id} does not exist.")
            return False
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("DELETE FROM pull_history WHERE pull_id = ?", (pull_id,))
            return cur.rowcount > 0

    # for the session history !!
    # add new session, browse history of sessions, delete session
    # SQLITE CURRENT_TIMESTAMP DEFAULTS TO UTC. JUST CONVERT IT TO LOCAL TIME VIA BACKEND XD

    def start_session(self, session_name):
        if not self.is_connected():
            print("Database is not connected")
            return False 
                
        with self.connection:        
            cur = self.connection.cursor()            
            cur.execute("""
                INSERT INTO sessions (session_id, session_name) VALUES (?)
            """, (session_name))
            print(f"Added new session")
            return cur.rowcount > 0

    def end_session(self, session_id, end_time):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        if not self.session_exists(session_id):
            print(f"session id: {session_id} does not exists.")
            return False
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("UPDATE sessions SET end_time = ? WHERE session_id = ?", (end_time, session_id,))
            return cur.rowcount > 0

    def browse_sessions(self):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM sessions")
        return cur.fetchall()

    def add_session_break(self, session_id):
        if not self.is_connected():
            print("Database is not connected")
            return False 
                
        with self.connection:        
            cur = self.connection.cursor()            
            cur.execute("""
                INSERT INTO session_breaks (session_id) VALUES (?)
            """, (session_id))
            print(f"Added new session break for the session id: {session_id}")
            return cur.rowcount > 0

    def end_session_break(self, break_session_id):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        if not self.break_session_exists(break_session_id):
            print(f"break session id: {break_session_id} does not exists.")
            return False
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("UPDATE session_breaks SET break_end = CURRENT_TIMESTAMP WHERE break_id = ?", (break_session_id,))
            return cur.rowcount > 0

    def get_breaks_for_session(self, session_id):
        if not self.is_connected():
            print("Database is not connected")
            return False 
        
        if not self.break_session_exists(session_id):
            print(f"session id: {session_id} does not exists")
            return False
        
        cur = self.connection.cursor()
        cur.execute("SELECT break_start, break_end FROM session_breaks WHERE session_id = ?", (session_id,))
        return cur.fetchall()

    def delete_session(self, session_id):
        if not self.is_connected():
            print("Database is not connected")
            return False
        
        if not self.session_exists(session_id):
            print(f"Cannot be deleted. session id: {session_id} does not exist.")
            return False
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            return cur.rowcount > 0
        
    def delete_break_session(self, break_id):
            if not self.is_connected():
                print("Database is not connected")
                return False
            
            if not self.break_session_exists(break_id):
                print(f"Cannot be deleted. break session id: {break_id} does not exist.")
                return False
            
            with self.connection:
                cur = self.connection.cursor()
                cur.execute("DELETE FROM session_breaks WHERE break_id = ?", (break_id,))

                # TODO: we also have to decrease the total break time on session lol

                return cur.rowcount > 0

    # for the settings table !!

    def get_settings(self):
        if not self.is_connected():
            print("Database is not connected")
            return None 
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM settings")
        return cur.fetchall()

    def update_pagination(self,p_size):
        if not self.is_connected():
            print("Database is not connected")
            return None 
        
        with self.connection:        
            cur = self.connection.cursor()
            cur.execute("UPDATE settings SET pagination_size = ? WHERE id = 1",(p_size,))
            return cur.rowcount > 0