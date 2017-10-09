import os
import sys
import datetime

import base_yyc
import util_yyc


class FeatureExtractor(object):
    def __init__(self, src):
        self.train_csv = src + 'train.csv'
        self.test_csv = src + 'sample_submission_zero.csv'
        self.transactions_csv = src + 'transactions.csv'
        self.user_logs_csv = src + 'user_logs.csv'
        self.members_csv = src + 'members.csv'
        #
        src_ = '/home/yyc/Code/WSDM_ChurnPrediction/data/'#'/data2/kkbox/Churn_Prediction/src/yyc/data/'
        self.train_instances = src_ + 'instances.train.dump'
        self.test_instances = src_ + 'instances.test.dump'

        self.users_train = {}
        self.users_test = {}
        self.is_loaded = os.path.exists(self.train_instances) and os.path.exists(self.test_instances)
        print self.is_loaded

        assert os.path.exists(self.train_csv), 'train.csv does not exist'
        assert os.path.exists(self.test_csv), 'sample_submission_zero.csv does not exist'
        assert os.path.exists(self.transactions_csv), 'transactions.csv does not exist'
        assert os.path.exists(self.user_logs_csv), 'user_logs.csv does not exist'
        assert os.path.exists(self.members_csv), 'members.csv does not exist'

        if not self.is_loaded:
            self.load_raw_data()

        self.config_file = src_ + 'configure.in'
        self.users_train = {}
        self.users_test = {}
        self.feature_templates = {}

        assert os.path.exists(self.config_file), 'configure.in does not exist'
        util_yyc.load_configure(self.config_file, self.feature_templates)

        self.build_features(self.train_instances, self.users_train)
        self.build_features(self.test_instances, self.users_test)

    def build_features(self, src, features):
        # fill feature_templates
        with open(src, 'r') as fin:
            for line in fin:
                if not line:
                    continue
                user_instance = util_yyc.string_2_instance(line.strip())
                member_info = user_instance.member_info
                member_info = util_yyc.string_2_member(member_info, user_instance.user_id)

                if 'Age' in self.feature_templates:
                    age = member_info.age
                    self.feature_templates['Age'].add_value(age)
                elif 'City' in self.feature_templates:
                    city = member_info.city
                    self.feature_templates['City'].add_value(city)
                elif 'Gender' in self.feature_templates:
                    gender = member_info.gender
                    self.feature_templates['Gender'].add_value(gender)
                elif 'RegisteredDays' in self.feature_templates:
                    registered_days = member_info.registered_days
                    self.feature_templates['RegisteredDays'].add_value(registered_days)
                elif 'RegisteredVia' in self.feature_templates:
                    registered_via = member_info.registered_via
                    self.feature_templates['RegisteredVia'].add_value(registered_via)



        # build categorical features


        # build numerical features

    def load_raw_data(self):
        progress_print = 'Begin to solve %s' % self.train_csv
        print progress_print
        util_yyc.load_train_test(self.train_csv, self.users_train)
        print '\nDone'
        progress_print = 'Begin to solve %s' % self.test_csv
        print progress_print
        util_yyc.load_train_test(self.test_csv, self.users_test)
        print '\nDone'

        progress_print = 'Begin to solve %s' % self.members_csv
        print progress_print
        util_yyc.load_members(self.members_csv, self.users_train, self.users_test)
        print '\nDone'

        progress_print = 'Begin to solve %s' % self.user_logs_csv
        print progress_print
        util_yyc.load_logs(self.user_logs_csv, self.users_train, self.users_test)
        print '\nDone'

        progress_print = 'Begin to solve %s' % self.transactions_csv
        print progress_print
        util_yyc.load_transactions(self.transactions_csv, self.users_train, self.users_test)
        print '\nDone'

        # save
        progress_print = 'Begin to save %s' % self.train_instances
        print progress_print
        util_yyc.instances_2_file(self.train_instances, self.users_train)
        print '\nDone'

        progress_print = 'Begin to save %s' % self.test_instances
        print progress_print
        util_yyc.instances_2_file(self.test_instances, self.users_test)
        print '\nDone'

    def unit_test(self, user_id):
        if user_id in self.users_train:
            print self.users_train[user_id]
        elif user_id in self.users_test:
            print self.users_test[user_id]
        else:
            print 'Not found!'

src_dir = sys.argv[1]
#user_id = sys.argv[2]
feature_extractor = FeatureExtractor(src_dir)
#feature_extractor.unit_test(user_id)

