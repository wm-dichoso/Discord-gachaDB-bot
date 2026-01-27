from database_manager import DatabaseManager
from help import Result

class Game_Service:
    def __init__(self):
        self.db = DatabaseManager()

    # existence checks already on db so no need to put it on service layers, just validate variable passed from the command

    def create_game(self, channel_id, game_name):
        # check if theres game name passed, check if game already exists for the channel id
        # check if theres any error on adding game. then add the game to the db
        if not game_name:
            return Result.fail(
                code="EMPTY_GAME_NAME",
                message="Game name is empty"
            )
        
        if not channel_id:
            return Result.fail(
                code="EMPTY_CHANNEL_ID",
                message="Channel ID for the command is empty"
            )
        
        game_exists = self.db.game_exists_with_channel_ID(channel_id)

        if game_exists:
            return Result.fail(
                code="GAME_ALREADY_EXISTS",
                message="Couldn't create game. Game already exists"
            )
        
        add_result = self.db.add_games(game_name, channel_id)
        
        if not add_result.success:
            return Result.fail(
                code="CREATE_GAME_FAILED",
                message="Failed creating new game",
                error=add_result.error
            )
        
        return Result.ok(
            code="GAME_CREATED",
            message="Success on creating a new game"
        )        


    def get_game_for_channel(self, channel_id):
        if not channel_id:
            return Result.fail(
                code="EMPTY_CHANNEL_ID",
                message="Channel ID for the command is empty"
            )
        
        get_game = self.db.get_game_by_channel_id(channel_id)

        if not get_game.success:
            return Result.fail(
                code="FAILED_FETCHING_GAME",
                message="Couldn't get the game with the channel ID",
                error=get_game.error
            )
        
        game_id, game_name, game_ch_id = get_game.data

        game = {
            "Game_ID" : game_id,
            "Game_Name" : game_name,
            "Game_Channel_ID" : game_ch_id
        }

        return Result.ok(
            code="GAME_FETCHED",
            message=get_game.message,
            data = game
        )


    def list_games(self):
        games = self.db.list_games()

        if not games.success:
            return Result.fail(
                code="FAILED_FETCHING_GAME_LIST",
                message="Couldn't get the game list",
                error=games.error
            )
        # this uses fetchall so check for falsy instead of just None because it will still give you a tuple an empty tuple 
        if not games.data:
            return Result.fail(
                code="NO_GAMES_FOUND",
                message="No registered games on the db",
                error=games.error
            )
        
        game_list = []

        for game in games.data:
            Game_ID, Game_Name = game
            game_list.append({
                "Game_ID": Game_ID,
                "Game_Name": Game_Name
            })

        return Result.ok(
            code="GAME_LIST_RETRIEVED",
            message=games.message,
            data=game_list
        )


    def rename_game(self, game_id, new_name:str):
        if not game_id:
            return Result.fail(
                code="EMPTY_GAME_ID",
                message="Game ID for the command is empty"
            )
        
        if not new_name:
            return Result.fail(
                code="EMPTY_NEW_GAME_NAME",
                message="New Game Name for rename command is empty"
            )
        
        rename = self.db.update_game_name(game_id, new_name)

        if not rename.success:
            return Result.fail(
                code="RENAME_GAME_FAILED",
                message=rename.message,
                error=rename.error
            )
        
        return Result.ok(
            code="GAME_RENAMED",
            message=rename.message
        )


    def delete_game(self, game_id):
        if not game_id:
            return Result.fail(
                code="EMPTY_GAME_ID",
                message="Game ID for the command is empty"
            )

        delete = self.db.delete_game(game_id)

        if not delete.success:
            return Result.fail(
                code="DELETE_GAME_FAILED",
                message=delete.message,
                error=delete.error
            )
        
        return Result.ok(
            code="DELETE_GAME_SUCCESSFULLY",
            message=delete.message
        )
    
    
    # update game channel to be followed