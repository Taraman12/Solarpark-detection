from sqlalchemy.orm import Session

from . import models, schemas


def get_solar_plant(db: Session, id_plant: int):
    return (
        db.query(models.SolarPlants)
        .filter(models.SolarPlants.id_plant == id_plant)
        .first()
    )


def create_solar_plant(db: Session, solar_plant: schemas.SolarPlantsCreate) -> models.SolarPlants:
    db_solar_plant = models.SolarPlants(**solar_plant.dict())
    db.add(db_solar_plant)
    db.commit()
    db.refresh(db_solar_plant)
    return db_solar_plant
