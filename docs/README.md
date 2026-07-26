# Documentation — index

Organisation **par thème**, pas par fonctionnalité ni par branche : chaque fichier couvre un domaine du logiciel et est mis à jour au fil des fonctionnalités qui le concernent, plutôt que de créer un nouveau fichier à chaque fois.

- `specs/` décrit le comportement attendu (ce que le logiciel fait, cas limites, cas de tests à couvrir).
- `architecture/` décrit comment c'est construit (fichiers concernés, raisons, ce qui ne change pas).

`SPEC.md` et `DIAGRAMS.md` (racine du dépôt) restent des résumés courts pour une vue d'ensemble rapide ; ce dossier contient le détail.

## Thèmes couverts

| Thème | Spec | Architecture | Dernière mise à jour |
|---|---|---|---|
| Types d'équipements (volet, porte de garage, lumière, ventilateur...) | [specs/device-types.md](specs/device-types.md) | [architecture/device-types.md](architecture/device-types.md) | Base initiale (volet, porte de garage) |
| Contrat API front/back (REST + WebSocket) | [specs/api-contract.md](specs/api-contract.md) | [architecture/api-contract.md](architecture/api-contract.md) | Base initiale |

## Processus pour une nouvelle fonctionnalité

1. Identifier quel(s) thème(s) ci-dessus la fonctionnalité concerne (ou si un nouveau thème est nécessaire).
2. Sur la branche dédiée, commencer par mettre à jour la section concernée dans le(s) fichier(s) `specs/*.md` (comportement + cas de tests) et `architecture/*.md` (fichiers touchés + raison) — avant tout code.
3. Implémenter, écrire les tests listés, ouvrir la PR en référençant les sections de doc modifiées.
4. Une fois mergé, mettre à jour la colonne "dernière mise à jour" ci-dessus.
