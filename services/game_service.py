from database_manager import DatabaseManager

class Game_Service:
    def __init__(self):
        self.db = DatabaseManager()

    def create_game(self, channel_id, game_name):
        pass

    def get_game_for_channel(self, channel_id):
        pass

    def list_games(self):
        pass

    def rename_game(self, game_id, new_name):
        pass

    def delete_game(self, game_id):
        pass