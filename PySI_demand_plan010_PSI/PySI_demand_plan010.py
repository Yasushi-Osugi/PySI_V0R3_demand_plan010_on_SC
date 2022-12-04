# coding: utf-8
#
#
#            Copyright (C) 2020 Yasushi Ohsugi
#            Copyright (C) 2021 Yasushi Ohsugi
#            Copyright (C) 2022 Yasushi Ohsugi
#
#            license follows MIT license
#


# PySI_demand_plan010.py
#
# ******************************
# PSIの複数年N_year対応とDataframeとCSV fileによるI/O処理
# ******************************
#

import numpy as np
import matplotlib.pyplot as plt

#  # メモリ解放
#  import gc
#  del tmp_data
#  del bulk
#  gc.collect()

# ******************************
# PySI related module
# ******************************
from PySILib.PySI_library_V0R1_070 import *

from PySILib.PySI_env_V0R3_1 import *

from PySILib.PySI_PlanLot_V0R3_2 import *

from PySILib.PySI_search_LEAF_in_SCMTREE_V0R3 import *


# **********************************
# 複数年の週ツナギの考え方
# **********************************
#
# 1. year属性の追加
# Arv_weekの前に該当年のYYYYをセット
# Dpt_weekの前に該当年のYYYYをセット
#
# 2. マイナス週を前年で表現 write_CPUの中で変換
#    CPU:Common Plan Unitの略称
# ゼロ週(2023年0週)は、前年(2022年)の52週
# マイナス週(2023年 - W週)は、前年(2022年)の(52-W)週
#
# common_plan_unitへの書き出し、読み出しで上記をルールでI/Oする。

# [[-7, 15], [-6, 28], [-5, 31], [-4, 1], [-3, 22], [-2, 6], [-1, 0], [2, 0], 
# [3, 15], [4, 10], [6, 0], [8, 10], [9, 28], [10, 3], [11, 55], [12, 28], 
# [13, 28], [14, 114], [15, 54], [16, 48], [18, 210], [19, 92], [20, 55], 
# [21, 157], [22, 46], [23, 579], [24, 31], [25, 174], [26, 1], [27, 297], 
# [28, 3], [29, 45], [30, 0], [31, 0], [32, 55], [33, 6], [34, 21], 
# [36, 66], [37, 56], [38, 0], [40, 6], [41, 15], [42, 1], [44, 0], [45, 0]]


# 3. 上記の1と2より、CPU生成の行出力make_rawで変換してCPU.csvとしている
#    # **************************
#    #ETD_year
#    # **************************
#    ETD_week = week_no - i_PlanSpace.LT_boat    # 年の判定のために事前に計算
#
#    if ETD_week > 0:
#        ETD_year = i_PlanSpace.year
#    else:
#        ETD_year = i_PlanSpace.year - 1 # 前年をセット
#        ETD_week += 52                  # 前年週+52に変換
#
#    r.append(ETD_year)                           # ETD from_year
#    r.append(ETD_week)                           # ETD from_week_no



# **********************************
# <前提>  LT OFFSETした後、前年に割り出した週の「年週の補正」済みでCPU書出
#
# 1. "year"+"node"でリスト抽出するだけで良いが、
# 2. PSI_data_Sリストの生成のためには、欠番週を0で補完する必要がある。
# **********************************
def read_common_plan_unit_N( file_name, node, year ):

    df = pd.read_csv('common_plan_unit.csv')

    df_n_y = df.query("Dpt_year == @year & Dpt_entity == @node")

    #print('df_node_year in CPU ', df_n_y, node, year)
    

    # **************************
    # "step"は一ロット単位を表す要求元のシリアル番号
    # **************************

    # 出荷週をキーに、ロット数をcount、各ロットのValueを合計
    Dpt_S_V = df_n_y[['Dpt_week','Dpt_step','Value']].groupby('Dpt_week').agg(      {'Dpt_step':['count'], 'Value':['sum'] } )

    Dpt_S = df_n_y[['Dpt_week','Dpt_step']].groupby('Dpt_week').count()

    # ここで加算するのは、ロットの個数なので、sum()ではなく、count()
    #Dpt_S = df_n_y[['Dpt_week','Dpt_step']].groupby('Dpt_week').sum()
    
    #print('Dpt_S_V',Dpt_S_V)
    
    
    common_plan_S    = Dpt_S.reset_index().values.tolist()
    common_plan_S_V  = Dpt_S_V.reset_index().values.tolist()
    
    ####print('common_plan_S_V',common_plan_S_V)
    
####common_plan_S_V [[1.0, 27.0, 165.29999999999987], [2.0, 3.0, 77.96666666666664], [3.0, 5.0, 42.39999999999998], [4.0, 3.0, 117.2999999999999], [5.0, 25.0, 208.4666666666667], [6.0, 7.0, 175.46666666666678], [7.0, 4.0, 76.56666666666672], [8.0, 2.0, 0.0], [9.0, 4.0, 32.433333333333394], [10.0, 32.0, 225.2666666666666], [11.0, 7.0, 168.3666666666667], [12.0, 4.0, 94.06666666666655], [15.0, 30.0, 256.13333333333316], [16.0, 8.0, 121.96666666666653], [17.0, 7.0, 125.63333333333344], [18.0, 31.0, 279.5333333333332], [19.0, 17.0, 359.5], [20.0, 4.0, 45.266666666666666], [21.0, 3.0, 29.06666666666661], [22.0, 2.0, 19.466666666666683], [23.0, 40.0, 309.7666666666667], [24.0, 10.0, 196.3666666666667], [25.0, 3.0, 21.100000000000016], [26.0, 4.0, 32.800000000000004], [27.0, 32.0, 89.53333333333335], [29.0, 2.0, 36.00000000000001], [30.0, 10.0, 30.33333333333333], [31.0, 32.0, 59.46666666666667], [32.0, 2.0, 0.0], [33.0, 1.0, 0.0], [34.0, 1.0, 0.0], [35.0, 4.0, 0.0], [36.0, 33.0, 4.0], [37.0, 4.0, 0.0], [38.0, 2.0, 0.0], [39.0, 1.0, 0.0], [40.0, 32.0, 0.0], [41.0, 1.0, 0.0], [42.0, 1.0, 0.0], [44.0, 25.0, 0.0], [45.0, 4.0, 0.0], [46.0, 2.0, 0.0], [48.0, 3.0, 0.0]]



# <前提>  LT OFFSETした後、前年に割り出した週の「年週の補正」済み
#
# [[2, 0], [3, 15], [4, 10], [6, 0], [8, 10], 
# [9, 28], [10, 3], [11, 55], [12, 28], 
# [13, 28], [14, 114], [15, 54], [16, 48], [18, 210], [19, 92], [20, 55], 
# [21, 157], [22, 46], [23, 579], [24, 31], [25, 174], [26, 1], [27, 297], 
# [28, 3], [29, 45], [30, 0], [31, 0], [32, 55], [33, 6], [34, 21], 
# [36, 66], [37, 56], [38, 0], [40, 6], [41, 15], [42, 1], [44, 0], [45, 0]]


    ## ココは、複数年に対応する前の単年度処理の古いコメント
    ## *********************
    ##@220215 commomn_plan_Sの check and remake
    ## *********************
    ## 1. temporary solutionとしてW0以前のSは、W0にすべて集計する。
    ## 2. 欠番の週がある場合には、0で追加する。
    

# **********************************
# 複数年の週ツナギの考え方@221010
# **********************************
#
# Arv_weekの前に該当年のYYYYをセット
# Dpt_weekの前に該当年のYYYYをセット
# ゼロ週(2023年0週)は、前年(2022年)の52週
# マイナス週(2023年 - W週)は、前年(2022年)の(52-W)週

    common_plan_SX          = []
    element_SX              = [0,0]
    
    # ***********************************************
    
    i = 0
    
    # ***********************************************
    # 欠番週の穴埋め
    # ***********************************************

    # ***********************************************
    # 事前に range(0,54)までの[0,0],[1,0],[2,0],,,[53,0]リストを初期セット
    # ***********************************************
    element_SX =[]

    for i in range(0,54):

        element_SX.append([i,0])    # [0,0],[1,0],[2,0],,,[53,0]リスト


    week_no = 0


    # ***********************************************
    # common_plan_Sの要素[week_no, lot_count]から該当週にcopy、穴埋めになる
    # ***********************************************
    for element_S in common_plan_S:
        
        week_no = element_S[0]

        element_SX[ week_no ][1] = element_S[1]


    PSI_data_S = []
    PSI_data_S = element_SX

    #PSI_data_S = common_plan_SX

    return PSI_data_S
    # **********************************
    # end of reading 'common_plan_unit.csv'
    # **********************************



# **********************************
# OLD
# **********************************
def read_common_plan_unit( file_name, node ):

    # **********************************
    # start of reading 'common_plan_unit.csv'
    # **********************************
    
    df = pd.read_csv('common_plan_unit.csv')
    #df = pd.read_csv('common_plan_unit.csv',encoding='shift-jis',sep=',')
    
    #print(df)

    # 'Dpt_entity == @node '

    df_node = df.query( 'Dpt_entity == @node ' )

    #print('df_node in CPU ', df_node,node)
    
    # **************************
    # "step"は一ロット単位を表す要求元のシリアル番号
    # ここで加算するのは、ロットの個数なので、sum()ではなく、count()
    # **************************
    Dpt_S = df_node[['Dpt_week','Dpt_step']].groupby('Dpt_week').count()

    # monitor
    #print('Dpt_S',Dpt_S)
    
    
    #Dpt_S_list = Dpt_S.values.tolist()
    #print(Dpt_S_list)
    
    common_plan_S = Dpt_S.reset_index().values.tolist()
    
    # monitor
    #print('common_plan_S',common_plan_S)
    
    # [[-7, 15], [-6, 28], [-5, 31], [-4, 1], [-3, 22], [-2, 6], [-1, 0], [2, 0], 
    # [3, 15], [4, 10], [6, 0], [8, 10], [9, 28], [10, 3], [11, 55], [12, 28], 
    # [13, 28], [14, 114], [15, 54], [16, 48], [18, 210], [19, 92], [20, 55], 
    # [21, 157], [22, 46], [23, 579], [24, 31], [25, 174], [26, 1], [27, 297], 
    # [28, 3], [29, 45], [30, 0], [31, 0], [32, 55], [33, 6], [34, 21], 
    # [36, 66], [37, 56], [38, 0], [40, 6], [41, 15], [42, 1], [44, 0], [45, 0]]
    
    
    
    # *********************
    #@220215 commomn_plan_Sの check and remake
    # *********************
    # 1. temporary solutionとしてW0以前のSは、W0にすべて集計する。
    # 2. 欠番の週がある場合には、0で追加する。
    
    common_plan_SX = []
    element_SX = [0,0]
    
    
    # ***********************************************
    
    i = 0
    
    for element_S in common_plan_S:
    
        if element_S[0] <= i :
    
            element_SX[1] += element_S[1]
    
        else:
    
            break
    
    common_plan_SX.append(element_SX)
    
    # ***********************************************
    
    for i in range( 1,54 ):
    
        element_SX = [0,0]
    
        for element_S in common_plan_S:
        
            if element_S[0] < i :
    
                continue
    
            elif element_S[0] == i :
    
                element_SX[0] =  i
                element_SX[1] += element_S[1]
    
                common_plan_SX.append(element_SX)
    
                break
    
            else:
    
                element_SX[0] =  i
                element_SX[1] += 0
    
                common_plan_SX.append(element_SX)
    
                break
    
    # ***********************************************
    
    # monitor
    #print(common_plan_SX)
    
    # ***********************************************
    # range(0,54)の54に対応できるようにcommon_plan_SXの長さ=54に補正する。
    # ***********************************************
    
    check_len = len(common_plan_SX)
    
    # monitor
    #print(check_len)
    
    element_SX = [0,0]
    
    if check_len < 54 :
    
        for i in range(check_len,54):
    
            #print(i)
    
            element_SX[0] = i
            element_SX[1] = 0
    
            #print('before SX',element_SX,common_plan_SX)
    
            common_plan_SX.append(element_SX)
    
            #print('after  SX',element_SX,common_plan_SX)
    
            element_SX = [0,0]  #ココで明示的に0クリアしないと最後の値=53が入る
    
    #print(common_plan_SX)


    PSI_data_S = []
    PSI_data_S = common_plan_SX

    return PSI_data_S
    # **********************************
    # end of reading 'common_plan_unit.csv'
    # **********************************




# ******************************
# 複数年 NOLEAFの場合　PSI_data_file読み込み 
# ******************************
#
# leaf_node PSIでcommon_plan_unit.csvに"year"+"value"を付加し出力した後
#

#
# ココは、"year"+"node_to"の条件検索なのでdfに任せる@221006
#
def get_no_leaf_PSI_DB( df, PSI_L, year, node):

    #### コレを置き換え
    # PSI_data_current = read_PSI_data_csv( PSI_data_file_name )

# nodeはSCM tree のchild_nodeを指定

    PSI_data_current = [] #return用にリスト型を宣言


# ******************************
# NOLEAFの時も、まずは、PSI_DB_dataのdfを読んでPSI_dataのリストを作っておく。
# ******************************

    #*#*
    #* ココは、indexだけdfから持ってきて、
    #* そのindexでPSI_LISTの値を使うところ@221008

    PSI_data_current = [] #return用にリスト型を宣言

    # *********************************
    # PSI_DBのdataframeから、変数@year+@nodeで検索して、psiの行数indexを入手
    # *********************************
    psi_index = df.query("year == @year & node_to == @node").index.tolist()


    for ind in psi_index:

        l = PSI_LIST[ind]

        PSI_data_current.append( l )

        # monitor
        #print('after no_leaf year+node query PSI_DB_data',year, node, l)


# ******************************
# 次に、'common_plan_unit.csv'を読んでPSI_dataの'S'作る
# ******************************

#
# 共通計画単位common_plan_unit.csvは、nodeの上のディレクトリにある
#
    file_name = "common_plan_unit.csv" 

    PSI_data_S = [] #return用にリスト型を宣言

    PSI_data_S = read_common_plan_unit_N( file_name, node, year )
    #PSI_data_S = read_common_plan_unit( file_name, node )

    #print('NOLEAF PSI_data_S',PSI_data_S) 


# ******************************
# PSI_data_current[0][5:]    PSI_dataの'1S' のW0-W53に
# common_plan_unitのS        PSI_data_SのW0-W53     をセットする
# ******************************

# image #
# PSI_data_S [[0, 20], [1, 6], [2, 6], [3, 3], [4, 1], [5, 1], [6, 1], [7, 3], [8, 3], [9, 3], [10, 1], [11, 1], [12, 10], [13, 6], [14, 6], [15, 6], [16, 0], [17, 21], [18, 21], [19, 15], [20, 10], [21, 10], [22, 10], [23, 6], [24, 6], [25, 28], [26, 28], [27, 28], [28, 28], [29, 55], [30, 0], [31, 55], [32, 55], [33, 10], [34, 10], [35, 6], [36, 6], [37, 6], [38, 28], [39, 28], [40, 28], [41, 21], [42, 0], [43, 0], [44, 0], [45, 0], [46, 0], [47, 0], [48, 0], [49, 0], [50, 0], [51, 0], [52, 0], [53, 0]]


#@221011

#common_plan_S [[1, 3], [2, 1], [3, 4], [4, 1], [5, 3], [6, 7], [7, 2], [8, 1], [10, 7], [11, 1], [12, 7], [13, 2], [15, 5], [16, 11], [17, 4], [18, 6], [19, 8], [20, 5], [21, 4], [23, 15], [24, 6], [25, 13], [26, 1], [27, 14], [29, 13], [30, 6], [31, 5], [32, 9], [33, 5], [34, 3], [36, 6], [37, 8], [38, 7], [39, 2], [40, 11], [41, 1], [43, 2], [44, 1], [49, 3], [50, 5], [51, 2], [52, 2]]

#NOLEAF PSI_data_S@220930 [[0, 0], 3, 1, 4, 1, 3, 7, 2, 1, [9, 0], 7, 1, 7, 2, [14, 0], 5, 11, 4, 6, 8, 5, 4, [22, 0], 15, 6, 13, 1, 14, [28, 0], 13, 6, 5, 9, 5, 3, [35, 0], 6, 8, 7, 2, 11, 1, [42, 0], 2, 1, [45, 0], [46, 0], [47, 0], [48, 0], 3, 5, 2, 2, [53, 0]]

#PSI_data_S [[0, 0], 3, 1, 4, 1, 3, 7, 2, 1, [9, 0], 7, 1, 7, 2, [14, 0], 5, 11, 4, 6, 8, 5, 4, [22, 0], 15, 6, 13, 1, 14, [28, 0], 13, 6, 5, 9, 5, 3, [35, 0], 6, 8, 7, 2, 11, 1, [42, 0], 2, 1, [45, 0], [46, 0], [47, 0], [48, 0], 3, 5, 2, 2, [53, 0]]



    S_cpu_year = []

    for s in PSI_data_S :

        S_cpu_year.append( s[1] )
    

    #print('NOLEAF S_cpu_year @#@#',S_cpu_year) 

    PSI_data_current[0][7:] = S_cpu_year   #### W0,W1,W2,,,,W52,W53

    #print('NOLEAF PSI_data_current @#@#',PSI_data_current) 


    return PSI_data_current


# ******************************
# 複数年のLEAFの場合　PSI_DB読み込み 
# ******************************

#
# ココは、"year"+"node_to"の条件検索なのでdfに任せる
#
def get_leaf_PSI_DB( df, PSI_LIST, year, node ):

# nodeはSCM tree のchild_nodeを指定
#
#@#@ PSI_DB_CSV_readを初期処理に置く　ココでは、dfをget&putする
#
# 'node_to'&'year'でPSI_DBを検索


    PSI_DB_data = [] #return用にリスト型を宣言

    #
    # PSI_DBのdataframeから、変数@year+@nodeで検索して、psiの行数indexを入手
    #
    psi_index = df.query("year == @year & node_to == @node").index.tolist()


    for ind in psi_index:

        l = PSI_LIST[ind]

        PSI_DB_data.append( l )

        # monitor
        #print('after year+node query PSI_DB_data',year, node, l)
        # LEAFの時、Sが入ってくる

    return PSI_DB_data


# *******************************
# df_psi_db のdump image
# *******************************

#行数は連番に変更し、"year"を付加している。
#df_psi_db_new          prod_name scm_id node_from  node_to  year  SIP  W00  W01  W02  W03  \
#0  prod56789012345  sc010       YTO  YTOLEAF  2023   1S    2   50   30   30   
#1  prod56789012345  sc010       YTO  YTOLEAF  2023  2CO    0    2    0    0   
#2  prod56789012345  sc010       YTO  YTOLEAF  2023   3I    0    0   98  218   
#3  prod56789012345  sc010       YTO  YTOLEAF  2023   4P    0  150  150   90   
#4  prod56789012345  sc010       YTO  YTOLEAF  2023  5IP    0   -2   98  218   
#0  prod56789012345  sc010       YTO  YTOLEAF  2024   1S    2   50   30   30   
#1  prod56789012345  sc010       YTO  YTOLEAF  2024  2CO    0    2    0    0   
#2  prod56789012345  sc010       YTO  YTOLEAF  2024   3I    0    0   98  218   
#3  prod56789012345  sc010       YTO  YTOLEAF  2024   4P    0  150  150   90   
#4  prod56789012345  sc010       YTO  YTOLEAF  2024  5IP    0   -2   98  218   
#0  prod56789012345  sc010       YTO  YTOLEAF  2025   1S    2   50   30   30   
#1  prod56789012345  sc010       YTO  YTOLEAF  2025  2CO    0    2    0    0   
#2  prod56789012345  sc010       YTO  YTOLEAF  2025   3I    0    0   98  218   
#3  prod56789012345  sc010       YTO  YTOLEAF  2025   4P    0  150  150   90   
#4  prod56789012345  sc010       YTO  YTOLEAF  2025  5IP    0   -2   98  218   
#0  prod56789012345  sc010       YTO  YTOLEAF  2026   1S    2   50   30   30   
#1  prod56789012345  sc010       YTO  YTOLEAF  2026  2CO    0    2    0    0   
#2  prod56789012345  sc010       YTO  YTOLEAF  2026   3I    0    0   98  218   
#3  prod56789012345  sc010       YTO  YTOLEAF  2026   4P    0  150  150   90   
#4  prod56789012345  sc010       YTO  YTOLEAF  2026  5IP    0   -2   98  218   


# OLD
# ******************************
# 単年 LEAFの場合　PSI_data_file読み込み 
# ******************************
def set_leaf_PSI_data(node):

# nodeはSCM tree のchild_nodeを指定

    PSI_data_file_name = ".\\node_all\\" + node + "\\PySI_data_std_IO.csv" 
    #PSI_data_file_name = ".\\" + node + "\\PySI_data_std_IO.csv" 
    # PSI data IOファイル名を宣言

    #print('PSI_data_file_name@input@LEAF',PSI_data_file_name)

    PSI_data = [] #return用にリスト型を宣言
    PSI_data = read_PSI_data_csv( PSI_data_file_name )

    #print('PSI_data',PSI_data) # LEAFの時、Sが入ってくる

    return PSI_data


# OLD
# ******************************
# 単年 NOLEAFの場合　PSI_data_file読み込み 
# ******************************
def set_no_leaf_PSI_data(node):

# nodeはSCM tree のchild_nodeを指定

    PSI_data = [] #return用にリスト型を宣言

# nodeはSCM tree のchild_nodeを指定


# ******************************
# NOLEAFの時も、まずは、PSI_data_file読んでPSI_dataのリストを作っておく。
# ******************************
    PSI_data_file_name = ".\\node_all\\" + node + "\\PySI_data_std_IO.csv" 

    PSI_data_current = [] #return用にリスト型を宣言

    PSI_data_current = read_PSI_data_csv( PSI_data_file_name )

    #print('PSI_data@NOLEAF',PSI_data_current) 


# ******************************
# 次に、'common_plan_unit.csv'を読んでPSI_dataの'S'作る
# ******************************

#
# 共通計画単位common_plan_unit.csvは、nodeの上のディレクトリにある
#
    file_name = "common_plan_unit.csv" 

    PSI_data_S = [] #return用にリスト型を宣言

    PSI_data_S = read_common_plan_unit_N( file_name, node, year )
    #PSI_data_S = read_common_plan_unit( file_name, node )

    #print('NOLEAF PSI_data_S@220630',PSI_data_S) 


# ******************************
# PSI_data_current[0][5:]    PSI_dataの'1S' のW0-W53に
# common_plan_unitのS        PSI_data_SのW0-W53     をセットする
# ******************************

    #print('PSI_data_S',PSI_data_S)

# image #
# PSI_data_S [[0, 20], [1, 6], [2, 6], [3, 3], [4, 1], [5, 1], [6, 1], [7, 3], [8, 3], [9, 3], [10, 1], [11, 1], [12, 10], [13, 6], [14, 6], [15, 6], [16, 0], [17, 21], [18, 21], [19, 15], [20, 10], [21, 10], [22, 10], [23, 6], [24, 6], [25, 28], [26, 28], [27, 28], [28, 28], [29, 55], [30, 0], [31, 55], [32, 55], [33, 10], [34, 10], [35, 6], [36, 6], [37, 6], [38, 28], [39, 28], [40, 28], [41, 21], [42, 0], [43, 0], [44, 0], [45, 0], [46, 0], [47, 0], [48, 0], [49, 0], [50, 0], [51, 0], [52, 0], [53, 0]]

    S_cpu_year = []

    for s in PSI_data_S :

        S_cpu_year.append( s[1] )
    
    PSI_data_current[0][5:] = S_cpu_year   #### W0,W1,W2,,,,W52,W53

    return PSI_data_current

# ************************************
# PSI_data image
# ************************************
#PSI_data [
#['TEST-PROD010', 'OD010', 'YTO', 'YTOLEAF', '1S', 0, 213, 213, 213, 213, 229, 236, 236, 236, 219, 213, 213, 213, 215, 220, 220, 220, 220, 213, 213, 213, 213, 217, 220, 220, 220, 218, 213, 213, 213, 213, 213, 213, 213, 213, 216, 220, 220, 220, 219, 213, 213, 213, 213, 218, 220, 220, 220, 217, 213, 213, 213, 213, 0], 
#['TEST-PROD010', 'OD010', 'YTO', 'YTOLEAF', '2CO', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
# ['TEST-PROD010', 'OD010', 'YTO', 'YTOLEAF', '3I', 0, 0, 237, 624, 771, 678, 779, 723, 847, 701, 752, 1079, 1046, 863, 678, 788, 808, 888, 698, 485, 692, 809, 686, 829, 939, 1049, 889, 701, 758, 755, 782, 569, 746, 533, 770, 557, 641, 781, 741, 521, 362, 1469, 1856, 2033, 1970, 1782, 1562, 1342, 1122, 905, 692, 509, 296, 83],
# ['TEST-PROD010', 'OD010', 'YTO', 'YTOLEAF', '4P', 0, 450, 600, 360, 120, 330, 180, 360, 90, 270, 540, 180, 30, 30, 330, 240, 300, 30, 0, 420, 330, 90, 360, 330, 330, 60, 30, 270, 210, 240, 0, 390, 0, 450, 0, 300, 360, 180, 0, 60, 1320, 600, 390, 150, 30, 0, 0, 0, 0, 0, 30, 0, 0, 0],
# ['TEST-PROD010', 'OD010', 'YTO', 'YTOLEAF', '5IP', 0, 0, 237, 624, 771, 678, 779, 723, 847, 701, 752, 1079, 1046, 863, 678, 788, 808, 888, 698, 485, 692, 809, 686, 829, 939, 1049, 889, 701, 758, 755, 782, 569, 746, 533, 770, 557, 641, 781, 741, 521, 362, 1469, 1856, 2033, 1970, 1782, 1562, 1342, 1122, 905, 692, 509, 296, 83]]




# ******************************
# 複数年用PSIのinput処理  @220917 'year'+'node'を追加したDataframeを更新@220924
# ******************************

def input_Y(df, PSI_LIST, year, node, isleaf):

    #print('monitor node is leaf', year, node, isleaf)

    # ******************************
    # PSI_data_file読み込み LEAF判定
    # ******************************

    PSI_data = [] #return用にリスト型を宣言

    # *******************************
    # df_psi_db のdump image
    # *******************************

#行数は連番に変更し、"year"を付加している。
#df_psi    Unnamed: 0        prod_name scm_id node_from  node_to  year  SIP  W00  ...  W46  W47  W48  W49  W50  W51  W52  W53
#5          10  prod56789012345  sc010       YTO  YTOLEAF  2024   1S    2  ...  100  100   10   10   10   10   10   10
#6          11  prod56789012345  sc010       YTO  YTOLEAF  2024  2CO    0  ...    0    0    0    0    0    0    0    0
#7          12  prod56789012345  sc010       YTO  YTOLEAF  2024   3I    0  ...  284  184   84  104   94   84   74   64
#8          13  prod56789012345  sc010       YTO  YTOLEAF  2024   4P    0  ...    0    0   30    0    0    0    0    0
#9          14  prod56789012345  sc010       YTO  YTOLEAF  2024  5IP    0  ...  284  184   84  104   94   84   74   64


#df_psi_db_new          prod_name scm_id node_from  node_to  year  SIP  W00  W01  W02  W03  \
#0  prod56789012345  sc010       YTO  YTOLEAF  2023   1S    2   50   30   30   
#1  prod56789012345  sc010       YTO  YTOLEAF  2023  2CO    0    2    0    0   
#2  prod56789012345  sc010       YTO  YTOLEAF  2023   3I    0    0   98  218   
#3  prod56789012345  sc010       YTO  YTOLEAF  2023   4P    0  150  150   90   
#4  prod56789012345  sc010       YTO  YTOLEAF  2023  5IP    0   -2   98  218   
#0  prod56789012345  sc010       YTO  YTOLEAF  2024   1S    2   50   30   30   
#1  prod56789012345  sc010       YTO  YTOLEAF  2024  2CO    0    2    0    0   
#2  prod56789012345  sc010       YTO  YTOLEAF  2024   3I    0    0   98  218   
#3  prod56789012345  sc010       YTO  YTOLEAF  2024   4P    0  150  150   90   
#4  prod56789012345  sc010       YTO  YTOLEAF  2024  5IP    0   -2   98  218   
#0  prod56789012345  sc010       YTO  YTOLEAF  2025   1S    2   50   30   30   
#1  prod56789012345  sc010       YTO  YTOLEAF  2025  2CO    0    2    0    0   
#2  prod56789012345  sc010       YTO  YTOLEAF  2025   3I    0    0   98  218   
#3  prod56789012345  sc010       YTO  YTOLEAF  2025   4P    0  150  150   90   
#4  prod56789012345  sc010       YTO  YTOLEAF  2025  5IP    0   -2   98  218   
#0  prod56789012345  sc010       YTO  YTOLEAF  2026   1S    2   50   30   30   
#1  prod56789012345  sc010       YTO  YTOLEAF  2026  2CO    0    2    0    0   
#2  prod56789012345  sc010       YTO  YTOLEAF  2026   3I    0    0   98  218   
#3  prod56789012345  sc010       YTO  YTOLEAF  2026   4P    0  150  150   90   
#4  prod56789012345  sc010       YTO  YTOLEAF  2026  5IP    0   -2   98  218   


    if isleaf == "LEAF":

        PSI_DB_data = get_leaf_PSI_DB( df, PSI_LIST, year, node )
        #PSI_DB_data = set_leaf_PSI_DB( year, node )

        #PSI_data[:] = PSI_DB_data[:][2:]
        #del PSI_data[0] # 先頭の'year'を削除して使う


        PSI_data = []
        psi_index = []

        for l in PSI_DB_data:
            PSI_data.append(l[2:])
            psi_index.append(l[0])

        # LEAFの時、Sが入ってくる
        #print('PSI_data 2 slices from PSI_DB',PSI_data) 


    elif isleaf == "NOLEAF":

        PSI_DB_data = get_no_leaf_PSI_DB( df, PSI_LIST, year, node )
        #PSI_DB_data = set_no_leaf_PSI_DB( year, node )

        PSI_data  = []
        psi_index = []

        for l in PSI_DB_data:
            PSI_data.append(l[2:])
            psi_index.append(l[0])

    else:

        print('isleaf flag error: LEAF or NOLEAF should be defined')


    return PSI_data, psi_index


# OLD
# ******************************
# 単年用PSIのinput処理
# ******************************
def input(node,isleaf):

    #print('monitor node is leaf',node,isleaf)


# ******************************
# profile読込み  
# ******************************
# reading "PySI_Profile_std.csv"
# setting planning parameters
#
# Plan_engine = "ML" or "FS" , cost marameters, planning one and so on
# ML:Machine Learning  FS:Fixed Sequence/Normal PSI

    profile_name = ".\\node_all\\"+node+"\\PySI_Profile_std.csv" 
    #プロファイル名を宣言

#    #file_path = ' .\\' + node+ '\\PySI_Profile_std.csv' ### nodeの下
#
#    dir_name  = node + '\\PySI_Profile_std.csv' ### nodeの下
#    file_path = os.path.join(os.path.dirname(__file__), dir_name)
#
#print('profile_name',profile_name)

    plan_prof = {} #辞書型を宣言

    plan_prof = read_plan_prof_csv( profile_name )


    # ******************************
    # PSI_data_file読み込み LEAF判定
    # ******************************

    PSI_data = [] #return用にリスト型を宣言

    if isleaf == "LEAF":

        PSI_data = set_leaf_PSI_data( node )

    elif isleaf == "NOLEAF":

        PSI_data = set_no_leaf_PSI_data( node )

    else:

        print('isleaf flag error: LEAF or NOLEAF should be defined')


# *******************************
# instanciate class PlanSpace 初期設定
# *******************************

    i_PlanSpace = PlanSpace( plan_prof, PSI_data )


# ******************************
# instanciate class LotSpace 初期設定
# ******************************

    i_LotSpace = LotSpace( 54 )


# ******************************
# instanciate class PlanEnv 初期設定
# ******************************

    plan_env = PlanEnv()


    return i_PlanSpace, i_LotSpace, plan_env


# ******************************
# Q_learning modules
# ******************************

def observe(next_action,  i_PlanSpace,i_LotSpace,plan_env,  month_no, calendar_act_weeks,episode):

    week_pos     = next_action
    week_no      = week_pos + 1
    week_no_year = month2year_week( month_no, week_no )

    calendar_inact_weeks = act_inact_convert( calendar_act_weeks )

    #### calendar_inact_weeks == i_PlanSpace.act_week_poss

    week4_month_list = [1,2,4,5,7,8,10,11]

# *****************************
# actionできない環境制約の判定 < LotSpaceの世界において >
# *****************************
# LotSpaceの世界では、off_week_listでplace_lotの可否を判定する。
# 判定action可能かどうか
# 環境制約からaction不可能であれば、位置を保持してnegative rewardを返す

# ******************************
# 制約を判定
# 1) 小の月の第5週目
# 2) 長期休暇週
# 3) ユーザー指定の稼働・非稼働週指定　船便の有無など
# ******************************

# action可能かどうか判定
# 環境制約からaction不可能であれば、状態位置を保持してnegative rewardをセット

# ******************************
# 1) 小の月の第5週目の判定
# ******************************
    if week_pos == 4 : #### next_action=week_pos=4 week_no=第5週の月の判定

        if month_no in week4_month_list:

        #@memo month2year_week( month_no, week_no=5 )の4週月

        # ******************************
        # update act_week_poss = seletable_action_list 
        # ******************************
            if week_pos in i_PlanSpace.act_week_poss:

                #act_week_possから年週week_no_year=月週week_pos=next_action外し
                i_PlanSpace.act_week_poss.remove( week_pos )

                monthly_episode_end_flag = False
                reward = -1000000
                #reward = -1

                return next_action, reward , monthly_episode_end_flag, i_PlanSpace.act_week_poss

            else:
            ### 小の月のカレンダー制約の判定後に、再度next_actionが入って来た

                monthly_episode_end_flag = False

                reward = -1000000
                #reward = -1

            # 既にremove済み
            ## act_week_possから年週week_no_year=月週week_pos=next_actionを外す
            #i_PlanSpace.act_week_poss.remove( week_pos )

                return next_action, reward , monthly_episode_end_flag, i_PlanSpace.act_week_poss


# ******************************
# 2) 長期休暇週の判定
# ******************************
    if week_no_year in i_PlanSpace.off_week_no_year_list:
    #week_pos     = next_action
    #week_no      = week_pos + 1
    #week_no_year = month2year_week( month_no, week_no )

        # ******************************
        # update act_week_poss = seletable_action_list 
        # ******************************
        if week_pos in i_PlanSpace.act_week_poss:

            # act_week_possから年週week_no_year=月週week_pos=next_actionを外す
            i_PlanSpace.act_week_poss.remove( week_pos )

            monthly_episode_end_flag = False
            reward = -1000000
            #reward = -1

            return next_action, reward , monthly_episode_end_flag, i_PlanSpace.act_week_poss

        else:
        ### 長期休暇のカレンダー制約の判定後に、再度next_actionが入って来た

            monthly_episode_end_flag = False

            reward = -1000000
            #reward = -1

            # 既にremove済み
            ## act_week_possから年週week_no_year=月週week_pos=next_actionを外す
            #i_PlanSpace.act_week_poss.remove( week_pos )

            return next_action, reward , monthly_episode_end_flag, i_PlanSpace.act_week_poss


# ******************************
# 3) ユーザー指定の稼働・非稼働週指定　船便の有無など
# ******************************
    elif week_pos in calendar_inact_weeks:

    #### MEMO
    #week_pos     = next_action
    #week_no      = week_pos + 1
    #week_no_year = month2year_week( month_no, week_no )

        # ******************************
        # update act_week_poss = seletable_action_list 
        # ******************************
        if week_pos in i_PlanSpace.act_week_poss:

            # act_week_possから年週week_no_year=月週week_pos=next_actionを外す
            i_PlanSpace.act_week_poss.remove( week_pos )

            monthly_episode_end_flag = False
            reward = -1000000
            #reward = -1

            return next_action, reward , monthly_episode_end_flag, i_PlanSpace.act_week_poss

        else:
            ### 物流カレンダー制約の判定後に、再度next_actionが入って来た

            monthly_episode_end_flag = False

            reward = -1000000
            #reward = -1


            # 既にremove済み
            ## act_week_possから年週week_no_year=月週week_pos=next_actionを外す
            #i_PlanSpace.act_week_poss.remove( week_pos )

            return next_action, reward , monthly_episode_end_flag, i_PlanSpace.act_week_poss


# ******************************
# ACTION(=place_lot)  UPDATE(=calc_plan)  EVALUATION(=eval_plan)
# ******************************

    else:

# ******************************
# 新規ロット番号の付番
# ******************************
        i_PlanSpace.lot_no += 1  #@ 新規ロット番号の付番


#@221009 lot_noが付番されていたので、
# i_PlanSpace.lot_no_value=[lot_no,lot_value]に保管
#
        i_PlanSpace.lot_no_value[0] = i_PlanSpace.lot_no


# ******************************
# 実行actin place_lot / 状態の更新update_state calc_plan_PSI / 評価eval_plan
# ******************************
        next_state, reward, monthly_episode_end_flag = plan_env.act_state_eval(next_action, month_no, i_PlanSpace, i_LotSpace, episode)

        return next_state, reward, monthly_episode_end_flag, i_PlanSpace.act_week_poss


# ******************************
# get_action 5つの週から選択する week_pos=[0,1,2,3,4] +1 week_no=[1,2,3,4,5]
# ******************************
def get_action(state, Qtable, act_week_poss, episode,i_PlanSpace):
#def get_action(state, Qtable, act_week_poss, episode):

    # e-greedy
    epsilon  = 0.2 

    #epsilon  = 0.5
    #epsilon  = 0.5 * (0.99 ** episode)  ### cartpoleのepsilon例


    #@220626 デバッグ用にエンジンを固定　& episode=3
    i_PlanSpace.plan_engine == "FS"


# ******************************
# plan_eigine="ML"を実行 確率epsilonでargmaxする。
# ******************************
    if i_PlanSpace.plan_engine == "ML":

        if  epsilon <= np.random.uniform(0, 1):
            ### exploit ###
            next_action = np.argmax(Qtable[state])

        else:  
            ### explore ###
            next_action = np.random.choice(act_week_poss) 

            ### 前処理の制約確認で選択可能な行動がact_week_possに入っている

            ### next_action = np.random.choice([0, 1, 2, 3, 4])
            ### 制約がなければ、5つの週を選択できる行動がact_week_possに入る


# ******************************
# plan_eigine="FS"を実行
# ******************************
    elif i_PlanSpace.plan_engine == "FS":

### ロットシーケンスlot_noを月内のaction可能数で割った余りで固定シーケンス発生
#
#w_mod = i_PlanSpace.lot_no % len(active_week) 
#
#next_action = active_week[w_mod]

        # ******************************
        # [0,1,2,3,4]の中にconstraint週が[1,4]ならselectableは[0,2,3]
        # ******************************
        next_action_list    = []
        next_action_list    = Qtable[state]

        ### act_week_poss # list of next_action
        selectable_pos_list = i_PlanSpace.act_week_poss 

        w_mod = i_PlanSpace.lot_no % len(selectable_pos_list) 

        next_action = selectable_pos_list[w_mod]

    else:
# ******************************
# plan_eigineを追加する場合はココでelifする
# ******************************
        print('No plan_engine definition')

    return next_action


# ******************************
# Qtableの更新
# ******************************
def update_Qtable(state, Qtable, next_state, reward, next_action):

# ******************************
# 新しい状態を判定してQtableに新規追加
# ******************************
    if next_state not in Qtable: #Q_tableにない状態を追加セット

        Qtable[next_state] = np.repeat(0.0, 5) ### action 0-4 = w1-w5

    cur_state = state

    state = next_state

# ******************************
# Q_table update
# ******************************
    alpha = 0.1   
    #alpha = 0.2  
    #alpha = 0.5  

    gamma = 0.99

    Qtable[cur_state][next_action]=(1-alpha)*Qtable[cur_state][next_action]+\
              alpha * (reward + gamma * max(Qtable[next_state]))

    return state, Qtable


# ******************************
# main process
# ******************************
def main_process(i_PlanSpace, i_LotSpace, plan_env):

#if __name__ == '__main__':




    # ******************************
    # episode_no for Machine Learning
    # ******************************
    
    #episode_no = 10 ####必ず10回以上回す output maxが10回目以降のmaxを拾う
    
    #@220626
    episode_no = 3
    #episode_no = 20
    
    #episode_no = 50
    
    #episode_no = 100
    
    
    # ******************************
    # ML initianise and Q_learning modules
    # ******************************
    
    state = 0      #stateは (x,y) = x + 54 * y の数値で座標を定義
    
    prev_state  = 0 
    work_state  = 0 
    
    # ******************************
    #
    # stateは計画状態
    # place_lot時に、計画状態と一対一のposition=(x,y)を生成
    # position=(x,y)=(week_no_year,lot_step_no)をstateとして取り扱う
    #
    # 3月の第5週は、年間の第13週目、pos=(13,0)
    # week_no_year   = 13
    # lot_step_no    = 0     # ロットを1つ積み上げた数
    
    # (x,y)座標は1つの数字に相互変換する
    #   x=week_no_year  y=lot_step
    #   num = x + 54 * y
    #
    # ******************************
    # x軸 : 0<=x<=54週 week_no_year 年週: 年間を通した週
    #
    #       年週と別に、月内の週week_no=[W1,W2,W3,W4,W5]がある
    #
    #       Qlearningでの取り扱いは、0スタートのweek_pos=[0,1,2,3,4]とする
    #
    #       get_actionは、week_pos=[0,1,2,3,4]から一つの行動を選択すること
    #
    #
    # ******************************
    #
    # actionはplace_lotすることで、get_actionした週にロットを積み上げる
    # get_actionでx軸を選択したら、actionしてy軸を生成して、pos(x,y)が決まる
    #
    # ******************************
    # y軸 : lot_step_no 選択したx軸週にロットを積み上げた数
    #
    # 内部の処理上はlist.append(a_lot)したリストの要素数len(list.append(a_lot))
    #
    # ******************************
    
    
    prev_reward = 0 
    prev_profit = 0 
    
    profit_accum_prev_week = 0
    profit_accum_curr_week = 0
    
    Qtable = {}
    Qtable[state] = np.repeat(0.0, 5)  # actions=0-4 week=1-5
    
    lot_space_Y_LOG    = {}
    lot_space_Y_LOG[0] = []

    lot_space_Y_value_LOG    = {}
    lot_space_Y_value_LOG[0] = []
    
    PSI_plan_log       = {}
    PSI_plan_log[0]    = []

    plan_reward = []    # reward logging

    monthly_episode_end_flag = False  # エージェントがゴールしてるかどうか？


    for episode in range(episode_no):

        #print('START episode = ',episode)

        episode_reward = []   #  報酬log


# ******************************
# 次のepisodeスタート前にPSI_dataとlot_countsを0クリアする
# ******************************

        # 需要Sの入力データを保持する。需要はゼロクリアしない
        # i_PlanSpace.S_year

# ******************************
# 前年PSI-W53を当年PSI-W0にcopyしているのでW0活きゼロクリアしない@221003@221008
# ******************************
        i_PlanSpace.CO_year[1:]    = [ 0 for i in range(53)]
        i_PlanSpace.I_year[1:]     = [ 0 for i in range(53)]
        i_PlanSpace.P_year[1:]     = [ 0 for i in range(53)]
        i_PlanSpace.IP_year[1:]    = [ 0 for i in range(53)]

        #i_PlanSpace.CO_year    = [ 1 for i in range(54)]
        #i_PlanSpace.I_year     = [ 1 for i in range(54)]
        #i_PlanSpace.P_year     = [ 1 for i in range(54)]
        #i_PlanSpace.IP_year    = [ 1 for i in range(54)]

        #i_PlanSpace.CO_year    = [ 0 for i in range(54)]
        #i_PlanSpace.I_year     = [ 0 for i in range(54)]
        #i_PlanSpace.P_year     = [ 0 for i in range(54)]
        #i_PlanSpace.IP_year    = [ 0 for i in range(54)]

        i_PlanSpace.lot_counts = [ 0 for i in range(54)]


# ******************************
# Q学習は月次で12回の処理を実施する
# ******************************
        for month_no in range(1,13): #LOOP 12ヶ月分

            #print('episode_no and month_no = ', episode, month_no )

            WEEK_NO = 5

            i_LotSpace.init_lot_space_M( WEEK_NO )
            #i_LotSpace.init_lot_space_M( 5 )


# ******************************
#   月のS==0で、i_PlanSpace.S445_month[month_no] == 0の時、月の処理をスキップ
# ******************************

            if i_PlanSpace.S445_month[month_no] == 0 :

                continue

# lot_place処理のためのget_actionをend_flagまで繰り返す。
# もし、月内にactive_weekがなければ、end_flag=Trueを返す。

            #辞書型で、{month_no,[week_list,,,]}のデータを持たせる
            calendar_week_dic = {} # active_week_dicの辞書型の宣言

            calendar_week_list = i_PlanSpace.calendar_cycle_week_list

#calendar_week_list = [1,3,5,7,9,11,14,16,17,20,22,24,27,29,31,33,35,37,40,42,44,46,48,50]

            calendar_week_dic = make_active_week_dic(calendar_week_list)

#an image
#calendar_week_dic {1: [1, 2, 3, 4], 2: [1, 2, 3, 4], 3: [1, 2, 3, 4, 5], 4: [1, 2, 3, 4], 5: [1, 2, 3, 4], 6: [1, 2, 3, 4, 5], 7: [1, 2, 3, 4], 8: [1, 2, 3, 4], 9: [1, 2, 3, 4, 5], 10: [1, 2, 3, 4], 11: [1, 2, 3, 4], 12: [1, 2, 3, 4, 5]}

            calendar_act_week = []
            calendar_act_week = calendar_week_dic[month_no]

# カレンダー制約、1)小の月、2)長期休暇off週制約、3)船便物流制約を見て、
# active_weekSを生成する

# 制約共通のactive_weekS=[0,1,2,3,4]を定義する。
# 月内のplanningのconstraint checkでactive_weekS=[]となったらend_flag == True

            act_week_poss             = [0,1,2,3,4] ###初期化 local
            i_PlanSpace.act_week_poss = [0,1,2,3,4] ###初期化 i_PlanSpaceの中


            while not(monthly_episode_end_flag == True):    

            # 終了判定の基本は、 accume_P >= accume_Sで終了を判定する
            #
            # 変化形として、
            # 1) 安全在庫日数 safty_stock_daysを上乗せして終了判定するケース
            #
            #    accume_P >= accume_S + SS_days
            #
            # 2) accume_Profitが減少し始めた時に終了判定するケース
            #
            #    accume_Profit_current < accume_Profit_previous

                # ******************************
                # get_action
                # ******************************
                next_action = get_action(state, Qtable, act_week_poss, episode,i_PlanSpace) 
                #next_action= get_action(state, Qtable, act_week_poss, episode)
# memo
# 機能拡張の案 get_actionには事前にpre_observeして評価する案が考えられる
# 例えば、
# 1. place_back_lotして状態を戻す。
# 2. PlanSpaceのcopy退避で状態を戻す。
# 3. check_action_constraint後、lot_countsを仮更新してEvalPalnSIPする

                # ******************************
                # monitor before_observe
                # ******************************
                pac = sum(i_PlanSpace.Profit[1:])
                #profit_accum_curr = sum(i_PlanSpace.Profit[1:])


                # ******************************
                # observe    check_action_constraint/action/update_state/eval
                # ******************************
                next_state, reward, monthly_episode_end_flag, act_week_poss = observe(next_action,  i_PlanSpace,i_LotSpace,plan_env,  month_no, calendar_act_week,episode) 


                # ******************************
                # monitor after_observe
                # ******************************
                pap = sum(i_PlanSpace.Profit[1:])
                #profit_accum_prev = sum(i_PlanSpace.Profit[1:])


                # ******************************
                # "PROFIT"の終了判定
                # ******************************
                if i_PlanSpace.reward_sw == "PROFIT":

                    if month_no >= 4: # 立ち上がりの3か月はそのまま

                        profit_deviation = ( pac - pap ) / pap

                        #print('profit_deviation',profit_deviation)


                # ******************************
                # 利益累計の変化を見てend conditionを設定する点に注目
                # ******************************
                        if profit_deviation <= 0:  #利益の変化率が0%以下

                        #if profit_deviation <= - 0.01:  #利益の変化率が-1%以下
                        #if (pac - pap) / pap <= - 0.03: #利益の変化率が-3%以下

                            monthly_episode_end_flag = True


                # ******************************
                # Q学習の処理　stateとrewardの変化からQ-Tableを管理
                # ******************************
                state, Qtable = update_Qtable(state,Qtable,next_state,reward,next_action) 

                episode_reward.append(reward)

                # M month
                #show_lot_space_M(i_LotSpace.lot_space_M)

                # Y year
                #show_lot_space_Y(i_LotSpace.lot_space_Y)

                # 制約loopから抜ける
                # ******************************
                # Q学習後、すべての制約を通過した結果act_week_poss== []なら終了
                # ******************************
                if act_week_poss == []: # 選択できるactive week positionsがない

                    monthly_episode_end_flag = true

            # ******************************
            # 月次終了のこの位置で、月次の操作域lot_space_Mを初期化
            # ******************************

            i_LotSpace.lot_space_M = [[] for j in range(5)] 

            monthly_episode_end_flag = False

            i_PlanSpace.lot_no = 0  ### クラス中の変数とする


        # ******************************
        # 年次終了の前に show_lot_space_Yを見たい時に使用
        # ******************************
        # print('episode NO',episode)
        # show_lot_space_Y(i_LotSpace.lot_space_Y)


        # ******************************
        # 年次終了の前に episode_noとshow_lot_space_YのLOG
        # ******************************
        lot_space_Y_LOG[episode]       = i_LotSpace.lot_space_Y
        lot_space_Y_value_LOG[episode] = i_LotSpace.lot_space_Y_value


        # ******************************
        # 年次終了の前に episode_noとPSI_planのLOG
        # ******************************
        PSI_plan_log[episode] = [ ["1S"]+i_PlanSpace.S_year, ["2CO"]+i_PlanSpace.CO_year, ["3I"]+i_PlanSpace.I_year, ["4P"]+i_PlanSpace.P_year, ["5IP"]+i_PlanSpace.IP_year ]

        #print('PSI_plan_log[episode]', episode, PSI_plan_log[episode] )

# ******************************
# 次のepisodeスタート前にlot_space_Yを0クリアする
# ******************************
        i_LotSpace.lot_space_Y       = [[] for j in range(53)]
        i_LotSpace.lot_space_Y_value = [[] for j in range(53)]

        #print('lot_space_Yを0クリア')
        #show_lot_space_Y(i_LotSpace.lot_space_Y)


        # ******************************
        # episode reward log
        # ******************************
        plan_reward.append(np.sum(episode_reward))


        #@220625 Qtableの重みは保持して、学習し続ける???
        # ******************************
        # 年次終了のこの位置で、Q学習の初期化 
        # ******************************
        state = plan_env.reset(i_LotSpace)           # init state

        state = 0             #stateは (x,y) = x + 54 * y の数値で座標を定義

        update_Qtable(state,Qtable,next_state,reward,next_action) 

        monthly_episode_end_flag = False


# ******************************
# pickup TOP reward plan    lot_space_Y[top_reward]
# ******************************

# ******************************
# episode毎にloggingした計画結果から、episode10回目以降でreward maxを取り出す
# ******************************

    max_value = max(plan_reward[1:]) ### episode2回目以降
    #max_value = max(plan_reward[9:]) ### episode10回目以降

    #print('plan_reward',plan_reward)
    #print('plan_reward[9:]',plan_reward[9:])
    #print('max_value',max_value)

    max_index = plan_reward.index(max_value)

    #print('max value and index',max_value,max_index)


    fin_lot_space_Y       = lot_space_Y_LOG[max_index]
    fin_lot_space_Y_value = lot_space_Y_value_LOG[max_index]


    PSI_plan        = PSI_plan_log[max_index] #@221006


    #show_lot_space_Y('showing fin_lot_space_Y', fin_lot_space_Y)

#@220625 SCMTREEのバッチ処理なのでepisodeの描画はSTOP
## ******************************
## episode & reward log plot
## ******************************
#
#    # 結果のプロット
#    plt.plot(np.arange(episode_no), plan_reward)
#    plt.xlabel("episode")
#    plt.ylabel("reward")
#    plt.savefig("plan_value.jpg")
#    plt.show()


    return fin_lot_space_Y, fin_lot_space_Y_value, PSI_plan



# ********************************************************
# 当年W53の結果を翌年W0にセット
# put PSI W53_61 in next_PSI W0_8
# ********************************************************
def put_PSI_W53_in_next_W0( df, year, node, i_PlanSpace, PSI_data ):

    # 翌年のPSIを生成する
    year_next = year + 1 

    PSI_data_next = []

    #
    # PSI_DBのdataframeから、変数@year+@nodeで検索して、psiの行数indexを入手
    #
    psi_index = df.query("year == @year_next & node_to == @node").index.tolist()

    # monitor
    #print('psi_index_next',psi_index)

    # "l"で、i_PlanSpaceの中のPSIをリスト化
    l       = []
    l_index = []

    l_index.append( year_next ) #@220929

    l_index.append( i_PlanSpace.product_name )
    l_index.append( i_PlanSpace.SC_tree_id )
    l_index.append( i_PlanSpace.node_from )
    l_index.append( i_PlanSpace.node_to )

    # monitor
    #print('l_index@i_PlanSpace@output',l_index)

    l.append( l_index + ["1S"]  + i_PlanSpace.S_year  )
    l.append( l_index + ["2CO"] + i_PlanSpace.CO_year )
    l.append( l_index + ["3I"]  + i_PlanSpace.I_year  )
    l.append( l_index + ["4P"]  + i_PlanSpace.P_year  )
    l.append( l_index + ["5IP"] + i_PlanSpace.IP_year )

    # 生成されたpsi_dataをリスト化
    PSI_data_next = l

    # 当年PSI_dataのW53を翌年PSI_data_nextのW0にセット
    # put PSI W53_61-3 in next_PSI W0_8-3   3カラム飛ばす"index"+"year"+"node"

    # "year","prod_name",,,
    for i , ind in enumerate(psi_index):

        # "year"+                 # "index"+"year"+
        PSI_data_next[i][1+4+1] = PSI_data[i][2+4+54] # 54 = W0 + 52 + W53

    # ***********************
    # スタート週W0を更新した翌年PSIをdfに戻す
    # ***********************

    l = PSI_data_next        

    for i , ind in enumerate(psi_index):

        ####print('ind, df.loc[ind]', ind, df.loc[ind] )

        # psiのリストから、一つ取り出して、dfのデータレイアウトに整合
        l_work = []

        l_work = l[i]

        ####print('l_work1 next', i, l_work , len(l_work) )

        # psiリストの先頭にPSI_DBのindexを1回追加して、dfと整合
        l_work.insert(0, ind)

        ####print('l_work2 next', i, l_work , len(l_work) )

        # PDI_DB更新  行数index指定でpsiリストを代入 ####@221003 inplaceの方法
        df.loc[ind] = l_work 

        ####print('df.loc[ind] next', df.loc[ind] )


        ## checking df
        #df_l = df.loc[ind].values.tolist()
        #print('df_l_AFTER', df_l, len(df_l) )

#df_psi_l [2023, 'prod56789012345', 'sc010', 'YTO', 'YTOLEAF', '1S', 2, 50, 30, 30, 30, 63, 63, 63, 63, 80, 80, 80, 80, 80, 125, 125, 125, 125, 150, 150, 150, 150, 140, 140, 140, 140, 140, 223, 223, 223, 223, 250, 250, 250, 250, 180, 180, 180, 180, 180, 175, 175, 175, 175, 100, 100, 100, 100, 10, 10, 10, 10, 10, 10] 60

#i, l[i] 0 [0, 2023, 'prod56789012345', 'sc010', 'YTO', 'YTOLEAF', '1S', 2, 50, 30, 30, 30, 63, 63, 63, 63, 80, 80, 80, 80, 80, 125, 125, 125, 125, 150, 150, 150, 150, 140, 140, 140, 140, 140, 223, 223, 223, 223, 250, 250, 250, 250, 180, 180, 180, 180, 180, 175, 175, 175, 175, 100, 100, 100, 100, 10, 10, 10, 10, 10, 10] 61

    # 翌年の結果は戻さなくてよいので STOP
    #return PSI_data_next


    # dfをすべて表示
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    ####print('df next', df )

    return df


# ********************************************************
# output 複数年用
# ********************************************************

def output_Y(df, year, is_lastyear, node,  i_PlanSpace,i_LotSpace,  fin_lot_space_Y):


    # *************************
    # 複数年 PSI結果は、dfにputし、PSI_dataリスト生成
    # *************************
    PSI_data = []

    PSI_data = update_PSI_DB_data2df( df, year, node, i_PlanSpace  )


    # *************************
    # 複数年のPSIツナギ　当年W53の結果を翌年W0にセット
    # *************************
    if is_lastyear: #@221001 年ツナギ

        pass

    else:

        # 最終年ではなければ、翌年year_next = year + 1をセットして
        # 当年W53の結果を翌年W0にセット
        df = put_PSI_W53_in_next_W0( df, year, node, i_PlanSpace, PSI_data )  
        #put_PSI_W53_in_next_W0( df, year, node, i_PlanSpace, PSI_data )  

    return df

## ここの位置は、STOP
## ******************************
## csv write common_plan_unit.csv 共通計画単位による入出力
## ******************************
## 将来的にSCM treeでサプライチェーン拠点間の需要を連携する時に使用する
#
#    csv_write2common_plan_unit_N(i_LotSpace,i_PlanSpace, fin_lot_space_Y)
#    #csv_write2common_plan_unit(i_LotSpace,i_PlanSpace, fin_lot_space_Y)


# OLD
# ********************************************************
# output 単年用
# ********************************************************
def output(node,  i_PlanSpace,i_LotSpace,  fin_lot_space_Y):

# ******************************
# write_PSI_data2csv 
# ******************************

    ####print('node@output',node)

    PSI_data_file_name = ".\\node_all\\" + node + "\\PySI_data_std_IO.csv" 

    #PSI_data_file_name = '.\\'+ node+ '\\'+ 'PySI_data_std_IO.csv'

    #file_name = 'PySI_data_std_IO.csv'         ### .\dataより開きやすい
    #file_name = '.\data\PySI_data_std_IO.csv' 

    ####print('PSI_data_file_name@output',PSI_data_file_name)

    write_PSI_data2csv( i_PlanSpace, PSI_data_file_name )


# ここの位置でOK #*ココは単年用なので、複数年の"xxx_N"関数は定義しない
# ******************************
# csv write common_plan_unit.csv 共通計画単位による入出力
# ******************************
# 将来的にSCM treeでサプライチェーン拠点間の需要を連携する時に使用する

    csv_write2common_plan_unit(i_LotSpace,i_PlanSpace, fin_lot_space_Y)


# ********************************************************
# 生成されたPSI_splanとindexでPSI_LISTをupdateする
# ********************************************************
def update_PSI( PSI_LIST, PSI_plan, psi_index ):

    for i, ind in enumerate( psi_index ):

        #*** ind PSIの行番
        #*** i PSIの1つの行番0,1,2,3,4
        #*** 
        # [ 0,       1,      2,            3,         4,            5,
        # ["index", "year", "prod_name" , "scm_id" , "node_from" , "node_to",
        PSI_LIST[ind][6:] = PSI_plan[i]

        #print('update_PSI PSI_LIST[ind]',PSI_LIST[ind])
        #print('update_PSI PSI_plan[i]',PSI_plan[i])

# PSI_dataから
#   header = ["index", "year", "prod_name" , "scm_id" , "node_from" , "node_to" , "SIP" , "W00" , "W01" , "W02" , "W03" , "W04" , "W05" , "W06" , "W07" , "W08" , "W09" , "W10" , "W11" , "W12" , "W13" , "W14" , "W15" , "W16" , "W17" , "W18" , "W19" , "W20" , "W21" , "W22" , "W23" , "W24" , "W25" , "W26" , "W27" , "W28" , "W29" , "W30" , "W31" , "W32" , "W33" , "W34" , "W35" , "W36" , "W37" , "W38" , "W39" , "W40" , "W41" , "W42" , "W43" , "W44" , "W45" , "W46" , "W47" , "W48" , "W49" , "W50" , "W51" , "W52" , "W53"]


# PSI_plan_log[episode] = [ ["1S"]+i_PlanSpace.S_year, ["2CO"]+i_PlanSpace.CO_year, ["3I"]+i_PlanSpace.I_year, ["4P"]+i_PlanSpace.P_year, ["5IP"]+i_PlanSpace.IP_year ]


# ********************************************************
# 当年W53の結果を翌年W0にセット
# put PSI W53_61 in next_PSI W0_8
# ********************************************************
def set_next_year_W0(df, PSI_LIST, PSI_plan, year, node):

#def set_next_year_W0( df, PSI_LIST, year, node):

#def put_PSI_W53_in_next_W0( df, year, node, i_PlanSpace, PSI_data ):


    # 翌年のPSIを生成する
    year_next = year + 1 

    PSI_data_next = []

    #
    # PSI_DBのdataframeから、変数@year+@nodeで検索して、psiの行数indexを入手
    #
    psi_N_index = df.query("year == @year_next & node_to == @node").index.tolist()

    ####print('psi_N_index',psi_N_index)

#    # "l"で、i_PlanSpaceの中のPSIをリスト化
#    l       = []
#    l_index = []
#
#    l_index.append( year_next ) #@221006
#
#    l_index.append( i_PlanSpace.product_name )
#    l_index.append( i_PlanSpace.SC_tree_id )
#    l_index.append( i_PlanSpace.node_from )
#    l_index.append( i_PlanSpace.node_to )
#
#    print('l_index@i_PlanSpace@output',l_index)
#
#    l.append( l_index + ["1S"]  + i_PlanSpace.S_year  )
#    l.append( l_index + ["2CO"] + i_PlanSpace.CO_year )
#    l.append( l_index + ["3I"]  + i_PlanSpace.I_year  )
#    l.append( l_index + ["4P"]  + i_PlanSpace.P_year  )
#    l.append( l_index + ["5IP"] + i_PlanSpace.IP_year )
#
#    # 生成されたpsi_dataをリスト化
#    PSI_data_next = l


    # 当年PSI_dataのW53を翌年PSI_data_nextのW0にセット
    # put PSI W53 in next_PSI W0

    # "year","prod_name",,,
    for i , ind in enumerate(psi_N_index):

        #  "index"+"year"+           # "index"+"year"+
        #print('PSI_LIST[ind]',PSI_LIST[ind])
        #print('PSI_plan[i]',PSI_plan[i])

        PSI_LIST[ind][0+2+4+1] = PSI_plan[i][0+54] # 54 = W0 + 52 + W53

        # monitor
        #print('set_next_year_W0 PSI_LIST[ind]',PSI_LIST[ind])
        #print('set_next_year_W0 PSI_plan[i]',PSI_plan[i])

# *** PSI image ***
#PSI_LIST[ind] 
#[5, 2024, 'prod56789012345', 'sc010', 'YTO', 'YTOLEAF', '1S', 10, 50, 30, 30, 30, 63, 63, 63, 63, 80, 80, 80, 80, 80, 125, 125, 125, 125, 150, 150, 150, 150, 140, 140, 140, 140, 140, 223, 223, 223, 223, 250, 250, 250, 250, 180, 180, 180, 180, 180, 175, 175, 175, 175, 100, 100, 100, 100, 10, 10, 10, 10, 10, 10]
#
#PSI_plan[i] 
#['1S', 2, 50, 30, 30, 30, 63, 63, 63, 63, 80, 80, 80, 80, 80, 125, 125, 125, 125, 150, 150, 150, 150, 140, 140, 140, 140, 140, 223, 223, 223, 223, 250, 250, 250, 250, 180, 180, 180, 180, 180, 175, 175, 175, 175, 100, 100, 100, 100, 10, 10, 10, 10, 10, 10]

#    header = ["index", "year", "prod_name" , "scm_id" , "node_from" , "node_to" , "SIP" , "W00" , "W01" , "W02" , "W03" , "W04" , "W05" , "W06" , "W07" , "W08" , "W09" , "W10" , "W11" , "W12" , "W13" , "W14" , "W15" , "W16" , "W17" , "W18" , "W19" , "W20" , "W21" , "W22" , "W23" , "W24" , "W25" , "W26" , "W27" , "W28" , "W29" , "W30" , "W31" , "W32" , "W33" , "W34" , "W35" , "W36" , "W37" , "W38" , "W39" , "W40" , "W41" , "W42" , "W43" , "W44" , "W45" , "W46" , "W47" , "W48" , "W49" , "W50" , "W51" , "W52" , "W53"]

#    index, year, prod_name, 
# 0 [0, 2023, 'prod56789012345', 'sc010', 'YTO', 'YTOLEAF', '1S', 2, 50, 30, 30, 30, 63, 63, 63, 63, 80, 80, 80, 80, 80, 125, 125, 125, 125, 150, 150, 150, 150, 140, 140, 140, 140, 140, 223, 223, 223, 223, 250, 250, 250, 250, 180, 180, 180, 180, 180, 175, 175, 175, 175, 100, 100, 100, 100, 10, 10, 10, 10, 10, 10] 61


        #PSI_data_next[i][1+4+1] = PSI_data[i][2+4+54] # 54 = W0 + 52 + W53

    # ***********************
    # スタート週W0を更新した翌年PSIをdfに戻す
    # ***********************

#    l = PSI_data_next        
#
#    for i , ind in enumerate(psi_index):
#
#        print('ind, df.loc[ind]', ind, df.loc[ind] )
#
#        # psiのリストから、一つ取り出して、dfのデータレイアウトに整合
#        l_work = []
#
#        l_work = l[i]
#
#        print('l_work1 next', i, l_work , len(l_work) )
#
#        # psiリストの先頭にPSI_DBのindexを1回追加して、dfと整合
#        l_work.insert(0, ind)
#
#        #l_work.insert(0, ind)
#
#        print('l_work2 next', i, l_work , len(l_work) )
#
#        # PDI_DB更新  行数index指定でpsiリストを代入 ####@221003 inplaceの方法
#        df.loc[ind] = l_work 
#
#        print('df.loc[ind] next', df.loc[ind] )




        ## checking df
        #df_l = df.loc[ind].values.tolist()
        #print('df_l_AFTER', df_l, len(df_l) )

#df_psi_l [2023, 'prod56789012345', 'sc010', 'YTO', 'YTOLEAF', '1S', 2, 50, 30, 30, 30, 63, 63, 63, 63, 80, 80, 80, 80, 80, 125, 125, 125, 125, 150, 150, 150, 150, 140, 140, 140, 140, 140, 223, 223, 223, 223, 250, 250, 250, 250, 180, 180, 180, 180, 180, 175, 175, 175, 175, 100, 100, 100, 100, 10, 10, 10, 10, 10, 10] 60

#i, l[i] 0 [0, 2023, 'prod56789012345', 'sc010', 'YTO', 'YTOLEAF', '1S', 2, 50, 30, 30, 30, 63, 63, 63, 63, 80, 80, 80, 80, 80, 125, 125, 125, 125, 150, 150, 150, 150, 140, 140, 140, 140, 140, 223, 223, 223, 223, 250, 250, 250, 250, 180, 180, 180, 180, 180, 175, 175, 175, 175, 100, 100, 100, 100, 10, 10, 10, 10, 10, 10] 61

    # 翌年の結果は戻さなくてよいので STOP
    #return PSI_data_next


    # dfをすべて表示
#    pd.set_option('display.max_rows', None)
#    pd.set_option('display.max_columns', None)
#
#    print('df next', df )
#
#    return df

    return PSI_LIST


# ********************************************************
# PySI 複数年用
# ********************************************************

####years_list = [2022, 2023, 2024]

def PySI_Y(df_prof, df, PSI_LIST, years_list, node, isleaf):


    # monitor
    PSI_LIST[0][7] = 20
    ####print('monitor in PySI_Y(',PSI_LIST[:50])


    # PSI_LISTは、years+nodeの全てのデータをリスト化している

    #PSI_LIST_work = PSI_LIST

    for year in years_list:

        #print('isleaf node', isleaf, node)


        # *************************************
        # chacking 'year' exist or not
        # *************************************
        years_in_df = df_prof['year'].unique()
    
        # monitor
        #print( "df['year'].unique()", years_in_df ) # df year 確認
    
        #for year in years_list:
    
        if ( year in years_in_df ) == True :
    
            print( 'year', year, ' is in DF', years_in_df )
    
        else :
    
            print( 'error: year', year, ' is NOT in DF', years_in_df )
    
        #
        # query 
        #
        df_prof_Y = df_prof[(df_prof['year'] == year)&(df_prof['node_to'] == node)]
    
        ####print('df_prof_Y',df_prof_Y)
    
        #@220924 条件指定で1行になっているのて、headerと値のペアで辞書を作る
    
        plan_prof_Y_list = [] #リスト型を宣言 
        plan_prof_Y      = {} #辞書型を宣言 
    
        plan_prof_label  = []
        plan_prof_value  = []
    
        # dfをラベル付きで、リスト変換して、辞書にする・・・という手順
    
        # .reset_index().values.tolist()
        #
        #    plan_prof_Y_list = df_prof_Y.reset_index().values.tolist()
        
        #列名（列ラベル）をリセットするメソッドは無いため、pandas.DataFrameで行    名も    列名もリストのデータとして残したい場合は、reset_index()メソッドを適用    したあと    .Tで転置して再度reset_index()メソッドを適用し、さらに.Tで元に戻    す。
        
        plan_prof_Y_list = df_prof_Y.T.reset_index().T.values.tolist()
        
        ####print('plan_prof_Y_list',plan_prof_Y_list)
        
        plan_prof_label  = plan_prof_Y_list[ 0 ]
        #print('plan_prof_label',plan_prof_label)
    
        plan_prof_value  = plan_prof_Y_list[ 1 ]
        #print('plan_prof_value',plan_prof_value)
    
        #
        #    for prof in plan_prof_Y_list:
        #
        #        plan_prof_label.append( prof[0] )
        #        plan_prof_value.append( prof[1] )
        #
        #    print('plan_prof_label',plan_prof_label)
    
        plan_prof = dict( zip( plan_prof_label , plan_prof_value ) )
    
        ####print('plan_prof',plan_prof)
    
    ## ************************
    ## test run
    ## ************************
    #
    #prof_dic = input_Y(2023, "YTO", "LEAF")
    #
    #print('prof_dic',prof_dic)


        # ***********************
        # PSI input process
        # ***********************

        # PSI_dataは"index"+"year"+"node"のPSIで、PlanSpaceインスタンスを生成

        # PSI_LISTから"year"+"node"のPSIを抽出 indexを含む


        ## monitor
        #PSI_LIST[0][7] = 21
        #print('monitor in year loop before input_Y(',PSI_LIST[:50])


        PSI_data, psi_index = input_Y(df, PSI_LIST, year, node, isleaf)

        ## monitor
        #PSI_LIST[0][7] = 22
        #print('monitor in year loop after input_Y( before PlanSpace(',PSI_LIST[:50])


# *******************************
# instanciate class PlanSpace 初期設定
# *******************************

# monitor
#
#        for l in PSI_data:
#            print('before instanciate PlanSpace PSI_data', l )

        i_PlanSpace = PlanSpace( plan_prof, PSI_data )


# ******************************
# instanciate class LotSpace 初期設定
# ******************************

        i_LotSpace = LotSpace( 54 )


# ******************************
# instanciate class PlanEnv 初期設定
# ******************************

        plan_env = PlanEnv()


# ***********************
# PSI main process
# ***********************

        # PSI_planは"index"+"year"+"node"のPSIで、PSI計画結果

        # ***********************
        # reward maxのfin_lot_space_Y_log[epi]とPSI_plan_log[epi]をpick up
        # ***********************

        # 1. PSI_dataを取って、計算して、PSI_planへ

        fin_lot_space_Y, fin_lot_space_Y_value, PSI_plan = main_process(i_PlanSpace, i_LotSpace, plan_env)


        #for l in PSI_plan:
        #
        #    print('after PSI calc PSI_plan', l )

        ## ***********************
        ## reward maxのfin_lot_space_Yをpick upして、S-CO-I-P-IPを生成
        ## ***********************
        #PSI_plan = get_PSI( fin_lot_space_Y, i_PlanSpace, i_LotSpace, plan_env )

        # ***********************
        # PSI output process
        # ***********************
        # 1. PSI_LISTへの変更
        # 2. common plan unitへの書き出し
        # 3. 最終年でなければ、当年W53を翌年のW0に計画初期値セット


        # ***********************
        # 1. PSI_LISTへの変更
        # save PSI     PSI計画結果PSI_planをindexでPSI_LISTにupdate
        # ***********************

        # monitor
        #PSI_LIST[0][7] = 23
        #print('monitor in year loop before update_PSI(',PSI_LIST[:50])


        # ***********************
        #生成されたPSI_planとindexでPSI_LISTをupdateする
        # ***********************
        update_PSI( PSI_LIST, PSI_plan, psi_index ) 

        # monitor
        #PSI_LIST[0][7] = 24
        #print('monitor in year loop after update_PSI(',PSI_LIST[:50])


        # ***********************
        # 2. common plan unitへの書き出し
        # ***********************

        # ******************************
        # csv write common_plan_unit.csv 共通計画単位による入出力
        # ******************************
        # 将来的にSCM treeでサプライチェーン拠点間の需要を連携する時に使用する

        #@221009 lot_place毎のvalueをlogして、main process終了後に取り出す
        # [lot_no, lot_value]のペアリストでlogを保持する。
        # したがって、fin_lot_space_Yの中で、valueを保持している

        csv_write2common_plan_unit_N(i_LotSpace,i_PlanSpace, fin_lot_space_Y, fin_lot_space_Y_value)


        # ***********************
        # 3. 最終年でなければ、当年W53を翌年のW0に計画初期値セット
        # is_lastyear = check_year( year, years_list)
        # ***********************
        is_lastyear = False

        if year == years_list[-1]:

            is_lastyear = True
            pass

        else :

            # monitor
            #PSI_LIST[0][7] = 31
            #print('monitor in year loop before set_next_year_W0(',PSI_LIST[:50])
            for l in PSI_LIST[:50]:

                if l[6] == "3I":

                    #print(l)
                    pass

                else:

                    pass


            set_next_year_W0(df, PSI_LIST, PSI_plan, year, node)

            # monitor
            #PSI_LIST[0][7] = 32
            #print('monitor in year loop after set_next_year_W0(',PSI_LIST[0][7])

            for l in PSI_LIST[:50]:

                if l[6] == "3I":

                    #print(l)
                    pass

                else:

                    pass


# ********************************************************
# PySI 単年用
# ********************************************************
def PySI(node,isleaf):

    #print('isleaf node', isleaf, node)

    #LEAFの時、leaf_nodeを処理
    i_PlanSpace, i_LotSpace, plan_env = input(node,isleaf)

    fin_lot_space_Y = main_process(i_PlanSpace, i_LotSpace, plan_env)

    output(node,  i_PlanSpace,i_LotSpace,  fin_lot_space_Y)


# ********************************************************
# csv_write2common_plan_header 共通計画単位のヘッダー書き出し
# ********************************************************
def csv_write2common_plan_header_N(): 

    l = []
    r = []

    #seq_no, control_flag , priority_no, modal, LT , from_x , from_Wxx , step_xx , to_y , to_Wyy , step_yy 

    # ********* ヘッダーのみ先に書き出す 各PSI計画の出力の前に
    #@221117 ,'Value_onSC'を取り

    r = ['seq_no','control_flag','priority_no','modal','LT','Dpt_entity','Dpt_year','Dpt_week','Dpt_step','Arv_entity','Arv_year','Arv_week','Arv_step','Value'] #@221009@221010@221020@221117

    #r = ['seq_no','control_flag','priority_no','modal','LT','Dpt_entity','Dpt_year','Dpt_week','Dpt_step','Arv_entity','Arv_year','Arv_week','Arv_step','Value','Value_onSC'] #@221009@221010@221020

    # lot_noで出力するcsv file nameを作成
    csv_file_name = "common_plan_unit.csv"

    l.append(r)


# ****************************************
# CSV ファイル書き出し
# ****************************************

    #print('l',l)

    with open( csv_file_name , 'w', newline="") as f:

        writer = csv.writer(f)
        writer.writerows(l)


def csv_write2common_plan_header(): 


    l = []
    r = []

    #seq_no, control_flag , priority_no, modal, LT , from_x , from_Wxx , step_xx , to_y , to_Wyy , step_yy 

    # ********* ヘッダーのみ先に書き出す 各PSI計画の出力の前に
    r = ['seq_no','control_flag','priority_no','modal','LT','Dpt_entity','Dpt_week','Dpt_step','Arv_entity','Arv_week','Arv_step','Value','Value_onSC'] #@221009

    # lot_noで出力するcsv file nameを作成
    csv_file_name = "common_plan_unit.csv"

    l.append(r)

# ****************************************
# CSV ファイル書き出し
# ****************************************

    #print('l',l)

    with open( csv_file_name , 'w', newline="") as f:

        writer = csv.writer(f)
        writer.writerows(l)

#### csv_write2common_plan_header ####


def PSI_DB_csv_read(filename):

    # PSI_DB名を宣言
    #filename = "PSI_DB.csv" 

    print('profile filename',filename)

    # 'node_to'&'year'でPSI_DBを検索

    df      = pd.read_csv( filename, header=0, index_col=None )

    return df


if __name__ == '__main__':


# ******************************
# csv_write2common_plan_header　計画共通単位のヘッダー初期設定
# ******************************

    csv_write2common_plan_header_N() # 複数年に対応
    #csv_write2common_plan_header()

    # 修正メモ 'year'+'node'キーを追加したCSVファイルに対応@220918

    # read_profile()

    #df_prof = pd.read_to_csv('PySI_Profile_std_Y.csv')

    #本来は、
    # 1. PSIの入力ファイルから'year'をkeyにuniqeして、years_listを作成する
    # 2. UIから処理対象年度を入力する

    years_list = [2023, 2024, 2025, 2026]


    # planningでは
    # 注: current_year=Nは使わない。N+1,N+2,N+3の末端市場S_outlookを使用する。
    # adjustingでは、crrent_year=Nの'S_actual'でadjust計算する。

    # SC_activity_table   S-I-P( node, time ) + lot_step  cost_profile(node)

    # 制約
    # 部分問題(ネットワーク、配分)のsolver modelと制約 
    #  => 供給ネットワーク定義、最適配分、　　　ら
    # Supply_chain activity全体の表現、planning結果、評価



    PSI_LIST         = []
    PSI_LIST_node    = []


# ******************************
# PSI_DB.csvの読込み 初期設定
# ******************************
    # PSI_DB名を宣言
    filename = "PSI_DB.csv" 


    # dataframeはindex参照に利用する
    df = pd.read_csv(filename)

    # dfからlist生成  valuesなのでheaderなし
    PSI_LIST = df.values.tolist()

    ####print('PSI_LIST',PSI_LIST)


# ******************************
# node_profile.csvの読込み 初期設定
# ******************************
# reading "PySI_Profile_std.csv"
# setting planning parameters
#
# Plan_engine = "ML" or "FS" , cost marameters, planning one and so on
# ML:Machine Learning  FS:Fixed Sequence/Normal PSI
#
#
    #プロファイル名を宣言
    filename = "node_profile.csv" 

# node別、year別 profileを辞書に入れる 'year'+'node'を追加したDataBase
#
    df_prof      = pd.read_csv(filename)
#
    ####print('df_prof', df_prof)
    



# ***********************************
# is_leaf node
# ***********************************

    total_node = len(node_name)

    for i, node in enumerate(node_name):  #### SCM tree nodes are postordering 

        print('')
        print('SCM tree postorder node ', i+1 , 'of', total_node , node )
        print('')

        if is_leaf(node):

            print('------------------')
            print('leaf node',node)
            print('------------------')

            # **************************
            # leaf nodeの場合、複数年のPSIを処理 PSI_dataのSからC-P-U生成
            # **************************

            PySI_Y(df_prof, df, PSI_LIST, years_list, node, 'LEAF')

            ## monitor
            #PSI_LIST[0][7] = 11
            #print('monitor in node loop after PySI_Y(',PSI_LIST[:50])

        else:              #### root node処理が必要な場合はelif is_root分岐

            print('------------------')
            print('mid or root node',node)
            print('------------------')

            # **************************
            # NOLEAF nodeの場合、複数年のPSIを処理 C-P-UのSからC-P-U更新
            # **************************

            PySI_Y(df_prof, df, PSI_LIST, years_list, node, 'NOLEAF')

            ## monitor
            #PSI_LIST[0][7] = 12
            #print('monitor in node loop after PySI_Y(',PSI_LIST[:50])

        # **************************
        # N年間のPSI計算後のnodeのPSI_LIST_node参照をもとのPSI_LISTに戻す
        # **************************

        #PSI_LIST = PSI_LIST_node

        ## monitor
        #PSI_LIST[0][7] = 13
        #print('monitor after node loop after PySI_Y(',PSI_LIST[:50])


# *******************************
# write to csv
# *******************************

    file_name = "PSI_DB_out.csv"
    
    #df.to_csv( file_name , header=True, index=False)


    header = ["index", "year", "prod_name" , "scm_id" , "node_from" , "node_to" , "SIP" , "W00" , "W01" , "W02" , "W03" , "W04" , "W05" , "W06" , "W07" , "W08" , "W09" , "W10" , "W11" , "W12" , "W13" , "W14" , "W15" , "W16" , "W17" , "W18" , "W19" , "W20" , "W21" , "W22" , "W23" , "W24" , "W25" , "W26" , "W27" , "W28" , "W29" , "W30" , "W31" , "W32" , "W33" , "W34" , "W35" , "W36" , "W37" , "W38" , "W39" , "W40" , "W41" , "W42" , "W43" , "W44" , "W45" , "W46" , "W47" , "W48" , "W49" , "W50" , "W51" , "W52" , "W53"]

    ## monitor
    #PSI_LIST[0][7] = 14
    #print('monitor out node loop after PySI_Y(',PSI_LIST[:50])

    with open( file_name , 'w'  , newline="") as f:
        writer = csv.writer(f)

        # *********************
        # *** write headder ***
        # *********************
        writer.writerow(header)

        # *********************
        # *** write S-CO-I-P-IP
        # *********************
        for l in PSI_LIST:

            writer.writerow(l)


    print('end of process')


# ******************************
# end of main process
# ******************************
