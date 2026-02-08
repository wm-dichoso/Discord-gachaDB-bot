from help import Result
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database_manager import DatabaseManager

class Pull_Service:
    def __init__(self, db: "DatabaseManager"):
        self.db = db

    def add_pull_to_banner(self, entry_name, banner_id, pity, notes = None):
        if not entry_name:
            return Result.fail(
                code="EMPTY_PULL_ENTRY_NAME",
                message="Pull entry name for the command is empty"
            )
        
        if not banner_id:
            return Result.fail(
                code="EMPTY_BANNER_ID",
                message="Banner ID for the command is empty"
            )
        
        if not pity:
            return Result.fail(
                code="EMPTY_PITY",
                message="Pity number for the command is empty"
            )
        
        # add to pull history
        pull_entry = self.db.add_pull(entry_name, banner_id, pity, notes)
        
        if not pull_entry.success:
            return Result.fail(
                code="FAILED_ADDING_PULL_ENTRY",
                message=pull_entry.message,
                error=pull_entry.error
            )
        
        # update banner pity too
        update_pity = self.db.update_banner_pity(banner_id, pity)

        if not update_pity.success:            
            return Result.fail(
                code="FAILED_ADDING_PULL_ENTRY",
                message=update_pity.message,
                error=update_pity.error            
            )
        
        return Result.ok(
            code="PULL_ENTRY_ADDED",
            message=pull_entry.message
        )
    
    def edit_pull(self, pull_id, entry_name, pity, notes = None):
        if not entry_name:
            return Result.fail(
                code="EMPTY_PULL_ENTRY_NAME",
                message="Pull entry name for the command is empty"
            )
        
        if not pull_id:
            return Result.fail(
                code="EMPTY_BANNER_ID",
                message="Banner ID for the command is empty"
            )
        
        if not pity:
            return Result.fail(
                code="EMPTY_PITY",
                message="Pity number for the command is empty"
            )
        
        # edit pull entry
        pull_entry = self.db.edit_pull(pull_id, entry_name, pity, notes)
        
        if not pull_entry.success:
            return Result.fail(
                code="FAILED_ADDING_PULL_ENTRY",
                message=pull_entry.message,
                error=pull_entry.error
            )
        
        return Result.ok(
            code="PULL_ENTRY_EDITED",
            message=pull_entry.message
        )

    def get_banner_pulls(self, banner_id):
        if not banner_id:
            return Result.fail(
                code="EMPTY_BANNER_ID",
                message="Banner ID for the command is empty"
            )
        
        banner_pulls = self.db.get_pulls_by_banner(banner_id)

        if not banner_pulls.success:
            return Result.fail(
                code="FAILED_FETCHING_PULL_HISTORY",
                message=banner_pulls.message,
                error=banner_pulls.error
            )
        
        if not banner_pulls.data:
            return Result.fail(
                code="NO_PULL_ENTRIES_FOUND",
                message=banner_pulls.message,
                error=banner_pulls.error
            )
        
        pull_history = []

        for pull in banner_pulls.data:
            id, entry, pity, notes, time = pull
            pull_history.append({
                "ID": id,
                "Timestamp": time,
                "Pity": pity,
                "Name": entry,
                "Notes": notes
            })

        return Result.ok(
            code="PULL_HISTORY_RETRIEVED",
            message=banner_pulls.message,
            data=pull_history
        )

    def delete_pull(self, pull_id):
        if not pull_id:
            return Result.fail(
                code="EMPTY_GAME_ID",
                message="Game ID for the command is empty"
            )

        delete = self.db.delete_pull(pull_id)

        if not delete.success:
            return Result.fail(
                code="DELETE_ENTRY_FAILED",
                message=delete.message,
                error=delete.error
            )
        
        return Result.ok(
            code="PULL_ENTRY_DELETED",
            message=delete.message
        )