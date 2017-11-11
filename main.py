import sys
import feature_extractor
import feature_selector
import churn_learner

extractor = feature_extractor.FeatureExtractor()
extractor.extract()

src_ = '/home/yyc/Code/WSDM_ChurnPrediction/data/'

use_all = True
print 'Begin to select features'
selector = feature_selector.FeatureSelector(src_, use_all)
selector.select()
print 'Done'

print 'Begin to train learner'
learner = churn_learner.ChurnLearner(src_)
learner.learn()
print 'Done'
