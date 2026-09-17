import { io } from 'socket.io-client'

// Connect lazily — call connectSocket() once, from App.jsx, after mount.
// The backend team decides the event names; update the constants below
// to match whatever they land on (ask them for an "events" doc).
let socket = null

export const SOCKET_EVENTS = {
  CYCLE_UPDATED: 'cycle:updated', // full state refresh after a simulation tick
  HERD_MOVED: 'herd:moved', // incremental single-herd position update
  SIGHTING_VERIFIED: 'sighting:verified' // an officer's manual update was accepted
}

export function connectSocket(onEvent) {
  if (socket) return socket
  socket = io('/', { path: '/socket.io', transports: ['websocket'] })

  Object.values(SOCKET_EVENTS).forEach(eventName => {
    socket.on(eventName, payload => onEvent(eventName, payload))
  })

  return socket
}

export function disconnectSocket() {
  socket?.disconnect()
  socket = null
}
