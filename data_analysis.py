import matplotlib.pyplot as plt
import numpy as np
from time import *
import sys
import os
import csv


# ================================ Only keep track of instances that admits a super-stable matching ================================
def get_soluble_instances(filename):
    is_super_stable = []
    with open(filename, 'r') as read_csvfile:
        I = list(csv.reader(read_csvfile, delimiter=' '))
        for row in I:
            if row[1] == 'Y':
                is_super_stable.append(int(row[2]))
    return is_super_stable
#  ---------------------------------------------------------------------------------------------------------------------------------
#  =================================================================================================================================


# =================================== The proportion of these instances -- 1000 instances in all ===================================
def proportion(value):
    return round((value/1000)*100, 2)
#  ---------------------------------------------------------------------------------------------------------------------------------
#  =================================================================================================================================


# ================================= Perform basic statistics on these instances =================================
def write_statistics(write_to, write_from):
    proportion_matching = []
    #mean_matching = []
    #min_matching = []
    #max_matching = []
    #median_matching = []
    with open(write_to, 'w', newline='') as write_csvfile:
        O = csv.writer(write_csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        O.writerow(['n1', 'proportion', 'mean', 'min', 'max', 'median'])
        for i in range(100, 1100, 100):
            filename = write_from + str(i) + '/output.csv'
            is_super_stable = get_soluble_instances(filename)
            p = proportion(len(is_super_stable))
            #me = np.mean(is_super_stable)
            #mi = min(is_super_stable)
            #ma = max(is_super_stable)
            #med = np.median(is_super_stable)

            proportion_matching.append(p)
            #mean_matching.append(me)
            #min_matching.append(mi)
            #max_matching.append(ma)
            #median_matching.append(med)
            O.writerow([i, p])
        write_csvfile.close()
    return proportion_matching
#  ---------------------------------------------------------------------------------------------------------------------------------
#  =================================================================================================================================
instances = list(range(100, 1100, 100))
write_to_1_005 = 'experiments/1_005/experiment1_005.csv'
write_to_1_05 = 'experiments/1_05/experiment1_05.csv'

write_from_1_005 = 'experiments/1_005/'
write_from_1_05 = 'experiments/1_05/'

proportion_matching_1_005 = write_statistics(write_to_1_005, write_from_1_005)
proportion_matching_1_05 = write_statistics(write_to_1_05, write_from_1_05)

plt.figure()
plt.grid()

plt.plot(instances, proportion_matching_1_005, color='r', label='0.005')
plt.plot(instances, proportion_matching_1_05, color='b', label='0.05')

plt.xlabel('instance size')
plt.ylabel('proportion of soluble instances')

plt.legend(loc='upper right')
plt.show()
# -------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------



#
# def write_statistics_1_005():
#     instances_1_005 = []
#     proportion_matching_1_005 = []
#     mean_matching_1_005 = []
#     min_matching_1_005 = []
#     max_matching_1_005 = []
#     median_matching_1_005 = []
#     write_to = '/home/sofiat/Documents/Glasgow/research/spa-st-super-stability/experiments/1_005/experiment1_005.csv'
#     with open(write_to, 'w', newline='') as write_csvfile:
#         O = csv.writer(write_csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
#         O.writerow(['n1', 'proportion', 'mean', 'min', 'max', 'median'])
#         f = 'experiments/1_005/'
#         for i in range(100, 1100, 100):
#             instances_1_005.append(i)
#             filename = f + str(i) + '/output.csv'
#             is_super_stable = get_soluble_instances(filename)
#             p = proportion(len(is_super_stable))
#             me = np.mean(is_super_stable)
#             mi = min(is_super_stable)
#             ma = max(is_super_stable)
#             med = np.median(is_super_stable)
#
#             proportion_matching_1_005.append(p)
#             mean_matching_1_005.append(me)
#             min_matching_1_005.append(mi)
#             max_matching_1_005.append(ma)
#             median_matching_1_005.append(med)
#             O.writerow([i, p, me, mi, ma, med])
#         write_csvfile.close()
#     return instances_1_005, proportion_matching_1_005, mean_matching_1_005, min_matching_1_005, max_matching_1_005, median_matching_1_005
