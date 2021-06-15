import sys
import iric
import numpy as np

#--------------------------------------------------
# 計算結果出力関数
#--------------------------------------------------
def write_calc_result(ctime, xx, yy, zz, ss, qq, uu, vv, hh, zb, hs):

    ier = 0

    # # write time
    iric.cg_iRIC_Write_Sol_Time(ctime)
    
    # # write discharge
    iric.cg_iRIC_Write_Sol_BaseIterative_Real('Discharge', qq)

    # # write grid
    iric.cg_iRIC_Write_Sol_GridCoord2d(xx.reshape(-1), yy.reshape(-1))

    # # write node values
    # iric.cg_iRIC_Write_Sol_Integer("for integer array", zz.reshape(-1))
    iric.cg_iRIC_Write_Sol_Real("Elevation", zz.reshape(-1))
    iric.cg_iRIC_Write_Sol_Real("VelocityX", uu.reshape(-1))
    iric.cg_iRIC_Write_Sol_Real("VelocityY", vv.reshape(-1))

    # # write cell values
    iric.cg_iRIC_Write_Sol_Cell_Real("ManningN_c", ss.reshape(-1))
    iric.cg_iRIC_Write_Sol_Cell_Real("Elevation_c", zb.reshape(-1))
    iric.cg_iRIC_Write_Sol_Cell_Real("Depth_c", hs.reshape(-1))
    iric.cg_iRIC_Write_Sol_Cell_Real("WaterLevel_c", hh.reshape(-1))

    return ier
#--------------------------------------------------
# main 関数
#--------------------------------------------------
def main(fname0):

    ier = 0

    # ファイルを開く
    fid = iric.cg_open(fname0, iric.CG_MODE_MODIFY)
    iric.cg_iRIC_Init(fid)

    # 計算格子数
    ni, nj = iric.cg_iRIC_GotoGridCoord2d()

    # 計算格子x,y
    x, y = iric.cg_iRIC_GetGridCoord2d()
    xx = x.reshape(nj, ni)  #1次元配列で読みこまれるため２次元配列に形状変更
    yy = y.reshape(nj, ni)  #1次元配列で読みこまれるため２次元配列に形状変更

    # 格子属性　標高
    z = iric.cg_iRIC_Read_Grid_Real_Node('Elevation')
    zz = z.reshape(nj, ni)  #1次元配列で読みこまれるため２次元配列に形状変更

    # 格子属性　粗度
    s = iric.cg_iRIC_Read_Grid_Real_Cell('roughness_cell')
    ss = s.reshape(nj-1, ni-1)  #1次元配列で読みこまれるため２次元配列に形状変更

    # ## for debug 2d plot
    # fig, ax = plt.subplots()
    # ax.contourf(xx, yy, zz, 20)
    # plt.show()
    
    # 計算条件の読込
    # 関数リファレンス
    # https://iric-solver-dev-manual-jp.readthedocs.io/ja/latest/06/03_reference.html
    cip = iric.cg_iRIC_Read_Integer('j_cip')
    conf = iric.cg_iRIC_Read_Integer('j_conf')

    #流量条件
    t_series = iric.cg_iRIC_Read_FunctionalWithName('discharge_waterlevel', 'time')
    q_series = iric.cg_iRIC_Read_FunctionalWithName('discharge_waterlevel', 'discharge')

    #計算時間の設定
    if iric.cg_iRIC_Read_Integer('i_sec_hour') == 2:
        t_series = t_series*3600.

    t_start = t_series[0]
    t_end = t_series[-1]
    t_out = iric.cg_iRIC_Read_Real('tuk')
    dt = iric.cg_iRIC_Read_Real('dt')

    istart = int(t_start / dt)
    iend = int(t_end / dt) + 1
    iout = int(t_out / dt)

    #流れ計算の初期条件を設定する
    uu = np.zeros(nj*ni, dtype = np.float64).reshape(nj, ni)
    vv = np.zeros(nj*ni, dtype = np.float64).reshape(nj, ni)
    hs = np.zeros((nj-1)*(ni-1), dtype = np.float64).reshape(nj-1, ni-1)
    zb = 0.25*(zz[0:nj-1,0:ni-1]+zz[1:nj,0:ni-1]+zz[0:nj-1,1:ni]+zz[1:nj,1:ni])
    hh = hs + zb
    
    #　時間ループ
    for it in range(istart, iend):

        #現在時刻            
        ctime = dt*it

        #現時刻の上流端流量・下流端水位設定
        qq = 0  #　scipyなど利用すると様々な補間関数が利用できるがここで暫定値とする

        #出力
        if it % iout == 0:
            print('time:{:.1f} [min]'.format(ctime/60.))
            ier = write_calc_result(ctime, xx, yy, zz, ss, qq, uu, vv, hh, zb, hs)
        

        # 流況更新・河床高更新など
        # 更新される変数は、uu,vv, hh, hs (河床変動が有効の場合zbも)
        




    # ファイルを閉じる
    iric.cg_close(fid)

    return ier

if __name__ == '__main__':
    import time

    if len(sys.argv) == 2:
        start_time = time.time()
        print('> Program starts.')
        if main(sys.argv[1]) == 0:
            process_time = time.time() - start_time
            print('> It took {:.1f} [sec] for this calculation.'.format(process_time)) #2桁まで表示
            # print("It took {}[sec] for this calculation.", process_time)
            print('> Program ended normaly.')
        else:
            print('>>Error : Something\'s wrong.')
    else:
        print('>>Error : Specify the CGNS file as the arguments.')