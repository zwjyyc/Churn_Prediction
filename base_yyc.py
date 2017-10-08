import datetime


class UserInstance(object):
    def __init__(self, user_id, is_churn):
        self.user_id = user_id  # string
        self.is_churn = is_churn  # 0, 1
        self.member_info = None
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
                 boundary=[float('inf'), -float('inf')],
                 time_boundary=[datetime.date(2900, 1, 1), datetime.date(1900, 1, 1)],
                 internal=[]):
        self.name = name
        self.input_type = input_type
        self.output_type = output_type
        self.boundary = boundary
        self.time_boundary = time_boundary
        self.internal = internal

        self.id_map = {}
        self.value_dist = {}
        self.dim = -1

    def add_value(self, value):
        if value not in self.value_dist:
            self.value_dist[value] = 0
            if self.input_type == FeatureType.Categorical:
                id_size = len(self.id_map) + 1
                self.id_map[value] = id_size

            if self.input_type == FeatureType.Numerical:
                if self.boundary[0] > value:
                    self.boundary[0] = value

                if self.boundary[1] < value:
                    self.boundary[1] = value

        self.value_dist[value] += 1

    def get_dim(self):
        if self.output_type == FeatureType.Numerical:
            self.dim = 1
            return 1
        else:
            if self.input_type == FeatureType.Categorical:
                self.dim = len(self.value_dist) + 1
                return self.dim
            else:
                self.dim = self.internal + 2
                return self.dim

    def value_2_feature(self, value):
        if self.output_type == FeatureType.Numerical:
            normalized_value = (value - self.boundary[0]) / (self.boundary[1] - self.boundary[0] + 1e-8)
            return [normalized_value]
        elif self.output_type == FeatureType.Categorical:
            feature = [0] * self.dim
            if self.input_type == FeatureType.Numerical:
                if value < self.boundary[0]:
                    feature[0] = 1
                elif value > self.boundary[1]:
                    feature[self.dim - 1] = 1
                else:
                    ind = (value - self.boundary[0]) * self.internal / (self.boundary[1] - self.boundary[0] + 1e-8)
                    feature[int(ind)] = 1
            elif self.input_type == FeatureType.Categorical:
                feature[self.id_map.get(value, default=0)] = 1





