"""Module is responsible for adding token into black list, and
removing old tokens from database.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app import models, config


def save_in_black_list(user_token: str, user_id: int, db: Session) -> bool:
    """function is responsible for adding user token into
    black list table.
    """
    black_token = models.BlackList(token=user_token, user_id=user_id)
    db.add(black_token)
    db.commit()
    db.refresh(black_token)
    return True


def remove_old_black_tokens(db: Session) -> bool:
    """function checks and removes tokens from database,
    that are older than determined - (access_token_expire_minutes) time.
    """
    expiration_time = config.settings.access_token_expire_minutes
    limit = datetime.now() - timedelta(minutes=int(expiration_time))
    my_query = db.query(models.BlackList).filter(models.BlackList.created_at < limit)
    my_query.delete()
    db.commit()
    return True
