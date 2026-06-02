from core.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, func
from sqlalchemy import Enum as SqlEnum
from enum import Enum
from models.enums import Priority, Difficulty, Status

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    priority = Column(SqlEnum(Priority), default=Priority.MEDIUM)

    deadline = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(), 
        default=func.now()
      )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)

    title = Column(String, nullable=False)
    
    description = Column(Text, nullable=True)

    estimated_minutes = Column(Integer, nullable=True)
    
    difficulty = Column(SqlEnum(Difficulty), default=Difficulty.MEDIUM)

    status = Column(SqlEnum(Status), default=Status.PENDING)

    created_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(), 
        default=func.now()
    )