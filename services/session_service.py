from help import Result
from typing import TYPE_CHECKING
from datetime import datetime, timezone, timedelta

if TYPE_CHECKING:
    from database_manager import DatabaseManager

class Session_Service:
    def __init__(self, db: "DatabaseManager"):
        self.db = db

    # HELPER FUNCTIONS 
    def require_params_with_codes(self, param_map):
        for name, value in param_map.items():
            if value is None:
                return Result.fail(
                    code=f"EMPTY_{name.upper()}",
                    message=f"{name.replace('_', ' ').title()} is empty"
                )
        return None
    
    def format_seconds_to_hms(self, seconds: int | None) -> str | None:
        # duration in seconds to H:MM:SS
        if seconds is None:
            return None
        return str(timedelta(seconds=int(seconds)))
        
    def utc_string_to_local(self, dt_string: str | None):
        # from UTC timestamp(sqlite default) to date plus time in 12hrs format
        if dt_string is None:
            return None

        dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        local_dt = dt.replace(tzinfo=timezone.utc).astimezone()

        return local_dt.strftime("%b %d, %Y %I:%M %p")

    
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
        duration_hms = self.format_seconds_to_hms(duration)
        session_detail = {
            "session_name": end_sesh.data[1],
            "duration": duration_hms
        }
        
        return Result.ok(
            code="SESSION_ENDED",
            message=end_sesh.message,
            data=session_detail
        )        
    
    def get_current_session(self, session_id):
        param_e = self.require_params_with_codes({
            "session_id": session_id
        })

        if param_e:
            return param_e
        
        session = self.db.get_current_session(session_id)
        if not session.success:
            return Result.fail(
                code="FETCH_SESSION_FAILED",
                message=session.message,
                error=session.error
            )

        # convert duration (secs) to hh:mm:ss
        duration = session.data[1]
        duration_hms = self.format_seconds_to_hms(duration)
        session_detail = {
            "session_start_time": self.utc_string_to_local(session.data[0]),
            "elapsed_duration": duration_hms,
            "has_break": session.data[2], # add list of breaks here
            "breaks": []
        }
        
        # check for session breaks, if we have session breaks, get the list
        if session.data[2] == 1:
            breaks = self.db.get_breaks_for_session(session_id)
            if not breaks.success:
                return Result.fail(
                code="FETCH_BREAKS_FOR_CURRENT_SESSION_FAILED",
                message=breaks.message,
                error=breaks.error
            )
            break_list = []
            for sesh in breaks.data:
                break_start, break_end, duration, is_fin = sesh
                # convert timestamp to local time
                start_local_time = self.utc_string_to_local(break_start)
                if break_end is not None:
                    end_local_time = self.utc_string_to_local(break_end)
                else:
                    end_local_time = None                
                # convert duration
                duration_hms = self.format_seconds_to_hms(duration)
                break_list.append({
                    "Start_Time": start_local_time,
                    "End_Time": end_local_time,
                    "Duration": duration_hms,
                    "is_finished": is_fin
                })
            session_detail["breaks"] = break_list

        return Result.ok(
            code="SESSION_LIST_RETRIEVED",
            message=session.message,
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
            session_id, session_name, start_time, end_time, total_break_time, duration = session
            
            start_local_time = self.utc_string_to_local(start_time)
            end_local_time = self.utc_string_to_local(end_time)
            duration_hms = str(self.format_seconds_to_hms(duration)) + " elapsed"
            name_formatted = "└──> " + str(session_id) + " - " + str(session_name)

            if total_break_time is not None:
                total_break_time = str(total_break_time) + " s"

            sessions_list.append({
                "Start_Time": start_local_time,
                "End_Time": end_local_time,
                "Total_Break_Time": total_break_time,
                "Session_Name": name_formatted,
                "Duration": duration_hms
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
            message=start_break.message,
            data=start_break.data[0]
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
        
        duration = end.data[0]
        duration_hms = self.format_seconds_to_hms(duration)
        new_duration = duration_hms

        return Result.ok(
            code="BREAK_ENDED",
            message=end.message,
            data=new_duration
        )

    def delete_session(self, session_id):
        param_e = self.require_params_with_codes({
            "session_id": session_id
        })

        if param_e:
            return param_e
        
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