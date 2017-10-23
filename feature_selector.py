import os
import shutil

import util_yyc

class FeatureSelector(object):
    def __init__(self, src, use_all=True):
        self.src = src
        self.data1_src = src + 'dist.train.rawfeatures'
        self.data2_src = src + 'dist.test.rawfeatures'

        self.train_ratio = 0.2

        self.feature_set = ['Age', 'RegisteredDays', 'City', 'Gender', 'RegisteredVia',\
                            'Trans', 'ExpirationDate', 'TotalSecs', 'NumUnq', 'Num25', 'Num50', 'Num75',\
                            'Num985', 'Num100', 'RegistrationInitTime', 'ExpirationDate']

        feature_ind_src = src + 'dist.train.featureind'
        
        self.use_all = use_all
        assert os.path.exists(self.data1_src)
        assert os.path.exists(self.data2_src)
        assert os.path.exists(feature_ind_src)

        self.feature_ind = util_yyc.load_feature_ind(feature_ind_src)
    
    def select(self):
       
        data1_out = self.src + 'dist.train.features'
        data2_out = self.src + 'dist.test.features' 
        #data3_out = self.src + 'dist.valid.features'
        if self.use_all:
            shutil.copyfile(self.data1_src, data1_out)
            shutil.copyfile(self.data2_src, data2_out)
            #shutil.copyfile(self.data3_src, data3_out)
            return 
        dic = {}
        for k, v in self.feature_ind.iteritems():
            if k in self.feature_set:
                dic[v[0]] = v[1]
        tmp_dic = [(k, dic[k]) for k in sorted(dic)]
        print tmp_dic
        
        with open(data1_out, 'w') as fout, open(self.data1_src, 'r') as fin:
            cnt = 0
            for line in fin:
                cnt += 1
                #if cnt % 5 != 0:
                #    continue
                items = line.strip().split('\t')
                label = items[0]
                if label == '0' and cnt % 3 != 1:
                    continue
                #features = items[1].split()
                #iitems = []
                #for k, v in tmp_dic:
                #    iitems.extend(features[k:v])
                #out_str = label + '\t' + ' '.join(iitems)
                #fout.write(out_str + '\n')
                fout.write(line)

        data2_out = self.src + 'dist.test.features'
        with open(data2_out, 'w') as fout, open(self.data2_src, 'r') as fin:
            for line in fin:
                #items = line.strip().split('\t')
                #label = items[0]
                #features = items[1].split()

                #iitems = []
                #for k, v in tmp_dic:
                #    iitems.extend(features[k:v])
                #out_str = label + '\t' + ' '.join(iitems)
                #fout.write(out_str + '\n')
                fout.write(line)

