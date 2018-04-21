#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-1-8
# datas.py
import time
import os

import pandas as pd

def get_live_frr_far(df,colomn1,score,colomn2):
    
    total = len(df)
    unknow = len(df[df[colomn1] == -1])
    df = df[df[colomn1] != -1]
    real_number = len(df[df[colomn2] == 0])
    photo_number = len(df[df[colomn2] == 1])
    
    # 真人识别为假人
    frr_number = len(df.loc[((df[colomn1] > score) & (df[colomn2] == 0))])
    # 假人识别为真人
    far_number = len(df.loc[((df[colomn1] < score) & (df[colomn2] == 1))])
    frr = 0 if not real_number else frr_number/float(real_number)
    far = 0 if not photo_number else far_number/float(photo_number)
    return (far, frr, total, real_number, frr_number, photo_number, far_number, unknow, unknow/float(total))

def get_gaze_frr_far(df,colomn1,score):
    
    total = len(df)
    unknow = len(df[df[colomn1] == -1])
    df = df[df[colomn1] != -1]
    real_number = len(df.loc[df['filename'].str.contains('/gaze/')])
    no_number = len(df.loc[df['filename'].str.contains('/no_gaze/')])
    
    # 真人识别为假人
    frr_number = len(df.loc[(df['score'] < score) & df['filename'].str.contains('/gaze/')])
    # 假人识别为真人
    far_number = len(df.loc[(df['score'] > score) & df['filename'].str.contains('/no_gaze/')] )
    frr = 0 if not real_number else frr_number/float(real_number)
    far = 0 if not no_number else far_number/float(no_number)
    return (far, frr, total, real_number, frr_number, no_number, far_number, unknow, unknow/float(total))


def load_verify_server_result(names,files,scores, 
    replace_file="/home/andrew/code/data/tof/base_test_data/vivo-verify-452/./",
    replace_name="output/enroll_list/",
    ):

    real_photos = pd.read_csv(files, names=['filename'])
    real_photos['filename'] = real_photos['filename'].apply(
        lambda x:x.replace(replace_file, ''))
    real_photos['person'] =  real_photos['filename'].apply(
        lambda x:x.split('/')[0])
    
    
    persons = pd.read_csv(names,names=['person'])
    persons['person'] = persons['person'].apply(
        lambda x:x.replace(replace_name, ''))
    
    df = pd.read_csv(scores, header=None, engine='c',
                     na_filter=False, low_memory=False)
    df.index = persons['person']
    return df, real_photos


def get_verify_errors(df, real_photos, score):
    
    other_errors = []
    self_errors = []
    for person in df.index:
        print("index:", person)
        print(time.ctime())
        row = df.loc[person]
        row.index = [real_photos['person'], real_photos['filename']]
        self = row[person]
        self_error = self[(self<score) & (self>-1)]
        for item in self_error.index:
            self_errors.append((item, self_error[item]))
        #print(self_error)
        others = row.drop(person,level=0)
        other_error = others[others>=score]
        for item in other_error.index:
            other_errors.append([person,item[1], other_error.loc[item]])    
        #print(other_error)
                
    df_person_errors = pd.DataFrame(self_errors,columns=['filename','score'])
    df_other_errors = pd.DataFrame(other_errors,columns=['person','filename','score'])
    
    return df_person_errors, df_other_errors

def get_verify_frr_far(selfs_num, others_num, df_person_errors, df_other_errors, colomn, score):
    
    frr_num = len(df_person_errors[df_person_errors[colomn] < score])
    far_num = len(df_other_errors[df_other_errors[colomn] > score])
    frr = 0 if not frr_num else frr_num/float(selfs_num)
    far = 0 if not far_num else far_num/float(others_num)
    return (far, frr, selfs_num + others_num, selfs_num, frr_num, others_num, far_num)
    
def get_verify_server_result(
    names,files,scores, score=0.7, output_dir="./",
    replace_file="/home/andrew/code/data/tof/base_test_data/vivo-verify-452/./",
    replace_name="output/enroll_list/",
    ):

    df, real_photos = load_verify_server_result(names,files,scores, 
    replace_file=replace_file,replace_name=replace_name,)
    
    df_person_errors, df_other_errors = get_verify_errors(df, real_photos, score)
    df_person_errors.to_csv('{}{}self_errors.csv'.format(
        output_dir.strip(os.sep), os.sep), index=False)
    df_other_errors.to_csv('{}{}others_errors.csv'.format(
        output_dir.strip(os.sep), os.sep), index=False)
    print(time.ctime())


