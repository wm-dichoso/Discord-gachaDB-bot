from services.game_service import Game_Service
from services.banner_service import Banner_Service
from services.pull_service import Pull_Service
# from services.session_service import Session_Service
from services.settings_service import Setting_Service
from database_manager import DatabaseManager

class Services():
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.settings_service = Setting_Service(db)
        self.game_service = Game_Service(db)
        self.banner_service = Banner_Service(db)
        self.pull_service = Pull_Service(db)
        # self.session_service = Session_Service(db)