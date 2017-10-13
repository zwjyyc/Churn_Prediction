import sys
import feature_extractor
import churn_learner

src_dir = sys.argv[1]
extractor = feature_extractor.FeatureExtractor(src_dir)
data1, data2 = extractor.extract()

learner = churn_learner.ChurnLearner(data1, data2)
learner.learn()