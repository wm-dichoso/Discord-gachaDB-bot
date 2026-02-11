from help import Result
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database_manager import DatabaseManager

class Banner_Service:
    def __init__(self, db: "DatabaseManager"):
        self.db = db

    def require_params_with_codes(param_map):
        for name, value in param_map.items():
            if value is None:
                return Result.fail(
                    code=f"EMPTY_{name.upper()}",
                    message=f"{name.replace('_', ' ').title()} is empty"
                )
        return None
    
    # session service things !!
    # SQLITE CURRENT_TIMESTAMP DEFAULTS TO UTC. JUST CONVERT IT TO LOCAL TIME AFTER BACKEND XD

    def start_session(self, name):
        param_e = self.require_params_with_codes({
            "name": name
        })

        if not param_e:
            return param_e
        
        # check if session name already exists !
        start = self.db.start_session(name)
        if not start.success:
            return Result.fail(
                code="START_SESSION_FAILED",
                message=start.message,
                error=start.error
            )
        
        return Result.ok(
            code="SESSION_STARTED",
            message=start.message
        )
    
    def end_session(self, session_id, end_time):
        param_e = self.require_params_with_codes({
            "session_id": session_id,
            "end_time": end_time
        })

        if not param_e:
            return param_e
        
        # check if session name already exists !
        end = self.db.end_session(session_id, end_time)
        if not end.success:
            return Result.fail(
                code="END_SESSION_FAILED",
                message=end.message,
                error=end.error
            )
        
        
        return Result.ok(
            code="SESSION_ENDED",
            message=end.message
        )
        # when ending session, figure out how to send the accumulated time !
    
    def browse_sessions(self):
        sessions = self.db.browse_sessions()

        if not sessions.success:
            return Result.fail(
                code="FAILED_FETCHING_SESSION_LIST",
                message=sessions.message,
                error=sessions.error
            )
        
        if not sessions.data:
            return Result.fail(
                code="NO_SESSIONS_FOUND",
                message=sessions.message,
                error=sessions.error
            )
        
        sessions_list = []

        for session in sessions.data:
            session_id, session_name, start_time, end_time, total_break_time = session
            sessions_list.append({
            "Session_ID": session_id,
            "Session_Name": session_name,
            "Start_Time": start_time,
            "End_Time": end_time,
            "Total_Break_Time": total_break_time
            })

        return Result.ok(
            code="SESSION_LIST_RETRIEVED",
            message=sessions.message,
            data=sessions_list
        )


    def add_session_break(self, session_id):
        pass

    def end_break(self, session_id):
        pass

    def delete_session(self, session_id):
        pass

    def delete_break(self, break_id):
        pass