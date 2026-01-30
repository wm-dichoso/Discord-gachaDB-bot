from help import Result
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database_manager import DatabaseManager

class Banner_Service:
    def __init__(self, db: "DatabaseManager"):
        self.db = db

    def create_banner(self, game_id, banner_name, current_pity, max_pity):
        if not game_id:
            return Result.fail(
                code="EMPTY_GAME_ID",
                message="Game id is empty"
            )
        
        if not banner_name:
            return Result.fail(
                code="EMPTY_BANNER_NAME",
                message="Banner name is empty"
            )
        
        banner_exists = self.db.banner_name_exists(banner_name)

        if banner_exists:
            return Result.fail(
                code="BANNER_ALREADY_EXITS",
                message="Banner name already exists in the table"
            )
        
        create_banner = self.db.add_banner(game_id, banner_name, current_pity, max_pity)

        if not create_banner.success:
            return Result.fail(
                code="CREATE_BANNER_FAILED",
                message=create_banner.message,
                error=create_banner.error
            )
        
        return Result.ok(
            code="BANNER_CREATED",
            message="Success on creating banner"
        )

    def get_banners(self, game_id):
        if not game_id:
            return Result.fail(
                code="EMPTY_GAME_ID",
                message="Game id is empty"
            )
        
        banners = self.db.get_game_banners(game_id)
        
        if not banners.success:
            return Result.fail(
                code="GET_BANNERS_FAILED",
                message=banners.message,
                error=banners.error
            )
        
        banner_list = []

        for banner in banners.data:
            banner_name, current_pity, last_updated = banner
            banner_list.append({
                "Banner_Name": banner_name, 
                "Current_Pity": current_pity, 
                "Last_Updated": last_updated
            })

        return Result.ok(
            code="BANNERS_RETRIEVED",
            message=banners.message,
            data=banner_list
        )

    def get_banner(self, banner_id):
        if not banner_id:
            return Result.fail(
                code="EMPTY_BANNER_ID",
                message="Banner ID is empty"
            )
        
        banner = self.db.get_banner(banner_id)

        if not banner.success:
            return Result.fail(
                code="BANNER_FETCH_FAIL",
                message=banner.message,
                error=banner.error
            )
        
        banner_id, game_id, banner_name, current_pity, max_pity, last_updated = banner.data
        
        banner_data = {
            "Banner_id":banner_id,
            "Game_id":game_id,
            "Banner_Name": banner_name, 
            "Current_Pity": current_pity, 
            "Max_Pity":max_pity,
            "Last_Updated": last_updated
        }

        # TODO: after fetching banner data, display pull history too !! 

        return Result.ok(
            code="BANNER_FETCHED",
            message=banner.message,
            data=banner_data
        )

    def update_pity(self, banner_id, new_data):
        if not banner_id:
            return Result.fail(
                code="EMPTY_BANNER_ID",
                message="Banner ID is empty"
            )
        
        if not new_data:
            return Result.fail(
                code="EMPTY_NEW_PITY",
                message="New pity is empty"
            )
        
        update = self.db.update_banner_pity(banner_id, new_data)

        if not update.success:
            return Result.fail(
                code="UPDATE_PITY_FAILED",
                message=update.message,
                error=update.error
            )
        
        return Result.ok(
            code="UPDATED_PITY",
            message=update.message
        )
    
    # other update but not really needed early on so XD
    # - update max pity, update banner name

    def delete_banner(self, banner_id):
        if not banner_id:
            return Result.fail(
                code="EMPTY_BANNER_ID",
                message="Banner ID is empty"
            )
        
        delete = self.db.delete_banner(banner_id)

        if not delete.success:
            return Result.fail(
                code="DELETE_FAILED",
                message=delete.message,
                error=delete.error
            )
        
        return Result.ok(
            code="DELETE_SUCCESS",
            message=delete.message
        )
    