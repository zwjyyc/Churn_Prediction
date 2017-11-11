import xgboost as xgb
import lightgbm as lgb
import numpy as np
import os

import sys
sys.path.append('/home/yyc/Code/WSDM_ChurnPrediction/src/liblinear/python')
sys.path.append('/home/yyc/Code/WSDM_ChurnPrediction/src/libsvm/python')

#from svmutil import *
import liblinearutil
import svmutil
#from liblinearutil import *
#import liblinearutil

from sklearn.model_selection import train_test_split

import util_yyc
import gc; gc.enable()

class ChurnLearner(object):
    def __init__(self, src, configure = ''):
        self.data0_src = src + 'dist.old.train.features'
        self.data1_src = src + 'dist.train.features'
        self.data2_src = src + 'dist.test.features'
        data2_src_ids = src + 'dist.test.ids'

        assert os.path.exists(self.data1_src)
        assert os.path.exists(self.data2_src)
        assert os.path.exists(data2_src_ids)

        self.data2_ids = util_yyc.load_ids(data2_src_ids)

        self.result_file = src + 'results0'

        self.k_fold = 5
        self.models = {'xgboost': {'max_depth': 7, 'eta': 0.02, 'silent': 1, 'objective': 'binary:logistic',
                                   'eval_metric': 'logloss'}, 'libsvm': {'train': '-t 0 -c 4 -b 1 ', 'pred': '-b 1'},
                                   'liblinear': {'train': '-s 0 -c 8 -B 1', 'pred': '-b 1'},
                                    #'lgb': {'max_depth': 6, 'metric': 'binary_logloss', 'num_threads': 4}}
                                    'lgb': {'learning_rate': 0.1, 'num_leaves': 200, 'num_trees': 200, 'num_threads': 4, \
                                    'min_data_in_leaf': 0, 'min_sum_hessian_in_leaf': 100, 'metric': 'binary_logloss'}}
        self.ensemble = 'Average'

        self.load_configure()

    def load_configure(self):
        return

    def learn(self):
        if 'xgboost' in self.models and True:
            params = self.models['xgboost']
            print 'xgboost train begins'
            old_train_x, old_train_y = util_yyc.svminput_2_list(self.data0_src)
            train_x, train_y = util_yyc.svminput_2_list(self.data1_src)
            train_x.extend(old_train_x)
            train_y.extend(old_train_y)
            train_x = np.array(train_x)
            train_y = np.array(train_y)
            print len(train_x)
            test_x, test_y = util_yyc.svminput_2_list(self.data2_src)
            test_x = np.array(test_x)
            test_y = np.array(test_y)            

            x1, x2, y1, y2 = train_test_split(train_x, train_y, test_size=0.3, random_state=0)
            watchlist = [(xgb.DMatrix(x1, y1), 'train'), (xgb.DMatrix(x2, y2), 'valid')]
            model = xgb.train(params, xgb.DMatrix(x1, y1), 400,  watchlist,  maximize=False, verbose_eval=5,
                              early_stopping_rounds=50) #use 1500
            print 'done'
            print 'xgboost predict begins'
            preds = model.predict(xgb.DMatrix(test_x, test_y), ntree_limit=model.best_ntree_limit)
            print 'done'
            assert len(preds) == len(self.data2_ids)
            
            pred_file = self.result_file + '.xgboost'
            util_yyc.generate_results(preds, self.data2_ids, pred_file)

        if 'lgb' in self.models and False:
            params = self.models['lgb']
            print 'lgb train begins'
            #train_data = lgb.Dataset(self.data1_src)
            train_x, train_y = util_yyc.svminput_2_list(self.data1_src)
            train_x = np.array(train_x)
            train_y = np.array(train_y)
            
            x1, x2, y1, y2 = train_test_split(train_x, train_y, test_size=0.3, random_state=0)
            train_data = lgb.Dataset(x1, y1)
            valid_data = lgb.Dataset(x2, y2)
            watchlist = [train_data, valid_data]
            model = lgb.train(params, train_data, 100, watchlist, early_stopping_rounds=5)
            print 'done'
            
            train_data = valid_data =None
            x1 = x2 = y1 = y2 = None
            print 'lgb predict begins'
            test_x, test_y = util_yyc.svminput_2_list(self.data2_src)
            test_x = np.array(test_x)
            
            preds = model.predict(test_x, num_iteration=model.best_iteration)
            print 'done'
            print preds
            assert len(preds) == len(self.data2_ids)
            
            pred_file = self.result_file + '.lgb'
            util_yyc.generate_results(preds, self.data2_ids, pred_file)

        if 'libsvm' in self.models and False:
            params = self.models['libsvm']
            print 'libsvm train begins'
            train_y, train_x = svmutil.svm_read_problem(self.data1_src)
            #print train_y[:10]
            #print train_x[:10]
            train_params = params['train']
            model = svmutil.svm_train(train_y, train_x, train_params)
            print 'Done'
            
            print 'libsvm predict begins' 
            test_y, test_x = svmutil.svm_read_problem(self.data2_src)
            test_params = params['pred']
            _, _, preds = svmutil.svm_predict(test_y, test_x, model, test_params)
            print 'Done'

            preds = [ pred[0] for pred in preds]
            pred_file = self.result_file + '.libsvm'
            util_yyc.generate_results(preds, self.data2_ids, pred_file)
            return

        if 'liblinear' in self.models and False:
            params = self.models['liblinear']
            print 'liblinear train begins'
            train_y, train_x = liblinearutil.svm_read_problem(self.data1_src)
            train_params = params['train']
            model = liblinearutil.train(train_y, train_x, train_params)
            print 'Done'

            train_x = None
            train_x = None
            print 'liblinear predict begins'
            test_y, test_x = liblinearutil.svm_read_problem(self.data2_src)
            test_params = params['pred']
            _, _, preds = liblinearutil.predict(test_y, test_x, model, test_params)
            print 'Done'

            #print preds
            preds = [ pred[1] for pred in preds]
            pred_file = self.result_file + '.liblinear'
            util_yyc.generate_results(preds, self.data2_ids, pred_file)
            return

    def predict(self):
        return

    def create_train_dev(self):
        return


