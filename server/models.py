from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # Relationship to Recipe model
    recipes = relationship("Recipe", back_populates="user", cascade="all, delete-orphan")

    # Serialization rules to avoid recursion
    serialize_rules = ('-recipes.user', '-_password_hash')

    # Password hashing using bcrypt
    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hash is not readable.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Password authentication
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    # Validation for username
    @validates("username")
    def validate_username(self, key, username):
        if not username:
            raise ValueError("Username must be present.")
        if User.query.filter(User.username == username).first():
            raise ValueError("Username must be unique.")
        return username


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Relationship to User model
    user = relationship("User", back_populates="recipes")

    # Serialization rules to avoid recursion
    serialize_rules = ('-user.recipes',)

    # Validation for title
    @validates("title")
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Title must be present.")
        return title

    # Validation for instructions
    @validates("instructions")
    def validate_instructions(self, key, instructions):
        if not instructions:
            raise ValueError("Instructions cannot be empty.")
        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return instructions

    # Validation for minutes_to_complete
    @validates("minutes_to_complete")
    def validate_minutes_to_complete(self, key, minutes):
        if not isinstance(minutes, int) or minutes < 1:
            raise ValueError("Minutes to complete must be a positive integer.")
        return minutes