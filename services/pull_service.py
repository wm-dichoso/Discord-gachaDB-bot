from database_manager import DatabaseManager
from help import Result

class Pull_Service:
    def __init__(self):
        self.db = DatabaseManager()

    def add_pull_to_banner(self, entry_name, banner_id, pity, notes):
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
        
        pull_entry = self.db.add_pull(entry_name, banner_id, pity, notes)
        
        if not pull_entry.success:
            return Result.fail(
                code="FAILED_ADDING_PULL_ENTRY",
                message=pull_entry.message,
                error=pull_entry.error
            )
        
        return Result.ok(
            code="PULL_ENTRY_ADDED",
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
            entry, pity, notes, time = pull
            pull_history.append({
                "Name": entry,
                "Pity": pity,
                "Notes": notes,
                "Timestamp": time
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