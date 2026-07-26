import type { Floor } from '../types/floor'

export function FloorSwitcher({
  floors,
  selectedFloorId,
  onSelect,
}: {
  floors: Floor[]
  selectedFloorId: string | null
  onSelect: (floorId: string) => void
}) {
  return (
    <div className="floor-switcher">
      {floors.map((floor) => (
        <button
          key={floor.id}
          className={floor.id === selectedFloorId ? 'active' : ''}
          onClick={() => onSelect(floor.id)}
        >
          {floor.name}
        </button>
      ))}
    </div>
  )
}
