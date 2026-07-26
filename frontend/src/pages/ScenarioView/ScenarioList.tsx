import { useEffect, useState } from 'react'
import type { Scenario } from '../../types/scenario'
import * as scenariosApi from '../../api/scenarios'

const DAY_LABELS = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam']

// Stub phase 1 : liste en lecture seule. L'éditeur de création/modification et le moteur
// d'exécution (scheduler) sont des sujets différés — cf. todo list de session.
export function ScenarioList() {
  const [scenarios, setScenarios] = useState<Scenario[]>([])

  useEffect(() => {
    scenariosApi.getScenarios().then(setScenarios)
  }, [])

  return (
    <div className="page">
      <h2>Scénarios</h2>
      <div className="device-grid">
        {scenarios.map((scenario) => (
          <div key={scenario.id} className="device-card">
            <h4>{scenario.name}</h4>
            <div className="state">
              {scenario.daysOfWeek.map((d) => DAY_LABELS[d]).join(', ')} à {scenario.time}
            </div>
            <div className="state">{scenario.actions.length} action(s)</div>
          </div>
        ))}
      </div>
      <p className="stub-note">
        Création/édition de scénario et exécution planifiée disponibles une fois le moteur de
        scénarios (backend, phase différée) implémenté.
      </p>
    </div>
  )
}
