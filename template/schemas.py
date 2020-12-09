from datetime import date

from pydantic import BaseModel
from typing import List


class Conversion(BaseModel):
    fraction: int
    start_tier: str


class PilotSet(BaseModel):
    id: str
    count: int
    start_range: List[date]
    spacing: str
    value: int
    duration_months: int
    conversion: Conversion


class SubscriptionSet(BaseModel):
    id: str
    count: int
    start_range: List[date]
    spacing: str
    start_tier: str
    upgrade_period_months: int
    total_duration_months: int


class Scenario(BaseModel):
    id: str
    name: str
    pilot_sets: List[PilotSet]
    subscription_sets: List[SubscriptionSet]

