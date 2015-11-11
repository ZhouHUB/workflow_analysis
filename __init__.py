__author__ = 'christopher'

from simdb.search import *


def sim_unpack(sim):
    sim.reload()
    d = {}
    cl = sim.pes.calc_list
    for cal in cl:
        if cal.calculator == 'PDF':
            calc, = find_calc_document(_id=cal.id)
            d['scatter'] = calc.payload.scatter
            d['gobs'] = calc.payload.gobs
            if calc.calc_exp['ase_config_id'] is not None:
                ac, = find_atomic_config_document(
                    _id=calc.calc_exp.ase_config_id.id)
                d['target_configuration'], = ac.file_payload
    atomic_configs, = find_atomic_config_document(_id=sim.atoms.id)

    d['traj'] = atomic_configs.file_payload

    return d


if __name__ == '__main__':
    from analysis import *

    sim = find_simulation_document(name=unicode('C60 rattle->DFT 0.05')).next()
    sim_dict = sim_unpack(sim)
    print sim_dict['target_configuration']

    ase_view(**sim_dict)
    # plot_pdf(atoms=sim_dict['traj'][-1], **sim_dict)
    # plot_pdf(atoms=sim_dict['traj'][0], **sim_dict)
    # plot_waterfall_pdf(**sim_dict)
    # plot_waterfall_diff_pdf(**sim_dict)

    # MASSIVE PROBLEM HERE DON'T KNOW WHY
    # plot_angle(1.6, **sim_dict)
    plot_coordination(1.6, **sim_dict)
