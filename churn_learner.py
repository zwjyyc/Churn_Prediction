import xgboost as xgb
import numpy as np
import os

from sklearn.model_selection import train_test_split
import util_yyc
import gc; gc.enable()

class ChurnLearner(object):
    def __init__(self, src, configure = ''):
        self.data1_src = src + 'dist.train.features'
        self.data2_src = src + 'dist.test.features'
        #data3_src = src + 'dist.valid.features'
        data2_src_ids = src + 'dist.test.ids'

        assert os.path.exists(self.data1_src)
        assert os.path.exists(self.data2_src)
        assert os.path.exists(data2_src_ids)

        #self.data1 = xgb.DMatrix(data1_src)
        #self.data2 = xgb.DMatrix(data2_src)
        #self.data3 = xgb.DMatrix(data3_src)
        self.data2_ids = util_yyc.load_ids(data2_src_ids)

        self.result_file = src + 'results1'

        self.k_fold = 5
        self.models = {'xgboost': {'max_depth': 7, 'eta': 0.02, 'silent': 1, 'objective': 'binary:logistic',
                                   'eval_metric': 'logloss'}}
        self.ensemble = 'Average'

        self.load_configure()

    def load_configure(self):
        return

    def learn(self):
        if 'xgboost' in self.models:
            params = self.models['xgboost']
            print 'train begins'
            train_x, train_y = util_yyc.svminput_2_list(self.data1_src)
            train_x = np.array(train_x)
            train_y = np.array(train_y)
            
            test_x, test_y = util_yyc.svminput_2_list(self.data2_src)
            test_x = np.array(test_x)
            test_y = np.array(test_y)

            x1, x2, y1, y2 = train_test_split(train_x, train_y, test_size=0.3, random_state=0)
            watchlist = [(xgb.DMatrix(x1, y1), 'train'), (xgb.DMatrix(x2, y2), 'valid')]
            model = xgb.train(params, xgb.DMatrix(x1, y1), 150,  watchlist,  maximize=False, verbose_eval=5, early_stopping_rounds=50) #use 1500
            print 'done'
            print 'predict begins'
            preds = model.predict(xgb.DMatrix(test_x), ntree_limit=model.best_ntree_limit)
            print 'done'
            assert len(preds) == len(self.data2_ids)
            util_yyc.generate_results(preds, self.data2_ids, self.result_file)


    def predict(self):
        return

    def create_train_dev(self):
        return


