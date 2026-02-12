from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import date, datetime


# Family Schemas
class FamilyCreate(BaseModel):
    name: str
    location_city: Optional[str] = None
    location_country: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None


class FamilyUpdate(BaseModel):
    name: Optional[str] = None
    location_city: Optional[str] = None
    location_country: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None


class FamilyResponse(BaseModel):
    id: int
    name: str
    location_city: Optional[str]
    location_country: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Family Member Schemas
class MemberCreate(BaseModel):
    family_id: int
    name: str
    role: str = "adult"


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None


class MemberResponse(BaseModel):
    id: int
    family_id: int
    name: str
    role: str
    photo_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

    @field_validator('photo_path', mode='after')
    @classmethod
    def normalize_photo_path(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        if v.startswith('http'):
            return v
        if 'static/photo s/' in v:
            return v.replace('static/photo s/', 'static/photos/')
        return v


# Custom Checklist Item Schemas
class CustomChecklistItemCreate(BaseModel):
    member_id: int
    title: str
    description: Optional[str] = None


class CustomChecklistItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CustomChecklistItemResponse(BaseModel):
    id: int
    member_id: int
    title: str
    description: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Daily Entry Schemas
class DailyEntryCreate(BaseModel):
    member_id: int
    date: date
    fasting_status: str = "not_fasting"
    fajr: bool = False
    dhuhr: bool = False
    asr: bool = False
    maghrib: bool = False
    isha: bool = False
    taraweeh: bool = False
    quran_juz: int = 0
    quran_page: int = 0
    daily_goal: Optional[str] = None
    custom_items: Optional[Dict[str, bool]] = None


class DailyEntryUpdate(BaseModel):
    fasting_status: Optional[str] = None
    fajr: Optional[bool] = None
    dhuhr: Optional[bool] = None
    asr: Optional[bool] = None
    maghrib: Optional[bool] = None
    isha: Optional[bool] = None
    taraweeh: Optional[bool] = None
    quran_juz: Optional[int] = None
    quran_page: Optional[int] = None
    daily_goal: Optional[str] = None
    custom_items: Optional[Dict[str, bool]] = None


class DailyEntryResponse(BaseModel):
    id: int
    member_id: int
    date: date
    fasting_status: str
    fajr: bool
    dhuhr: bool
    asr: bool
    maghrib: bool
    isha: bool
    taraweeh: bool
    quran_juz: int
    quran_page: int
    starting_quran_juz: int = 0
    starting_quran_page: int = 0
    current_max_quran_juz: int = 0
    current_max_quran_page: int = 0
    daily_goal: Optional[str]
    custom_items: Optional[Dict[str, bool]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Prayer Times Schemas
class PrayerTimesResponse(BaseModel):
    date: str
    fajr: str
    dhuhr: str
    asr: str
    maghrib: str
    isha: str


# Family Progress Schemas
class MemberProgress(BaseModel):
    member_id: int
    member_name: str
    photo_path: Optional[str]
    fasting_status: str
    prayers_completed: int  # out of 6 (5 daily + taraweeh)
    quran_progress: int  # percentage
    daily_goal: Optional[str]
    custom_items_completed: int = 0
    custom_items_total: int = 0

    class Config:
        from_attributes = True

    @field_validator('photo_path', mode='after')
    @classmethod
    def normalize_photo_path(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        if v.startswith('http'):
            return v
        if 'static/photo s/' in v:
            return v.replace('static/photo s/', 'static/photos/')
        return v


class FamilyProgressResponse(BaseModel):
    family_id: int
    family_name: str
    date: date
    members: List[MemberProgress]


# Monthly Stats & Leaderboard Schemas
class MemberDailyScore(BaseModel):
    member_id: int
    member_name: str
    role: str
    score: float
    fasting_status: str


class DailySummary(BaseModel):
    date: date
    total_score: float
    members_scores: List[MemberDailyScore]
    fasting_count: int


class MonthlyStatsResponse(BaseModel):
    family_id: int
    month: str
    dates: List[DailySummary]


class LeaderboardEntry(BaseModel):
    member_id: int
    member_name: str
    role: str
    photo_path: Optional[str]
    total_score: float
    fasting_streak: int
    quran_streak: int
    fasting_total: int
    quran_pages_total: int

    @field_validator('photo_path', mode='after')
    @classmethod
    def normalize_photo_path(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        if v.startswith('http'):
            return v
        if 'static/photo s/' in v:
            return v.replace('static/photo s/', 'static/photos/')
        return v


class LeaderboardResponse(BaseModel):
    family_id: int
    entries: List[LeaderboardEntry]
