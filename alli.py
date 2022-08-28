from Events.system import system_events
from Monitors.heart_beat import HeartBeat

alli = HeartBeat()

system_events.on('avoid_streamer',alli.unclaim_streamer)