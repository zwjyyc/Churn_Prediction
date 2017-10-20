import base_yyc

import datetime
import pickle
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
        match = 0
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
                        match += 1
                    if user_id in test_users:
                        test_users[user_id].add_member_info(','.join(items[1:]))
                        match += 1
    print 'matched %d/%d' % (match, len(test_users) + len(train_users))

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


def load_line_iterator(src):
    with open(src, 'r') as fin:
        for line in fin:
            yield line.strip()


def string_2_instance(line):
    items = line.split('\t')

    if len(items) != 5:
        print 'error input %s in string_2_instance' % (line)
        return None

    user_instance = base_yyc.UserInstance(items[0], int(items[1]))
    user_instance.add_member_info(items[2])

    if items[3]:
        logs = items[3].split('#@#')
        for log in logs:
            user_instance.add_logs(log)

    if items[4]:
        transactions = items[4].split('#@#')
        for transaction in transactions:
            user_instance.add_transactions(transaction)

    return user_instance


def instance_2_string(user_id, instance):
    user_id = user_id
    user_instance = instance

    items = []
    items.append(user_id)
    items.append(str(user_instance.is_churn))

    items.append(user_instance.member_info)

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


def load_configure(src, templates):
    with open(src, 'r') as fin:
        for line in fin:
            line = line.strip()
            if line and line[0] != '#':
                name = ''
                input_type = ''
                output_type = ''
                boundary = [float('inf'), -float('inf')]
                time_boundary = [datetime.date(2018, 1, 1), datetime.date(2000, 1, 1)]
                internal = []
                time_internal = []

                items = line.split(',')
                for item in items:
                    _items = item.split('=')
                    key = _items[0]
                    value = _items[1]
                    if key == 'Name':
                        name = value
                    elif key == 'InputType':
                        input_type = value
                    elif key == 'OutputType':
                        output_type = value
                    elif key == 'LowerBoundary':
                        boundary[0] = float(value)
                    elif key == 'UpperBoundary':
                        boundary[1] = float(value)
                    elif key == 'LowerTimeBoundary':
                        year = int(value[:4])
                        mon = int(value[4:6])
                        day = int(value[6:8])
                        time_boundary[0] = datetime.date(year, mon, day)
                    elif key == 'UpperTimeBoundary':
                        year = int(value[:4])
                        mon = int(value[4:6])
                        day = int(value[6:8])
                        time_boundary[1] = datetime.date(year, mon, day)
                    elif key == 'TimeInternal':
                        time_internal = [int(item) for item in value.split('&')]
                    elif key == 'Internal':
                        internal = [int(item) for item in value.split('&')]
                if name not in templates:
                    templates[name] = base_yyc.FeatureTemplate(name, input_type, output_type,
                                                               boundary, time_boundary, internal,
                                                               time_internal)


def configure_2_string(templates):
    out_str = ''
    for template in templates:
        out_str = template
    return out_str


def string_2_member(line, user_id):
    if not line:
        return None

    items = line.strip().split(',')
    city = int(items[0])
    age = int(items[1])
    gender = items[2]
    registered_via = int(items[3])

    registration_init_time = datetime.date(2017, 10, 3)
    expiration_date = datetime.date(2017, 10, 3)

    if len(items[4]) != 8 or len(items[5]) != 8:
        err_print = 'wrong input %s' % line
        print err_print
        return None
    else:
        year = int(items[4][:4])
        mon = int(items[4][4:6])
        day = int(items[4][6:8])
        registration_init_time = datetime.date(year, mon, day)

        year = int(items[5][:4])
        mon = int(items[5][4:6])
        day = int(items[5][6:8])
        expiration_date = datetime.date(year, mon, day)
        member = base_yyc.MemberInstance(user_id, city, age, gender,
                                         registered_via,
                                         registration_init_time,
                                         expiration_date)
        return member


def strings_2_logs(lines, user_id):
    logs = []
    for line in lines:
        if not line:
            continue

        items = line.split(',')
        date = datetime.date(2017, 10, 3)

        if len(items[0]) != 8:
            err_print = 'wrong input %s' % line
            print err_print
        else:
            year = int(items[0][:4])
            mon = int(items[0][4:6])
            day = int(items[0][6:8])
            date = datetime.date(year, mon, day)

            num_25 = int(items[1])
            num_50 = int(items[2])
            num_75 = int(items[3])
            num_985 = int(items[4])
            num_100 = int(items[5])
            num_unq = int(items[6])
            total_secs = float(items[7])
            logs.append(base_yyc.LogInstance(user_id, date, num_25, num_50, num_75, num_985,
                                             num_100, num_unq, total_secs))
    return logs


def strings_2_transactions(lines, user_id):
    transactions = []
    for line in lines:
        if not line:
            continue

        items = line.split(',')
        date = datetime.date(2017, 10, 3)

        payment_method_id = items[0]
        payment_plan_days = int(items[1])
        plan_list_price = int(items[2])
        actual_amount_paid = int(items[3])
        is_auto_renew = items[4]

        transaction_date = datetime.date(2017, 10, 3)
        membership_expire_date = datetime.date(2017, 10, 3)

        if len(items[5]) != 8 or len(items[6]) != 8:
            err_print = 'wrong input %s' % line
            print err_print
        else:
            year = int(items[5][:4])
            mon = int(items[5][4:6])
            day = int(items[5][6:8])
            transaction_date = datetime.date(year, mon, day)

            year = int(items[6][:4])
            mon = int(items[6][4:6])
            day = int(items[6][6:8])
            membership_expire_date = datetime.date(year, mon, day)

            is_cancel = int(items[7])
            transactions.append(base_yyc.TranInstance(user_id, payment_method_id, payment_plan_days, plan_list_price,
                                                      actual_amount_paid, is_auto_renew, transaction_date,
                                                      membership_expire_date, is_cancel))
    return transactions


def dict_2_file(dic, src):
    with open(src, 'w') as fout:
        for key, value in sorted(dic.items()):
            fout.write(str(key) + ':' + str(value) + '\n')


def dict_dict_2_file(dic1, dic2, src):
    with open(src, 'w') as fout:
        for key, value in sorted(dic1.items()):
            label_dist = dic2[key]
            out_str = str(key) + ':' + str(value)

            for key_, value_ in sorted(label_dist.items(), key=lambda (k, v): (v, k)):
                out_str += '@#@' + str(key_) + ':' + str(value_)

            if 0 in label_dist and 1 in label_dist:
                cnt = label_dist[0] + label_dist[1]
                c_cnt = label_dist[1]

                out_str += '@#@' + str(c_cnt * 1.0 / cnt)
                fout.write(out_str + '\n')


def features_2_file(labels, features, file):
    with open(file, 'w') as fout:
        for label, feature in zip(labels, features):
            out_str = str(label) + '\t'

            for ind, val in enumerate(feature):
                out_str += '%d:%f ' % (ind + 1, val)
            fout.write(out_str.strip() + '\n')


def ids_2_file(ids, file):
    with open(file, 'w') as fout:
        fout.write('\n'.join(ids))


def load_ids(file):
    ids = []
    with open(file, 'r') as fin:
        for line in fin:
            ids.append(line.strip())
    return ids


def generate_results(preds, ids, file):
    with open(file, 'w') as fout:
        fout.write('msno,is_churn\n')
        for pred, id in zip(preds, ids):
            out_str = '%s,%.7f\n' % (id, pred)
            fout.write(out_str)


def save_feature_ind(inds, src):
    with open(src, 'wb') as fout:
        pickle.dump(inds, fout, protocol=pickle.HIGHEST_PROTOCOL)


def load_feature_ind(src):
    with open(src, 'rb') as fin:
        return  pickle.load(fin)


def svminput_2_list(src):
    features = []
    labels = []
    with open(src, 'r') as fin:
        for line in fin:
            items = line.strip().split('\t')
            labels.append(int(items[0]))
            features.append([ float(item.split(':')[1]) for item in items[1].split()])

    return features, labels
