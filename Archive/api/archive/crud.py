from sqlalchemy.orm import Session

from . import models, schemas


def get_solar_plant(db: Session, id_plant: int):
    return (
        db.query(models.SolarPlants)
        .filter(models.SolarPlants.id_plant == id_plant)
        .first()
    )


def get_solar_plants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SolarPlants).offset(skip).limit(limit).all()


def create_solar_plant(
    db: Session, solar_plant: schemas.SolarPlantsCreate
) -> models.SolarPlants:
    db_solar_plant = models.SolarPlants(**solar_plant.dict())
    db.add(db_solar_plant)
    db.commit()
    db.refresh(db_solar_plant)
    return db_solar_plant


def update_solar_plant(
    db: Session, db_solar_plant: models.SolarPlants, solar_plant: schemas.SolarPlants
) -> models.SolarPlants:
    update_data = solar_plant.dict(exclude_unset=True)
    for field in update_data:
        setattr(db_solar_plant, field, update_data[field])
    db.add(db_solar_plant)
    db.commit()
    db.refresh(db_solar_plant)
    return db_solar_plant


def delete_solar_plant(db: Session, id_plant: int) -> models.SolarPlants:
    db_solar_plant = (
        db.query(models.SolarPlants)
        .filter(models.SolarPlants.id_plant == id_plant)
        .first()
    )
    db.delete(db_solar_plant)
    db.commit()
    return db_solar_plant
