from help import Result
from typing import TYPE_CHECKING
from datetime import datetime, timezone, timedelta

if TYPE_CHECKING:
    from database_manager import DatabaseManager

class Currency_Service:
    def __init__(self, db: "DatabaseManager"):
        self.db = db

    # helper functions: timestamp convert, error if empty
    def utc_string_to_local(self, dt_string: str | None):
        # from UTC timestamp(sqlite default) to date plus time in 12hrs format
        if dt_string is None:
            return None

        dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        local_dt = dt.replace(tzinfo=timezone.utc).astimezone()

        return local_dt.strftime("%b %d, %Y %I:%M %p")
    
    def require_params_with_codes(self, param_map):
        for name, value in param_map.items():
            if value is None:
                return Result.fail(
                    code=f"EMPTY_{name.upper()}",
                    message=f"{name.replace('_', ' ').title()} is empty"
                )
        return None
    
    # 1: add currency for a game, 2: set a currency goal for the game, 3: unset goal
    # 4: get the currency info for a game, 5: update the currency amount, 6: update currency token
    # 7: log currency actions, 8: get the game currency logs

    def install_game_currency(self, game_id, currency, pull_token):
        param_e = self.require_params_with_codes({
            "game_id": game_id,
            "currency": currency,
            "pull_token": pull_token
        })

        if param_e:
            return param_e
        
        install = self.db.add_game_currency(game_id, currency, pull_token)
        
        if not install.success:
            return Result.fail(
                code="INSTALL_CURRENCY_FAILED",
                message=install.message,
                error=install.error
            )
        
        return Result.ok(
            code="GAME_CURRENCY_INSTALLED",
            message=install.message
        )

    def get_game_currency_info(self, game_id):
        param_e = self.require_params_with_codes({
            "game_id": game_id
        })

        if param_e:
            return param_e
        
        currency = self.db.get_currency_for_game(game_id)
        
        if not currency.success:
            return Result.fail(
                code="GET_CURRENCY_FAILED",
                message=currency.message,
                error=currency.error
            )

        currency, pull_token, goal = currency.data

        game_currency = {
            "Game_Currency": currency,
            "Pull_Tokens": pull_token, 
            "Goal": goal
        }

        return Result.ok(
            code="CURRENCY_RETRIEVED",
            message=currency.message,
            data=game_currency
        )

    def set_game_currency_goal(self, game_id, goal):
        param_e = self.require_params_with_codes({
            "game_id": game_id,
            "goal": goal
        })

        if param_e:
            return param_e
        
        goal = self.db.set_currency_goal(game_id, goal)
        
        if not goal.success:
            return Result.fail(
                code="SET_CURRENCY_GOAL_FAILED",
                message=goal.message,
                error=goal.error
            )
        
        return Result.ok(
            code="SET_GAME_CURRENCY_GOAL",
            message=goal.message
        )
        
    def unset_game_currency_goal(self, game_id):
        param_e = self.require_params_with_codes({
            "game_id": game_id
        })

        if param_e:
            return param_e
        
        goal = self.db.unset_currency_goal(game_id)
        
        if not goal.success:
            return Result.fail(
                code="UNSET_CURRENCY_GOAL_FAILED",
                message=goal.message,
                error=goal.error
            )
        
        return Result.ok(
            code="UNSET_CURRENCY_GOAL_SUCCESS",
            message=goal.message
        )
        
    def update_currency_amount(self, game_id, amount):
        param_e = self.require_params_with_codes({
            "game_id": game_id,
            "amount": amount
        })

        if param_e:
            return param_e
        
        currency_amount = self.db.update_currency_amount(game_id, amount)
        
        if not currency_amount.success:
            return Result.fail(
                code="UPDATE_CURRENCY_AMOUNT_FAILED",
                message=currency_amount.message,
                error=currency_amount.error
            )
        
        return Result.ok(
            code="UPDATE_CURRENCY_AMOUNT_SUCCESSFULLY",
            message=currency_amount.message
        )    
        
    def update_currency_token(self, game_id, token):
        param_e = self.require_params_with_codes({
            "game_id": game_id,
            "token": token
        })

        if param_e:
            return param_e
        
        currency_token = self.db.update_currency_token(game_id, token)
        
        if not currency_token.success:
            return Result.fail(
                code="UPDATE_CURRENCY_TOKEN_FAILED",
                message=currency_token.message,
                error=currency_token.error
            )
        
        return Result.ok(
            code="UPDATE_CURRENCY_TOKEN_SUCCESSFULLY",
            message=currency_token.message
        )
    
    

        