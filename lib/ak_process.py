# -*- coding: utf-8 -*-
from logging import getLogger


log = getLogger('Doctopus.ak_process')


code_dict = {
    # emergency stop errors
    1: "Over temperature in the Power Control Cabinet",
    5: "Brush abrasion GPM",
    9: "Motor temperature GPM",
    17: "Power supply",
    18: "False roller direction",
    22: "Direction of current",
    26: "Max. tractive force of the roller",
    30: "Max. tractive force of test stand",
    # quick stop errors
    1001: "CMOS – battery empty!",
    1010: "Compressed air",
    1011: "Max. speed of the vehicle",
    1012: "Max. speed of the roller",
    # warnings
    2005: "Static converter cannot be switched on",
    2009: "Early warning for motor temperature",
    2013: "Wheel base unit",
    2017: "EMERGENCY STOP",
    2018: "Valve lift 1 → release",
    2019: "Valve lift 2 → release",
    2020: "Valve lift 1 raise", 
    2021: "Valve lift 1 lower",
    2022: "Valve lift 2 raise",
    2023: "Valve lift 2 lower",
    2024: "Limit up position lift 1",
    2025: "Limit up position lift 2",
    2026: "Limit down position lift 1",
    2027: "Limit down position lift 2",
    2028: "GPM ventilator",
    2032: "Human protection",
    2036: "Coupling flywheel mass 0 (balancing mass)",
    2037: "Coupling flywheel mass 1",
    2038: "Coupling flywheel mass 2",
    2039: "Coupling flywheel mass 3",
    2040: "Coupling flywheel mass 4",
    2041: "Coupling flywheel mass 5",
    2042: "Coupling flywheel mass 6",
    2043: "Coupling left GPM 1",
    2045: "Coupling left GPM 2",
    2047: "Coupling left Roller 1",
    2049: "Coupling left Roller 2",
    2051: "Locking left coupling axle 1" ,
    2053: "Locking left coupling axle 2",
    2055: "Locking flywheel mass 0 (balancing mass)",
    2056: "Locking flywheel mass 1",
    2057: "Locking flywheel mass 2",
    2058: "Locking flywheel mass 3",
    2059: "Locking flywheel mass 4",
    2060: "Locking flywheel mass 5",
    2061: "Locking flywheel mass 6",
    2062: "Remote control cannot be activated",
    2063: "Control voltage (24V-supply)", 
    2064: "Over temperature ZSS",
    2065: "Vehicle cooling fan 1",
    2066: "Vehicle cooling fan 2",
    2067: "Tractive force measuring device cannot be selected",
    2075: "Tractive force measuring fault",
    2079: "Fault in static converter",
    2083: "Interface error Static converter → Controller VECON",
    2087: "Deviation of 0.5 percent of full scale in zero point adjustment of the tractive force",
    2091: "Deviation of 0.5 percent f full scale after loading of the tractive force measuring device with a calibration weight",
    2146: "CMOS – battery voltage too low",
}

order_dict = {
    "SREV": "backwards",
    "SVOR": "forward",
}

def process_AGST(data):
    """
    process AGST data to grade
    """
    d_list = data.split()

    data_handle = {
        "grade": float(d_list[0]),
    }

    return data_handle


def process_ASTF(data):
    """
    process ASTF data to warning and warning_string
    """
    codes = data.split()
    warning = 0
    warning_string = ''
    for code in [int(code) for code in codes]:
        warn_word = _dict_get(code, code_dict)
        warning_string = warning_string + warn_word

    if warning_string:
        warning = 1
    
    data_handle = {
        "warning": warning,
        "warning_string": warning_string       
    }

    return data_handle


def _dict_get(code, code_dict):
    """
    handle value by different key case
    """
    if code > 2000:
        suffix = ' warning;'
    elif code > 1000:
        suffix = ' quick stop error;'
    else:
        suffix = ' emergency stop error;'
    
    word = code_dict.get(code, '')
    
    if word:
        word = word + suffix
    
    return word
    

def process_ASIE(data):
    pass

def process_ASME(data):
    """
    process ASME data to F0, F1, F2, n 
    """
    F0, F1, F2, _, f0, f1, f2, _,= data.split()
    data_handle = {
        "F0": float(F0),
        "F1": float(F1),
        "F2": float(F2),
        "f0": float(f0),
        "f1": float(f1),
        "f2": float(f2),
    }

    return data_handle


def process_ASTZ(data):
    """
    process ASTZ data to mode, direction
    """
    d1, d2, d3, d4, d5, d6, d7 = data.split()[0:7]
    
    direction = order_dict.get(d6, "undefined")
    mode = d2

    if mode == 'STBY':
        status = 0
    else:
        status = 1

    data_handle = {
        "mode": d2,
        "direction": direction,
        "status": status,
    }
    
    return data_handle


# def process_AVFI(data):
#     """
#     process data to speed and tractive_force
#     """
#     speed, tractive_force = data.split(' ')

#     data_handle = {
#         "speed": float(speed),
#         "tractive_force": tractive_force
#     }
    
#     return data_handle


def process_AWRT(data):
    """
    process AWRT data to actual_speed ,actual_tractive_force, weight, status
    """
    actual_speed, actual_tractive_force, _, weight, _ = data.split()

    # calculate status by speed

    data_handle = {
        "actual_speed": float(actual_speed), 
        "actual_tractive_force": float(actual_tractive_force),
        "weight": float(weight),
    }
    
    return data_handle
    
process = b'198522(30) 44.43 0.2887 0.03132 2.00 -4.8 -0.0260 -0.00256 1700.00 SVOR SKA1 2903 AS16PV04  2017-9 90.50 0.2290 0.03170 2.00 -4.8 -0.0260 -0.00256 1600.00 SVOR S2HI 2860 BYD-tang -34.76 -2.3375 0.04796 2.00 -4.8 -0.0260 -0.00256 2280.00 SVOR S4ON\
            2721 DU15OV10 -19.76 0.4299 0.04024 2.00 -4.8 -0.0260 -0.00256 1800.00 SVOR S4ON 2747 DU17PV01 29.48 -0.0317 0.04220 2.00 -4.8 -0.0260 -0.00256 1700.00 SVOR SKA1 2749 DU18IV02 -15.35 -0.0353 0.04073 2.00 -4.8 -0.0260 -0.00256 1700.00 SVOR SKA1 2724 DU18NV004 0.00 0.0000 0.00000 1.00 -4.8 -0.0260 -0.00256 0.00 SVOR S4ON 0 DU18NV004 -2017- 35.15 0.3023 0.03961 2.00 -4.8 -0.0260 -0.00256 1683.00 SVOR S2VO 2724 DU18OV009 -15.35 -0.0353 0.04073 2.00 -4.8 -0.0260 -0.00256 1730.00 SVOR S4ON 2725 DU19IV004 29.73 0.0220 0.04207 2.00 -4.8 -0.0260 -0.00256 1736.00 SVOR SKA1 2725 DU19IV004-RDE 29.73 0.0220 0.04207 2.00 -4.8 -0.0260 -0.00256 2002.50\
            SVOR SKA1 2725 DU19IV023 0.00 0.0000 0.00000 1.00 -4.8 -0.0260 -0.00256 1692.90 SVOR SKA1 2715 DU19IV025 22.16 0.5208 0.03826 2.00 -4.8 -0.0260 -0.00256 1683.00 SVOR SKA1 2725 DU19IV025-1 24.38 0.5729 0.04208 2.00 -4.8 -0.0260 -0.00256 1683.00 SVOR SKA1 2725 EPA 97-08  2000 38.37 -1.6335 0.05209 2.00 -4.8 -0.0260 -0.00256 907.20 SVOR S2VO 2589 EPA 97-08  6000 247.21 -4.4031 0.12056 2.00 -4.8 -0.0260 -0.00256 2721.60 SVOR S2VO 3000 EPA 97-8C  2000 66.72 0.0000 0.00000 2.00 -4.8 -0.0260 -0.00256 907.20 SVOR S2VO\
            3000 EPA 97-8C  6000 834.04 0.0000 0.00000 2.00 -4.8 -0.0260 -0.00256 2721.60 SVOR S2VO 3000 ES1 38.37 -1.6335 0.05209 2.00 -4.8\
            -0.0260 -0.00256 907.20 SVOR S2VO 2589 ES12SV61 143.04 0.4615 0.03528 2.00 -4.8 -0.0260 -0.00256 1700.00 SVOR S2VO 2736 ES17IV08\
            39.30 0.0869 0.04024 2.00 -4.8 -0.0260 -0.00256 1700.00 SVOR S4ON 2750 FH17OV052 70.87 -0.3128 0.03257 2.00 -4.8 -0.0260 -0.00256 1700.00 SVOR S2VO 2695 FUTE FORCE 81.35 0.6358 0.04718 2.00 -4.8 -0.0260 -0.00256 1360.00 SVOR S2VO 2795 GS19IV032 6.23 0.3102 0.02832 2.00 -4.8 -0.0260 -0.00256 1090.00 SVOR S2VO 2610 GS19IV08-2 90.50 0.2290 0.03170 2.00 -4.8 -0.0260 -0.00256 1250.00 SVOR\
            S2VO 2611 GU17PV03 -67.27 1.3297 0.03193 2.00 -4.8 -0.0260 -0.00256 1590.00 SVOR S2VO 2556 JILI 65.75 0.6091 0.03240 2.00 -4.8 -0.0260 -0.00256 1700.00 SVOR S2VO 2649 JU20IV023 27.07 -0.4929 0.04489 2.00 -4.8 -0.0260 -0.00256 1430.00 SVOR S2VO 2568 KH18SV004 49.72 -0.2477 0.03235 2.00 -4.8 -0.0260 -0.00256 1360.00 SVOR S2VO 2661 KH19OV111 55.47 -0.0589 0.03308 2.00 -4.8 -0.0260 -0.00256 1590.00 SVOR S2VO 2670 KH19OV111-IV 59.79 0.5864 0.02525 2.00 -4.8 -0.0260 -0.00256 1590.00 SVOR S2VO 2670 KH19OV111-TA 54.12\
            -0.1001 0.03341 2.00 -4.8 -0.0260 -0.00256 1590.00 SVOR S2VO 2670 KH19OV111-VTS 43.33 -0.4925 0.03639 2.00 -4.8 -0.0260 -0.00256\
            1590.00 SVOR S2VO 2670 KM17PV005 -89.12 0.1568 0.03361 2.00 -4.8 -0.0260 -0.00256 1666.00 SVOR S2VO 2795 KS16PV022 51.88 -0.2345\
            0.03195 2.00 -4.8 -0.0260 -0.00256 1360.00 SVOR S2VO 2598 KS16PV024 35.71 -0.0471 0.03125 2.00 -4.8 -0.0260 -0.00256 13000.00 SVOR S2VO 2600 KS17NV62 53.72 0.0785 0.02685 2.00 -4.8 -0.0260 -0.00256 1360.00 SVOR SKA1 2701 KS18SV009 42.74 0.2375 0.03219 2.00 -4.8 -0.0260 -0.00256 1751.00 SVOR S2VO 2641 KS19IV014 43.46 -0.2474 0.03307 2.00 -4.8 -0.0260 -0.00256 1360.00 SVOR S2VO 2640 LH19MV11 48.98 0.0409 0.03523 2.00 -4.8 -0.0260 -0.00256 1540.00 SVOR S2VO 2660 LM17IV09 38.37 -1.6335 0.05209 2.00 -4.8 -0.0260 -0.00256 907.20 SVOR S2VO 2796 LS15NV10-GVW 29.01 -0.7300 0.03409 2.00 -4.8 -0.0260 -0.00256 1690.00 SVOR S4ON 2641 LS15NV10-LVW 33.06 -0.2992 0.03220 2.00 -4.8 -0.0260 -0.00256 1250.00 SVOR S2VO 2590 LS17MV03 46.05 0.2688 0.02921 2.00 -4.8 -0.0260 -0.00256 1440.00 SVOR S2VO 2641 LS17MV03 46.05 0.0747 0.00225 2.00 -4.8 -0.0260 -0.00256 1440.00 SVOR S4ON 2640 OW16BV003(1) 69.95 0.3943 0.03436 2.00 -4.8 -0.0260 -0.00256 1590.00 SVOR SKA1 2790 OW16IV003 24.88 0.6268 0.03526 2.00 -4.8 -0.0260 -0.00256 1590.00 SVOR SKA1 2791 PIKA  SK8103EP25 7.04 -0.6318 0.07698 2.00 -4.8 -0.0260 -0.00256 1810.00 SVOR S2HI 3132 RS16IV40 0.00 0.0000 0.00000 2.00\
            -4.8 -0.0260 -0.00256 1000.00 SVOR S2VO 2639 RS16IV74 37.81 0.0345 0.03032 2.00 -4.8 -0.0260 -0.00256 1360.00 SVOR S2VO 2598 RS20MV004 44.93 -0.1438 0.03248 2.00 -4.8 -0.0260 -0.00256 1360.00 SVOR S2VO 2628 SV71-07 118.96 2.1864 0.04110 2.00 -4.8 -0.0260 -0.00256 2950.00 SVOR S2HI 3198 SV81 268.53 -0.2832 0.06412 1.00 -4.8 -0.0260 -0.00256 3050.00 SVOR S2HI 3155 SV91-6mt-rear-dr 268.53 -0.2832 0.06412 1.00 -4.8 -0.0260 -0.00256 2755.00 SVOR S2HI 2950 SV91EV63 73.84 -0.0848 0.04388 2.00 -4.8 -0.0260 -0.00256 2190.00 SVOR S2HI 2949 UM19IV001 50.90 0.1113 0.04665 2.00 -4.8 -0.0260 -0.00256 2161.00 SVOR S2VO 3088 UM19IV202 13.90 1.4817 0.03781 2.00 -4.8 -0.0260 -0.00256 2050.00 SVOR S2VO 3085 UW17IV02 16.09 0.9825 0.04452 2.00 -4.8 -0.0260 -0.00256 1910.00 SVOR S2VO 3088 UW19IV006 5.47 0.5247 0.04359 2.00 -4.8 -0.0260 -0.00256 2091.00 SVOR SKA1 3085 V5 145.01 -0.0263 0.03335 2.00 -4.8 -0.0260 -0.00256 1700.00 SVOR S4ON 2694 Zero 0.00 0.0000 0.00000 2.00 -4.8 -0.0260 -0.00256 2400.00 SVOR S4ON 3000 cu18ov12 68.23 0.1788 0.04293 2.00 -4.8 -0.0260 -0.00256 2040.00 SVOR S4ON 2857 es16ov97 63.31 0.1933 0.02835 2.00 -4.8 -0.0260 -0.00256 1840.00 SVOR S2VO 2836 ju20iv023 27.07 -0.4929 0.04489 2.00 -4.8 -0.0260 -0.00256 1430.00 SVOR S2VO 2568 kh19iv027 42.74 0.2375 0.03219 2.00 -4.8 -0.0260 -0.00256 1751.00 SVOR S2VO 2671 ks16nv017 42.72 -0.2448 0.03205 2.00 -4.8 -0.0260 -0.00256 1360.00 SVOR S2VO 2600 ks18iv52 55.47 -0.0589 0.03308 2.00 -4.8 -0.0260 -0.00256 1590.00 SVOR S2VO 2670 ks18iv52 39.74 0.3699 0.02486 1.00 -4.8 -0.0260 -0.00256 1370.00 SVOR S2VO 2680'

def process_ASIA(data=process):
    """
    make keys :
    "198522(30) 44.43 0.2887 0.03132 2.00 -4.8 -0.0260 -0.00256 1700.00 SVOR SKA1 2903"

    以“2.00” 进行分界
    """
    data_list = data.split("2.00")
    # log.debug(data_list)

    data_handle = {}
    for model_string in data_list:
        model_dict = _make_redis_vin_dict(model_string)
        data_handle.update(model_dict)
    # print(data_handle)
    return data_handle


def _make_redis_vin_dict(model_string):
    """
    make redis key
    mode_string:
    ' -4.8 -0.0260 -0.00256 1440.00 SVOR S2VO 2641 LS17MV03 46.05 0.0747 0.00225 '

    """
    model_list = model_string.split()
    model_list_handle = model_list[len(model_list)-4:len(model_list)]
    # print(model_list_handle)
    value = model_list_handle[0]
    key = '_'.join(model_list_handle[1:])
    
    data_handle = {key:value}
    return data_handle

process_methods_dict = {
    "ASTF": process_ASTF ,
    "ASTZ": process_ASTZ ,
    "ASIE": process_ASIE ,
    "ASME": process_ASME ,
    "ASIA": process_ASIA ,
    "AWRT": process_AWRT ,
    "AGST": process_AGST ,
}

if __name__ == '__main__':
    process_ASIA(process.decode('utf-8'))
