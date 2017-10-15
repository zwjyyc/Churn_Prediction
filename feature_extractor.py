from sklearn import preprocessing

import os
import sys
import numpy
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

        self.feature_templates = {}

    def extract(self):
        src_ = '/home/yyc/Code/WSDM_ChurnPrediction/data/'
        config_file = src_ + 'configure.in'
        assert os.path.exists(config_file), 'configure.in does not exist'
        util_yyc.load_configure(config_file, self.feature_templates)

        features_train_file = src_ + 'dist.train.'
        features_test_file = src_ + 'dist.test.'
        data1 = self.build_features(self.train_instances, features_train_file)
        data2 = self.build_features(self.test_instances,  features_test_file)
        return data1, data2

    def build_features(self, src, outfile):
        # fill feature_templates
        features = {}
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

                if 'Age' in self.feature_templates and member_info:
                    age = member_info.age
                    self.feature_templates['Age'].add_value(age, label)

                if 'City' in self.feature_templates and member_info:
                    city = member_info.city
                    self.feature_templates['City'].add_value(city, label)

                if 'Gender' in self.feature_templates and member_info:
                    gender = member_info.gender
                    self.feature_templates['Gender'].add_value(gender, label)

                if 'RegisteredDays' in self.feature_templates and member_info:
                    registered_days = member_info.registered_days
                    self.feature_templates['RegisteredDays'].add_value(registered_days, label)

                if 'RegisteredVia' in self.feature_templates and member_info:
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
        
        feature_test = False
        # build numerical features
        with open(src, 'r') as fin:
            cnt = 0
            for line in fin:
                cnt += 1
                if cnt % print_per_block == 0:
                    sys.stdout.write('%d\r' % cnt)
                    sys.stdout.flush()
                
                if not line:
                    continue
                user_instance = util_yyc.string_2_instance(line.strip('\n'))
                if not user_instance:
                    continue

                user_id = user_instance.user_id
                label = user_instance.is_churn
                member_info = util_yyc.string_2_member(user_instance.member_info, user_instance.user_id)

                if user_id not in features:
                    features[user_id] = [label]

                if 'Age' in self.feature_templates:
                    value = None
                    if member_info:
                        value = member_info.age
                    feature = self.feature_templates['Age'].value_2_feature(value)
                    features[user_id].extend(feature)
                    if feature_test:
                        print 'Age'
                        print feature                 

                if 'RegisteredDays' in self.feature_templates:
                    value = None
                    if member_info:
                        value = member_info.registered_days
                    feature = self.feature_templates['RegisteredDays'].value_2_feature(value)
                    features[user_id].extend(feature)
                    if feature_test:
                        print 'RegisteredDays'
                        print feature                    

                if 'City' in self.feature_templates:
                    value = None
                    if member_info:
                        value = member_info.city
                    feature = self.feature_templates['City'].value_2_feature(value)
                    features[user_id].extend(feature)
                    if feature_test:
                        print 'City'
                        print feature                    

                if 'Gender' in self.feature_templates:
                    value = None
                    if member_info:
                        value = member_info.gender
                    feature = self.feature_templates['Gender'].value_2_feature(value)
                    features[user_id].extend(feature)
                    if feature_test:
                        print 'Gender'
                        print feature                    

                if 'RegisteredVia' in self.feature_templates:
                    value = None
                    if member_info:
                        value = member_info.registered_via
                    feature = self.feature_templates['RegisteredVia'].value_2_feature(value)
                    features[user_id].extend(feature)
                    if feature_test:
                        print 'RegisteredVia'
                        print feature                    

                transactions = util_yyc.strings_2_transactions(user_instance.transactions, user_instance.user_id)
                if 'NumTrans' in self.feature_templates:
                    value = len(transactions)
                    feature = self.feature_templates['NumTrans'].value_2_feature(value)
                    features[user_id].extend(feature)
                    if feature_test:
                        print 'NumTrans'
                        print feature                    

                logs = util_yyc.strings_2_logs(user_instance.logs, user_instance.user_id)

                if 'NumLogs' in self.feature_templates:
                    value = len(logs)
                    feature = self.feature_templates['NumLogs'].value_2_feature(value)
                    features[user_id].extend(feature)
                    if feature_test:
                        print 'NumLogs'
                        print feature

                if 'Num25' in self.feature_templates:
                    values = []
                    dates = []
                    if logs:
                        values = [log.num_25 for log in logs]
                        dates = [log.date for log in logs]
                    feature = self.feature_templates['Num25'].value_2_features(values, dates)
                    features[user_id].extend(feature)
                    if feature_test:
                        print 'Num25'
                        print feature                       

                if 'Num50' in self.feature_templates:
                    values = []
                    dates = []
                    if logs:
                        values = [log.num_50 for log in logs]
                        dates = [log.date for log in logs]
                    feature = self.feature_templates['Num50'].value_2_features(values, dates)
                    features[user_id].extend(feature)
                    if feature_test:
                        print 'Num50'
                        print feature

                if 'Num75' in self.feature_templates:
                    values = []
                    dates = []
                    if logs:
                        values = [log.num_75 for log in logs]
                        dates = [log.date for log in logs]
                    feature = self.feature_templates['Num75'].value_2_features(values, dates)
                    features[user_id].extend(feature)
                    if feature_test:
                        print 'Num75'
                        print feature

                if 'Num985' in self.feature_templates:
                    values = []
                    dates = []
                    if logs:
                        values = [log.num_985 for log in logs]
                        dates = [log.date for log in logs]
                    feature = self.feature_templates['Num985'].value_2_features(values, dates)
                    features[user_id].extend(feature)
                    if feature_test:
                        print 'Num985'
                        print feature

                if 'Num100' in self.feature_templates:
                    values = []
                    dates = []
                    if logs:
                        values = [log.num_100 for log in logs]
                        dates = [log.date for log in logs]
                    feature = self.feature_templates['Num100'].value_2_features(values, dates)
                    features[user_id].extend(feature)
                    if feature_test:
                        print 'Num100'
                        print feature

                if 'NumUnq' in self.feature_templates:
                    values = []
                    dates = []
                    if logs:
                        values = [log.num_unq for log in logs]
                        dates = [log.date for log in logs]
                    feature = self.feature_templates['NumUnq'].value_2_features(values, dates)
                    features[user_id].extend(feature)
                    if feature_test:
                        print 'NumUnq'
                        print feature

                if 'TotalSecs' in self.feature_templates:
                    values = []
                    dates = []
                    if logs:
                        values = [log.total_secs for log in logs]
                        dates = [log.date for log in logs]
                    feature = self.feature_templates['TotalSecs'].value_2_features(values, dates)
                    features[user_id].extend(feature)
                    if feature_test:
                        print 'TotalSecs'
                        print feature

                feature_test = False                

        labels = [v[0] for k, v in features.iteritems()]
        ids = [k for k, v in features.iteritems()]
        scaled_features = numpy.array([v[1:] for k, v in features.iteritems()])
        #scaled_features = preprocessing.scale(scaled_features)
        print 'Begin to write features to file'
        file_name = outfile + 'rawfeatures'
        util_yyc.features_2_file(labels, scaled_features, file_name)
        file_name = outfile + 'ids'
        util_yyc.ids_2_file(ids, file_name)
        return labels, scaled_features

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




