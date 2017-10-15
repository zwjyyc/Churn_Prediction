import xgboost as xgb
import os

import util_yyc

class ChurnLearner(object):
    def __init__(self, src, configure = ''):
        data1_src = src + 'dist.train.rawfeatures'
        data2_src = src + 'dist.test.rawfeatures'
        data2_src_ids = src + 'dist.test.ids'

        assert os.path.exists(data1_src)
        assert os.path.exists(data2_src)
        assert os.path.exists(data2_src_ids)

        self.data1 = xgb.DMatrix(data1_src)
        self.date2 = xgb.DMatrix(data2_src)
        self.data2_ids = util_yyc.load_ids(data2_src_ids)

        self.result_file = src + 'results'

        self.k_fold = 5
        self.models = {'xgboost': {'max_depth': 2, 'eta': 1, 'silent': 1, 'objective': 'binary:logistic',
                                   'eval_metric': 'logloss'}}
        self.ensemble = 'Average'

        self.load_configure()

    def load_configure(self):
        return

    def learn(self):
        if 'xgboost' in self.models:
            params = self.models['xgboost']
            num_round = 10
            xgb.cv(params, self.data1, num_round, nfold=5, seed=0)

            bst = xgb.train(params, self.data1, num_round)
            preds = bst.predict(self.data2)
            assert len(preds) == len(self.ids)
            util_yyc.generate_results(preds, self.ids, self.result_file)


    def predict(self):
        return

    def create_train_dev(self):
        return


