import type { Room } from '../../types/room'

// Le viewBox 0-100 correspond directement aux coordonnées en pourcentage stockées dans Room.zoneShape,
// donc le rendu (image + zones) reste responsive sans recalcul JS quelle que soit la taille d'écran.
// Tant qu'aucune image n'est configurée pour l'étage, on retombe sur un fond gris uni.
export function FloorPlanImage({
  planImagePath,
  rooms,
  selectedRoomId,
  onSelectRoom,
}: {
  planImagePath: string | null
  rooms: Room[]
  selectedRoomId: string | null
  onSelectRoom: (roomId: string) => void
}) {
  return (
    <div className="floor-plan">
      <svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
        {planImagePath ? (
          <image href={planImagePath} x={0} y={0} width={100} height={100} preserveAspectRatio="none" />
        ) : (
          <rect x={0} y={0} width={100} height={100} fill="#e5e9ef" />
        )}
        {rooms.map((room) => {
          const points = room.zoneShape.map((p) => `${p.xPct},${p.yPct}`).join(' ')
          const centerX = room.zoneShape.reduce((sum, p) => sum + p.xPct, 0) / room.zoneShape.length
          const centerY = room.zoneShape.reduce((sum, p) => sum + p.yPct, 0) / room.zoneShape.length
          return (
            <g key={room.id} onClick={() => onSelectRoom(room.id)}>
              <polygon
                points={points}
                className={`room-zone${room.id === selectedRoomId ? ' selected' : ''}`}
              />
              <text x={centerX} y={centerY} textAnchor="middle" className="room-zone-label">
                {room.name}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
