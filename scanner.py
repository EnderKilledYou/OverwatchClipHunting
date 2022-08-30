from Events.system import system_events
from Ocr.re_scaner import ReScanner

rescanner = ReScanner()
system_events.on('rescan', rescanner.add_job)
