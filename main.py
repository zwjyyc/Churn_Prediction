import sys
import feature_extractor
import churn_learner

#src_dir = sys.argv[1]
#extractor = feature_extractor.FeatureExtractor(src_dir)
#data1, data2 = extractor.extract()


src_ = '/home/yyc/Code/WSDM_ChurnPrediction/data/'
learner = churn_learner.ChurnLearner(src_)
learner.learn()