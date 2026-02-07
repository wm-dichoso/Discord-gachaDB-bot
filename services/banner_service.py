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
            banner_id, banner_name, current_pity, last_updated = banner
            banner_list.append({
                "Banner_ID": banner_id,
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
    
    def require_params_with_codes(param_map):
        for name, value in param_map.items():
            if value is None:
                return Result.fail(
                    code=f"EMPTY_{name.upper()}",
                    message=f"{name.replace('_', ' ').title()} is empty"
                )
        return None

    def update_pity_detail(self, banner_id, new_pity, new_max_pity):
        param_e = self.require_params_with_codes({
            "banner_id": banner_id,
            "new_pity": new_pity,
            "new_max_pity": new_max_pity
        })

        if not param_e:
            return param_e

        update_pity = self.db.update_banner_pity(banner_id, new_pity)

        if not update_pity.success:
            return Result.fail(
                code="UPDATE_PITY_FAILED",
                message=update_pity.message,
                error=update_pity.error
            )
        
        update_max_pity = self.db.update_banner_max_pity(banner_id, new_max_pity)

        if not update_max_pity.success:
            return Result.fail(
                code="UPDATE_MAX_PITY_FAILED",
                message=update_max_pity.message,
                error=update_max_pity.error
            )
        
        return Result.ok(
            code="UPDATE_PITY_SUCCESS",
            message=update_pity.message
        )
    
    def update_banner_name(self, banner_id, name):
        param_e = self.require_params_with_codes({
            "banner_id": banner_id,
            "name": name
        })

        if not param_e:
            return param_e
        
        update_name = self.db.update_banner_name(banner_id, name)

        if not update_name.success:
            return Result.fail(
                code="UPDATE_BANNER_NAME_FAILED",
                message=update_name.message,
                error=update_name.error
            )
        
        return Result.ok(
            code="BANNER_NAME_UPDATED",
            message=update_name.message
        )
        

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
    