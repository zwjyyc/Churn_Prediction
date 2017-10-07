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