import os
import pickle

import base_yyc
import util_yyc


class FeatureExtractor(object):
    def __init__(self, src):
        self.train_csv = src + 'train.csv'
        self.test_csv = src + 'sample_submission_zero.csv'
        self.transactions_csv = src + 'transactions.csv'
        self.user_logs_csv = src + 'users_logs.csv'
        self.members_csv = src + 'members.csv'
        self.train_test_instances = src + 'instances.pickle'

        self.users_train = {}
        self.users_test = {}

        self.is_loaded = os.path.exists(self.train_test_instances)

        assert os.path.exists(self.train_csv), 'train.csv does not exist'
        assert os.path.exists(self.test_csv), 'sample_submission_zero.csv does not exist'
        assert os.path.exists(self.transactions_csv), 'transactions.csv does not exist'
        assert os.path.exists(self.user_logs_csv), 'user_logs.csv does not exist'
        assert os.path.exists(self.members_csv), 'members.csv does not exist'

        if not self.is_loaded:
            self.load_raw_data()
        else:
            progress_print = 'Load pickled file %s' % self.train_test_instances
            print progress_print
            file_in = open(self.train_test_instances, 'rb')
            self.users_train, self.users_test = pickle.load(file_in)
            print 'Done'

    def load_raw_data(self):
        progress_print = 'Begin to solve %s' % self.train_csv
        print progress_print
        util_yyc.load_train_test(self.train_csv, self.users_train)
        print 'Done'
        progress_print = 'Begin to solve %s' % self.test_csv
        print progress_print
        util_yyc.load_train_test(self.test_csv, self.users_test)
        print 'Done'

        progress_print = 'Begin to solve %s' % self.members_csv
        print progress_print
        util_yyc.load_members(self.members_cvs, self.users_train, self.users__test)
        print 'Done'

        progress_print = 'Begin to solve %s' % self.user_logs_csv
        print progress_print
        util_yyc.load_logs(self.user_logs_csv, self.users_train, self.users_test)
        print 'Done'

        progress_print = 'Begin to solve %s' % self.transactions_csv
        print progress_print
        util_yyc.load_transactions(self.transactions_csv, self.users_train, self.users_test)
        print 'Done'

        # save
        progress_print = 'Begin to save %s' % self.train_test_instances
        print progress_print
        file_out = file(self.train_test_instances, 'wb')
        pickle.dump((self.users_train, self.users_test), file_out)
        print 'Done'

