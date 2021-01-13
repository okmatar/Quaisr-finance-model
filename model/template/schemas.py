from datetime import date

from pydantic import BaseModel
from typing import List


class Conversion(BaseModel):
    fraction: float
    start_tier: str
    subscription_duration_months: int


class PilotSet(BaseModel):
    id: str
    count: int
    start_range: List[date]
    spacing: str
    value: int
    pilot_duration_months: int
    conversion: Conversion


class SubscriptionSet(BaseModel):
    id: str
    count: int
    start_range: List[date]
    spacing: str
    start_tier: str
    subscription_duration_months: int


class Scenario(BaseModel):
    id: str
    name: str
    pilot_sets: List[PilotSet]
    subscription_sets: List[SubscriptionSet]

