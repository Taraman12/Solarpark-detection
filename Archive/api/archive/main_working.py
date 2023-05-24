# import uvicorn
from fastapi import Depends, FastAPI, HTTPException, APIRouter, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session


from . import crud, models, schemas
from .database import SessionLocal, engine
from .models import SolarPlants

models.Base.metadata.create_all(bind=engine)

# app = FastAPI(root_path="/api/v1")
app = FastAPI()

origins = [
    "https://localhost.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://localhost:*",
    "172.19.0.1:34048",
    "172.19.0.1:*",
    "172.20.0.1" "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Hello World!"}


@app.get("/app")
def read_main(request: Request):
    return {"message": "Hello World", "root_path": request.scope.get("root_path")}


@app.get(
    "/solar-plant/{id_plant}",
    response_model=schemas.SolarPlants,
    tags=["solar-plants"],
)
def read_solar_plant(id_plant: int, db: Session = Depends(get_db)) -> SolarPlants:
    db_solar_plant = crud.get_solar_plant(db, id_plant=id_plant)
    if db_solar_plant is None:
        raise HTTPException(status_code=404, detail="Solar plant not found")
    return db_solar_plant


@app.get(
    "/solar-plants",
    response_model=schemas.SolarPlants,
    tags=["solar-plants"],
)
def read_solar_plants(db: Session = Depends(get_db)) -> SolarPlants:
    db_solar_plant = crud.get_solar_plants(db)
    if db_solar_plant is None:
        raise HTTPException(status_code=404, detail="Solar plant not found")
    return db_solar_plant


@app.post(
    "/solar-plant/",
    response_model=schemas.SolarPlants,
    status_code=status.HTTP_201_CREATED,
    tags=["solar-plants"],
)
def create_solar_plant(
    solar_plant: schemas.SolarPlantsCreate, db: Session = Depends(get_db)
):
    db_solar_plant = crud.get_solar_plant(db, id_plant=id_plant)
    if db_solar_plant:
        raise HTTPException(status_code=400, detail="Solar plant already registered")
    return crud.create_solar_plant(db=db, solar_plant=solar_plant)


@app.put(
    "/solar-plant/{id_plant}",
    response_model=schemas.SolarPlants,
    tags=["solar-plants"],
)
def update_solar_plant(
    id_plant: int, solar_plant: schemas.SolarPlants, db: Session = Depends(get_db)
):
    db_solar_plant = crud.update_solar_plant(db, id_plant=id_plant)
    if db_solar_plant is None:
        raise HTTPException(status_code=404, detail="Solar plant not found")
    return crud.update_solar_plant(
        db=db, db_solar_plant=db_solar_plant, solar_plant=solar_plant
    )


@app.delete(
    "/solar-plant/{id_plant}",
    response_model=schemas.SolarPlants,
    tags=["solar-plants"],
)
def delete_solar_plant(id_plant: int, db: Session = Depends(get_db)):
    db_solar_plant = crud.get_solar_plant(db, id_plant=id_plant)
    if db_solar_plant is None:
        raise HTTPException(status_code=404, detail="Solar plant not found")
    return crud.delete_solar_plant(db=db, db_solar_plant=db_solar_plant)


# optional parameters
# def read_item(skip: int = 0, limit: int = 10):
# def create_item(item_id: int, item: Item, q: str | None = None):
# def read_items(q: Annotated[str | None, Query(max_length=50)] = None)

# if __name__ == "__main__":
#    uvicorn.run(app, host="127.0.0.1", port=8000)
