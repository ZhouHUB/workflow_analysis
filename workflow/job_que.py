__author__ = 'christopher'
from time import sleep
import traceback

from simdb.search import find_simulation_document
from pyiid.workflow.simulation import run_simulation

i = 0
print 'Start job queue'
while True:
    if i%10 == 0:
        print 'search for simulations to be run'
    sims = list(find_simulation_document(priority=True, ran=False, skip=False,
                                         error=False))
    if len(sims) == 0:
        # we didn't find anything, implying that there were no more un-run
        # simulations
        if i >= 300:
            print 'Idle for too long, exiting'
            exit()
        i += 1
        sleep(1)

    else:
        i = 0
        print 'Found {0} simulation enteries which have not been ran or ' \
              'flagged' \
              ' to be skipped'.format(len(sims))
        # run the simulations in the order they were added.
        for sim in reversed(sims):
            print 'start simulation number ', sim.id
            print 'simulation name', sim.name
            try:
                run_simulation(sim)
                # put a mass_save() here
            except KeyboardInterrupt:
                print 'run ended'
                pass
            except Exception as e:
                print 'Simulation number {} has errored'.format(sim.id)
                print traceback.format_exc()
                sim.error = True
                sim.save()
                pass
