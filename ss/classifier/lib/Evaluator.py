###########################################################################################
#                                                                                         #
# Evaluator class: Implements the most popular metrics for object detection               #
#                                                                                         #
# Developed by: Rafael Padilla (rafael.padilla@smt.ufrj.br)                               #
#        SMT - Signal Multimedia and Telecommunications Lab                               #
#        COPPE - Universidade Federal do Rio de Janeiro                                   #
#        Last modification: Oct 9th 2018                                                 #
###########################################################################################

import os
import sys
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np

try:
    from lib.BoundingBox import *
    from lib.BoundingBoxes import *
except ImportError:
    from aicr_classification_train.lib.BoundingBox import *
    from aicr_classification_train.lib.BoundingBoxes import *


classes_vn = "ĂÂÊÔƠƯÁẮẤÉẾÍÓỐỚÚỨÝÀẰẦÈỀÌÒỒỜÙỪỲẢẲẨĐẺỂỈỎỔỞỦỬỶÃẴẪẼỄĨÕỖỠŨỮỸẠẶẬẸỆỊỌỘỢỤỰỴăâêôơưáắấéếíóốớúứýàằầèềìòồờùừỳảẳẩđẻểỉỏổởủửỷãẵẫẽễĩõỗỡũữỹạặậẹệịọộợụựỵ"
class_list_vn = [x for x in classes_vn]

classes_symbol = '*:,@$.-(#%\'\")/~!^&_+={}[]\;<>?※”'
class_list_symbol = [x for x in classes_symbol]

classes_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
class_list_alphabet = [x for x in classes_alphabet]

classes_number = '0123456789'
class_list_number = [x for x in classes_number]


chinese_file_path = "textimg_data_generator_dev/dataprovision/config/chinese.txt"
class_list_chinese = list()
if chinese_file_path is not None:
    with open(chinese_file_path) as fp:
        class_list_chinese = [c for c in fp.read(-1)]

class Evaluator:
    def GetF1ScoreMetrics(self, boundingboxes):
        groundTruths = []
        detections = []
        # Loop through all bounding boxes and separate them into GTs and detections
        for bb in boundingboxes.getBoundingBoxes():
            if bb.getBBType() == BBType.GroundTruth:
                groundTruths.append([
                    bb.getImageName(),
                    bb.getClassId(), 1,
                    bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                ])
            else:
                (x, y, x2, y2) = bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                x_cent = (x + x2) / 2
                y_cent = (y + y2) / 2
                detections.append([
                    bb.getImageName(),
                    bb.getClassId(),
                    bb.getConfidence(),
                    (x_cent, y_cent)
                ])

        dects = detections
        gts = groundTruths

        TP = np.zeros(len(dects))
        FP = np.zeros(len(dects))
        FN = np.zeros(len(gts))
        TP_g = np.zeros(len(gts))

        for d in range(len(dects)):
            gt = [gt for gt in gts if gt[0] == dects[d][0]]
            for j in range(len(gt)):
                # cal TN and FN
                (xmin, ymin, xmax, ymax) = gt[j][3]
                # print(j)
                (preds_x, preds_y) = dects[d][3]
                label = gt[j][1]
                preds_label = dects[d][1]
                matching = (xmin < preds_x) & (xmax > preds_x) & (ymin < preds_y) & (ymax > preds_y) & (
                        preds_label == label)
                if matching:
                    TP[d] = 1
            if TP[d] == 0:
                FP[d] = 1

        # print(np.sum(TP))
        # print(np.sum(FP))
        for g in range(len(gts)):

            pd = [pd for pd in dects if pd[0] == gts[g][0]]
            # iouMax = sys.float_info.min
            for j in range(len(pd)):
                # cal FN
                (preds_x, preds_y) = pd[j][3]
                # print(j)
                (xmin, ymin, xmax, ymax) = gts[g][3]
                label = pd[j][1]
                preds_label = gts[g][1]
                matching = (xmin < preds_x) & (xmax > preds_x) & (ymin < preds_y) & (ymax > preds_y) & (
                        preds_label == label)
                if matching:
                    TP_g[g] = 1
            #         # print('true: ',(xmin, xmax, ymin, ymax), (preds_x, preds_y))
            if TP_g[g] == 0:
                FN[g] = 1
        r = {
            'TP': np.sum(TP),
            'FP': np.sum(FP),
            'FN': np.sum(FN)
        }
        # ret.append(r)
        return r

    def GetF1ScoreMetricsChinese(self, boundingboxes):
        groundTruths = []
        detections = []
        # Loop through all bounding boxes and separate them into GTs and detections
        for bb in boundingboxes.getBoundingBoxes():
            if bb.getBBType() == BBType.GroundTruth:
                groundTruths.append([
                    bb.getImageName(),
                    bb.getClassId(), 1,
                    bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                ])
            else:
                (x, y, x2, y2) = bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                x_cent = (x + x2) / 2
                y_cent = (y + y2) / 2
                detections.append([
                    bb.getImageName(),
                    bb.getClassId(),
                    bb.getConfidence(),
                    (x_cent, y_cent)
                ])

        dects = detections
        gts = groundTruths

        TP = np.zeros(len(dects))
        FP = np.zeros(len(dects))
        FN = np.zeros(len(gts))
        TP_g = np.zeros(len(gts))
        NonBlankBox = np.zeros(len(dects))
        BlankBox = np.zeros(len(dects))
        CN_blankbox = 0
        Alp_blankbox = 0
        Sym_blankbox = 0
        Numb_blankbox = 0
        Bg_blankbox   = 0

        for d in range(len(dects)):
            gt = [gt for gt in gts if gt[0] == dects[d][0]]
            isBackground = False
            if  dects[d][1] == 'background':
                isBackground = True
            for j in range(len(gt)):
                # cal TN and FN
                (xmin, ymin, xmax, ymax) = gt[j][3]
                # print(j)
                (preds_x, preds_y) = dects[d][3]
                label = gt[j][1]
                preds_label = dects[d][1]
                matching = (xmin < preds_x) & (xmax > preds_x) & (ymin < preds_y) & (ymax > preds_y) & (
                        preds_label == label)
                if matching:
                    TP[d] = 1
                matching_1 = (xmin < preds_x) & (xmax > preds_x) & (ymin < preds_y) & (ymax > preds_y)
                if matching_1:
                    NonBlankBox[d] = 1
            if TP[d] == 0 and isBackground == False:
                FP[d] = 1
            if NonBlankBox[d] == 0:
                BlankBox[d] = 1
                if preds_label in class_list_number:
                    Numb_blankbox +=1
                elif preds_label in class_list_alphabet:
                    Alp_blankbox += 1
                elif preds_label in class_list_chinese:
                    CN_blankbox += 1
                elif preds_label in class_list_symbol:
                    Sym_blankbox += 1
                elif preds_label == 'background':
                    Bg_blankbox += 1

        # print(np.sum(TP))
        # print(np.sum(FP))
        missing_text = 0
        for g in range(len(gts)):

            pd = [pd for pd in dects if pd[0] == gts[g][0]]
            # iouMax = sys.float_info.min
            missing = True
            for j in range(len(pd)):
                # cal FN
                (preds_x, preds_y) = pd[j][3]
                # print(j)
                (xmin, ymin, xmax, ymax) = gts[g][3]
                label = pd[j][1]
                preds_label = gts[g][1]
                matching = (xmin < preds_x) & (xmax > preds_x) & (ymin < preds_y) & (ymax > preds_y) & (
                        preds_label == label)
                if missing != False and xmin < preds_x and xmax > preds_x and ymin < preds_y and ymax > preds_y:
                    missing = False
                if matching:
                    TP_g[g] = 1
            #         # print('true: ',(xmin, xmax, ymin, ymax), (preds_x, preds_y))
            if TP_g[g] == 0:
                FN[g] = 1
            if missing == True:
                missing_text +=1

        MultiLabel = len(dects) + np.sum(FN) - np.sum(BlankBox) - len(gts)

        r = {
            'TP': np.sum(TP),
            'FP': np.sum(FP),
            'FN': np.sum(FN),
            'Miss': missing_text,
            'Multi_Label':MultiLabel,
            'Blank_Box': np.sum(BlankBox),
            'CN_blankbox': CN_blankbox,
            'Sym_blankbox': Sym_blankbox,
            'Alp_blankbox': Alp_blankbox,
            'Numb_blankbox': Numb_blankbox,
            'Bg_blankbox' : Bg_blankbox
        }
        # ret.append(r)
        return r

    def GetTruePositiveChinese(self, boundingboxes,numb_class_bg = None, numb_class_bg_sym = None):
        # groundTruths = []
        detections = []
        chinese_gt_chars = []
        alphabet_gt_chars = []
        number_gt_chars = []
        sym_gt_chars = []
        # Loop through all bounding boxes and separate them into GTs and detections
        for bb in boundingboxes.getBoundingBoxes():
            if bb.getBBType() == BBType.GroundTruth:
                if bb.getClassId() in class_list_alphabet:
                    alphabet_gt_chars.append([
                        bb.getImageName(),
                        bb.getClassId(), 1,
                        bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                    ])
                elif bb.getClassId() in class_list_number:
                    number_gt_chars.append([
                        bb.getImageName(),
                        bb.getClassId(), 1,
                        bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                    ])
                elif bb.getClassId() in class_list_symbol:
                    sym_gt_chars.append([
                        bb.getImageName(),
                        bb.getClassId(), 1,
                        bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                    ])
                elif bb.getClassId() in class_list_chinese:
                    chinese_gt_chars.append([
                        bb.getImageName(),
                        bb.getClassId(), 1,
                        bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                    ])
            else:
                (x, y, x2, y2) = bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                x_cent = (x + x2) / 2
                y_cent = (y + y2) / 2
                detections.append([
                    bb.getImageName(),
                    bb.getClassId(),
                    bb.getConfidence(),
                    (x_cent, y_cent)
                ])
        dects = detections

        TP_gt_cn = np.zeros(len(chinese_gt_chars))
        FN_gt_cn = np.zeros(len(chinese_gt_chars))
        TP_gt_alp = np.zeros(len(alphabet_gt_chars))
        FN_gt_alp = np.zeros(len(alphabet_gt_chars))
        TP_gt_sym = np.zeros(len(sym_gt_chars))
        FN_gt_sym = np.zeros(len(sym_gt_chars))
        TP_gt_num = np.zeros(len(number_gt_chars))
        FN_gt_num = np.zeros(len(number_gt_chars))


        Numb_predict_cn = len([c for c in dects if c[1] in class_list_chinese])
        Numb_predict_alp = len([c for c in dects if c[1] in class_list_alphabet])
        Numb_predict_sym = len([c for c in dects if c[1] in class_list_symbol])
        Numb_predict_num = len([c for c in dects if c[1] in class_list_number])

        TruePredict_classFilter = len(dects)
        FalsePredict_classFilter = 0
        FalsePredict_background  = 0
        FalsePredict_backgroundSymbol = 0

        Predict_CN ={}
        Predict_CN['sym'] = 0
        Predict_CN['alp'] = 0
        Predict_CN['numb'] = 0
        Predict_CN['bg'] = 0

        Predict_Sym = {}
        Predict_Sym['cn'] = 0
        Predict_Sym['alp'] = 0
        Predict_Sym['numb'] = 0
        Predict_Sym['bg'] = 0

        Predict_Alp = {}
        Predict_Alp['cn'] = 0
        Predict_Alp['sym'] = 0
        Predict_Alp['numb'] = 0
        Predict_Alp['bg'] = 0

        Predict_Numb = {}
        Predict_Numb['cn'] = 0
        Predict_Numb['sym'] = 0
        Predict_Numb['alp'] = 0
        Predict_Numb['bg'] = 0

        for g in range(len(chinese_gt_chars)):
            pd = [pd for pd in dects if pd[0] == chinese_gt_chars[g][0]]
            for j in range(len(pd)):
                # cal FN
                (preds_x, preds_y) = pd[j][3]
                (xmin, ymin, xmax, ymax) = chinese_gt_chars[g][3]
                preds_label = pd[j][1]
                label = chinese_gt_chars[g][1]
                matching = (xmin < preds_x) & (xmax > preds_x) & (ymin < preds_y) & (ymax > preds_y) & (
                        preds_label == label)
                if matching:
                    TP_gt_cn[g] = 1
                if xmin < preds_x and xmax > preds_x and ymin < preds_y and ymax > preds_y :
                    if preds_label not in class_list_chinese:
                        FalsePredict_classFilter +=1
                        if preds_label == 'background':
                            FalsePredict_background += 1
                            Predict_CN['bg'] += 1
                        elif preds_label in class_list_symbol:
                            Predict_CN['sym'] += 1
                        elif preds_label in class_list_alphabet:
                            Predict_CN['alp'] += 1
                        elif preds_label in class_list_number:
                            Predict_CN['numb'] += 1
                        elif preds_label == 'background2':
                            FalsePredict_backgroundSymbol += 1

            if TP_gt_cn[g] == 0:
                FN_gt_cn[g] = 1

        for g in range(len(sym_gt_chars)):
            pd = [pd for pd in dects if pd[0] == sym_gt_chars[g][0]]
            for j in range(len(pd)):
                # cal FN
                (preds_x, preds_y) = pd[j][3]
                (xmin, ymin, xmax, ymax) = sym_gt_chars[g][3]
                preds_label = pd[j][1]
                if preds_label == 'dot':
                    preds_label = '.'
                elif preds_label == 'slash':
                    preds_label = '/'

                label = sym_gt_chars[g][1]
                matching = (xmin < preds_x) & (xmax > preds_x) & (ymin < preds_y) & (ymax > preds_y) & (
                        preds_label == label)
                if xmin < preds_x and xmax > preds_x and ymin < preds_y and ymax > preds_y :
                    if preds_label not in class_list_symbol:
                        FalsePredict_classFilter +=1
                        if preds_label == 'background':
                            FalsePredict_background += 1
                            Predict_Sym['bg'] += 1
                        elif preds_label in class_list_chinese:
                            Predict_Sym['cn'] += 1
                        elif preds_label in class_list_alphabet:
                            Predict_Sym['alp'] += 1
                        elif preds_label in class_list_number:
                            Predict_Sym['numb'] += 1
                        elif preds_label == 'background2':
                            FalsePredict_backgroundSymbol += 1
                if matching:
                    TP_gt_sym[g] = 1
            if TP_gt_sym[g] == 0:
                FN_gt_sym[g] = 1

        for g in range(len(alphabet_gt_chars)):
            pd = [pd for pd in dects if pd[0] == alphabet_gt_chars[g][0]]
            for j in range(len(pd)):
                # cal FN
                (preds_x, preds_y) = pd[j][3]
                (xmin, ymin, xmax, ymax) = alphabet_gt_chars[g][3]
                preds_label = pd[j][1]
                if len(preds_label) == 2:
                    preds_label = preds_label[0]
                label = alphabet_gt_chars[g][1]
                matching = (xmin < preds_x) & (xmax > preds_x) & (ymin < preds_y) & (ymax > preds_y) & (
                        preds_label == label)
                if xmin < preds_x and xmax > preds_x and ymin < preds_y and ymax > preds_y :
                    if preds_label not in class_list_alphabet:
                        FalsePredict_classFilter +=1
                        if preds_label == 'background':
                            FalsePredict_background += 1
                            Predict_Alp['bg'] += 1
                        elif preds_label in class_list_symbol:
                            Predict_Alp['sym'] += 1
                        elif preds_label in class_list_chinese:
                            Predict_Alp['cn'] += 1
                        elif preds_label in class_list_number:
                            Predict_Alp['numb'] += 1
                        elif preds_label == 'background2':
                            FalsePredict_backgroundSymbol += 1
                if matching:
                    TP_gt_alp[g] = 1
            if TP_gt_alp[g] == 0:
                FN_gt_alp[g] = 1

        for g in range(len(number_gt_chars)):
            pd = [pd for pd in dects if pd[0] == number_gt_chars[g][0]]
            for j in range(len(pd)):
                # cal FN
                (preds_x, preds_y) = pd[j][3]
                (xmin, ymin, xmax, ymax) = number_gt_chars[g][3]
                preds_label = pd[j][1]
                label = number_gt_chars[g][1]
                matching = (xmin < preds_x) & (xmax > preds_x) & (ymin < preds_y) & (ymax > preds_y) & (
                        preds_label == label)
                if xmin < preds_x and xmax > preds_x and ymin < preds_y and ymax > preds_y:
                    if preds_label not in class_list_number:
                        FalsePredict_classFilter += 1
                        if preds_label == 'background':
                            FalsePredict_background += 1
                            Predict_Numb['bg'] += 1
                        elif preds_label in class_list_symbol:
                            Predict_Numb['sym'] += 1
                        elif preds_label in class_list_alphabet:
                            Predict_Numb['alp'] += 1
                        elif preds_label in class_list_chinese:
                            Predict_Numb['cn'] += 1
                        elif preds_label == 'background2':
                            FalsePredict_backgroundSymbol += 1
                if matching:
                    TP_gt_num[g] = 1
            if TP_gt_num[g] == 0:
                FN_gt_num[g] = 1
        if numb_class_bg is not None:
            TruePredict_background = numb_class_bg - FalsePredict_background
            # print('True Predict bg : ',TruePredict_background ,' False predict bg: ',FalsePredict_background)

        r = {
            'TP_gt_cn': np.sum(TP_gt_cn),
            'FN_gt_cn': np.sum(FN_gt_cn),
            'TP_gt_alp': np.sum(TP_gt_alp),
            'FN_gt_alp': np.sum(FN_gt_alp),
            'TP_gt_sym': np.sum(TP_gt_sym),
            'FN_gt_sym': np.sum(FN_gt_sym),
            'TP_gt_num': np.sum(TP_gt_num),
            'FN_gt_num': np.sum(FN_gt_num),
            'TruePredict_cn': np.sum(TP_gt_cn),
            'TruePredict_alp':  np.sum(TP_gt_alp),
            'TruePredict_sym': np.sum(TP_gt_sym),
            'TruePredict_num': np.sum(TP_gt_num),
            'FalsePredict_cn' : Numb_predict_cn - np.sum(TP_gt_cn),
            'FalsePredict_alp' : Numb_predict_alp - np.sum(TP_gt_alp),
            'FalsePredict_sym' : Numb_predict_sym - np.sum(TP_gt_sym),
            'FalsePredict_num' : Numb_predict_num - np.sum(TP_gt_num),
            'TruePredict_background': TruePredict_background,
            'FalsePredict_background': FalsePredict_background,
            'TruePredict_backgroundSym' : numb_class_bg_sym - FalsePredict_backgroundSymbol,
            'FalsePredict_backgroundSym' : FalsePredict_backgroundSymbol,
            'TruePredict_Filter_language': TruePredict_classFilter - FalsePredict_classFilter,
            'FalsePredict_Filter_language': FalsePredict_classFilter,
            'PredictFailCN': Predict_CN,
            'PredictFailNumb': Predict_Numb,
            'PredictFailSym': Predict_Sym,
            'PredictFailAlp':Predict_Alp
        }
        return r

    def GetTruePositive(self, boundingboxes):
        # groundTruths = []
        detections = []
        chinese_gt_chars = []
        alphabet_gt_chars = []
        number_gt_chars = []
        sym_gt_chars = []
        # Loop through all bounding boxes and separate them into GTs and detections
        for bb in boundingboxes.getBoundingBoxes():
            if bb.getBBType() == BBType.GroundTruth:
                if bb.getClassId() in class_list_alphabet:
                    alphabet_gt_chars.append([
                        bb.getImageName(),
                        bb.getClassId(), 1,
                        bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                    ])
                elif bb.getClassId() in class_list_number:
                    number_gt_chars.append([
                        bb.getImageName(),
                        bb.getClassId(), 1,
                        bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                    ])
                elif bb.getClassId() in class_list_symbol:
                    sym_gt_chars.append([
                        bb.getImageName(),
                        bb.getClassId(), 1,
                        bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                    ])
                elif bb.getClassId() in class_list_vn:
                    chinese_gt_chars.append([
                        bb.getImageName(),
                        bb.getClassId(), 1,
                        bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                    ])
            else:
                (x, y, x2, y2) = bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                x_cent = (x + x2) / 2
                y_cent = (y + y2) / 2
                detections.append([
                    bb.getImageName(),
                    bb.getClassId(),
                    bb.getConfidence(),
                    (x_cent, y_cent)
                ])
        dects = detections

        TP_gt_vn = np.zeros(len(chinese_gt_chars))
        FN_gt_vn = np.zeros(len(chinese_gt_chars))
        TP_gt_alp = np.zeros(len(alphabet_gt_chars))
        FN_gt_alp = np.zeros(len(alphabet_gt_chars))
        TP_gt_sym = np.zeros(len(sym_gt_chars))
        FN_gt_sym = np.zeros(len(sym_gt_chars))
        TP_gt_num = np.zeros(len(number_gt_chars))
        FN_gt_num = np.zeros(len(number_gt_chars))

        for g in range(len(chinese_gt_chars)):
            pd = [pd for pd in dects if pd[0] == chinese_gt_chars[g][0]]
            for j in range(len(pd)):
                # cal FN
                (preds_x, preds_y) = pd[j][3]
                (xmin, ymin, xmax, ymax) = chinese_gt_chars[g][3]
                preds_label = pd[j][1]
                label = chinese_gt_chars[g][1]
                matching = (xmin < preds_x) & (xmax > preds_x) & (ymin < preds_y) & (ymax > preds_y) & (
                        preds_label == label)
                if matching:
                    TP_gt_vn[g] = 1
            if TP_gt_vn[g] == 0:
                FN_gt_vn[g] = 1

        for g in range(len(sym_gt_chars)):
            pd = [pd for pd in dects if pd[0] == sym_gt_chars[g][0]]
            for j in range(len(pd)):
                # cal FN
                (preds_x, preds_y) = pd[j][3]
                (xmin, ymin, xmax, ymax) = sym_gt_chars[g][3]
                preds_label = pd[j][1]
                label = sym_gt_chars[g][1]
                matching = (xmin < preds_x) & (xmax > preds_x) & (ymin < preds_y) & (ymax > preds_y) & (
                        preds_label == label)
                if matching:
                    TP_gt_sym[g] = 1
            if TP_gt_sym[g] == 0:
                FN_gt_sym[g] = 1

        for g in range(len(alphabet_gt_chars)):
            pd = [pd for pd in dects if pd[0] == alphabet_gt_chars[g][0]]
            for j in range(len(pd)):
                # cal FN
                (preds_x, preds_y) = pd[j][3]
                (xmin, ymin, xmax, ymax) = alphabet_gt_chars[g][3]
                preds_label = pd[j][1]
                label = alphabet_gt_chars[g][1]
                matching = (xmin < preds_x) & (xmax > preds_x) & (ymin < preds_y) & (ymax > preds_y) & (
                        preds_label == label)
                if matching:
                    TP_gt_alp[g] = 1
            if TP_gt_alp[g] == 0:
                FN_gt_alp[g] = 1

        for g in range(len(number_gt_chars)):
            pd = [pd for pd in dects if pd[0] == number_gt_chars[g][0]]
            for j in range(len(pd)):
                # cal FN
                (preds_x, preds_y) = pd[j][3]
                (xmin, ymin, xmax, ymax) = number_gt_chars[g][3]
                preds_label = pd[j][1]
                label = number_gt_chars[g][1]
                matching = (xmin < preds_x) & (xmax > preds_x) & (ymin < preds_y) & (ymax > preds_y) & (
                        preds_label == label)
                if matching:
                    TP_gt_num[g] = 1
            if TP_gt_num[g] == 0:
                FN_gt_num[g] = 1

        r = {
            'TP_gt_vn': np.sum(TP_gt_vn),
            'FN_gt_vn': np.sum(FN_gt_vn),
            'TP_gt_alp': np.sum(TP_gt_alp),
            'FN_gt_alp': np.sum(FN_gt_alp),
            'TP_gt_sym': np.sum(TP_gt_sym),
            'FN_gt_sym': np.sum(FN_gt_sym),
            'TP_gt_num': np.sum(TP_gt_num),
            'FN_gt_num': np.sum(FN_gt_num)
        }
        return r

    def GetPascalVOCMetrics(self,
                            boundingboxes,
                            IOUThreshold=0.5,
                            method=MethodAveragePrecision.EveryPointInterpolation):
        """Get the metrics used by the VOC Pascal 2012 challenge.
        Get
        Args:
            boundingboxes: Object of the class BoundingBoxes representing ground truth and detected
            bounding boxes;
            IOUThreshold: IOU threshold indicating which detections will be considered TP or FP
            (default value = 0.5);
            method (default = EveryPointInterpolation): It can be calculated as the implementation
            in the official PASCAL VOC toolkit (EveryPointInterpolation), or applying the 11-point
            interpolatio as described in the paper "The PASCAL Visual Object Classes(VOC) Challenge"
            or EveryPointInterpolation"  (ElevenPointInterpolation);
        Returns:
            A list of dictionaries. Each dictionary contains information and metrics of each class.
            The keys of each dictionary are:
            dict['class']: class representing the current dictionary;
            dict['precision']: array with the precision values;
            dict['recall']: array with the recall values;
            dict['AP']: average precision;
            dict['interpolated precision']: interpolated precision values;
            dict['interpolated recall']: interpolated recall values;
            dict['total positives']: total number of ground truth positives;
            dict['total TP']: total number of True Positive detections;
            dict['total FP']: total number of False Negative detections;
        """
        ret = []  # list containing metrics (precision, recall, average precision) of each class
        # List with all ground truths (Ex: [imageName,class,confidence=1, (bb coordinates XYX2Y2)])
        groundTruths = []
        # List with all detections (Ex: [imageName,class,confidence,(bb coordinates XYX2Y2)])
        detections = []
        # Get all classes
        classes = []
        # Loop through all bounding boxes and separate them into GTs and detections
        for bb in boundingboxes.getBoundingBoxes():
            # [imageName, class, confidence, (bb coordinates XYX2Y2)]
            if bb.getBBType() == BBType.GroundTruth:
                groundTruths.append([
                    bb.getImageName(),
                    bb.getClassId(), 1,
                    bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                ])
            else:
                detections.append([
                    bb.getImageName(),
                    bb.getClassId(),
                    bb.getConfidence(),
                    bb.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
                ])
            # get class
            if bb.getClassId() not in classes:
                classes.append(bb.getClassId())
        classes = sorted(classes)
        # Precision x Recall is obtained individually by each class
        # Loop through by classes
        for c in classes:
            # Get only detection of class c
            dects = []
            [dects.append(d) for d in detections if d[1] == c]
            # Get only ground truths of class c
            gts = []
            [gts.append(g) for g in groundTruths if g[1] == c]
            npos = len(gts)
            # sort detections by decreasing confidence
            dects = sorted(dects, key=lambda conf: conf[2], reverse=True)
            TP = np.zeros(len(dects))
            FP = np.zeros(len(dects))
            # create dictionary with amount of gts for each image
            det = Counter([cc[0] for cc in gts])
            for key, val in det.items():
                det[key] = np.zeros(val)
            # print("Evaluating class: %s (%d detections)" % (str(c), len(dects)))
            # Loop through detections
            for d in range(len(dects)):
                # print('dect %s => %s' % (dects[d][0], dects[d][3],))
                # Find ground truth image
                gt = [gt for gt in gts if gt[0] == dects[d][0]]
                iouMax = sys.float_info.min
                for j in range(len(gt)):
                    # print('Ground truth gt => %s' % (gt[j][3],))
                    iou = Evaluator.iou(dects[d][3], gt[j][3])
                    if iou > iouMax:
                        iouMax = iou
                        jmax = j
                # Assign detection as true positive/don't care/false positive
                if iouMax >= IOUThreshold:
                    if det[dects[d][0]][jmax] == 0:
                        TP[d] = 1  # count as true positive
                        det[dects[d][0]][jmax] = 1  # flag as already 'seen'
                        # print("TP")
                    else:
                        FP[d] = 1  # count as false positive
                        # print("FP")
                # - A detected "cat" is overlaped with a GT "cat" with IOU >= IOUThreshold.
                else:
                    FP[d] = 1  # count as false positive
                    # print("FP")
            # compute precision, recall and average precision
            acc_FP = np.cumsum(FP)
            acc_TP = np.cumsum(TP)
            rec = acc_TP / npos
            prec = np.divide(acc_TP, (acc_FP + acc_TP))
            # Depending on the method, call the right implementation
            if method == MethodAveragePrecision.EveryPointInterpolation:
                [ap, mpre, mrec, ii] = Evaluator.CalculateAveragePrecision(rec, prec)
            else:
                [ap, mpre, mrec, _] = Evaluator.ElevenPointInterpolatedAP(rec, prec)
            # add class result in the dictionary to be returned
            r = {
                'class': c,
                'precision': prec,
                'recall': rec,
                'AP': ap,
                'interpolated precision': mpre,
                'interpolated recall': mrec,
                'total positives': npos,
                'total TP': np.sum(TP),
                'total FP': np.sum(FP)
            }
            ret.append(r)
        return ret

    def PlotPrecisionRecallCurve(self,
                                 boundingBoxes,
                                 IOUThreshold=0.5,
                                 method=MethodAveragePrecision.EveryPointInterpolation,
                                 showAP=False,
                                 showInterpolatedPrecision=False,
                                 savePath=None,
                                 showGraphic=False):
        """PlotPrecisionRecallCurve
        Plot the Precision x Recall curve for a given class.
        Args:
            boundingBoxes: Object of the class BoundingBoxes representing ground truth and detected
            bounding boxes;
            IOUThreshold (optional): IOU threshold indicating which detections will be considered
            TP or FP (default value = 0.5);
            method (default = EveryPointInterpolation): It can be calculated as the implementation
            in the official PASCAL VOC toolkit (EveryPointInterpolation), or applying the 11-point
            interpolatio as described in the paper "The PASCAL Visual Object Classes(VOC) Challenge"
            or EveryPointInterpolation"  (ElevenPointInterpolation).
            showAP (optional): if True, the average precision value will be shown in the title of
            the graph (default = False);
            showInterpolatedPrecision (optional): if True, it will show in the plot the interpolated
             precision (default = False);
            savePath (optional): if informed, the plot will be saved as an image in this path
            (ex: /home/mywork/ap.png) (default = None);
            showGraphic (optional): if True, the plot will be shown (default = True)
        Returns:
            A list of dictionaries. Each dictionary contains information and metrics of each class.
            The keys of each dictionary are:
            dict['class']: class representing the current dictionary;
            dict['precision']: array with the precision values;
            dict['recall']: array with the recall values;
            dict['AP']: average precision;
            dict['interpolated precision']: interpolated precision values;
            dict['interpolated recall']: interpolated recall values;
            dict['total positives']: total number of ground truth positives;
            dict['total TP']: total number of True Positive detections;
            dict['total FP']: total number of False Negative detections;
        """
        results = self.GetPascalVOCMetrics(boundingBoxes, IOUThreshold, method)
        result = None
        # Each resut represents a class
        for result in results:
            if result is None:
                raise IOError('Error: Class %d could not be found.' % classId)

            classId = result['class']
            precision = result['precision']
            recall = result['recall']
            average_precision = result['AP']
            mpre = result['interpolated precision']
            mrec = result['interpolated recall']
            npos = result['total positives']
            total_tp = result['total TP']
            total_fp = result['total FP']

            plt.close()
            if showInterpolatedPrecision:
                if method == MethodAveragePrecision.EveryPointInterpolation:
                    plt.plot(mrec, mpre, '--r', label='Interpolated precision (every point)')
                elif method == MethodAveragePrecision.ElevenPointInterpolation:
                    # Uncomment the line below if you want to plot the area
                    # plt.plot(mrec, mpre, 'or', label='11-point interpolated precision')
                    # Remove duplicates, getting only the highest precision of each recall value
                    nrec = []
                    nprec = []
                    for idx in range(len(mrec)):
                        r = mrec[idx]
                        if r not in nrec:
                            idxEq = np.argwhere(mrec == r)
                            nrec.append(r)
                            nprec.append(max([mpre[int(id)] for id in idxEq]))
                    plt.plot(nrec, nprec, 'or', label='11-point interpolated precision')
            plt.plot(recall, precision, label='Precision')
            plt.xlabel('recall')
            plt.ylabel('precision')
            if showAP:
                ap_str = "{0:.2f}%".format(average_precision * 100)
                # ap_str = "{0:.4f}%".format(average_precision * 100)
                plt.title('Precision x Recall curve \nClass: %s, AP: %s' % (str(classId), ap_str))
            else:
                plt.title('Precision x Recall curve \nClass: %s' % str(classId))
            plt.legend(shadow=True)
            plt.grid()
            if savePath is not None:
                try:
                    plt.savefig(os.path.join(savePath, classId + '.png'))
                except OSError:
                    continue

            if showGraphic is True:
                plt.show()
                plt.waitforbuttonpress()
                plt.pause(0.05)
        return results

    @staticmethod
    def CalculateAveragePrecision(rec, prec):
        mrec = []
        mrec.append(0)
        [mrec.append(e) for e in rec]
        mrec.append(1)
        mpre = []
        mpre.append(0)
        [mpre.append(e) for e in prec]
        mpre.append(0)
        for i in range(len(mpre) - 1, 0, -1):
            mpre[i - 1] = max(mpre[i - 1], mpre[i])
        ii = []
        for i in range(len(mrec) - 1):
            if mrec[1:][i] != mrec[0:-1][i]:
                ii.append(i + 1)
        ap = 0
        for i in ii:
            ap = ap + np.sum((mrec[i] - mrec[i - 1]) * mpre[i])
        # return [ap, mpre[1:len(mpre)-1], mrec[1:len(mpre)-1], ii]
        return [ap, mpre[0:len(mpre) - 1], mrec[0:len(mpre) - 1], ii]

    @staticmethod
    # 11-point interpolated average precision
    def ElevenPointInterpolatedAP(rec, prec):
        # def CalculateAveragePrecision2(rec, prec):
        mrec = []
        # mrec.append(0)
        [mrec.append(e) for e in rec]
        # mrec.append(1)
        mpre = []
        # mpre.append(0)
        [mpre.append(e) for e in prec]
        # mpre.append(0)
        recallValues = np.linspace(0, 1, 11)
        recallValues = list(recallValues[::-1])
        rhoInterp = []
        recallValid = []
        # For each recallValues (0, 0.1, 0.2, ... , 1)
        for r in recallValues:
            # Obtain all recall values higher or equal than r
            argGreaterRecalls = np.argwhere(mrec[:] >= r)
            pmax = 0
            # If there are recalls above r
            if argGreaterRecalls.size != 0:
                pmax = max(mpre[argGreaterRecalls.min():])
            recallValid.append(r)
            rhoInterp.append(pmax)
        # By definition AP = sum(max(precision whose recall is above r))/11
        ap = sum(rhoInterp) / 11
        # Generating values for the plot
        rvals = []
        rvals.append(recallValid[0])
        [rvals.append(e) for e in recallValid]
        rvals.append(0)
        pvals = []
        pvals.append(0)
        [pvals.append(e) for e in rhoInterp]
        pvals.append(0)
        # rhoInterp = rhoInterp[::-1]
        cc = []
        for i in range(len(rvals)):
            p = (rvals[i], pvals[i - 1])
            if p not in cc:
                cc.append(p)
            p = (rvals[i], pvals[i])
            if p not in cc:
                cc.append(p)
        recallValues = [i[0] for i in cc]
        rhoInterp = [i[1] for i in cc]
        return [ap, rhoInterp, recallValues, None]

    # For each detections, calculate IOU with reference
    @staticmethod
    def _getAllIOUs(reference, detections):
        ret = []
        bbReference = reference.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
        # img = np.zeros((200,200,3), np.uint8)
        for d in detections:
            bb = d.getAbsoluteBoundingBox(BBFormat.XYX2Y2)
            iou = Evaluator.iou(bbReference, bb)
            # Show blank image with the bounding boxes
            # img = add_bb_into_image(img, d, color=(255,0,0), thickness=2, label=None)
            # img = add_bb_into_image(img, reference, color=(0,255,0), thickness=2, label=None)
            ret.append((iou, reference, d))  # iou, reference, detection
        # cv2.imshow("comparing",img)
        # cv2.waitKey(0)
        # cv2.destroyWindow("comparing")
        return sorted(ret, key=lambda i: i[0], reverse=True)  # sort by iou (from highest to lowest)

    @staticmethod
    def iou(boxA, boxB):
        # if boxes dont intersect
        if Evaluator._boxesIntersect(boxA, boxB) is False:
            return 0
        interArea = Evaluator._getIntersectionArea(boxA, boxB)
        union = Evaluator._getUnionAreas(boxA, boxB, interArea=interArea)
        # intersection over union
        iou = interArea / union
        assert iou >= 0
        return iou

    # boxA = (Ax1,Ay1,Ax2,Ay2)
    # boxB = (Bx1,By1,Bx2,By2)
    @staticmethod
    def _boxesIntersect(boxA, boxB):
        if boxA[0] > boxB[2]:
            return False  # boxA is right of boxB
        if boxB[0] > boxA[2]:
            return False  # boxA is left of boxB
        if boxA[3] < boxB[1]:
            return False  # boxA is above boxB
        if boxA[1] > boxB[3]:
            return False  # boxA is below boxB
        return True

    @staticmethod
    def _getIntersectionArea(boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        # intersection area
        return (xB - xA + 1) * (yB - yA + 1)

    @staticmethod
    def _getUnionAreas(boxA, boxB, interArea=None):
        area_A = Evaluator._getArea(boxA)
        area_B = Evaluator._getArea(boxB)
        if interArea is None:
            interArea = Evaluator._getIntersectionArea(boxA, boxB)
        return float(area_A + area_B - interArea)

    @staticmethod
    def _getArea(box):
        return (box[2] - box[0] + 1) * (box[3] - box[1] + 1)