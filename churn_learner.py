import xgboost

class ChurnLearner(object):
    def __init__(self, data1, date2, configure):
        self.data1 = data1
        self.date2 = date2

        self.k_fold = 5
        self.models = {}
        self.ensemble = 'Average'

        self.load_configure()

    def load_configure(self):
        return

    def learn(self):
        train, dev = None, None

        if 'xgboost' in self.models:
            params = self.models['xgboost']




    def predict(self):
        return

    def create_train_dev(self):
        return


