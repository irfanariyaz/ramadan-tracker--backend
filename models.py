from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Family(Base):
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location_city = Column(String)
    location_country = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("FamilyMember", back_populates="family", cascade="all, delete-orphan")


class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"))
    name = Column(String, index=True)
    role = Column(String, default="adult")  # "adult" or "child"
    photo_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    family = relationship("Family", back_populates="members")
    daily_entries = relationship("DailyEntry", back_populates="member", cascade="all, delete-orphan")
    custom_checklist_items = relationship("CustomChecklistItem", back_populates="member", cascade="all, delete-orphan")


class DailyEntry(Base):
    __tablename__ = "daily_entries"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("family_members.id"))
    date = Column(Date, index=True)
    
    # Fasting status: "fasting", "not_fasting", "excused"
    fasting_status = Column(String, default="not_fasting")
    
    # Prayer tracking
    fajr = Column(Boolean, default=False)
    dhuhr = Column(Boolean, default=False)
    asr = Column(Boolean, default=False)
    maghrib = Column(Boolean, default=False)
    isha = Column(Boolean, default=False)
    taraweeh = Column(Boolean, default=False)
    
    # Quran progress
    quran_juz = Column(Integer, default=0)  # 0-30
    quran_page = Column(Integer, default=0)  # 0-604
    
    # Daily goal
    daily_goal = Column(String, nullable=True)
    
    # Custom checklist items (stored as JSON: {item_id: completed})
    custom_items = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    member = relationship("FamilyMember", back_populates="daily_entries")


class CustomChecklistItem(Base):
    __tablename__ = "custom_checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("family_members.id"))
    title = Column(String)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    member = relationship("FamilyMember", back_populates="custom_checklist_items")


class PrayerTimesCache(Base):
    __tablename__ = "prayer_times_cache"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    location_key = Column(String, index=True)  # city_country or lat_long
    
    fajr = Column(String)
    dhuhr = Column(String)
    asr = Column(String)
    maghrib = Column(String)
    isha = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
