from help import Result
from typing import TYPE_CHECKING
from datetime import datetime, timezone, timedelta

if TYPE_CHECKING:
    from database_manager import DatabaseManager

class Session_Service:
    def __init__(self, db: "DatabaseManager"):
        self.db = db

    def require_params_with_codes(self, param_map):
        for name, value in param_map.items():
            if value is None:
                return Result.fail(
                    code=f"EMPTY_{name.upper()}",
                    message=f"{name.replace('_', ' ').title()} is empty"
                )
        return None
    
    # session service things !!
    # SQLITE CURRENT_TIMESTAMP DEFAULTS TO UTC. JUST CONVERT IT TO LOCAL TIME AFTER BACKEND XD
    # ^^^ done?

    def start_session(self, name):
        # check for missing parameter, if theres error, return it
        param_e = self.require_params_with_codes({
            "name": name
        })

        if param_e:
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
            message=start.message,
            data=start.data[0]
        )
    
    def end_session(self, session_id):
        param_e = self.require_params_with_codes({
            "session_id": session_id
        })

        if param_e:
            return param_e
        
        # check if session name already exists !
        end_sesh = self.db.end_session(session_id)
        if not end_sesh.success:
            return Result.fail(
                code="END_SESSION_FAILED",
                message=end_sesh.message,
                error=end_sesh.error
            )
        # convert duration (secs) to hh:mm:ss
        duration = end_sesh.data[0]
        duration_hms = f"{int(duration)//3600:02d}:{(int(duration)%3600)//60:02d}:{int(duration)%60:02d}"
        session_detail = {
            "session_name": end_sesh.data[1],
            "duration": duration_hms
        }
        
        return Result.ok(
            code="SESSION_ENDED",
            message=end_sesh.message,
            data=session_detail
        )        
    
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
            
            start_utc_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end_utc_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            start_local_time = start_utc_time + timedelta(hours=8)
            end_local_time = end_utc_time + timedelta(hours=8)

            sessions_list.append({
            "Start_Time": start_local_time,
            "End_Time": end_local_time,
            "Total_Break_Time": total_break_time,
            "Session_Name": session_name
            })

        return Result.ok(
            code="SESSION_LIST_RETRIEVED",
            message=sessions.message,
            data=sessions_list
        )

    def add_session_break(self, session_id):
        param_e = self.require_params_with_codes({
            "session_id": session_id
        })

        if param_e:
            return param_e
        
        # check if session name already exists !
        start_break = self.db.add_session_break(session_id)
        if not start_break.success:
            return Result.fail(
                code="ADD_BREAK_FAILED",
                message=start_break.message,
                error=start_break.error
            )
        
        return Result.ok(
            code="BREAK_STARTED",
            message=start_break.message
        )

    def end_break(self, session_id):
        param_e = self.require_params_with_codes({
            "session_id": session_id
        })

        if param_e:
            return param_e
        
        # check if session name already exists !
        end = self.db.end_session_break(session_id)
        if not end.success:
            return Result.fail(
                code="END_BREAK_FAILED",
                message=end.message,
                error=end.error
            )
        
        
        return Result.ok(
            code="BREAK_ENDED",
            message=end.message
        )
        # when ending break, figure out how to send the accumulated time !

    def delete_session(self, session_id):
        param_e = self.require_params_with_codes({
            "session_id": session_id
        })

        if not param_e:
            return param_e
        
        # check if session name already exists !
        delete_s = self.db.delete_session(session_id)
        if not delete_s.success:
            return Result.fail(
                code="DELETE_SESSION_FAILED",
                message=delete_s.message,
                error=delete_s.error
            )        
        
        return Result.ok(
            code="SESSION_DELETED",
            message=delete_s.message
        )

    def delete_break(self, break_id):
        param_e = self.require_params_with_codes({
            "break_id": break_id
        })

        if param_e:
            return param_e
        
        # check if session name already exists !
        delete_B = self.db.delete_break_session(break_id)
        if not delete_B.success:
            return Result.fail(
                code="DELETE_BREAK_FAILED",
                message=delete_B.message,
                error=delete_B.error
            )        
        
        return Result.ok(
            code="BREAK_DELETED",
            message=delete_B.message
        )