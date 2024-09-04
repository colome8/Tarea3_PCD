from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserCreate(BaseModel):
    user_id: int
    user_name: str = Field(min_length=1)
    user_email: EmailStr
    age: int = Field(default=None, gt=0, lt=120)
    recommendations: list[str] = Field(default=[])
    ZIP: str = Field(default=None)


@app.get("/")
def read_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@app.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(models.User.user_email == user.user_email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email ya registrado"
        )

    user_model = models.User(
        user_id=user.user_id,
        user_name=user.user_name,
        user_email=user.user_email,
        age=user.age,
        recommendations=user.recommendations,
        ZIP=user.ZIP,
    )

    db.add(user_model)
    db.commit()

    return user


@app.put("/{user_id}")
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):

    user_model = db.query(models.User).filter(models.User.user_id == user_id).first()

    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {user_id} : No existe"
        )

    user_model.user_name = user.user_name
    user_model.user_email = user.user_email
    user_model.age = user.age
    user_model.recommendations = user.recommendations
    user_model.ZIP = user.ZIP

    db.add(user_model)
    db.commit()

    return user


@app.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):

    user_model = db.query(models.User).filter(models.User.user_id == user_id).first()

    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {user_id} : No existe"
        )

    db.query(models.User).filter(models.User.user_id == user_id).delete()

    db.commit()

    return {"detail": f"Usuario con ID {user_id} eliminado"}
