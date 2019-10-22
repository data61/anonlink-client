import clkhash
from poc.filter import filter_signatures
from poc.block_filter_generator import candidate_block_filter_from_signatures
from poc.server import compute_blocking_filter
from poc.signature_generator import compute_signatures
from recordlinkage.datasets import load_febrl4


def compute_candidate_block_filter(data, blocking_config):
    """

    :param data:
    :param blocking_config:
    :return:
        A 3-tuple containing:
        - the candidate block filter (CBF) and
        - a dict mapping block index (e.g. index in the cbf) to the list of
          signatures that are associated with that cbf location, and
        - a dict mapping signatures to records
    """
    signature_config = blocking_config['signature']
    filter_config = blocking_config['filter']
    config = blocking_config['candidate-blocking-filter']

    candidate_signatures = compute_signatures(data, signature_config)
    signatures = filter_signatures(candidate_signatures, filter_config)
    return candidate_block_filter_from_signatures(signatures, config)


def filter_reverse_index(block_filter, bf_map, sig_rec_map):
    """

    :param block_filter: The combined blocking filter - a numpy bool array.
    :param bf_map: Dict mapping block id to list of signatures.
    :param sig_rec_map: Dict mapping signatures to records.
    :return:
        Dict mapping block id to list of records.
    """
    return {}



def run_gender_blocking():

    blocking_config = {
        'signature': {
            # 'type': 'feature-value',
            'type': 'p-sig',
            'feature-index': 3,
            'config': {
                'num_hash_funct': 5,
                'bf_len': 2048,
                'attr_select_list': [3],
                'max_occur_ratio': 1.0,
                'min_occur_ratio': 0.001,
            }
        },
        'filter': {
            'type': 'none'
            # 'type': 'frequency',
            # 'min': 2,
            # 'max': 1000
        },
        'candidate-blocking-filter': {
            'type': 'dummy',
            'filter-length': 2,
            'values': ['5104', '3856', '3045', '2387', '5079', '2300', '3182', '2147', '2154', '6405', '3164', '5048',
                       '2171', '5453', '2584', '3130', '4869', '4454', '2257', '2619', '2162', '6159', '4725', '6147',
                       '2608', '3215', '4068', '4737', '6362', '4750', '5371', '2285', '6714', '4035', '2534', '2174',
                       '0870', '2161', '2075', '3123', '6275', '5054', '6018', '3231', '3550', '2326', '2615', '3039',
                       '6196', '6102', '2215', '6112', '3041', '3083', '3101', '3765', '4119', '2198', '4680', '3490',
                       '2216', '3151', '2365', '3204', '4061', '7004', '2098', '2042', '6022', '3630', '4897', '2904',
                       '2298', '2859', '6071', '2641', '3113', '6163', '2631', '5041', '4027', '2025', '2402', '2600',
                       '4110', '5461', '3620', '3227', '5400', '2478', '2767', '3060', '3334', '5091', '3212', '7112',
                       '4507', '6081', '3510', '0835', '7262', '2316', '2824', '4745', '3175', '5600', '4670', '7183',
                       '1413', '6615', '2065', '4511', '3911', '6000', '5022', '2587', '5111', '3942', '2538', '6014',
                       '2306', '4161', '2749', '6180', '2808', '2032', '3023', '3143', '5075', '5141', '5152', '3029',
                       '2151', '3788', '5352', '7173', '2004', '3581', '2120', '2060', '5322', '2141', '2271', '4500',
                       '2839', '4032', '3429', '3953', '5680', '2339', '4812', '2559', '3082', '4578', '3165', '2656',
                       '5014', '7035', '3977', '3669', '7104', '5070', '6064', '6017', '2380', '6311', '3442', '2013',
                       '5089', '4184', '2903', '2776', '3995', '4868', '5355', '4221', '2784', '3975', '3412', '3081',
                       '6056', '7054', '3044', '2426', '3929', '4077', '3146', '3186', '2430', '2396', '4815', '5723',
                       '3754', '4005', '2340', '6021', '4214', '4222', '4810', '2735', '3033', '2400', '3360', '3018',
                       '3040', '0586', '3363', '3111', '4285', '2571', '3414', '2328', '3616', '2618', '3016', '6062',
                       '4152', '2773', '3976', '3218', '3187', '3132', '6774', '2083', '4300', '3009', '3355', '2630',
                       '2821', '5033', '3074', '4151', '3463', '2648', '2119', '3328', '3413', '5690', '2422', '2072',
                       '3076', '4807', '2046', '2104', '3171', '4287', '6063', '4076', '5097', '2207', '2907', '3032',
                       '2537', '4125', '3469', '2137', '2164', '3225', '4708', '2510', '5062', '2574', '3124', '2089',
                       '4806', '5051', '6015', '5032', '2505', '2660', '4078', '6174', '2577', '3884', '5034', '2913',
                       '3934', '5120', '2019', '4109', '2604', '4824', '2370', '3152', '5037', '3420', '2165', '4201',
                       '4165', '2163', '7261', '3207', '4672', '2445', '7440', '4630', '0800', '4470', '2030', '6016',
                       '6552', '4818', '4218', '2847', '6225', '6442', '6052', '4828', '6170', '3026', '3377', '7011',
                       '3617', '2504', '7256', '5082', '2590', '6617', '3139', '3860', '6457', '3089', '6614', '6058',
                       '2130', '3166', '4311', '3185', '3136', '4132', '5280', '3205', '2360', '2256', '3546', '2825',
                       '2390', '4816', '2702', '6069', '2270', '4305', '5252', '2209', '5169', '2842', '2621', '2155',
                       '3981', '3104', '2283', '2323', '5340', '5201', '0821', '5573', '4608', '2675', '3046', '3944',
                       '3523', '4065', '2266', '4490', '4605', '2526', '4120', '4515', '1395', '7307', '5076', '3337',
                       '6019', '2152', '2354', '3058', '4880', '3931', '5422', '4253', '2150', '2278', '3943', '5031',
                       '3169', '2553', '2284', '2224', '6030', '2084', '3144', '4885', '3073', '2477', '2447', '1479',
                       '7315', '2652', '4171', '2840', '2001', '5068', '4225', '5067', '2466', '2077', '6020', '2484',
                       '3025', '2126', '4207', '5024', '2479', '4133', '2108', '4503', '6002', '4404', '3941', '6057',
                       '6726', '3660', '2106', '2643', '4107', '5046', '2293', '2582', '5608', '4858', '2731', '2127',
                       '7116', '2080', '3179', '2388', '3564', '5112', '6208', '3106', '3730', '2429', '5107', '5126',
                       '2094', '2744', '4730', '2745', '2167', '4075', '2558', '3927', '2872', '2038', '5357', '4811',
                       '2034', '6258', '3614', '6110', '2064', '2024', '4307', '2774', '2138', '4108', '4674', '1382',
                       '5255', '2217', '2871', '6025', '2663', '7027', '2452', '2594', '2870', '4304', '3084', '3501',
                       '6213', '2035', '2240', '6168', '2560', '4551', '3643', '2542', '7006', '5244', '3624', '2486',
                       '2592', '4879', '6101', '5087', '5159', '5260', '2469', '2290', '5148', '2261', '2804', '4156',
                       '7009', '3102', '7017', '4178', '2111', '3851', '2529', '4350', '2223', '2640', '2213', '4557',
                       '5523', '7310', '3196', '3909', '2332', '2190', '5235', '5006', '5019', '6306', '2455', '2601',
                       '6105', '4073', '4558', '4753', '4226', '3085', '5052', '2088', '3268', '2016', '6355', '3200',
                       '2287', '8235', '6070', '3916', '2517', '6525', '4747', '2264', '3162', '3338', '3585', '5010',
                       '2121', '3154', '6512', '2033', '0355', '5607', '4695', '4114', '6333', '4580', '5250', '5558',
                       '3735', '6260', '4850', '0802', '4198', '4865', '2144', '2607', '6059', '3672', '4034', '2665',
                       '3180', '5223', '2222', '5172', '2411', '5008', '5171', '6167', '4800', '3014', '3644', '4217',
                       '6140', '2010', '3639', '2158', '2073', '2145', '2565', '2830', '2715', '3190', '2048', '3666',
                       '2267', '2228', '3173', '3807', '7171', '3160', '2545', '2230', '4660', '4007', '3216', '6055',
                       '4830', '7212', '3066', '5049', '2302', '2193', '2066', '6155', '5631', '4124', '9316', '2852',
                       '2902', '3126', '7268', '2229', '2606', '3284', '3135', '0828', '3021', '2262', '2502', '2250',
                       '2079', '3070', '7520', '2132', '3818', '3309', '3752', '7130', '6024', '3036', '2514', '4705',
                       '2646', '3311', '4210', '3718', '2823', '2251', '6045', '6298', '4130', '2319', '6201', '4006',
                       '4575', '3803', '2576', '0827', '4579', '5020', '2460', '5028', '3019', '2234', '5197', '6010',
                       '2208', '3691', '4506', '2578', '2333', '4017', '2099', '5023', '2169', '3498', '4043', '3980',
                       '6156', '3107', '2673', '7260', '5162', '4002', '2602', '3345', '2103', '3971', '2450', '3134',
                       '4883', '2754', '3228', '6029', '2212', '6083', '4011', '3265', '3250', '2280', '5127', '3174',
                       '4501', '2666', '3184', '2708', '7000', '2067', '0810', '4821', '5435', '3746', '5095', '6530',
                       '2389', '5158', '3804', '2116', '3088', '6072', '4187', '7120', '7330', '4413', '3260', '2168',
                       '2176', '3984', '1296', '2039', '5155', '6720', '3444', '4013', '2877', '2320', '3155', '7301',
                       '6085', '2027', '5353', '4271', '3917', '2259', '2444', '4788', '5365', '4153', '2931', '7320',
                       '2627', '3810', '5098', '4356', '3129', '6450', '2810', '5063', '7051', '3516', '2195', '6220',
                       '5290', '3226', '3142', '2248', '2324', '3122', '2087', '7024', '4741', '4306', '3724', '4662',
                       '2777', '2657', '2395', '4066', '2014', '4502', '3068', '2580', '4116', '3116', '4179', '0864',
                       '5124', '7010', '2480', '3158', '4164', '4565', '2282', '5271', '3087', '2783', '2850', '1409',
                       '4113', '3892', '6535', '6436', '1261', '6148', '5698', '5074', '2535', '3418', '3812', '2037',
                       '2539', '2530', '4704', '2146', '0830', '2375', '3831', '6539', '3006', '6065', '3249', '5086',
                       '2831', '1346', '3357', '2820', '5251', '5043', '4172', '5295', '3629', '2603', '3049', '5088',
                       '3178', '6051', '2291', '5113', '3141', '4650', '5096', '5641', '3858', '4154', '2770', '4380',
                       '3809', '4871', '4519', '3375', '2516', '3177', '4516', '3756', '2200', '2157', '3108', '3291',
                       '4242', '4086', '6011', '2181', '2918', '2307', '2090', '2310', '4659', '3069', '4564', '3919',
                       '3222', '2760', '6108', '7410', '3192', '4744', '6169', '3015', '2827', '4121', '7275', '4422',
                       '2763', '3053', '5072', '4819', '3003', '3194', '2275', '3195', '5009', '2736', '4820', '4574',
                       '2700', '2166', '3147', '5109', '4169', '2765', '3766', '3631', '3500', '4709', '2123', '6165',
                       '4209', '5434', '2566', '6203', '4129', '7303', '6026', '3091', '5203', '2214', '2795', '5410',
                       '3020', '2528', '3918', '3939', '6103', '6008', '2792', '2573', '5157', '5333', '2759', '2564',
                       '6012', '2550', '3634', '4872', '3484', '3556', '2485', '5301', '4361', '3002', '5345', '3219',
                       '4655', '2572', '2117', '3109', '5267', '2156', '4223', '2047', '4817', '6171', '4710', '2299',
                       '5732', '2787', '3221', '2335', '2191', '4197', '2440', '4823', '3137', '2031', '3352', '2068',
                       '2115', '2170', '3315', '5902', '3206', '3203', '2642', '5268', '2338', '2044', '5212', '5153',
                       '6285', '3816', '2049', '2305', '3835', '2009', '2327', '0822', '3431', '3952', '3910', '4228',
                       '4614', '5081', '4573', '6111', '3400', '4031', '3293', '5039', '3127', '6620', '3808', '2782',
                       '6722', '2096', '2778', '3930', '2100', '2464', '0328', '2706', '4100', '2605', '6317', '4504',
                       '3024', '3148', '2614', '5418', '5011', '2258', '3022', '4550', '4010', '5576', '6028', '3432',
                       '5170', '4382', '2625', '3285', '2160', '3715', '2321', '6149', '2317', '5108', '5700', '5092',
                       '2036', '2833', '2470', '4021', '6054', '2148', '2766', '5161', '5253', '2790', '3915', '5351',
                       '2063', '3202', '3437', '0237', '4615', '2527', '4220', '5279', '2201', '3658', '4030', '2710',
                       '5806', '3038', '6826', '6084', '2184', '4157', '5341', '2140', '1245', '4112', '2620', '0630',
                       '6352', '7008', '3280', '2008', '3775', '5066', '2177', '2069', '6244', '3242', '2438', '2131',
                       '7179', '5018', '6027', '5175', '3028', '3438', '3736', '2110', '2905', '4106', '3075', '5013',
                       '5084', '3844', '3266', '4212', '2203', '5554', '2026', '4508', '6489', '4625', '4241', '3799',
                       '2076', '7325', '4419', '3097', '3272', '2000', '2225', '0880', '4825', '7101', '2358', '0850',
                       '0280', '2114', '2304', '2105', '3850', '3010', '7270', '3325', '2885', '6096', '3450', '3378',
                       '3777', '4071', '5038', '4571', '4070', '2322', '4700', '6143', '6158', '2015', '5504', '2350',
                       '4044', '3168', '3209', '3000', '4074', '3013', '4280', '2093', '4103', '3714', '2029', '2756',
                       '6320', '2446', '3749', '3390', '5114', '6146', '7053', '4627', '2404', '4520', '5118', '2474',
                       '0832', '7470', '4440', '6324', '2548', '3071', '2192', '4128', '2265', '4140', '5518', '5093',
                       '2173', '3125', '6701', '2762', '4146', '3805', '2041', '2325', '4711', '3159', '3056', '7250',
                       '4000', '2518', '5007', '4018', '3875', '3055', '4102', '2780', '3318', '2018', '3090', '3707',
                       '2086', '2315', '3305', '2515', '2125', '6166', '4122', '3926', '2194', '5080', '6280', '5520',
                       '2050', '4570', '4284', '3043', '3840', '5061', '6200', '4127', '3064', '2622', '4115', '3067',
                       '5259', '7285', '3181', '5356', '3341', '2199', '3740', '2085', '2101', '4059', '2533', '3300',
                       '1350', '0820', '2785', '4802', '2232', '2159', '7190', '2880', '2002', '6338', '5119', '3170',
                       '2496', '9319', '2915', '4600', '2202', '5090', '4251', '2107', '7279', '3978', '3885', '4216',
                       '7030', '3094', '4020', '2494', '2598', '3555', '3465', '3356', '4111', '2133', '2753', '2579',
                       '3921', '2330', '6330', '6003', '5263', '4191', '4715', '7216', '3680', '6104', '4572', '3050',
                       '4607', '3201', '6053', '3264', '4224', '3214', '3781', '6233', '3161', '2610', '2227', '5703',
                       '3912', '6151', '3052', '3925', '4505', '3959', '3099', '1334', '3394', '4054', '3011', '3047',
                       '2775', '2095', '2681', '4230', '2204', '4720', '2869', '3770', '4718', '6100', '5211', '2134',
                       '4170', '5012', '4051', '2761', '0860', '2022', '2758', '4123', '4163', '4852', '5720', '2536',
                       '2303', '4064', '5277', '2231', '3383', '5242', '2211', '2483', '2239', '2456', '5057', '0801',
                       '2611', '2800', '0886', '4370', '3065', '6154', '4019', '3350', '4566', '4014', '6107', '3453',
                       '2449', '4181', '6023', '2226', '2481', '3140', '4610', '4873', '5266', '0846', '5021', '2220',
                       '3012', '3191', '2011', '0276', '2750', '6061', '2525', '4510', '4455', '2021', '3172', '3051',
                       '4722', '2028', '7140', '4421', '4814', '2519', '4406', '2493', '3796', '3121', '5025', '5125',
                       '2409', '2755', '2751', '7109', '3962', '3030', '3078', '6391', '2448', '4805', '3114', '4352',
                       '2143', '3880', '3223', '5241', '3189', '6060', '2092', '4174', '5214', '3551', '4401', '2835',
                       '5605', '3188', '2343', '2645', '4262', '4359', '3561', '4101', '2541', '6602', '6353', '5417',
                       '6210', '4067', '3057', '2653', '2570', '2711', '3193', '2845', '2707', '3183', '3871', '3095',
                       '2233', '4104', '4308', '4860', '3035', '2040', '2052', '3824', '4721', '3424', '2546', '2406',
                       '3220', '3167', '2680', '3079', '3782', '5480', '6076', '4567', '6323', '2206', '2061', '2070',
                       '2556', '4626', '3287', '2940', '2017', '2260', '6264', '0812', '2205', '2113', '4621', '3802',
                       '2112', '2829', '6006', '3340', '3904', '2910', '5556', '2738', '3757', '3825', '3579', '6560',
                       '3133', '6007', '4012', '3496', '3820', '2508', '2458', '3764', '4890', '5045', '3478', '2506',
                       '2292', '5660', '2713', '2020', '5167', '4405', '4053', '5085', '4173', '5264', '5065', '2007',
                       '4301', '6074', '2866', '4576', '5083', '3936', '4096', '2441', '3241', '6075', '6164', '3992',
                       '3842', '5166', '4252', '7122', '7304', '2585', '2219', '6308', '3505', '2443', '2295', '7052',
                       '6009', '7019', '6215', '2794', '6153', '2843', '3335', '7018', '5128', '2768', '3582', '0872',
                       '7205', '2543', '3665', '4702', '5050', '5532', '3059', '3048', '4556', '4773', '2650', '5069',
                       '3138', '2218', '2583', '6707', '4751', '4560', '5073', '3153', '7248', '2454', '5064', '3806',
                       '5116', '4211', '7322', '4371', '2540', '5044', '3198', '3792', '6618', '2102', '6230', '2500',
                       '7050', '5501', '2082', '4160', '3008', '6430', '7249', '2071', '4015', '5213', '2045', '5606',
                       '5604', '7113', '7207', '3149', '3131', '2722', '4037', '4310', '4205', '5343', '2489', '3072',
                       '4060', '7252', '6510', '3304', '5725', '3456', '3690', '2425', '6050', '3364', '4118', '2705',
                       '3603', '3031', '2507', '5433', '5016', '3625', '3889', '4261', '2286', '3728', '3233', '3163',
                       '2142', '9205', '3393', '2342', '2420', '2153', '2817', '4215', '3461', '6152', '4208', '3763',
                       '4069', '2428', '4514', '2263', '6042', '4552', '6150', '4717', '0216', '4213', '6066', '2884',
                       '7300', '6751', '7316', '2337', '2074', '5035', '2520', '2487', '3197', '2575', '4055', '2281',
                       '4870', '4569', '3732', '6415', '4703', '6004', '2359', '2097', '2318', '3199', '5540', '2221',
                       '4808', '3710', '2720', '7184', '3042', '2135', '3150', '5115', '4343', '4585', '3636', '4878',
                       '0836', '2122', '2062', '4158', '6255', '4740', '4701', '2196', '3688', '6172', '2457', '5047',
                       '2197', '3213', '5042', '2289', '2118', '6302', '2617', '2210', '3103', '6001', '6326', '6532',
                       '6136', '2356', '5334', '5330', '6564', '5163', '4016', '4707', '2747', '2357', '3034', '3156',
                       '3128', '4105', '6135', '4390']
        }

    }

    df1, df2 = load_febrl4()
    df1 = df1.fillna('')
    df2 = df2.fillna('')
    data1 = df1.to_dict(orient='split')['data']
    data2 = df2.to_dict(orient='split')['data']
    print("Example PII", data1[0])
    dp1_candidate_block_filter, cbf_map_1 = compute_candidate_block_filter(data1, blocking_config)
    dp2_candidate_block_filter, cbf_map_2 = compute_candidate_block_filter(data2, blocking_config)
    print("Candidate block filter dp1:", dp1_candidate_block_filter)
    print("Candidate block filter dp2:", dp2_candidate_block_filter)
    print("Candidate block filter map 1:", cbf_map_1)
    print("Candidate block filter map 2:", cbf_map_2)

    block_filter = compute_blocking_filter((dp1_candidate_block_filter, dp2_candidate_block_filter))
    print("Block filter:", block_filter)

    dp1_blocks = filter_reverse_index(block_filter, cbf_map_1, 'todo GS? signature -> record mapping')
    dp2_blocks = filter_reverse_index(block_filter, cbf_map_2, 'todo GS? signature -> record mapping')

    #for every dp_pair in ...
    for block_id in dp1_blocks:
        records_1 = dp1_blocks[block_id]
        records_2 = dp2_blocks[block_id]

        print(f"Block {block_id}")
        print("DP 1")
        print(records_1)

        print("DP 2")
        print(records_2)


if __name__ == '__main__':
    run_gender_blocking()
