from typing import Protocol
from services.game_service import Game_Service
from services.banner_service import Banner_Service
from services.pull_service import Pull_Service
from services.session_service import Session_Service
from services.settings_service import Setting_Service
from services.currency_service import Currency_Service
from database_manager import DatabaseManager

class ServicesProtocol(Protocol):
    db: DatabaseManager
    banner_service: Banner_Service
    game_service: Game_Service
    pull_service: Pull_Service
    settings_service: Setting_Service
    session_service: Session_Service
    currency_service: Currency_Service