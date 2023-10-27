"""
This is multi-threading based framework for constructing multiple UIOs
using Genetic Algorithms (GAs).
"""


from simulation.fsm import fsm
from simulation.sst import sst
from simulation.evaluation import fitness_evaluation as fe
from simulation.evaluation import uio_statistics as st
from simulation.ga import ga
import json
import os
import sys
from datetime import datetime
import pickle


x = sys.getrecursionlimit()
sys.setrecursionlimit(50*x)


width = 65
info = []

sys_config = {
    'GENERAL_PATH': ['input_output'],
    'CONFIG_PATH': ['input_output', 'config'],
    'FSM_PATH': ['input_output', 'config', 'fsm'],
    'PARM_PATH': ['input_output', 'config', 'parms'],
    'DATA_PATH': ['input_output', 'results'],
    'PARM_FILE': 'parms.json',
    'CPUs': os.cpu_count()}


def save_statistics_obj(f_base, uio_stat, ext='db', mode='wb'):
    #  Save computational results to a file
    data_file = ''.join([f_base, '_obj', '.', ext])
    data_file = os.path.join(
        *(sys_config['DATA_PATH'] + [f_base, data_file]))
    data_file = os.path.normpath(data_file)

    with open(data_file, mode) as fn:
        pickle.dump(uio_stat, fn)

    obj_profile = data_file.replace('.' + ext, '_path.txt')
    obj_profile = os.path.normpath(obj_profile)

    with open(obj_profile, 'w') as fn:
        info = '{0}'.format([data_file])
        fn.write(info)


def plot_statitiscs_graphs(f_base, uio_stat):
    #  Produce and save statistical graph
    g_line_file = ''.join([f_base, '_line', '.', 'png'])
    g_line_file = os.path.join(
        *(sys_config['DATA_PATH'] + [f_base, g_line_file]))
    g_line_file = os.path.normpath(g_line_file)
    uio_stat.plot_trendency_graph(g_line_file)


    g_pie_file = ''.join([f_base, '_pie', '.', 'png'])
    g_pie_file = os.path.join(
        *(sys_config['DATA_PATH'] + [f_base, g_pie_file]))
    g_pie_file = os.path.normpath(g_pie_file)
    uio_stat.plot_UIO_distribution(g_pie_file)


    g_bar_file = ''.join([f_base, '_bar', '.', 'png'])
    g_bar_file = os.path.join(
        *(sys_config['DATA_PATH'] + [f_base, g_bar_file]))
    g_bar_file = os.path.normpath(g_bar_file)
    uio_stat.plot_UIO_frequencies(g_bar_file)


def save_uio_data(f_base, uio_stat, stat_enabled, ext='txt'):
    data_file = ''.join([f_base, '_uio', '.', ext])
    data_file = os.path.join(
        *(sys_config['DATA_PATH'] + [f_base, data_file]))
    data_file = os.path.normpath(data_file)

    width = 50
    with open(data_file, 'w') as fn:
        fn.write('  All discovred UIOs\n')
        fn.write('-'*width + '\n')
        fn.write(str(uio_stat.all_discovered_uios))
        fn.write('\n\n')

        if stat_enabled:
            fn.write('  Generation based discovred UIOs\n')
            fn.write('-'*width + '\n')
            fn.write(str(uio_stat.gen_discovered_uios))
            fn.write('\n\n')

            fn.write('  Generation based UIO frequencies:\n')
            fn.write('-'*width + '\n')
            fn.write(str(uio_stat.gen_uio_frequencies))
            fn.write('\n\n')

            fn.write('  Generation based UIO distributions:\n')
            fn.write('-'*width + '\n')
            fn.write(str(uio_stat.gen_uio_distribution))


def save_simulation_result(gen_file_name,
                           uio_stat,
                           stat_enabled,
                           ext='db',
                           mode='wb'):

    #  Save UIO statistics
    if stat_enabled:
        save_statistics_obj(gen_file_name, uio_stat)
        plot_statitiscs_graphs(gen_file_name, uio_stat)
    save_uio_data(gen_file_name, uio_stat, stat_enabled)


def read_parms(f_gen_name):
    parms = {}
    parm_config = os.path.join(
        *(sys_config['PARM_PATH'] +
          [sys_config['PARM_FILE']]))

    with open(parm_config, 'r') as fn:
        parms = json.load(fn)

    parms['SysConfig'] = sys_config
    parms['GeneralFileName'] = f_gen_name

    return parms


def produce_fsm(parms, save_enabled=True):
    fsm_file = (parms['FSM']).get('File')
    fsm_settings = {}    
    all_targetted_uios = {}

    if fsm_file:
        fsm_file = os.path.join(
            *(sys_config['FSM_PATH']+[fsm_file]))
        
        uio_set_file = (parms['FSM']).get('UIOSet')
        if uio_set_file is not None:
            uio_set_file = (os.path.join(
                *(sys_config['FSM_PATH'] +
                  [uio_set_file])))
            with open(uio_set_file, 'r') as fn:
                uio_data = json.load(fn)
                for uio in uio_data['UIOs']:
                    all_targetted_uios[uio] = 0
        return (all_targetted_uios,
                fsm.FSM(fsm_file, save_enabled=False))

    return (all_targetted_uios,
            fsm.FSM(parms=parms, save_enabled=save_enabled))


def generate_file_name(dt=datetime.now(), create_dir=True):
    """
    The function creates a general name that is used to prefix the
    file names for all experimental results.
    """
    f_name = str(dt)
    for c in ['-', ':']:
        f_name = f_name.split(c)
        f_name = ''.join(f_name)

    for c in [' ', '.']:
        f_name = f_name.replace(c, '_')

    if create_dir:
        gen_dir = (os.path.join(*(sys_config['DATA_PATH'] +
                                  [f_name])))
        if not os.path.exists(gen_dir):
            os.mkdir(gen_dir)

    return f_name


def measure_times(funcs=[]):
    """
    The measure_times() function measures the time (in seconds) used to execute
    a list of functions with their specified arguments.
    """
    t1 = datetime.now()

    for func, args in funcs:
        func(*args)

    t2 = datetime.now()

    t1 = t1.timestamp()
    t2 = t2.timestamp()

    return t2 - t1
    

def read_settings():
    f_gen_name = generate_file_name(create_dir=True)
    parms = read_parms(f_gen_name)
    
    all_targetted_uios, f_template = produce_fsm(
        parms, save_enabled=True)

    return f_gen_name, parms, all_targetted_uios, f_template


#  ----------------------------------------------------
#      Start simulation here ...
#  ----------------------------------------------------
def start_sim(f_gen_name,
              parms,
              all_targetted_uios,
              f_template):

    sst_template = sst.SST(fsm=f_template)
    fitness_eval = fe.FitnessEvaluation(parms)
    uio_stat = st.UIOStatistics(parms, all_targetted_uios)

    g_sim = ga.GA(f_template, sst_template, parms)

    funcs = [(g_sim.start, (fitness_eval, uio_stat))]
    
    # if parms['GA']['StatisticsEnabled']:
    #    funcs.append((save_simulation_result, (f_gen_name, uio_stat)))

    ts = measure_times(funcs)
    print('')
    save_simulation_result(f_gen_name,
                           uio_stat,
                           parms['GA']['StatisticsEnabled'])

    return ts


def read_pickle_data(f):
    with open(f, 'rb') as fn:
        obj = pickle.load(fn)

    print(obj.gen_uio_frequencies)
    print(obj.gen_discovered_uios)


def start(printing_enabled=True):
    f_gen_name, parms, all_targetted_uios, f_template = read_settings()

    info = [
        '-' * width,
        "  >> Constructing multiple UIOs using Genetic Algorithms <<",
        '-' * width]
    item = parms['SysConfig']['CPUs']
    item = '    [.] Number of CPUs:             ' + str(item)
    info.append(item)

    if parms['ParallelismEnabled']:
        item = parms['NumberOfThreadsPerCPU']
        item = '    [.] Threads per CPU:            ' + str(item)
        info.append(item)

    item = f_template.num_of_states
    item = '    [.] Number of States:           ' + str(item)
    info.append(item)

    item = f_template.num_of_transitions
    item = '        Number of Transitions:      ' + str(item)
    info.append(item)

    item = len(f_template.input_set)
    item = '        Input Size:                 ' + str(item)
    info.append(item)

    item = parms['MaxUIOLength']
    item = '        Max UIO Length:             ' + str(item)
    info.append(item)

    item = parms['GA']['PopulationSize']
    item = '    [.] GA Population Size:         ' + str(item)
    info.append(item)

    item = parms['GA']['Generation']
    item = '    [.] GA Generation:              ' + str(item)
    info.append(item)

    info.extend([
        '       ' + '~' * 40,
        '    [-] Simulation is started!',
        '    [-] It will take a while. Please be patient ...',
        '',
        '         ... working in progress ...',
        ''])

    if printing_enabled:
        print('\n'.join(info))

    time_used = start_sim(f_gen_name,
                          parms,
                          all_targetted_uios,
                          f_template)

    info2 = [
        "    [*] Simulation is completed.",
        "    [*] It takes total " + str(time_used) + " seconds",
        "        to complete the work",
        '-' * width]

    if printing_enabled:
        print('\n'.join(info2))

    info.extend(info2)

    f_time_name = (f_gen_name +
                  ('_parallel' if parms['ParallelismEnabled']
                   else '_single'))
    f_time_name = f_time_name+'_timer.txt'
    f_time_name = (sys_config['DATA_PATH'] + [f_gen_name, f_time_name])

    f_time_name = os.path.join(*f_time_name)
    f_time_name = os.path.normpath(f_time_name)

    with open(f_time_name, 'w') as fn:
        fn.write('\n'.join(info))

    sys.setrecursionlimit(x)



if __name__ == '__main__':
    start()
    # read_pickle_data(f)
