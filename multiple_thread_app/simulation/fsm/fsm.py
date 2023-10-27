from . import state
from . import transition
import copy
import random
import sys
import os
from datetime import datetime


class FSM:
    SEP = ':'

    def __init__(self, f_fsm_file=None, parms={}, save_enabled=True):
        self.parms = parms
        self.num_of_states = 0
        self.num_of_transitions = 0
        self.input_set = None
        self.output_set = None
        self.states = []
        self.transitions = []
        self.current_state = None
        self.init_state = None

        if f_fsm_file:
            self.__read_fsm(f_fsm_file)
            self.num_of_transitions = len(self.states)
            self.num_of_transitions = len(self.transitions)
        else:
            self.__generate_random_fsm(save_enabled)
            self.num_of_transitions = len(self.states)
            self.num_of_transitions = len(self.transitions)


    def __read_fsm(self, f_fsm_file):
        with open(f_fsm_file, 'r') as fn:
            for line in fn:
                line = line.strip()
                items = line.split(':')
                items = [item.strip() for item in items]
                
                if items[0].lower() == 'states':
                    self.num_of_states = int(items[1])
                    if len(items) > 2:
                        tokens = items[-1]
                    else:
                        tokens = ''
                    tokens = tokens.split('|')
                    tokens = [t.strip() for t in tokens]
                    self.__create_states(tokens)
                elif items[0].lower() == 'input_set':
                    symbols = items[1].split(',')
                    symbols = [c.strip() for c in symbols]
                    self.input_set = tuple(symbols)
                elif items[0].lower() == 'output_set':
                    symbols = items[1].split(',')
                    symbols = [c.strip() for c in symbols]
                    self.output_set = tuple(symbols)
                elif items[0] == '':
                    continue
                else:
                    self.transitions.append(self.__create_trans(items))
                    self.num_of_transitions += 1
        self.transitions = tuple(self.transitions)


    def __generate_random_fsm(self, save_enabled):
        settings = self.parms['FSM']['FSMDefault']    
        self.num_of_states = settings.get('NumberOfStates', 100)
        self.input_set = tuple(settings.get('InputSet', ('a', 'b', 'c')))
        self.output_set = tuple(settings.get('OutputSet', ('x', 'y')))

        self.__create_states()

        digraph_options = settings['DigraphShapeOptions']
        digraph_sel = settings['DigraphShapeSelection']

        if digraph_options[digraph_sel] == 'symmetric':
            self.__randomise_trans_symmetric(settings, save_enabled)


    def __create_states(self, tokens=[]):
        for i in range(self.num_of_states):
            try:
                t = tokens[i]
            except:
                t = ''
            s = state.State(i, token=t)
            self.states.append(s)
        self.states = tuple(self.states)
        self.set_init_state(0)
        self.set_current_state(0)


    def __create_trans(self, info):
        try:
            tr_id, start_s_id, end_s_id, i, o, t = info
            t = t.strip()
        except:
            tr_id, start_s_id, end_s_id, i, o = info
            t = ''

        tr_id = int(tr_id)
        start_s_id = int(start_s_id)
        end_s_id = int(end_s_id)

        start_s = False
        end_s = False

        for s in self.states:
            if s.id == start_s_id:
                start_s = s
            if s.id == end_s_id:
                end_s = s
            if start_s and end_s:
                break

        
        trx = transition.Transition(tr_id,
                                    start_s,
                                    end_s,
                                    i,
                                    o,
                                    t)
        start_s.add_out_transition(trx)
        end_s.add_in_transition(trx)
        return trx


    def __randomise_trans_symmetric(self, settings, save_enabled):
        tr_id = 0
        transitions = []
        for s_start in self.states:
            indexes = list(range(len(self.states)))
            for i in self.input_set:
                while indexes:
                    random.shuffle(indexes)
                    s_end_id = indexes[0]
                    s_end = self.states[s_end_id]

                    if s_end.get_in_degree() < len(self.input_set):
                        pos = random.randint(0, len(self.output_set)-1)
                        o = self.output_set[pos]
                        trx = transition.Transition(tr_id,
                                                    s_start,
                                                    s_end,
                                                    i, o, '')
                        s_start.add_out_transition(trx)
                        s_end.add_in_transition(trx)
                        transitions.append(trx)
                        tr_id = tr_id + 1
                        break
                    else:
                        indexes.remove(s_end_id)

        self.transitions = tuple(transitions)
        if save_enabled:
            self.save_fsm('symmetric', settings)


    def set_init_state(self, init_s=0):
        if isinstance(init_s, type(state.State())):
            self.init_state = init_s
            return self.init_state.id

        #  If current_s is a state ID.
        for s in self.states:
            if s.id == init_s:
                self.init_state = s
                return self.current_state


    def set_current_state(self, current_s=0):
        #  If current_s is a state object
        if isinstance(current_s, type(state.State())):
            self.current_state = current_s
            return self.current_state.id

        #  If current_s is a state ID.
        for s in self.states:
            if s.id == current_s:
                self.current_state = s
                return self.current_state


    def reset(self):
        """
        The FSM reset function resets M to its initial state.
            Note: Initial state may not be S0!
        """
        self.current_state = self.init_state


    def get_state(self, s_id):
        for s in self.states:
            if s.id == s_id:
                return s
        return None


    def trigger_trx(self, i):
        for trx in self.current_state.out_trans:
            if i == trx.input:
                self.set_current_state(trx.end_state)
                return trx.output

        #  An error state with id = -1
        self.set_current_state(state.State())
        return None


    def trigger_trxs(self, inputs):
        outputs = []
        for i in inputs:
            o = self.trigger_trx(i)
            outputs.append(o)
            if o is None:
                return outputs
        return outputs


    def copy(self):
        return copy.deepcopy(self)


    def is_minimal(self):
        return True


    def save_fsm(self, shape, settings):
        gen_file_name = self.parms['GeneralFileName']
        fsm_name = [gen_file_name, 'fsm', 'states',
                    (str(self.num_of_states)).zfill(10), shape]
        fsm_name = '_'.join(fsm_name)

        sys_config = self.parms['SysConfig']
        fsm_dir = sys_config['DATA_PATH'] + [gen_file_name]

        suffix = random.randint(10, 99)
        full_name = (os.path.join(*(fsm_dir+[fsm_name])) +
                     '_' + str(suffix) + '.txt')

        while os.path.exists(full_name):
            suffix = random.randint(10, 99)
            full_name = (os.path.join(*(fsm_dir+[fsm_name])) +
                     '_' + str(suffix) + '.txt')

        tmp = sys.stdout
        with open(full_name, 'w') as f:
            sys.stdout = f
            print('states:', self.num_of_states)
            print('input_set'+FSM.SEP, *','.join(self.input_set))
            print('output_set'+FSM.SEP, *','.join(self.output_set))
            print('')
            for tr in self.transitions:
                tr_id = str(tr.id)
                tr_id = tr_id + FSM.SEP + ' '*(5-len(tr_id))
                tr_str = '%d?%d?%s?%s' % (tr.start_state.id, tr.end_state.id, tr.input, tr.output)
                tr_str = tr_str.replace('?', FSM.SEP)
                print(tr_id, tr_str)
        sys.stdout = tmp


    def print_info(self, printing=False):
        width = 50
        prefix = '  '
        
        info = ['-'*width,
                prefix + ('Number of States: ' +
                          str(self.num_of_states)),
                prefix + ('Number of Transitions: ' +
                          str(self.num_of_transitions)),
                prefix + ('Initial State ID: ' +
                          str(self.init_state.id)),
                prefix + ('Current State ID: ' +
                          str(self.current_state.id)),
                ' ']
        for s in self.states:
            info.append(prefix*2 + '- ' + str(s))

        info.append(' ')
        
        for tr in self.transitions:
            info.append(prefix*2 + '[.] ' + str(tr))

        info.append('-'*width)
        info.append(' ')

        info = '\n'.join(info)

        if printing:
            print(info)

        return info


    def __str__(self):
        return self.print_info()
