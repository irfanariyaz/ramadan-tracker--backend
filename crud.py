from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List
import models
import schemas


# Family CRUD
def create_family(db: Session, family: schemas.FamilyCreate):
    db_family = models.Family(**family.model_dump())
    db.add(db_family)
    db.commit()
    db.refresh(db_family)
    return db_family


def get_family(db: Session, family_id: int):
    return db.query(models.Family).filter(models.Family.id == family_id).first()


def get_family_by_name(db: Session, name: str):
    return db.query(models.Family).filter(models.Family.name == name).first()


def get_all_families(db: Session):
    return db.query(models.Family).all()


def update_family(db: Session, family_id: int, family_update: schemas.FamilyUpdate):
    db_family = get_family(db, family_id)
    if db_family:
        for key, value in family_update.model_dump(exclude_unset=True).items():
            setattr(db_family, key, value)
        db.commit()
        db.refresh(db_family)
    return db_family


def delete_family(db: Session, family_id: int):
    db_family = get_family(db, family_id)
    if db_family:
        db.delete(db_family)
        db.commit()
    return db_family


# Family Member CRUD
def create_member(db: Session, member: schemas.MemberCreate):
    db_member = models.FamilyMember(**member.model_dump())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def get_member(db: Session, member_id: int):
    return db.query(models.FamilyMember).filter(models.FamilyMember.id == member_id).first()


def get_family_members(db: Session, family_id: int):
    return db.query(models.FamilyMember).filter(models.FamilyMember.family_id == family_id).all()


def update_member_photo(db: Session, member_id: int, photo_path: str):
    db_member = get_member(db, member_id)
    if db_member:
        db_member.photo_path = photo_path
        db.commit()
        db.refresh(db_member)
    return db_member


def update_member(db: Session, member_id: int, member_update: schemas.MemberUpdate):
    db_member = get_member(db, member_id)
    if db_member:
        for key, value in member_update.model_dump(exclude_unset=True).items():
            setattr(db_member, key, value)
        db.commit()
        db.refresh(db_member)
    return db_member


def delete_member(db: Session, member_id: int):
    db_member = get_member(db, member_id)
    if db_member:
        db.delete(db_member)
        db.commit()
    return db_member


# Custom Checklist Item CRUD
def create_custom_item(db: Session, item: schemas.CustomChecklistItemCreate):
    db_item = models.CustomChecklistItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_custom_items(db: Session, member_id: int, active_only: bool = True):
    query = db.query(models.CustomChecklistItem).filter(
        models.CustomChecklistItem.member_id == member_id
    )
    if active_only:
        query = query.filter(models.CustomChecklistItem.is_active == True)
    return query.all()


def get_custom_item(db: Session, item_id: int):
    return db.query(models.CustomChecklistItem).filter(
        models.CustomChecklistItem.id == item_id
    ).first()


def update_custom_item(db: Session, item_id: int, item_update: schemas.CustomChecklistItemUpdate):
    db_item = get_custom_item(db, item_id)
    if db_item:
        for key, value in item_update.model_dump(exclude_unset=True).items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item


def delete_custom_item(db: Session, item_id: int):
    db_item = get_custom_item(db, item_id)
    if db_item:
        db_item.is_active = False
        db.commit()
    return db_item


# Daily Entry CRUD
def create_daily_entry(db: Session, entry: schemas.DailyEntryCreate):
    db_entry = models.DailyEntry(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_daily_entry(db: Session, member_id: int, entry_date: date):
    return db.query(models.DailyEntry).filter(
        models.DailyEntry.member_id == member_id,
        models.DailyEntry.date == entry_date
    ).first()


def update_daily_entry(db: Session, member_id: int, entry_date: date, entry_update: schemas.DailyEntryUpdate):
    db_entry = get_daily_entry(db, member_id, entry_date)
    
    if not db_entry:
        # Create new entry if doesn't exist
        entry_data = entry_update.model_dump(exclude_unset=True)
        entry_data['member_id'] = member_id
        entry_data['date'] = entry_date
        # Initialize custom_items if not provided
        if 'custom_items' not in entry_data:
            entry_data['custom_items'] = {}
        db_entry = models.DailyEntry(**entry_data)
        db.add(db_entry)
    else:
        # Update existing entry
        for key, value in entry_update.model_dump(exclude_unset=True).items():
            setattr(db_entry, key, value)
    
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_family_daily_entries(db: Session, family_id: int, entry_date: date):
    """Get all daily entries for a family on a specific date"""
    members = get_family_members(db, family_id)
    entries = []
    for member in members:
        entry = get_daily_entry(db, member.id, entry_date)
        if entry:
            entries.append(entry)
    return entries


# Prayer Times Cache CRUD
def get_cached_prayer_times(db: Session, entry_date: date, location_key: str):
    return db.query(models.PrayerTimesCache).filter(
        models.PrayerTimesCache.date == entry_date,
        models.PrayerTimesCache.location_key == location_key
    ).first()


def cache_prayer_times(db: Session, entry_date: date, location_key: str, prayer_times: dict):
    db_cache = models.PrayerTimesCache(
        date=entry_date,
        location_key=location_key,
        fajr=prayer_times['fajr'],
        dhuhr=prayer_times['dhuhr'],
        asr=prayer_times['asr'],
        maghrib=prayer_times['maghrib'],
        isha=prayer_times['isha']
    )
    db.add(db_cache)
    db.commit()
    db.refresh(db_cache)
    return db_cache


def get_latest_daily_entry_before(db: Session, member_id: int, before_date: date):
    """Get the most recent daily entry for a member before a specific date"""
    return db.query(models.DailyEntry).filter(
        models.DailyEntry.member_id == member_id,
        models.DailyEntry.date < before_date
    ).order_by(models.DailyEntry.date.desc()).first()


def get_latest_quran_entry_before(db: Session, member_id: int, before_date: date):
    """Get the most recent daily entry with non-zero Quran progress for a member before a specific date"""
    return db.query(models.DailyEntry).filter(
        models.DailyEntry.member_id == member_id,
        models.DailyEntry.date < before_date,
        models.DailyEntry.quran_page > 0
    ).order_by(models.DailyEntry.date.desc()).first()


def get_max_quran_progress(db: Session, member_id: int):
    """Get the highest recorded Quran page for a member"""
    try:
        max_entry = db.query(models.DailyEntry).filter(
            models.DailyEntry.member_id == member_id
        ).order_by(models.DailyEntry.quran_page.desc()).first()
        return max_entry
    except:
        return None
