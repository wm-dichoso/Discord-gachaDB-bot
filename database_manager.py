import sqlite3
import os
from help import Result


class DatabaseManager:
    def __init__(self, db_path="data.db"):
        self.db_path = db_path
        self.connection = None

    def connect_db(self):
        try:
            file_exists = os.path.exists(self.db_path)
            # this is the database connection !!
            self.connection = sqlite3.connect(self.db_path)

            db_message = ""
            if file_exists:
                db_message = f"Connected to the database: {self.db_path}"
            else:
                db_message= f"New database created in: {self.db_path}"

            return Result.ok(
                code="DB_CONNECTED",
                message= db_message
            )

        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error occurred while connecting",
                error=str(e)
            )

    def is_connected(self):
        return self.connection is not None
        
    def create_tables(self):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't create table: Failed to connect to the database"
            )
        
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
                    max_pity INTEGER DEFAULT 0,
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
                    id INTEGER DEFAULT 1 CHECK("id" = 1),
                    pagination_size INTEGER DEFAULT 10,
                    features_enabled TEXT DEFAULT '{}',
                    PRIMARY KEY("id")
                );
                """)
        except sqlite3.OperationalError as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error occurred during table creation",
                error=str(e)
            )
        
        self.connection.commit()
        return Result.ok(
            code="TABLES_READY",
            message="Database tables are ready"
        )
    

    #region EXISTENCE CHECKS
   
    def game_exists(self, game_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM games WHERE game_id = ?", (game_id,))

        return cur.fetchone() is not None
    
    def game_exists_with_name(self, game_name):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM games WHERE game_name = ?", (game_name,))

        return cur.fetchone() is not None

    def game_exists_with_channel_ID(self, channel_id):  
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM games WHERE channel_id = ?", (channel_id,))

        return cur.fetchone() is not None

    def banner_exists(self, banner_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM banners WHERE banner_id = ?", (banner_id,))

        return cur.fetchone() is not None
    
    def banner_name_exists(self, banner_name):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM banners WHERE banner_name = ?", (banner_name,))

        return cur.fetchone() is not None

    def pull_entry_exists(self, pull_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM pull_history WHERE pull_id = ?",(pull_id,))

        return cur.fetchone() is not None
    
    def session_exists(self, session_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))

        return cur.fetchone() is not None
    
    def break_session_exists(self, break_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM session_breaks WHERE break_id = ?", (break_id,))

        return cur.fetchone() is not None

    #endregion

    #region STATS HELPER for banners

    def get_current_pity(self, banner_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't get current pity for the banner: Failed to connect to the database"
            ) 
        
        cur = self.connection.cursor()
        cur.execute("SELECT current_pity FROM banners WHERE banner_id = ?", (banner_id,))
        res = cur.fetchone()
        return Result.ok(
                code="BANNER_PITY_OBTAINED",
                message="Banner pity retrieved successfully",
                data=res[0]
            )
    
    def update_pity(self, banner_id, pity):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't update pity: Failed to connect to the database"
            ) 
        
        if not self.banner_exists(banner_id):
            print("banner does not exists")
            return Result.fail(
                code="BANNER_NOT_FOUND",
                message="Couldn't update pity: Banner does not exist"
            ) 
        try:
            with self.connection:
                cur = self.connection.cursor()
                cur.execute("UPDATE banners SET current_pity = ? WHERE banner_id = ?", (pity, banner_id,))
                if not cur.rowcount > 0:
                    return Result.fail(
                        code="BANNER_PITY_UPDATE_FAIL",
                        message="Couldn't update pity"
                    ) 
                else:
                    return Result.ok(
                    code="BANNER_PITY_UPDATED",
                    message="Updated banner's current pity"
                )

        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )
    #endregion
 

    # crud operations for the tables apparently

    #region for the meta table !!

    def get_meta_version(self):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't get meta version: Failed to connect to the database"
            ) 
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM meta")
        res = cur.fetchone()
        if res is None:
            return Result.fail(
                code="META_FETCH_FAILED",
                message="Couldn't get meta version"
            ) 
        else: 
            return Result.ok(
                code="META_FETCH_SUCCESS",
                message="successfully obtained meta version",
                data=res[0]
            )
    
    def add_version(self, version):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't add version: Failed to connect to the database"
            ) 
        
        try: 
            with self.connection:        
                cur = self.connection.cursor()
                # check if version already exists !
                cur.execute("SELECT version FROM meta WHERE version = ?", (version,))
                res = cur.fetchone()
                if res is not None: #version does exist
                    return Result.fail(
                    code="VERSION_ADD_FAIL",
                    message="Couldn't add version: version already exists"
                )
                else: #version does not exist 
                    cur.execute("INSERT INTO meta (version, created_at, last_modified) VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)", (version,))
                    return Result.ok(
                        code="VERSION_ADDED",
                        message=f"version {version} is added to the meta"
                    )
               
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )

    def update_version(self, version):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't update version: Failed to connect to the database"
            ) 
        
        try: 
            with self.connection:
                cur = self.connection.cursor()
                # check if version already exists !
                cur.execute("SELECT version FROM meta WHERE version = ?", (version,))
                res = cur.fetchone()
                if res is None:
                    return Result.fail(
                        code="VERSION_ADD_FAIL",
                        message="Couldn't add version: version already exists"
                    )
                else:
                    cur.execute("UPDATE meta SET last_modified = CURRENT_TIMESTAMP WHERE version = ?", (version,))
                    return Result.ok(
                        code="VERSION_UPDATED",
                        message="Version update successfully!"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )

    #endregion

    #region for the games !!
    # should be able to: add new games, list all the games on the table, get a particular game 
    # and display some info, update a game info, delete the game from the table.
    def add_games(self, game, ch_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't add game: Failed to connect to the database"
            ) 
        
        # check if game already exists 
        if self.game_exists_with_name(game):
            return Result.fail(
                code="GAME_ALREADY_EXISTS",
                message="A game already exists for this channel"
            )
        
        try: 
            with self.connection:        
                cur = self.connection.cursor()
                cur.execute("INSERT INTO games (game_name, channel_id) VALUES (?, ?)", (game, ch_id,))
                if not cur.rowcount > 0:
                    return Result.fail(
                        code="GAME_CREATE_FAILED",
                        message="Failed to add game"
                    )
                else:
                    return Result.ok(
                        code="GAME_CREATED",
                        message="Game added successfully"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )

    def get_game_by_id(self, game_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't get game by id: Failed to connect to the database"
            )
        
        if not self.game_exists(game_id):
            return Result.fail(
                code="GAME_NOT_FOUND",
                message=f"game with game id: {game_id} does not exists."
            )
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM games WHERE game_id = ?",(game_id,))
        res = cur.fetchone()
        if res is None:
            return Result.fail(
                code="GAME_NOT_FOUND",
                message=f"Game with game id: {game_id} does not exists."
            )
        else:
            return Result.ok(
                    code="GAME_FOUND",
                    message="Game retrieved successfully",
                    data=res
                )
        
    def get_game_by_channel_id(self, ch_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't get game by ch id: Failed to connect to the database"
            )
        
        if not self.game_exists_with_channel_ID(ch_id):
            return Result.fail(
                code="GAME_NOT_FOUND",
                message=f"game with channel id: {ch_id} does not exists."
            )
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM games WHERE channel_id = ?",(ch_id,))
        res = cur.fetchone()
        if res is None:
            return Result.fail(
                code="GAME_NOT_FOUND",
                message=f"Game with channel id: {ch_id} does not exists."
            )
        else:
            return Result.ok(
                    code="GAME_FOUND",
                    message="Game retrieved successfully",
                    data=res
                )
        
    def list_games(self):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't list games: Failed to connect to the database"
            ) 
        
        cur = self.connection.cursor()
        cur.execute("SELECT game_id, game_name FROM games")
        res = cur.fetchall()
        if not res:
            return Result.fail(
                code="NO_GAMES_FOUND",
                message="No games found"
            ) 
        else:
            return Result.ok(
                    code="GAMES_LISTED",
                    message="Games retrieved successfully",
                    data=res
                )

    def update_game_name(self, game_id, game_name):        
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="couldn't update game name: Failed to connect to the database"
            ) 
        
        if not self.game_exists(game_id):
            return Result.fail(
                code="GAME_NOT_FOUND",
                message=f"Game with id: {game_id} does not exists."
            )
        
        try: 
            with self.connection:        
                cur = self.connection.cursor()
                cur.execute("UPDATE games SET game_name = ? WHERE game_id = ?", (game_name, game_id,))
                if not cur.rowcount > 0:
                    return Result.fail(
                        code="GAME_UPDATE_FAILED",
                        message="Failed to update game name"
                    )
                else:
                    return Result.ok(
                        code="GAME_UPDATED",
                        message="Game name updated successfully"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )

    def update_game_channel(self, game_id, channel_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't update game channel id: Failed to connect to the database"
            ) 
        
        if not self.game_exists(game_id):
            return Result.fail(
                code="GAME_NOT_FOUND",
                message=f"game with game id: {game_id} does not exists."
            )
        
        try: 
            with self.connection:        
                cur = self.connection.cursor()
                cur.execute("UPDATE games SET channel_id = ? WHERE game_id = ?", (channel_id, game_id,))
                if not cur.rowcount > 0:
                    return Result.fail(
                        code="GAME_UPDATE_FAILED",
                        message="Failed to update game channel"
                    )
                else:
                    return Result.ok(
                        code="GAME_UPDATED",
                        message="Game channel updated successfully"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )

    def delete_game(self, game_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't delete game: Failed to connect to the database"
            ) 
        
        if not self.game_exists(game_id):
            return Result.fail(
                code="GAME_NOT_FOUND",
                message=f"game with game id: {game_id} does not exists."
            )
        
        try: 
            with self.connection:        
                cur = self.connection.cursor()
                cur.execute("DELETE FROM games WHERE game_id = ?", (game_id,))
                if not cur.rowcount > 0:
                    return Result.fail(
                        code="GAME_DELETE_FAILED",
                        message="Failed to delete game"
                    )
                else:
                    return Result.ok(
                        code="GAME_DELETED",
                        message="Game deleted successfully"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )
        
    # endregion

    #region for the banners !!
    # add new banner/ banner name to the table, get a banner for a particular game,
    # update a banner's information.

    def add_banner(self, game_id, banner_name, current_pity, max_pity):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't add banner: Failed to connect to the database"
            ) 
        
        # check if banner already exists first 
        if self.banner_name_exists(banner_name):
            return Result.fail(
                code="BANNER_ALREADY_EXISTS",
                message="A banner already exists with this name"
            )
        
        try: 
            with self.connection:        
                cur = self.connection.cursor()
                cur.execute("INSERT INTO banners (game_id, banner_name, current_pity, max_pity) VALUES (?, ?, ?, ?)", (game_id, banner_name,current_pity, max_pity,))
                if not cur.rowcount > 0:
                    return Result.fail(
                            code="BANNER_CREATE_FAILED",
                            message="Failed to add banner"
                        )
                else:
                    return Result.ok(
                        code="BANNER_CREATED",
                        message="Banner added successfully"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )

    def get_banner(self, banner_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't get banner: Failed to connect to the database"
            ) 
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM banners WHERE banner_id = ?", (banner_id,))
        res = cur.fetchone()
        if res is None:
            return Result.fail(
                code="BANNER_NOT_FOUND",
                message="Banner not found"
            ) 
        else:
            return Result.ok(
                code="BANNER_FOUND",
                message="Banner retrieved successfully",
                data=res
            )

    def get_game_banners(self, game_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't get game banners: Failed to connect to the database"
            ) 
        
        if not self.game_exists(game_id):
            print(f"Game id: {game_id} does not exists")
            return Result.fail(
                code="GAME_NOT_FOUND",
                message="Game does not exist"
            ) 
        
        cur = self.connection.cursor()
        cur.execute("SELECT banner_name, current_pity, last_updated FROM banners WHERE game_id = ?", (game_id,))
        res = cur.fetchall()
        if not res:
            return Result.fail(
                code="NO_BANNERS_FOUND",
                message="No banners found for this game"
            ) 
        else:
            return Result.ok(
                code="BANNERS_LISTED",
                message="Banners retrieved successfully",
                data=res
            )

    def update_banner_name(self, banner_id, new_banner_name):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't update banner name: Failed to connect to the database"
            ) 
        
        if not self.banner_exists(banner_id):
            return Result.fail(
                code="BANNER_NOT_FOUND",
                message=f"Banner with banner id: {banner_id} does not exists."
            ) 
        
        try: 
            with self.connection:        
                cur = self.connection.cursor()
                cur.execute("UPDATE banners SET banner_name = ? WHERE banner_id = ?", (new_banner_name, banner_id,))
                if not cur.rowcount > 0:
                    return Result.fail(
                    code="BANNER_UPDATE_FAILED",
                    message="Failed to update banner name"
                ) 
                else:
                    return Result.ok(
                        code="BANNER_UPDATED",
                        message="Banner updated successfully"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )
            
    def update_banner_pity(self, banner_id, new_pity):
        # already have update pity, why bother again XD
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't update banner pity: Failed to connect to the database"
            ) 
        
        if not self.banner_exists(banner_id):
            return Result.fail(
                code="BANNER_NOT_FOUND",
                message=f"Banner with banner id: {banner_id} does not exists."
            ) 
        
        try: 
            with self.connection:        
                cur = self.connection.cursor()
                cur.execute("UPDATE banners SET current_pity = ? WHERE banner_id = ?", (new_pity, banner_id,))
                if not cur.rowcount > 0:
                    return Result.fail(
                    code="BANNER_PITY_UPDATE_FAILED",
                    message="Couldn't update banner pity"
                ) 
                else:
                    return Result.ok(
                        code="BANNER_PITY_UPDATED",
                        message="Banner pity updated successfully"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )
    
    def update_banner_max_pity(self, banner_id, new_max_pity):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't update banner's max pity: Failed to connect to the database"
            ) 
        
        if not self.banner_exists(banner_id):
            return Result.fail(
                code="BANNER_NOT_FOUND",
                message=f"Banner with banner id: {banner_id} does not exists."
            ) 
        
        try: 
            with self.connection:        
                cur = self.connection.cursor()
                cur.execute("UPDATE banners SET max_pity = ? WHERE banner_id = ?", (new_max_pity, banner_id,))
                if not cur.rowcount > 0:
                    return Result.fail(
                        code="BANNER_MAXPITY_UPDATE_FAILED",
                        message="Couldn't update banner pity"
                    ) 
                else:
                    return Result.ok(
                        code="BANNER_MAXPITY_UPDATED",
                        message="Banner pity updated successfully"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )

    def delete_banner(self, banner_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't delete banner: Failed to connect to the database"
            ) 
        
        if not self.banner_exists(banner_id):
            return Result.fail(
                code="BANNER_NOT_FOUND",
                message=f"Banner with banner id: {banner_id} does not exists."
            ) 
        
        try: 
            with self.connection:        
                cur = self.connection.cursor()
                cur.execute("DELETE FROM banners WHERE banner_id = ?", (banner_id,))
                if not cur.rowcount > 0:
                    return Result.fail(
                        code="BANNER_DELETE_FAILED",
                        message="Failed to delete banner"
                    ) 
                else:
                    return Result.ok(
                        code="BANNER_DELETED",
                        message="Banner deleted successfully"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )
        
    # endregion

    #region for the pull history !! 
    # browse a list history of a particular banner, delete an entry

    def add_pull(self, entry_name, banner_id, pity, notes):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't add pull entry: Failed to connect to the database"
            ) 
        
        # check if banner for this pull actually xists 
        if not self.banner_exists(banner_id):
            return Result.fail(
                    code="BANNER_NOT_FOUND",
                    message=f"Banner with banner id: {banner_id} does not exists."
                )
        try: 
            with self.connection:        
                cur = self.connection.cursor()            
                cur.execute("""
                    INSERT INTO pull_history (banner_id, game_id, entry_name, pity, notes)
                    SELECT
                        b.banner_id, b.game_id, ?, ?, ?
                    FROM banners b
                    WHERE b.banner_id = ?
                """, (entry_name, pity, notes, banner_id))

                if not cur.rowcount > 0:
                    return Result.fail(
                        code="ADD_PULL_ENTRY_FAILED",
                        message="Couldn't add pull entry"
                    ) 
                else:
                    return Result.ok(
                        code="PULL_ENTRY_ADDED",
                        message="Pull entry added successfully"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )
            
    def get_pulls_by_banner(self, banner_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't get pulls by the banner: Failed to connect to the database"
            ) 
        
        if not self.banner_exists(banner_id):
            return Result.fail(
                code="BANNER_NOT_FOUND",
                message=f"Banner with banner id: {banner_id} does not exists."
            )
        
        cur = self.connection.cursor()
        cur.execute("SELECT entry_name, pity, notes, timestamp FROM pull_history WHERE banner_id = ?", (banner_id,))
        res = cur.fetchall()
        if not res:
            return Result.fail(
                    code="GET_BANNER_PULLS_FAILED",
                    message="Couldn't get pull entries for this banner."
                ) 
        else:
            return Result.ok(
                code="BANNER_PULL_ENTRIES_OBTAINED",
                message="Successfully retrieved pull entries for this banner",
                data=res
            )
        
    def delete_pull(self, pull_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't delete pull entry: Failed to connect to the database"
            )
        
        if not self.pull_entry_exists(pull_id):
            return Result.fail(
                code="PULL_ENTRY_NOT_FOUND",
                message=f"Cannot be deleted. pull entry id: {pull_id} does not exist."
            )
        
        try: 
            with self.connection:        
                cur = self.connection.cursor()
                cur.execute("DELETE FROM pull_history WHERE pull_id = ?", (pull_id,))
                if not cur.rowcount > 0:
                    return Result.fail(
                        code="DELETE_PULL_ENTRY_FAILED",
                        message="Couldn't delete pull entry."
                    ) 
                else:
                    return Result.ok(
                        code="PULL_ENTRY_DELETED",
                        message="Successfully deleted this pull entry."
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )
    #endregion

    #region for the session history !!
    # add new session, browse history of sessions, delete session
    # SQLITE CURRENT_TIMESTAMP DEFAULTS TO UTC. JUST CONVERT IT TO LOCAL TIME AFTER BACKEND XD

    def start_session(self, session_name):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't start session: Failed to connect to the database"
            )

        try:
            with self.connection:        
                cur = self.connection.cursor()            
                cur.execute("INSERT INTO sessions (session_name) VALUES (?)", (session_name,))
                if not cur.rowcount > 0:
                    return Result.fail(
                        code="START_SESSION_FAILED",
                        message="Couldn't start the session."
                    ) 
                else:
                    return Result.ok(
                        code="SESSION_STARTED",
                        message="Successfully started a session."
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )

    def end_session(self, session_id, end_time):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't end session: Failed to connect to the database"
            ) 
        
        if not self.session_exists(session_id):
            return Result.fail(
                    code="SESSION_NOT_FOUND",
                    message=f"session id: {session_id} does not exists."
                ) 
        
        try:
            with self.connection:        
                cur = self.connection.cursor()
                cur.execute("UPDATE sessions SET end_time = ? WHERE session_id = ?", (end_time, session_id,))
                if not cur.rowcount > 0:
                    return Result.fail(
                        code="END_SESSION_FAILED",
                        message="Couldn't end the session."
                    ) 
                else:
                    return Result.ok(
                        code="SESSION_STARTED",
                        message="Successfully ended a session."
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )
            
    def browse_sessions(self):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't get sessions: Failed to connect to the database"
            ) 
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM sessions")
        res = cur.fetchall()

        if not res:
            return Result.fail(
                code="FETCH_SESSIONS_FAILED",
                message="Couldn't fetch all session."
            ) 
        else:
            return Result.ok(
                code="FETCH_SESSIONS",
                message="Successfully retrieved all sessions.",
                data=res
            )

    def add_session_break(self, session_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't add session break: Failed to connect to the database"
            ) 
        
        if not self.session_exists(session_id):
            return Result.fail(
                code="SESSION_NOT_FOUND",
                message="Couldn't add session break: Session not found!"
            ) 
                
        try:
            with self.connection:        
                cur = self.connection.cursor()            
                cur.execute("INSERT INTO session_breaks (session_id) VALUES (?)", (session_id,))
                if not cur.rowcount > 0:
                    return Result.fail(
                        code="END_SESSION_FAILED",
                        message="Couldn't add break for the session."
                    ) 
                else:
                    return Result.ok(
                        code="SESSION_BREAK_STARTED",
                        message=f"Added new session break for the session id: {session_id}"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )

    def end_session_break(self, break_session_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't end session's break: Failed to connect to the database"
            ) 
        
        if not self.break_session_exists(break_session_id):
            return Result.fail(
                code="SESSION_BREAK_NOT_FOUND",
                message=f"Couldn't end session break: Break Session id: {break_session_id} does not exists."
            ) 
        
        try: 
            with self.connection:        
                cur = self.connection.cursor()
                cur.execute("UPDATE session_breaks SET break_end = CURRENT_TIMESTAMP WHERE break_id = ?", (break_session_id,))
                if not cur.rowcount > 0:
                    return Result.fail(
                        code="END_SESSION_BREAK_FAILED",
                        message="Couldn't end break for the session."
                    ) 
                else:
                    return Result.ok(
                        code="SESSION_BREAK_ENDED",
                        message="Session Break Ended"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )

    def get_breaks_for_session(self, session_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't get breaks for the session: Failed to connect to the database"
            ) 
        
        if not self.session_exists(session_id):
            return Result.fail(
                code="SESSION_NOT_FOUND",
                message="Couldn't get breaks for this session: Session not found!"
            ) 
        
        cur = self.connection.cursor()
        cur.execute("SELECT break_start, break_end FROM session_breaks WHERE session_id = ?", (session_id,))
        res = cur.fetchall()

        if not res:
            return Result.fail(
                code="NO_BREAK_SESSIONS_FOUND",
                message="Couldn't fetch breaks for this session."
            ) 
        else:
            return Result.ok(
                code="BREAK_SESSIONS_FOUND",
                message="Breaks found for this session",
                data=res
            )

    def delete_session(self, session_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't delete session: Failed to connect to the database"
            )
                
        if not self.session_exists(session_id):
            return Result.fail(
                code="SESSION_NOT_FOUND",
                message=f"Cannot be deleted. session id: {session_id} does not exist."
            ) 
        
        try: 
            with self.connection:        
                cur = self.connection.cursor()
                cur.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                if not cur.rowcount > 0:
                    return Result.fail(
                        code="DELETE_SESSION_FAILED",
                        message="Couldn't delete the session."
                    ) 
                else:
                    return Result.ok(
                        code="SESSION_DELETED",
                        message="Session deleted from the database"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )
        
    def delete_break_session(self, break_id):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't delete break session: Failed to connect to the database"
            )
            
        if not self.break_session_exists(break_id):
            return Result.fail(
                code="SESSION_BREAK_NOT_FOUND",
                message=f"Couldn't delete break: Break Session id: {break_id} does not exists."
            ) 
        
        try:
            with self.connection:
                cur = self.connection.cursor()
                cur.execute("DELETE FROM session_breaks WHERE break_id = ?", (break_id,))

                # TODO: we also have to decrease the total break time on session lol

                if not cur.rowcount > 0:
                    return Result.fail(
                        code="DELETE_BREAK_SESSION_FAILED",
                        message="Couldn't delete the break for this session."
                    ) 
                else:
                    return Result.ok(
                        code="SESSION_BREAK_DELETED",
                        message="Break for this session successfully deleted from the database"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )
    #endregion

    #region for the settings table !!

    def init_settings(self):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Failed to update pagination: Failed to connect to the database"
            )
        
        try: 
            with self.connection:        
                cur = self.connection.cursor()
                cur.execute("INSERT INTO settings DEFAULT VALUES")
                if not cur.rowcount > 0:
                    return Result.fail(
                        code="SETTINGS_INITIALIZE_FAILED",
                        message="Couldn't initialize settings."
                    ) 
                else:
                    return Result.ok(
                        code="SETTINGS_INITIALIZE_SUCCESS",
                        message="Setting initialize success"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )

    def get_settings(self):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Couldn't get settings: Failed to connect to the database"
            )
        
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM settings")
        res = cur.fetchall()

        if not res:
            return Result.fail(
                code="FETCH_SETTINGS_FAILED",
                message="Couldn't fetch global settings from the database"
            )
        else:
            return Result.ok(
                code="FETCH_SETTING_SUCCESS",
                message="Successfully retrieved global settings from the database",
                data=res
            )

    def update_pagination(self,p_size):
        if not self.is_connected():
            return Result.fail(
                code="DB_CONNECTION_FAILED",
                message="Failed to update pagination: Failed to connect to the database"
            )
        
        try:
            with self.connection:        
                cur = self.connection.cursor()
                cur.execute("UPDATE settings SET pagination_size = ? WHERE id = 1",(p_size,))
                if not cur.rowcount > 0:
                    return Result.fail(
                        code="SETTINGS_UPDATE_FAILED",
                        message="Couldn't update the pagination settings."
                    ) 
                else:
                    return Result.ok(
                        code="SETTINGS_UPDATE_SUCCESS",
                        message="Pagination successfully updated"
                    )
                   
        except sqlite3.Error as e:
            return Result.fail(
                code="SQLITE_ERROR",
                message="SQLite error during X",
                error=str(e)
            )
        
    #endregion