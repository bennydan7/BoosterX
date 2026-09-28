from typing import Optional
from backend.app.db import db
from backend.app.models.user import User
from backend.app.utils.phone import normalize_phone

class SQLAlchemyUserRepository:
    def get_by_identifier(self, identifier: str) -> Optional[User]:
        if not identifier:
            return None
        cleaned = identifier.strip().lower()
        # Check email
        user = User.query.filter(db.func.lower(User.email) == cleaned).first()
        if user:
            return user
        # Check phone
        norm_phone = normalize_phone(identifier)
        if norm_phone:
            user = User.query.filter_by(phone=norm_phone).first()
            if user:
                return user
        return None

    def get_by_id(self, user_id: int) -> Optional[User]:
        return db.session.get(User, user_id)

    def exists(self, identifier: str) -> bool:
        return self.get_by_identifier(identifier) is not None

    def save(self, user: User) -> User:
        if user.id == 0:
            user.id = None
        if user.phone:
            user.phone = normalize_phone(user.phone)
        if user.email:
            user.email = user.email.strip().lower()
        db.session.add(user)
        db.session.commit()
        return user
