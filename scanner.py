from Events.system import system_events
from Ocr.re_scaner import ReScanner

rescanner = ReScanner()
system_events.emit('rescan', rescanner.add_job)
