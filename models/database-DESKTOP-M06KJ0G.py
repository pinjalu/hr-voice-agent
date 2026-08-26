from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import datetime

Base = declarative_base()

def get_local_time():
    # Return local time for the server (IST)
    return datetime.datetime.now()

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=get_local_time)

    answers = relationship("InterviewAnswer", back_populates="candidate")
    aptitude_results = relationship("AptitudeResult", back_populates="candidate")
    final_result = relationship("FinalResult", back_populates="candidate", uselist=False)

class InterviewAnswer(Base):
    __tablename__ = "interview_answers"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    question_index = Column(Integer)
    question_text = Column(String(500))
    transcribed_answer = Column(Text)
    
    candidate = relationship("Candidate", back_populates="answers")

class AptitudeResult(Base):
    __tablename__ = "aptitude_results"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    question_index = Column(Integer)
    question_text = Column(String(500))
    given_answer = Column(String(500))
    correct_answer = Column(String(500))
    is_correct = Column(Boolean)

    candidate = relationship("Candidate", back_populates="aptitude_results")

class FinalResult(Base):
    __tablename__ = "final_results"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    interview_score = Column(Float)
    aptitude_score = Column(Float)
    total_score = Column(Float)
    status = Column(String(50))  # Shortlisted, Review, Reject
    transcript = Column(Text)
    created_at = Column(DateTime, default=get_local_time)

    candidate = relationship("Candidate", back_populates="final_result")

DATABASE_URL = "sqlite:///./hr_assistant.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
