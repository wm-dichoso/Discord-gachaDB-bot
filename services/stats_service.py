from help import Result
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database_manager import DatabaseManager

class Statistics_Service:
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
    
    # pull overview (how many ssr on all banner on this game)
    def get_game_pull_overview(self, game_id):
        param_e = self.require_params_with_codes({
            "game_id": game_id
        })

        if param_e:
            return param_e
        
        overview = self.db.get_game_pulls_and_SSR(game_id)
        if not overview.success:
            return Result.fail(
                code="FETCH_GAME_PULL_OVERVIEW_FAILED",
                message=overview.message,
                error=overview.error
            )
        
        total_ssr, total_pulls = map(int, overview.data)
        ssr_rate = round((total_ssr / total_pulls) * 100 if total_pulls > 0 else 0, 2)
        average_pull = round((total_pulls / total_ssr) if total_ssr > 0 else 0, 2)
        game_overview = {
            "Total_SSR": total_ssr,
            "Total_Pulls": total_pulls,
            "SSR_Rate": ssr_rate,
            "Average_Pull": average_pull
        }

        return Result.ok(
            code="GAME_PULL_OVERVIEW_RETRIEVED",
            message=overview.message,
            data=game_overview
        )    

    # banner stats (how many ssr on particular banner on this game)
    # forecast (how many pulls needed to get ssr)