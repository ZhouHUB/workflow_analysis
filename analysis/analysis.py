__author__ = 'christopher'
import os
from inspect import isgenerator
from copy import deepcopy as dc

import ase.io as aseio
import matplotlib.pyplot as plt
import numpy as np
from ase.visualize import view
import matplotlib
from asap3.analysis.particle import FullNeighborList

from pyiid.workflow import sim_unpack
from pyiid.calc import wrap_rw
from pyiid.utils import tag_surface_atoms, get_angle_list, \
    get_coord_list, get_bond_dist_list
from simdb.search import *
from pyiid.kernels.cpu_nxn import get_d_array, get_r_array

font = {'family': 'normal',
        # 'weight' : 'bold',
        'size': 18}

matplotlib.rc('font', **font)
plt.ion()
colors = ['grey', 'red', 'royalblue']


def plot_pdf(scatter, gobs, atoms, save_file=None, show=True, **kwargs):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    gcalc = scatter.get_pdf(atoms)
    r = scatter.get_r()

    rw, scale = wrap_rw(gcalc, gobs)
    print 'Rw', rw * 100, '%'

    baseline = -1 * np.abs(1.5 * gobs.min())
    gdiff = gobs - gcalc * scale

    ax.plot(r, gobs, 'bo', label="G(r) data")
    ax.plot(r, gcalc * scale, 'r-', label="G(r) fit")
    ax.plot(r, gdiff + baseline, 'g-', label="G(r) diff")
    ax.plot(r, np.zeros_like(r) + baseline, 'k:')
    ax.set_xlabel(r"$r (\AA)$")
    ax.set_ylabel(r"$G (\AA^{-2})$")
    plt.legend(loc='best', prop={'size': 12})
    if save_file is not None:
        plt.savefig(save_file + '_pdf.eps', bbox_inches='tight',
                    transparent='True')
        plt.savefig(save_file + '_pdf.png', bbox_inches='tight',
                    transparent='True')
    if show is True:
        plt.show()
    return


def plot_waterfall_pdf(scatter, gobs, traj, save_file=None, show=True,
                       **kwargs):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    r = scatter.get_r()
    # ax.plot(r, gobs, 'bo', label="G(r) data")
    for i, atoms in enumerate(traj):
        gcalc = scatter.get_pdf(atoms)
        rw, scale = wrap_rw(gcalc, gobs)
        print i, 'Rw', rw * 100, '%'
        plt.plot(r, gcalc * scale + i, '-', label="Fit {}".format(i))
    ax.set_xlabel(r"$r (\AA)$")
    ax.set_ylabel(r"$G (\AA^{-2})$")
    ax.legend(loc='best', prop={'size': 12})
    if save_file is not None:
        plt.savefig(save_file + '_pdf.eps', bbox_inches='tight',
                    transparent='True')
        plt.savefig(save_file + '_pdf.png', bbox_inches='tight',
                    transparent='True')
    if show is True:
        plt.show()
    return


def plot_waterfall_diff_pdf(scatter, gobs, traj, save_file=None, show=True,
                            **kwargs):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    r = scatter.get_r()
    # ax.plot(r, gobs, 'bo', label="G(r) data")
    for i, atoms in enumerate(traj):
        gcalc = scatter.get_pdf(atoms)
        rw, scale = wrap_rw(gcalc, gobs)
        print i, 'Rw', rw * 100, '%'
        plt.plot(r, gobs - (gcalc * scale)
                 # - i
                 , '-', label="Fit {}".format(i))
    ax.set_xlabel(r"$r (\AA)$")
    ax.set_ylabel(r"$G (\AA^{-2})$")
    ax.legend(loc='best', prop={'size': 12})
    if save_file is not None:
        plt.savefig(save_file + '_pdf.eps', bbox_inches='tight',
                    transparent='True')
        plt.savefig(save_file + '_pdf.png', bbox_inches='tight',
                    transparent='True')
    if show is True:
        plt.show()
    return


def plot_waterfall_pdf_2d(scatter, gobs, traj, save_file=None, show=True,
                          **kwargs):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    r = scatter.get_r()
    # ax.plot(r, gobs, 'bo', label="G(r) data")
    gcalcs = []
    for i, atoms in enumerate(traj):
        gcalc = scatter.get_pdf(atoms)
        rw, scale = wrap_rw(gcalc, gobs)
        print i, 'Rw', rw * 100, '%'
        gcalcs.append(gcalc * scale)
    ax.imshow(gcalcs, aspect='auto', origin='lower',
              extent=(r.min(), r.max(), 0, len(traj)))
    ax.set_xlabel(r"$r (\AA)$")
    ax.set_ylabel("iteration")
    ax.legend(loc='best', prop={'size': 12})
    if save_file is not None:
        plt.savefig(save_file + '_2d_water_pdf.eps', bbox_inches='tight',
                    transparent='True')
        plt.savefig(save_file + '_2d_water_pdf.png', bbox_inches='tight',
                    transparent='True')
    if show is True:
        plt.show()
    return


def plot_waterfall_diff_pdf_2d(scatter, gobs, traj, save_file=None, show=True,
                               **kwargs):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    r = scatter.get_r()
    # ax.plot(r, gobs, 'bo', label="G(r) data")
    gcalcs = []
    for i, atoms in enumerate(traj):
        gcalc = scatter.get_pdf(atoms)
        rw, scale = wrap_rw(gcalc, gobs)
        print i, 'Rw', rw * 100, '%'
        gcalcs.append(gobs - gcalc * scale)
    ax.imshow(gcalcs, aspect='auto', origin='lower',
              extent=(r.min(), r.max(), 0, len(traj)))
    ax.set_xlabel(r"$r (\AA)$")
    ax.set_ylabel("iteration")
    ax.legend(loc='best', prop={'size': 12})
    if save_file is not None:
        plt.savefig(save_file + '_2d_water_diff_pdf.eps', bbox_inches='tight',
                    transparent='True')
        plt.savefig(save_file + '_2d_water_diff_pdf.png', bbox_inches='tight',
                    transparent='True')
    if show is True:
        plt.show()
    return


def plot_angle(cut, traj, target_configuration=None, save_file=None, show=True,
               index=-1,
               **kwargs):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    stru_l = {}
    # If the PDF document created with atomic config, use that as target
    if target_configuration is not None:
        stru_l['Target'] = target_configuration
    stru_l['Start'] = traj[0]
    stru_l['Finish'] = traj[index]
    for atoms in stru_l.values():
        if len(set(atoms.get_tags())) == 1:
            tag_surface_atoms(atoms)

    symbols = set(stru_l['Start'].get_chemical_symbols())

    tags = {'Core': (0, '+'), 'Surface': (1, '*')}
    for tag in tags.keys():
        tagged_atoms = stru_l['Start'][
            [atom.index for atom in stru_l['Start'] if
             atom.tag == tags[tag][0]]]
        if len(tagged_atoms) == 0:
            del tags[tag]
    if len(tags) == 1:
        tags = {'': (1, '*')}
    # need to change this
    bins = np.linspace(0, 180, 100)
    # Bin the data
    for n, key in enumerate(stru_l.keys()):
        for symbol in symbols:
            for tag in tags.keys():
                a, b = np.histogram(
                    get_angle_list(stru_l[key], cut, element=symbol,
                                   tag=tags[tag][0]), bins=bins)
                if False:
                    pass
                    # if np.alltrue(stru_l[key].pbc):
                    # crystal
                    # for y, x in zip(a, b[:-1]):
                    #     plt.axvline(x=x, ymax=y, color='grey', linestyle='--')
                else:
                    total = np.sum(a)
                    ax.plot(b[:-1], a,
                            label='{0} {1} {2}, {3}'.format(key,
                                                            symbol,
                                                            tag,
                                                            total),
                            marker=tags[tag][1], color=colors[n])
    ax.set_xlabel('Bond angle in Degrees')
    ax.set_xlim(0, 180)
    ax.set_ylabel('Angle Counts')
    ax.legend(loc='best', prop={'size': 12})
    if save_file is not None:
        plt.savefig(save_file + '_angle.eps', bbox_inches='tight',
                    transparent='True')
        plt.savefig(save_file + '_angle.png', bbox_inches='tight',
                    transparent='True')
    if show is True:
        plt.show()


def plot_coordination(cut, traj, target_configuration=None, save_file=None,
                      show=True, index=-1, **kwargs):
    stru_l = {}
    # If the PDF document created with atomic config, use that as target
    if target_configuration is not None:
        stru_l['Target'] = target_configuration
    stru_l['Start'] = traj[0]
    stru_l['Finish'] = traj[index]
    for atoms in stru_l.values():
        if len(set(atoms.get_tags())) == 1:
            tag_surface_atoms(atoms)

    symbols = set(stru_l.itervalues().next().get_chemical_symbols())
    tags = {'Core': (0, '+'), 'Surface': (1, '*')}
    for tag in tags.keys():
        tagged_atoms = stru_l.itervalues().next()[
            [atom.index for atom in stru_l.itervalues().next() if
             atom.tag == tags[tag][0]]]
        if len(tagged_atoms) == 0:
            del tags[tag]
    if len(tags) == 1:
        tags = {'': (1, '*')}
    b_min = None
    b_max = None
    for key in stru_l.keys():
        total_coordination = get_coord_list(stru_l[key], cut)
        l_min = min(total_coordination)
        l_max = max(total_coordination)
        if b_min is None or b_min > l_min:
            b_min = l_min
        if b_max is None or b_max < l_max:
            b_max = l_max
    if b_min == b_max:
        bins = np.asarray([b_min, b_max])
    else:
        bins = np.arange(b_min, b_max + 2)
    width = 3. / 4 / len(stru_l)
    offset = .3 * 3 / len(stru_l)
    patterns = ('x', '\\', 'o', '.', '\\', '*')

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for n, key in enumerate(stru_l.keys()):
        bottoms = np.zeros(bins.shape)
        j = 0
        for symbol in symbols:
            for tag in tags.keys():
                hatch = patterns[j]
                coord = get_coord_list(stru_l[key], cut, element=symbol,
                                       tag=tags[tag][0])
                a, b = np.histogram(coord, bins=bins)
                total = np.sum(a)
                ax.bar(b[:-1] + n * offset, a, width, bottom=bottoms[:-1],
                       color=colors[n],
                       label='{0} {1} {2}, {3}'.format(key, symbol, tag,
                                                       total),
                       hatch=hatch)
                j += 1
                bottoms[:-1] += a

    ax.set_xlabel('Coordination Number')
    ax.set_xticks(bins[:-1] + 1 / 2.)
    ax.set_xticklabels(bins[:-1])
    ax.set_ylabel('Atomic Counts')
    ax2 = plt.twinx()
    ax2.set_ylim(ax.get_ylim())
    ax.legend(loc='best', prop={'size': 12})
    if save_file is not None:
        plt.savefig(save_file + '_coord.eps', bbox_inches='tight',
                    transparent='True')
        plt.savefig(save_file + '_coord.png', bbox_inches='tight',
                    transparent='True')
    if show is True:
        plt.show()
    return


def plot_radial_bond_length(cut, traj, target_configuration=None,
                            save_file=None,
                            show=True, index=-1, **kwargs):
    stru_l = {}
    # If the PDF document created with atomic config, use that as target
    if target_configuration is not None:
        stru_l['Target'] = target_configuration
    stru_l['Start'] = traj[0]
    stru_l['Finish'] = traj[index]


    # fig = plt.figure()
    # axes = []
    # for i, key in enumerate(stru_l.keys()):
    #     axes.append(fig.add_subplot(len(stru_l.keys()), 1, i + 1))
    fig, axes = plt.subplots(len(stru_l.keys()), sharey=True)
    maxdist = 0.
    maxbond = 0.
    minbond = 10.
    for n, (key, ax) in enumerate(zip(stru_l.keys(), axes)):
        print n, 1, len(stru_l.keys())
        atoms = stru_l[key]
        com = atoms.get_center_of_mass()
        n_list = list(FullNeighborList(cut, atoms))
        dist_from_center = []
        bond_lengths = []
        stat_dist = []
        for i, coord in enumerate(n_list):
            dist = np.sqrt(np.sum((atoms[i].position - com)) ** 2)
            stat_dist.append(dist)
            sub_bond_lengths = []
            for j in coord:
                dist_from_center.append(dist)
                sub_bond_lengths.append(atoms.get_distance(i, j))
            bond_lengths.extend(sub_bond_lengths)
        ax.scatter(dist_from_center, bond_lengths, c=colors[n], marker='o',
                   label='{0}'.format(key), s=40)
        if np.max(dist_from_center) > maxdist:
            maxdist = np.max(dist_from_center)
        if np.max(bond_lengths) > maxbond:
            maxbond = np.max(bond_lengths)
        if np.min(bond_lengths) < minbond:
            minbond = np.min(bond_lengths)

        ax.legend(loc='best', prop={'size': 12})

    for i, ax in enumerate(axes):
        ax.set_xlim(-0.5, maxdist + .5)
        ax.set_ylim(minbond - .1, maxbond + .1)
        if i == 1:
            ax.set_ylabel('Bond Distance $(\AA)$')
    ax.set_xlabel('Distance from Center $(\AA)$')

    if save_file is not None:
        plt.savefig(save_file + '_rbonds.eps', bbox_inches='tight',
                    transparent='True')
        plt.savefig(save_file + '_rbonds.png', bbox_inches='tight',
                    transparent='True')
    if show is True:
        plt.show()
    return


def plot_bonds(sim, cut, save_file=None, show=True, index=-1):
    atomic_config, = find_atomic_config_document(_id=sim.atoms.id)
    traj = atomic_config.file_payload
    stru_l = {}
    # If the PDF document created with atomic config, use that as target
    cl = sim.pes.calc_list
    for calc in cl:
        if calc.calculator == 'PDF':
            break
    # If we used a theoretical target structure, get it and name it
    # if calc.ase_config_id is not None:
    #     target_atoms, = find_atomic_config_document(_id=calc.ase_config_id)
    #     stru_l['Target'] = target_atoms.file_payload

    stru_l['Start'] = traj[0]
    stru_l['Finish'] = traj[index]
    for atoms in stru_l.values():
        tag_surface_atoms(atoms, cut)

    symbols = set(stru_l['Start'].get_chemical_symbols())
    tags = {'Core': (0, '+'), 'Surface': (1, '*')}
    for tag in tags.keys():
        tagged_atoms = stru_l['Start'][
            [atom.index for atom in stru_l['Start'] if
             atom.tag == tags[tag][0]]]
        if len(tagged_atoms) == 0:
            del tags[tag]
    linestyles = ['-', '--', ':']

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for n, key in enumerate(stru_l.keys()):
        for k, symbol in enumerate(symbols):
            for tag in tags.keys():
                bonds = get_bond_dist_list(
                    stru_l[key], cut, element=symbol, tag=tags[tag][0])
                a, b = np.histogram(bonds, bins=10)
                plt.plot(b[:-1], a, linestyles[k],
                         label=key + ' ' + symbol + ' ' + tag,
                         marker=tags[tag][1], color=colors[n])
    ax.set_xlabel('Bond distance in angstrom')
    ax.set_ylabel('Bond Counts')
    plt.legend(loc='best', prop={'size': 12})
    if save_file is not None:
        plt.savefig(save_file + '_angle.eps', bbox_inches='tight',
                    transparent='True')
        plt.savefig(save_file + '_angle.png', bbox_inches='tight',
                    transparent='True')
    if show is True:
        plt.show()


def ase_view(traj, **kwargs):
    view(traj)


def plot_average_coordination(cut, traj, target_configuration=None,
                              save_file=None,
                              show=True, index=-1, **kwargs):
    stru_l = {}
    # If the PDF document created with atomic config, use that as target
    if target_configuration is not None:
        stru_l['Target'] = target_configuration
    stru_l['Start'] = traj[0]
    stru_l['Equilibrium'] = traj[index]
    for atoms in stru_l.values():
        tag_surface_atoms(atoms)

    symbols = set(stru_l.itervalues().next().get_chemical_symbols())
    tags = {'Core': (0, '+'), 'Surface': (1, '*')}
    for tag in tags.keys():
        tagged_atoms = stru_l.itervalues().next()[
            [atom.index for atom in stru_l.itervalues().next() if
             atom.tag == tags[tag][0]]]
        if len(tagged_atoms) == 0:
            del tags[tag]
    if len(tags) == 1:
        tags = {'': (1, '*')}
    b_min = None
    b_max = None
    for key in stru_l.keys():
        total_coordination = get_coord_list(stru_l[key], cut)
        l_min = min(total_coordination)
        l_max = max(total_coordination)
        if b_min is None or b_min > l_min:
            b_min = l_min
        if b_max is None or b_max < l_max:
            b_max = l_max
    if b_min == b_max:
        bins = np.asarray([b_min, b_max])
    else:
        bins = np.arange(b_min, b_max + 2)
    width = 3. / 4 / len(stru_l)
    offset = .3 * 3 / len(stru_l)
    patterns = ('x', '\\', 'o', '.', '\\', '*')

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for n, key in enumerate(stru_l.keys()):
        bottoms = np.zeros(bins.shape)
        j = 0
        for symbol in symbols:
            for tag in tags.keys():
                hatch = patterns[j]
                coord = get_coord_list(stru_l[key], cut, element=symbol,
                                       tag=tags[tag][0])
                a, b = np.histogram(coord, bins=bins)
                total = np.sum(a)
                ax.bar(b[:-1] + n * offset, a, width, bottom=bottoms[:-1],
                       color=colors[n],
                       label='{0} {1} {2}, {3}'.format(key, symbol, tag,
                                                       total),
                       hatch=hatch)
                j += 1
                bottoms[:-1] += a

    ax.set_xlabel('Coordination Number')
    ax.set_xticks(bins[:-1] + 1 / 2.)
    ax.set_xticklabels(bins[:-1])
    ax.set_ylabel('Atomic Counts')
    ax2 = plt.twinx()
    ax2.set_ylim(ax.get_ylim())
    ax.legend(loc='best', prop={'size': 12})
    if save_file is not None:
        plt.savefig(save_file + '_coord.eps', bbox_inches='tight',
                    transparent='True')
        plt.savefig(save_file + '_coord.png', bbox_inches='tight',
                    transparent='True')
    if show is True:
        plt.show()
    return


def save_config(new_dir_path, name, d, index=-1, rotation_atoms=None):
    if rotation_atoms is None:
        atoms = d['traj'][index]
        n = len(atoms)
        q = atoms.positions
        dist = np.zeros((n, n, 3), np.float32)
        r = np.zeros((n, n), np.float32)
        get_d_array(dist, q)
        get_r_array(r, dist)
        maxpos = np.argmax(r)
        rotation_atoms = np.unravel_index(maxpos, r.shape)
    out_l = [
        d['traj'][index],
        d['target_configuration'],
        d['traj'][0]
    ]
    append_names = ['_min', '_target', '_start']
    file_endings = ['.eps', '.png', '.xyz', '.pov']

    for atoms, an in zip(out_l, append_names):
        atoms.center()
        # Rotate the config onto the viewing axis
        atoms.rotate(atoms[rotation_atoms[0]].position - atoms[
            rotation_atoms[1]].position, 'z')
        atoms.center()
        # save the total configuration
        for e in file_endings:
            file_name = os.path.join(new_dir_path, name + an + e)
            aseio.write(file_name, atoms)
        # cut the config in half along the xy plane
        atoms2 = dc(atoms)
        atoms2.set_constraint()
        atoms2.translate(-1 * atoms2.get_center_of_mass())
        print atoms2.positions
        del atoms2[[atom.index for atom in atoms2 if atom.position[2] >= 0]]
        for e in file_endings:
            file_name = os.path.join(new_dir_path, name + '_half' + an + e)
            aseio.write(file_name, atoms2)


def mass_plot(sims, cut, analysis_type='last'):
    if not isgenerator(sims) and not isinstance(sims, list):
        sims = [sims]
    for sim in sims:
        d = sim_unpack(sim)
        if analysis_type == 'min':
            pel = []
            for atoms in d['traj']:
                if atoms._calc is not None:
                    pel.append(atoms.get_potential_energy())
            index = np.argmin(pel)
            print index
            print pel[index]
        elif analysis_type == 'last':
            index = -1
        ase_view(**d)
        plot_pdf(atoms=d['traj'][index], **d)
        plot_angle(cut, index=index, **d)
        plot_coordination(cut, index=index, **d)
        plot_radial_bond_length(cut, index=index, **d)


def mass_save(sims, cut, destination_dir, analysis_type='last'):
    if not isgenerator(sims) or not isinstance(sims, list):
        sims = [sims]
    for sim in sims:
        name = str(sim.atoms.id)
        new_dir_path = os.path.join(destination_dir, str(sim.name))
        if not os.path.exists(new_dir_path):
            os.mkdir(os.path.join(destination_dir, sim.name))
        d = sim_unpack(sim)
        if analysis_type == 'min':
            pel = []
            for atoms in d['traj']:
                if atoms._calc is not None:
                    pel.append(atoms.get_potential_energy())
            index = int(np.argmin(pel))
            print index
            print pel[index]
        elif analysis_type == 'last':
            index = -1

        save_config(new_dir_path, name, d, index)
        plot_pdf(atoms=d['traj'][index], show=False,
                 save_file=os.path.join(new_dir_path, name), **d)

        plot_angle(cut, show=False, save_file=os.path.join(new_dir_path, name),
                   index=index, **d)

        plot_coordination(cut, show=False,
                          save_file=os.path.join(new_dir_path, name),
                          index=index, **d)

        plot_radial_bond_length(cut, show=False,
                                save_file=os.path.join(new_dir_path, name),
                                index=index, **d)


if __name__ == '__main__':
    from simdb.search import *

    sims = list(find_simulation_document())
    # sim = sims[20]
    # d = sim_unpack(sim)

    # atoms = d['target_configuration']
    # n = len(atoms)
    # q = atoms.positions
    # d = np.zeros((n, n, 3), np.float32)
    # r = np.zeros((n, n), np.float32)
    # get_d_array(d, q)
    # get_r_array(r, d)
    # maxr = np.max(r)
    # maxpos = np.argmax(r)
    # maxpos = np.unravel_index(maxpos, r.shape)
    # maxpos = (27, 28)
    # print maxr, maxpos
    # atoms.rotate(atoms[maxpos[0]].position - atoms[maxpos[1]].position, 'z')
    # view(atoms)
    dest = '/mnt/bulk-data/Dropbox/BNL_Project/HMC_paper/figures'
    mass_save(sims[40], 3.5, dest, 'min')

    # ase_view(**d)
    # plot_radial_bond_length(3.5, **d)
    # plot_coordination(3.2, **d)
    # a, b = get_coord_list(d['traj'][50:], 1.45)
    # plot_radial_bond_length(3.5, **d)
    # mass_plot(sim, 3.5, 'min')
