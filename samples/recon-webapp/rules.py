"""How long a car has sat in its stage, and the card colour that goes with it."""
from datetime import date

# Card colours by whole days in the current stage:
#   green under 3 days, yellow from 3 to 6 days, red at 7 days or more.
YELLOW_FROM_DAYS = 3
RED_FROM_DAYS = 7


def days_in_stage(entered_stage_on, today=None):
    today = today or date.today()
    return (today - date.fromisoformat(entered_stage_on)).days


def card_colour(days):
    if days > RED_FROM_DAYS:
        return "red"
    if days >= YELLOW_FROM_DAYS:
        return "yellow"
    return "green"
