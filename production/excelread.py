import xlrd
def iccidpy():
    ExcelFile = xlrd.open_workbook(r'/home/pi/production/iccid.xls')
    sheet_name = ExcelFile.sheet_names()[0]
    sheet = ExcelFile.sheet_by_name(sheet_name)
    m = sheet.nrows
    n = sheet.ncols
    with open('/home/pi/production/iccid_sim.py','w') as f:
        f.write('ICCID_SIM={'+'\n')
        for i in range(m):
            for j in range(n):
                k = sheet.cell(i,j).value
                if j== 0:
                    f.write('\''+str(k)+'\':')
                elif j == 1:
                    f.write('\''+str(k)+'\',')
            f.write('\n')
        f.write('}'+'\n')
    # with open('/home/pi/production/iccid_iem.py','w') as f:
    #     f.write('ICCID_IEEM={'+'\n')
    #     for i in range(m):
    #         for j in range(n):
    #             k = sheet.cell(i,j).value
    #             if j== 0:
    #                 f.write('\''+str(k)+'\':')
    #             elif j == 2:
    #                 f.write('\''+str(k)+'\',')
    #         f.write('\n')
    #     f.write('}'+'\n')


