import datetime
import math

class UserInstance(object):
    def __init__(self, user_id, is_churn):
        self.user_id = user_id  # string
        self.is_churn = is_churn  # 0, 1
        self.member_info = ''
        self.logs = []
        self.transactions = []

    def add_member_info(self, member_info):
        self.member_info = member_info

    def add_logs(self, log_info):
        self.logs.append(log_info)

    def add_transactions(self, transaction_info):
        self.transactions.append(transaction_info)


class TranInstance(object):
    def __init__(self, user_id, payment_method_id, payment_plan_days, plan_list_price, actual_amount_paid,
                 is_auto_renew, transaction_date, membership_expire_date, is_cancel):
        self.user_id = user_id
        self.payment_method_id = payment_method_id
        self.payment_plan_days = payment_plan_days
        self.plan_list_price = plan_list_price
        self.actual_amount_paid = actual_amount_paid
        self.is_auto_renew = is_auto_renew
        self.transaction_date = transaction_date
        self.membership_expire_date = membership_expire_date
        self.is_cancel = is_cancel
        self.is_ok = True

        #error_days = payment_plan_days - (membership_expire_date - transaction_date).days
        #if error_days >= 10 or error_days <= -10:  # remove illegal transaction
        #    self.is_ok = False
            #wrong_str = 'found wrong transaction entry: %d %s %s' % (payment_plan_days, membership_expire_date.strftime("%Y-%m-%d"), transaction_date.strftime("%Y-%m-%d"))
            #print wrong_str


class LogInstance(object):
    def __init__(self, user_id, date, num_25, num_50, num_75, num_985, num_100, num_unq, total_secs):
        self.user_id = user_id
        self.date = date
        self.num_25 = num_25
        self.num_50 = num_50
        self.num_75 = num_75
        self.num_985 = num_985
        self.num_100 = num_100
        self.num_unq = num_unq
        self.total_secs = total_secs


class MemberInstance(object):
    def __init__(self, user_id, city, age, gender, registered_via, registration_init_time, expiration_date):
        self.user_id = user_id
        self.city = city
        self.age = age
        self.gender = gender
        self.registered_via = registered_via
        self.registration_init_time = registration_init_time
        self.expiration_date = expiration_date
        self.registered_days = (expiration_date - registration_init_time).days


class FeatureType:
    Categorical = 'Categorical'
    Numerical = 'Numerical'


class FeatureTemplate(object):
    def __init__(self, name, input_type, output_type,
                 boundary=[],
                 time_boundary=[],
                 internal=[],
                 time_internal=[]):
        self.name = name
        self.input_type = input_type
        self.output_type = output_type

        self.boundary = boundary
        self.boundary_given = len(boundary) > 0

        self.time_boundary = time_boundary
        self.boundary_given = len(time_boundary) > 0
        if not self.boundary_given:
            self.time_boundary = [datetime.date(2018, 1, 1), datetime.date(1990, 1, 1)]

        self.internal = internal
        self.time_internal = time_internal

        self.id_map = {}
        self.value_dist = {}  # value_dist and label_dist could be merged.
        self.label_dist = {}
        self.dim = -1
        self.method_map = {'24': 12, '25': 23, '26': 21, '27': 15, '20': 24, '21': 3, '22': 20, '23': 9, '28': 19, '29': 18, '40': 5, '41': 1, '1': 40, '3': 37, '2': 38, '5': 26, '4': 39, '7': 29, '6': 36, '8': 35, '13': 30, '12': 31, '11': 28, '10': 33, '39': 2, '38': 10, '15': 34, '14': 13, '17': 25, '16': 32, '33': 7, '32': 22, '31': 8, '30': 17, '37': 4, '36': 14, '35': 16, '34': 6, '19': 11, '18': 27}
        self.renew_map = {1: 1, 0: 2}

    def add_value(self, value, label):
        if value not in self.value_dist:
            self.value_dist[value] = 0
            self.label_dist[value] = {}
            if self.input_type == FeatureType.Categorical:
                id_size = len(self.id_map) + 1
                self.id_map[value] = id_size

        self.value_dist[value] += 1
        if label not in self.label_dist[value]:
            self.label_dist[value][label] = 0

        self.label_dist[value][label] += 1

    def value_2_id(self, value):
        feature = [0]
        if self.output_type == FeatureType.Categorical:
            feature = [0] * (len(self.id_map) + 1)

        if not value:
            return feature
        elif self.output_type == FeatureType.Numerical:
            feature = [self.id_map.get(value, 0)]
        else:
            feature[self.id_map.get(value, 0)] = 1
        return feature

    def transactions_2_features(self, transactions, is_train):
        time_point_start = self.time_boundary[0]
        time_point_end = self.time_boundary[1]
        time_point_start = datetime.date(2016, 3, 1)
        time_point_end = datetime.date(2017, 3, 1)

        days_gap = (time_point_end - time_point_start).days
        if is_train:
            time_point_start = datetime.date(2016, 2, 1)
            time_point_end = datetime.date(2017, 2, 1)

        if self.dim < 0:
            cnt = 17
            for num in self.time_internal:
                cnt += num
            cnt += 2 * (len(self.method_map) + 1)
            self.dim = cnt

        feature = [0] * self.dim
        ind = 0
        num_trans = 0
        for transaction in transactions:
            date = transaction.transaction_date
            is_ok = transaction.is_ok
            if (date - time_point_start).days <= 0 or \
                                (date - time_point_end).days >= 0 or not is_ok:
                    continue
            is_cancel = transaction.is_cancel
            if is_cancel == 1:
                continue

            num_trans += 1

        feature[ind] = num_trans
        renew_dist = {}
        last_date = datetime.date(1900, 1, 1)
        last_instance = None
        
        plan_list_price_ind = 0
        actual_amount_pay_ind = 0
        payment_plan_days_ind = 0
        for transaction in transactions:
            date = transaction.transaction_date
            is_ok = transaction.is_ok
            if (date - time_point_start).days <= 0 or \
                                (date - time_point_end).days >= 0 or not is_ok:
                    continue

            if (date - last_date).days > 0:
                last_date = date
                last_instance = transaction

            ind = 1
            is_cancel = transaction.is_cancel
            feature[ind] += is_cancel / (num_trans + 1e-6)
            ind += 1
            
            payment_plan_days = transaction.payment_plan_days
            if is_cancel == 0:
                feature[ind] += payment_plan_days * 1.0
            if payment_plan_days_ind == 0:
                payment_plan_days_ind = ind
            ind += 1

            transaction_date = transaction.transaction_date
            membership_expire_date = transaction.membership_expire_date
            error_days = payment_plan_days - (membership_expire_date - transaction_date).days
            if error_days >= 5 or error_days <= -5:
                feature[ind] += 1
            ind += 1            

            plan_list_price = transaction.plan_list_price
            if is_cancel == 0:
                feature[ind] += plan_list_price * 1.0
            if plan_list_price_ind == 0:
                plan_list_price_ind = ind
            ind += 1

            actual_amount_paid = transaction.actual_amount_paid
            if is_cancel == 0:
                feature[ind] += actual_amount_paid * 1.0
            if actual_amount_pay_ind == 0:
                actual_amount_pay_ind = ind 
            ind += 1

            for num in self.time_internal:
                ind_ = (date - time_point_start).days * num / (days_gap + 1)
                feature[ind + ind_] += 1.0 * payment_plan_days
                ind += num

            payment_method_id = transaction.payment_method_id
            ind_ = self.method_map.get(payment_method_id, 0)
            if is_cancel == 0:
                feature[ind + ind_] += 1.0 / (num_trans + 1e-6)
            ind += len(self.method_map) + 1

            is_auto_renew = transaction.is_auto_renew
            if is_auto_renew and is_cancel == 0:
                feature[ind] += 1.0 / (num_trans + 1e-6)
            ind_ = self.renew_map.get(is_auto_renew, 0)
            if ind_ not in renew_dist:
                renew_dist[ind_] = 0
            renew_dist[ind_] += 1
            ind += 1

        # features of last instance
        if not last_instance:
            return feature, None       

        payment_plan_days = last_instance.payment_plan_days
        feature[ind] = payment_plan_days
        ind += 1

        plan_list_price = last_instance.plan_list_price
        feature[ind] = plan_list_price
        ind += 1

        actual_amount_paid = last_instance.actual_amount_paid
        feature[ind] = actual_amount_paid
        ind += 1
        
        discount_ratio = 1 - (actual_amount_paid + 1e-6) / (plan_list_price + 1e-6)
        feature[ind] = discount_ratio
        ind += 1
        
        payment_method_id = last_instance.payment_method_id
        ind_ = self.method_map.get(payment_method_id, 0)
        feature[ind + ind_] = 1
        ind += len(self.method_map) + 1

        is_auto_renew = last_instance.is_auto_renew
        feature[ind] = is_auto_renew
        ind += 1
        #ind_ = self.renew_map.get(is_auto_renew, 0)
        #feature[ind + ind_] = 1
        #ind += len(self.renew_map) + 1
        
        #transaction_date = (time_point_end - last_instance.transaction_date).days / 30.0
        #feature[ind] = transaction_date
        #ind += 1
        
        is_cancel = last_instance.is_cancel
        feature[ind] = is_cancel
        ind += 1
        
        discount_ratio = 1 - (feature[actual_amount_pay_ind] + 1e-6) / (feature[plan_list_price_ind] + 1e-6)
        feature[ind] = discount_ratio
        ind += 1

        pay_per_day = feature[actual_amount_pay_ind] / (feature[payment_plan_days_ind] + 1e-6)
        feature[ind] = pay_per_day
        ind += 1

        plan_days_per_tran = feature[payment_plan_days_ind] / (num_trans + 1e-4)
        feature[ind] = plan_days_per_tran
        ind += 1

        sorted_list = sorted(renew_dist.items(), key=lambda (k, v): (v, k), reverse=True)
        feature[ind] = sorted_list[0][0]
        ind += 1
        return feature, last_instance.membership_expire_date

    def logs_2_features(self, logs, time_point_end, is_train):
        if self.dim < 0:
            cnt = 1
            for num in self.time_internal:
                cnt += num * 3
            self.dim = cnt

        feature = [0] * self.dim
        if not logs or not time_point_end:
            return feature

        last_date = datetime.date(2016, 1, 1)
        time_point_start = time_point_end - datetime.timedelta(30)
        days_gap = 30
        num_logs = 0
        
        for log in logs:
            date = log.date
            if (date - time_point_start).days < 0 or \
                            (date - time_point_end).days > 0:
                continue

            num_logs += 1
            if (date - last_date).days > 0:
                last_date = date

        ind = 0
        day_delta = (time_point_end - datetime.date(2017, 2, 28)).days
        feature[ind] = num_logs if day_delta <= 0 else math.sqrt(30.0 / day_delta) * num_logs
        
        ind += 1
        #feature[ind] = (last_date - time_point_start).days
        #ind += 1
        for num in self.time_internal:
            for log in logs:
                date = log.date
                if (date - time_point_start).days < 0 or \
                                (date - time_point_end).days > 0:
                    continue
                ind_ = (date - time_point_start).days * num / (days_gap + 1)
                
                ind = 1
                #value = log.num_25 if log.num_25 <= 100 else 100
                #feature[ind + ind_] += value * 1.0 / num_logs
                #ind += num

                value = log.num_100 if log.num_100 <= 1000 else 1000
                feature[ind + ind_] += value * 1.0 / num_logs
                ind += num

                value = log.num_unq if log.num_unq <= 1000 else 1000
                feature[ind + ind_] += value * 1.0 / num_logs
                ind += num
                
                value = log.total_secs if log.total_secs <= 24 * 60 * 60 else 24 * 60 * 60
                feature[ind + ind_] += value * 1.0 / (num_logs * 60)
                ind += num

                #feature[ind + ind_] += 1.0
                #ind += num
        return feature
    
    def value_2_feature(self, value):
        if self.output_type == FeatureType.Numerical:
            if self.dim < 0:
                self.dim = 1
            feature = [0] * self.dim
            if not value:
                return feature
              
            feature[0] = value
            if value > self.boundary[1]:
                feature[0] = self.boundary[1] + 1

            if value < self.boundary[0]:
                feature[0] = self.boundary[0] - 1
            return feature
        elif self.output_type == FeatureType.Categorical:
            if self.dim < 0:
                if self.input_type == FeatureType.Categorical:
                    self.dim = len(self.id_map) + 1
                else:
                    self.dim = self.internal + 2
            
            feature = [0] * self.dim
            if not value:
                return feature
            
            if self.input_type == FeatureType.Numerical:
                if value < self.boundary[0]:
                    feature[0] = 1
                elif value > self.boundary[1]:
                    feature[self.dim - 1] = 1
                else:
                    ind = (value - self.boundary[0]) * self.internal / (self.boundary[1] - self.boundary[0] + 1e-8)
                    feature[int(ind)] = 1
            elif self.input_type == FeatureType.Categorical:
                feature[self.id_map.get(value, 0)] = 1
            return feature
