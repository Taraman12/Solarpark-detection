from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/solar_plants/", response_model=schemas.SolarPlants)
def create_solar_plant(
    solar_plant: schemas.SolarPlantsCreate, db: Session = Depends(get_db)
):
    db_solar_plant = crud.create_solar_plant(db, id_plant=solar_plant.id_plant)
    if db_solar_plant:
        raise HTTPException(status_code=400, detail="Solar plant already registered")
    return crud.create_solar_plant(db=db, solar_plant=solar_plant)


@app.get("/solar_plants/{id_plant}", response_model=schemas.SolarPlants)
def read_solar_plant(id_plant: int, db: Session = Depends(get_db)):
    db_solar_plant = crud.post_solar_plant(db, id_plant=id_plant)
    if db_solar_plant is None:
        raise HTTPException(status_code=404, detail="Solar plant not found")
    return db_solar_plant
