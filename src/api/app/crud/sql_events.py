from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models.solarpark import SolarPark
from app.models.solarpark_observation import SolarParkObservation


@event.listens_for(SolarParkObservation, "after_commit")
def update_name_of_model(mapper, connection, target):
    session = Session(bind=connection)
    solarpark = session.query(SolarPark).get(target.solarpark_id)
    observations = solarpark.observations
    solarpark.name_of_model = list(set(obs.name_of_model for obs in observations))
    session.commit()


@event.listens_for(SolarParkObservation, "after_commit")
def update_solarpark_dates(mapper, connection, target):
    session = Session(bind=connection)
    solarpark = session.query(SolarPark).get(target.solarpark_id)
    observations = solarpark.observations
    solarpark.first_detection = max(obs.date_of_data for obs in observations)
    solarpark.last_detection = min(obs.date_of_data for obs in observations)
    session.commit()


@event.listens_for(SolarParkObservation, "after_commit")
def update_average_confidence(mapper, connection, target):
    session = Session(bind=connection)
    solarpark = session.query(SolarPark).get(target.solarpark_id)
    observations = solarpark.observations
    solarpark.avg_confidence_over_all_observations = sum(
        obs.avg_confidence for obs in observations
    ) / len(observations)
    session.commit()


event.listen(SolarParkObservation, "after_insert", update_name_of_model)
event.listen(SolarParkObservation, "after_insert", update_solarpark_dates)
event.listen(SolarParkObservation, "after_insert", update_average_confidence)

event.listen(SolarParkObservation, "after_delete", update_name_of_model)
event.listen(SolarParkObservation, "after_delete", update_solarpark_dates)
event.listen(SolarParkObservation, "after_delete", update_average_confidence)
