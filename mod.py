import numpy as np
import pickle, itertools, time, os, datetime, utils

class Moderator:

    def __init__(self, canonical_p, note=True):
        self.canon_p = canonical_p
        self.test_var = None
        self.n_exp = None
        self.exp_list = None
        self.key_list = []
        self.ind_list = None
        self.titles = '{:<8}'
        self.err_mat = None
        self.time = None
        self.backup_filename = None
        self.runtime_arr = None
        self.ready = False
        self.output = []
        self.note = note
    
    def setup(self, test_range_dict):
        action = False
        if self.ready:
            if input('This batch has been arranged. Enter y to overwrite.') == 'y':
                action = True
            else:
                print('No action taken.')
        if self.ready == False:
            action = True
            self.ready = True

        if action == True:
            err_mat_shape = []
            grid_value_list = []
            ind_list = []
            for k, v in test_range_dict.items():
                if k not in self.canon_p:
                    raise ValueError('Key not found in the parameter dictionary.')
                err_mat_shape.append(len(v))
                grid_value_list.append(v)
                self.key_list.append(k)

                '''Prepare formatting for display'''
                self.titles += '{:<10}'
                ind_list.append(list(range(len(v))))

            err_mat_shape = tuple(err_mat_shape)
            self.err_mat = np.zeros(err_mat_shape)
            self.runtime_arr = np.zeros(len(self.err_mat.flatten()))

            self.titles += '{:<10} {:<10}'  # make space for error rate and runtime

            self.test_var = test_range_dict
            self.exp_list = list(itertools.product(*grid_value_list))
            self.ind_list = list(itertools.product(*ind_list))
            self.n_exp = len(self.exp_list)
            print(self.n_exp, 'experiments added')

    def run_exp(self, model):
        self.backup_filename = str(int(time.time()))  # back up err rate data after each experiment
        
        print(self.titles.format('Exp#', *self.key_list, 'Err %', 'Runtime'))
        
        for exp_ind in range(self.n_exp):
            p = self.canon_p
            '''get set of parameters'''
            param_tup = self.exp_list[exp_ind]
            to_print = []
            for key_ind in range(len(self.key_list)):
                p[self.key_list[key_ind]] = param_tup[key_ind]
                to_print.append(np.round(param_tup[key_ind], 5))
            
            tic = time.time()
            
            err_mean, output_dict = model.run(p)
            self.output.append(output_dict)

            self.err_mat[self.ind_list[exp_ind]] = err_mean
            self.runtime_arr[exp_ind] = int(time.time() - tic)
            pickle.dump(self.err_mat, open(self.backup_filename, 'wb'))
            print(self.titles.format(exp_ind, *to_print, err_mean.round(3), int(time.time() - tic)))

    def save(self, filename=None):
        if self.note:
            self.note = input('Enter note here (press enter to end):')
        'Remove backup file and save in new file'
        os.remove(self.backup_filename)
        now = datetime.datetime.now()
        time_stamp = str(format(now.month, '02d')) + str(format(now.day, '02d')) +\
         '_' + str(format(now.hour, '02d')) + str(format(now.minute, '02d'))
        self.time = time_stamp
        if filename is None:
            pickle.dump(self, open('batch_' + time_stamp, 'wb'))
        else:
            pickle.dump(self, open(filename, 'wb'))

    def summary(self):
        print("{:<10} {:<10}".format('Parameter','Value'))
        print('--------------------')
        for k, v in self.canon_p.items():
            print("{:<10} {:<10}".format(k, v))
        
        p_temp = self.canon_p
        print('----------')
        print(self.titles.format('Exp#', *self.key_list, 'Err %', 'Runtime'))
        for exp_ind in range(self.n_exp):
            param_tup = self.exp_list[exp_ind]
            to_print = []
            for key_ind in range(len(self.key_list)):
                p_temp[self.key_list[key_ind]] = param_tup[key_ind]
                to_print.append(np.round(param_tup[key_ind], 5))
            print(self.titles.format(exp_ind, *to_print, self.err_mat[self.ind_list[exp_ind]],                          self.runtime_arr[exp_ind]))

    def erase(self):
        if input('Erase experiments? [y/n]') == 'y':
            os.remove(self.backup_filename)
        else:
            print('No action taken.')
