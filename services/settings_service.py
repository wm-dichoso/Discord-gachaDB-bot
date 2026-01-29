from database_manager import DatabaseManager
from help import Result

class Setting_Service:
    def __init__(self):
        self.db = DatabaseManager()
        self.pagination = int(10)

    def initialize_settings(self):
        setting = self.db.init_settings()

        if not setting.success:
            return Result.fail(
                code="SETTINGS_FAILED",
                message=setting.message,
                error=setting.error
            )
        
        return Result.ok(
            code="SETTINGS_INITIALIZED",
            message=setting.message
        )

    def get_all_settings(self):
        all_setting = self.db.get_settings()

        if not all_setting.success:
            return Result.fail(
                code="FETCH_SETTINGS_FAILED",
                message=all_setting.message,
                error=all_setting.error
            )
        
        settings = []
        
        for options in all_setting.data:
            pagination, features = options
            settings.append({
                "Pagination": pagination,
                "Features": features
            })

            self.pagination = pagination

        return Result.ok(
            code="ALL_SETTINGS_RETRIEVED",
            message=all_setting.message,
            data = settings
        )
    
    def update_pagination(self, size):
        if not size:
            return Result.fail(
                code="EMPTY_PAGINATION_SIZE",
                message="Failed updating pagination, no pagination size inputted"                
            )
        
        update = self.db.update_pagination(size)

        if not update.success:
            return Result.fail(
                code="FAILED_UPDATING_PAGINATION",
                message=update.message,
                error=update.error
            )
        
        self.pagination = size
        
        return Result.ok(
            code="UPDATE_PAGINATION_SUCCESS",
            message=update.message
        )

    # feature to be added : idk yet so no need XD !
        