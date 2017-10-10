import os
import sys
import datetime

import base_yyc
import util_yyc

print_per_block = 1e5


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

        self.train_feature_dist = src_ + 'dist.train.'
        self.test_feature_dist = src_ + 'dist.test.'
        self.build_features(self.train_instances, self.users_train, self.train_feature_dist)
        self.build_features(self.test_instances, self.users_test, self.test_feature_dist)

    def build_features(self, src, features, outfile):
        # fill feature_templates
        with open(src, 'r') as fin:
            cnt = 0
            wcnt = 0
            for line in fin:
                cnt += 1
                if cnt % print_per_block == 0:
                    sys.stdout.write('%d\r' % cnt)
                    sys.stdout.flush()

                if not line:
                    continue
                user_instance = util_yyc.string_2_instance(line.strip('\n'))
                if not user_instance:
                    wcnt += 1
                    continue

                member_info = user_instance.member_info
                label = user_instance.is_churn
                member_info = util_yyc.string_2_member(member_info, user_instance.user_id)

                if 'Age' in self.feature_templates:
                    age = member_info.age
                    self.feature_templates['Age'].add_value(age, label)

                if 'City' in self.feature_templates:
                    city = member_info.city
                    self.feature_templates['City'].add_value(city, label)

                if 'Gender' in self.feature_templates:
                    gender = member_info.gender
                    self.feature_templates['Gender'].add_value(gender, label)

                if 'RegisteredDays' in self.feature_templates:
                    registered_days = member_info.registered_days
                    self.feature_templates['RegisteredDays'].add_value(registered_days, label)

                if 'RegisteredVia' in self.feature_templates:
                    registered_via = member_info.registered_via
                    self.feature_templates['RegisteredVia'].add_value(registered_via, label)

                logs = user_instance.logs
                if 'NumLogs' in self.feature_templates and logs:
                    self.feature_templates['NumLogs'].add_value(len(logs), label)

                transactions = user_instance.transactions
                if 'NumTrans' in self.feature_templates and transactions:
                    self.feature_templates['NumTrans'].add_value(len(transactions), label)


        print '%d/%d missing!' % (wcnt, cnt)
        for name, feature_template in self.feature_templates.items():
            if len(feature_template.value_dist) == 0:
                continue
            file_name = outfile + name
            util_yyc.dict_dict_2_file(feature_template.value_dist, feature_template.label_dist, file_name)
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
feature_extractor = FeatureExtractor(src_dir)

