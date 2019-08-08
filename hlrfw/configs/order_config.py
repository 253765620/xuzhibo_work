#!coding: utf-8

from hlrfw.configs.ip_config import PORT_DICT

###获取 平台设置链路的串口指令
ORDER_DICT = {
    
    'jtt808' : (
        '-SG000324I00',
        '-SG000324I01IP0:112.17.120.37({0}'.format(PORT_DICT['jtt808']),
        '-',
        '-SG000324I01IP0:(',
        ),
        
    'sirun' : (
        'IOT+L1+SR.PI.NH=?;SR.PI.NP=?',
        'IOT+L1+SR.PI.NH=112.17.120.37;SR.PI.NP={0}'.format(PORT_DICT['sirun']),
        'IOT+S3+PH.M.LINK1=?;',
        'IOT+S1+PH.M.LINK1=sirun.prime,1,TCP',
        'IOT+L1+SR.PI.NH=;SR.PI.NP=;',
        'sirun',
        ' ',
        ),
    
    'd1.xlg':(
        'IOT+L1+SG.PI.NH=?;SG.PI.NP=?;ZDM.NH.PI=?;ZDM.NP.PI=?;',
        'IOT+L1+SG.PI.NH=112.17.120.37;SG.PI.NP={0};ZDM.NH.PI=112.17.120.37;ZDM.NP.PI={1};'.format(PORT_DICT['sharengo'],PORT_DICT['zdmon']),
        'IOT+S3+PH.M.LINK1=?;PH.M.LINK2=?;',
        'IOT+S1+PH.M.LINK1=sharengo.prime,1,TCP;PH.M.LINK2=zdmon.pivar,1,TCP',
        'IOT+L1+SG.PI.NH=;SG.PI.NP=;ZDM.NH.PI=;ZDM.NP.PI=;',
        'IOT+L1+SG.PI.NH=;SG.PI.NP=;ZDM.NH.PI=;ZDM.NP.PI=;',
        ),
    
    'gbtele and jtt808'  :(
        'IOT+L1+GE.PI.NA=?;GE.PI.NP=?;',
        'IOT+L1+GE.PI.NA=112.17.120.37;GE.PI.NP={0};'.format(PORT_DICT['gbtele']),
        'IOT+S3+PH.M.LINK1=?;PH.M.LINK2=?;',
        'IOT+S1+PH.M.LINK1=jtt808.prime,1,TCP;PH.M.LINK2=gbtele.prime,1,TCP',
        'IOT+L1+GE.PI.NA=;GE.PI.NP=;',
        'gbtele',
        'jtt808',
        ), 
    'gbtele'  :(
        'IOT+L1+GE.PI.NA=?;GE.PI.NP=?;',
        'IOT+L1+GE.PI.NA=112.17.120.37;GE.PI.NP={0};'.format(PORT_DICT['gbtele']),
        'IOT+S3+PH.M.LINK1=?;',
        'IOT+S1+PH.M.LINK1=gbtele.prime,1,TCP',
        'IOT+L1+GE.PI.NA=;GE.PI.NP=;',
        'gbtele',
        ' ',
        ), 
    }
