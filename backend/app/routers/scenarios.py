from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..deps import get_current_user
from ..schemas import CamelModel, ScenarioOut

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"], dependencies=[Depends(get_current_user)])


class ScenarioActionCreate(CamelModel):
    device_id: str
    command: str
    params: dict = {}
    order: int = 0


class ScenarioCreate(CamelModel):
    name: str
    enabled: bool = True
    days_of_week: list[int]
    time: str
    actions: list[ScenarioActionCreate] = []


@router.get("", response_model=list[ScenarioOut])
def list_scenarios(db: Session = Depends(get_db)):
    return db.query(models.Scenario).all()


@router.post("", response_model=ScenarioOut, status_code=status.HTTP_201_CREATED)
def create_scenario(payload: ScenarioCreate, db: Session = Depends(get_db)):
    scenario = models.Scenario(
        name=payload.name,
        enabled=payload.enabled,
        days_of_week=payload.days_of_week,
        time=payload.time,
    )
    db.add(scenario)
    db.flush()
    for action in payload.actions:
        db.add(models.ScenarioAction(scenario_id=scenario.id, **action.model_dump()))
    db.commit()
    db.refresh(scenario)
    return scenario


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(scenario_id: str, db: Session = Depends(get_db)):
    scenario = db.get(models.Scenario, scenario_id)
    if scenario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Scénario introuvable")
    db.delete(scenario)
    db.commit()


# Note : pas d'endpoint /run-now ni de moteur d'exécution planifiée pour l'instant —
# le scheduler (APScheduler) est un sujet explicitement différé, cf. todo list de session.
