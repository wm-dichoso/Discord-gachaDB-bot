from help import Result
from typing import TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from database_manager import DatabaseManager

class Setting_Service:
    def __init__(self, db: "DatabaseManager"):
        self.db = db
        self.pagination = int(5) 
        
        # update pagination based on settings
        self.get_all_settings()

    def utc_string_to_local(self, dt_string: str | None):
        # from UTC timestamp(sqlite default) to date plus time in 12hrs format
        if dt_string is None:
            return None

        dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        local_dt = dt.replace(tzinfo=timezone.utc).astimezone()

        return local_dt.strftime("%b %d, %Y %I:%M %p")
    
    # db META stuff
    def update_db_version(self):
        version = "0.1"

        v = self.db.update_version(version)

        if not v.success:
            return Result.fail(
                code="UPDATE_VERSION_FAILED",
                message=v.message,
                error=v.error
            )
        
        return Result.ok(
            code="VERSION_UPDATED",
            message=v.message
        )
    
    def get_db_meta(self):
        v = self.db.get_meta_version()

        if not v.success:
            return Result.fail(
                code="UPDATE_VERSION_FAILED",
                message=v.message,
                error=v.error
            )
        
        meta = {
            **v.data,
            "created_at": self.utc_string_to_local(v.data["created_at"]),
            "last_modified": self.utc_string_to_local(v.data["last_modified"])
        }
        
        return Result.ok(
            code="VERSION_UPDATED",
            message=v.message,
            data=meta
        )
    
    # settings

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
        