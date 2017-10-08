import base_yyc

import datetime
import sys

print_per_block = 1e6


def load_train_test(src, users):
    with open(src, 'r') as fin:
        num_column = -1
        flag = False

        for line in fin:
            if not flag:
                num_column = len(line.strip().split(','))
                flag = True
            else:
                items = line.strip().split(',')
                if len(items) != num_column:
                    err_print = 'wrong input %s' % line
                    print err_print
                else:
                    user_id = items[0]
                    is_churn = int(items[1])

                    if user_id not in users:
                        users[user_id] = base_yyc.UserInstance(user_id, is_churn)


def load_members(src, train_users, test_users):
    with open(src, 'r') as fin:
        num_column = -1
        flag = False
        cnt = 0
        for line in fin:
            cnt += 1
            if cnt % print_per_block == 0:
                sys.stdout.write('%d\r' % cnt)
                sys.stdout.flush()

            if not flag:
                num_column = len(line.strip().split(','))
                flag = True
            else:
                items = line.strip().split(',')
                if len(items) != num_column:
                    err_print = 'wrong input %s' % line
                    print err_print
                else:
                    user_id = items[0]
                    if user_id in train_users:
                        train_users[user_id].add_member_info(','.join(items[1:]))
                    if user_id in test_users:
                        test_users[user_id].add_member_info(','.join(items[1:]))

                    continue

                    city = int(items[1])
                    age = int(items[2])
                    gender = items[3]
                    registered_via = int(items[4])

                    registration_init_time = datetime.date(2017, 10, 3)
                    expiration_date = datetime.date(2017, 10, 3)

                    if len(items[5]) != 8 or len(items[6]) != 8:
                        err_print = 'wrong input %s' % line
                        print err_print
                    else:
                        year = int(items[5][:4])
                        mon = int(items[5][4:6])
                        day = int(items[5][6:8])
                        registration_init_time = datetime.date(year, mon, day)

                        year = int(items[6][:4])
                        mon = int(items[6][4:6])
                        day = int(items[6][6:8])
                        expiration_date = datetime.date(year, mon, day)

                    if user_id in train_users:
                        train_users[user_id].add_member_info(base_yyc.MemberInstance(user_id, city, age, gender,
                                                                                     registered_via,
                                                                                     registration_init_time,
                                                                                     expiration_date))

                    if user_id in test_users:
                        test_users[user_id].add_member_info(base_yyc.MemberInstance(user_id, city, age, gender,
                                                                                    registered_via,
                                                                                    registration_init_time,
                                                                                    expiration_date))


def load_logs(src, train_users, test_users):
    with open(src, 'r') as fin:
        num_column = -1
        flag = False
        cnt = 0
        for line in fin:
            cnt += 1
            if cnt % print_per_block == 0:
                sys.stdout.write('%d\r' % cnt)
                sys.stdout.flush()

            if not flag:
                num_column = len(line.strip().split(','))
                flag = True
            else:
                items = line.strip().split(',')
                if len(items) != num_column:
                    err_print = 'wrong input %s' % line
                    print err_print
                else:
                    user_id = items[0]
                if user_id in train_users:
                    train_users[user_id].add_logs(','.join(items[1:]))

                if user_id in test_users:
                    test_users[user_id].add_logs(','.join(items[1:]))
                continue

                date = datetime.date(2017, 10, 3)

                if len(items[1]) != 8:
                    err_print = 'wrong input %s' % line
                    print err_print
                else:
                    year = int(items[1][:4])
                    mon = int(items[1][4:6])
                    day = int(items[1][6:8])
                    date = datetime.date(year, mon, day)

                    num_25 = int(items[2])
                    num_50 = int(items[3])
                    num_75 = int(items[4])
                    num_985 = int(items[5])
                    num_100 = int(items[6])
                    num_unq = int(items[7])
                    total_secs = float(items[8])

                    if user_id in train_users:
                        train_users[user_id].add_logs(base_yyc.LogInstance(user_id, date, num_25, num_50, num_75,
                                                                           num_985, num_100, num_unq, total_secs))

                    if user_id in test_users:
                        test_users[user_id].add_logs(base_yyc.LogInstance(user_id, date, num_25, num_50, num_75,
                                                                          num_985, num_100, num_unq, total_secs))


def load_transactions(src, train_users, test_users):
    with open(src, 'r') as fin:
        num_column = -1
        flag = False
        cnt = 0
        for line in fin:
            cnt += 1
            if cnt % print_per_block == 0:
                sys.stdout.write('%d\r' % cnt)
                sys.stdout.flush()

            if not flag:
                num_column = len(line.strip().split(','))
                flag = True
            else:
                items = line.strip().split(',')
                if len(items) != num_column:
                    err_print = 'wrong input %s' % line
                    print err_print
                else:
                    user_id = items[0]

                if user_id in train_users:
                    train_users[user_id].add_transactions(','.join(items[1:]))

                if user_id in test_users:
                    test_users[user_id].add_transactions(','.join(items[1:]))
                continue

                payment_method_id = int(items[1])
                payment_plan_days = int(items[2])
                plan_list_price = int(items[3])
                actual_amount_paid = int(items[4])
                is_auto_renew = int(items[5])

                transaction_date = datetime.date(2017, 10, 3)
                membership_expire_date = datetime.date(2017, 10, 3)

                if len(items[6]) != 8 or len(items[7]) != 8:
                    err_print = 'wrong input %s' % line
                    print err_print
                else:
                    year = int(items[6][:4])
                    mon = int(items[6][4:6])
                    day = int(items[6][6:8])
                    transaction_date = datetime.date(year, mon, day)

                    year = int(items[7][:4])
                    mon = int(items[7][4:6])
                    day = int(items[7][6:8])
                    membership_expire_date = datetime.date(year, mon, day)

                    is_cancel = int(items[8])

                    if user_id in train_users:
                        train_users[user_id].add_transactions(base_yyc.TranInstance(user_id, payment_method_id,
                                                                                    payment_plan_days, plan_list_price,
                                                                                    actual_amount_paid, is_auto_renew,
                                                                                    transaction_date,
                                                                                    membership_expire_date, is_cancel))

                    if user_id in test_users:
                        test_users[user_id].add_transactions(base_yyc.TranInstance(user_id, payment_method_id,
                                                                                   payment_plan_days, plan_list_price,
                                                                                   actual_amount_paid, is_auto_renew,
                                                                                   transaction_date,
                                                                                   membership_expire_date, is_cancel))


def load_line_iterator(src):
    with open(src, 'r') as fin:
        for line in fin:
            yield line.strip()


def string_2_instance(line):
    items = line.split('\t')
    user_instance = base_yyc.UserInstance(items[0], int(items[1]))
    user_instance.add_member_info(items[2])

    logs = items[3].split('#@#')
    for log in logs:
        user_instance.add_logs(log)

    transactions = items[4].split('#@#')
    for transaction in transactions:
        user_instance.add_transactions(transaction)

    return user_instance


def instance_2_string(user_id, instance):
    user_id = user_id
    user_instance = instance
    #print user_id
	
    items = []
    items.append(user_id)
    items.append(str(user_instance.is_churn))

    if user_instance.member_info:
    	items.append(user_instance.member_info)
    else:
 	return None

    logs = '#@#'.join(user_instance.logs)
    items.append(logs)

    transactions = '#@#'.join(user_instance.transactions)
    items.append(transactions)
   
    return '\t'.join(items)


def instances_2_file(src, instances):
    with open(src, 'w') as fout:
        for user_id, instance in instances.iteritems():
	    out_str = instance_2_string(user_id, instance)
            if out_str:
		fout.write(out_str + '\n')

