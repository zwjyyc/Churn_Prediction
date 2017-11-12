from sklearn import preprocessing

import os
import sys
import numpy
import datetime

import base_yyc
import util_yyc

print_per_block = 1e5


class FeatureExtractor(object):
    def __init__(self, src = ''):
        self.train_csv = src + 'train.csv'
        self.test_csv = src + 'sample_submission_zero.csv'
        self.transactions_csv = src + 'transactions.csv'
        self.user_logs_csv = src + 'user_logs.csv'
        self.members_csv = src + 'members.csv'
        #
        src_ = '/home/yyc/Code/WSDM_ChurnPrediction/data/'#'/data2/kkbox/Churn_Prediction/src/yyc/data/'
        self.train_old_instances = src_ + 'instances.train.dump'
        self.train_instances = src_ + 'instances.train.dump.v2'
        self.test_instances = src_ + 'instances.test.dump.v2'

        self.users_train = {}
        self.users_test = {}
        self.is_loaded = os.path.exists(self.train_instances) and os.path.exists(self.test_instances) and os.path.exists(self.train_old_instances)
        print self.is_loaded
        self.feature_templates = {}

        if not self.is_loaded:
            assert os.path.exists(self.train_csv), 'train.csv does not exist'
            assert os.path.exists(self.test_csv), 'sample_submission_zero.csv does not exist'
            assert os.path.exists(self.transactions_csv), 'transactions.csv does not exist'
            assert os.path.exists(self.user_logs_csv), 'user_logs.csv does not exist'
            assert os.path.exists(self.members_csv), 'members.csv does not exist'
            self.load_raw_data()

    def extract(self):
        src_ = '/home/yyc/Code/WSDM_ChurnPrediction/data/'
        config_file = src_ + 'configure.in'
        assert os.path.exists(config_file), 'configure.in does not exist'
        util_yyc.load_configure(config_file, self.feature_templates)

        features_old_train_file = src_ + 'dist.old.train.'
        features_train_file = src_ + 'dist.train.'
        features_test_file = src_ + 'dist.test.'
        
        self.build_features(self.train_old_instances, features_old_train_file, is_train=True, is_old=True)
        self.build_features(self.train_instances, features_train_file, is_train=True)
        self.build_features(self.test_instances,  features_test_file)

    def build_features(self, src, outfile, old_features=None, is_train=False, is_old=False):
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

                if 'RegisteredVia' in self.feature_templates and member_info:
                    registered_via = member_info.registered_via
                    self.feature_templates['RegisteredVia'].add_value(registered_via, label)

        print '%d/%d missing!' % (wcnt, cnt)
        for name, feature_template in self.feature_templates.items():
            if len(feature_template.value_dist) == 0:
                continue
            file_name = outfile + name
            util_yyc.dict_dict_2_file(feature_template.value_dist, feature_template.label_dist, file_name)

        current_time_point = datetime.date(2017, 5, 1)
        start_time_point = datetime.date(2016, 1, 1)
        if is_train:
            current_time_point -= datetime.timedelta(30)
            start_time_point -= datetime.timedelta(30)
            if is_old:
                current_time_point -= datetime.timedelta(30)
                start_time_point -= datetime.timedelta(30)

        print_feature_info = True
        feature_ind = {}
        ind = 0

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
                
                if old_features and user_id in old_features:
                    features[user_id] = old_features[user_id]
                    continue
                
                if user_id not in features:
                    features[user_id] = [label]

                transactions = util_yyc.strings_2_transactions(user_instance.transactions, user_instance.user_id)
                log_end_time = None
                if 'Trans' in self.feature_templates:
                    feature, log_end_time = self.feature_templates['Trans'].transactions_2_features(transactions, is_train, is_old)
                    features[user_id].extend(feature)
                    if print_feature_info:
                        print 'Trans'
                        print feature
                        feature_ind['Trans'] = [ind, ind + len(feature)]
                        ind += len(feature)

                if 'HasMemInfo' in self.feature_templates:
                    feature = [1] if member_info else [0]
                    features[user_id].extend(feature)
                    if print_feature_info:
                        print 'HasMemInfo'
                        print feature
                        feature_ind['HasMemInfo'] = [ind, ind + len(feature)]
                        ind += len(feature)

                if 'Age' in self.feature_templates:
                    value = member_info.age if member_info else None
                    feature = self.feature_templates['Age'].value_2_feature(value)
                    features[user_id].extend(feature)
                    if print_feature_info:
                        print 'Age'
                        print feature
                        feature_ind['Age'] = [ind, ind + len(feature)]                      
                        ind += len(feature)

                if 'RegistrationInitTime' in self.feature_templates:
                    feature = [(member_info.registration_init_time - start_time_point).days / 30.0] if member_info else [0]
                    features[user_id].extend(feature)
                    if print_feature_info:
                        print 'RegistrationInitTime'
                        print feature
                        feature_ind['RegistrationInitTime'] = [ind, ind + len(feature)]
                        ind += len(feature)

                if 'City' in self.feature_templates:
                    value = member_info.city if member_info else None
                    feature = self.feature_templates['City'].value_2_id(value)
                    features[user_id].extend(feature)
                    if print_feature_info:
                        print 'City'
                        print feature               
                        feature_ind['City'] = [ind, ind + len(feature)]
                        ind += len(feature)     

                if 'Gender' in self.feature_templates:
                    value = member_info.gender if member_info else None
                    feature = self.feature_templates['Gender'].value_2_id(value)
                    features[user_id].extend(feature)
                    if print_feature_info:
                        print 'Gender'
                        print feature
                        feature_ind['Gender'] = [ind, ind + len(feature)]
                        ind += len(feature)               

                if 'RegisteredVia' in self.feature_templates:
                    value = member_info.registered_via if member_info else None
                    feature = self.feature_templates['RegisteredVia'].value_2_id(value)
                    features[user_id].extend(feature)
                    if print_feature_info:
                        print 'RegisteredVia'
                        print feature       
                        feature_ind['RegisteredVia'] = [ind, ind + len(feature)]
                        ind += len(feature)             

                logs = util_yyc.strings_2_logs(user_instance.logs, user_instance.user_id)
                if 'HasLogInfo' in self.feature_templates:
                    feature = [1] if logs else [0]
                    features[user_id].extend(feature)
                    if print_feature_info:
                        print 'HasLogInfo'
                        print feature
                        feature_ind['HasLogInfo'] = [ind, ind + len(feature)]
                        ind += len(feature)

                if 'Logs' in self.feature_templates:
                    feature = self.feature_templates['Logs'].logs_2_features(logs, log_end_time)
                    features[user_id].extend(feature)
                    if print_feature_info:
                        print 'Logs'
                        print feature
                        feature_ind['Logs'] = [ind, ind + len(feature)]
                        ind += len(feature)
                print_feature_info = False                

        labels = [v[0] for k, v in features.iteritems()]
        ids = [k for k, v in features.iteritems()]
        scaled_features = numpy.array([v[1:] for k, v in features.iteritems()])
        #scaled_features = preprocessing.scale(scaled_features)

        print 'Begin to write features to file'
        file_name = outfile + 'rawfeatures'
        util_yyc.features_2_file(labels, scaled_features, file_name)

        file_name = outfile + 'ids'
        util_yyc.ids_2_file(ids, file_name)
        
        file_name = outfile + 'featureind'
        util_yyc.save_feature_ind(feature_ind, file_name)
        return features

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




