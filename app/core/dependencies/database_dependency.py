from sqlalchemy.orm import Session

import app.core.models  # noqa: F401
from app.database.session import SessionLocal


def db_session_dependency() -> Session:  # type: ignore
    """Database session dependency."""
    db_session = SessionLocal()
    db_session.info["managed_transaction"] = True
    try:
        yield db_session
        if db_session.in_transaction():
            db_session.commit()
    except Exception:
        if db_session.in_transaction():
            db_session.rollback()
        raise
    finally:
        db_session.close()
        SessionLocal.remove()
