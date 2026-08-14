# -*- coding: utf-8 -*-
"""PersonaRenderer v2 - 把 MatrAIx 合成人格转成中文自然语言描述（提示词形式）。

用法:
    from persona_render import PersonaRenderer
    r = PersonaRenderer()
    text = r.render(row)        # core 模式：只保留显著特征，~600-900 字
    text = r.render(row, mode='full')   # 全量模式：330 维全部描述

输出示例:
    "性格上非常外向，喜欢与人交往；行事谨慎，决策喜欢听取大家意见。……
     睡眠习惯不规律；轮班制工作，乘坐公共交通通勤；每天屏幕时间超过 8 小时。……"
"""
import json
import os


class PersonaRenderer:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or os.path.dirname(os.path.abspath(__file__))
        self.zh_map = self._load_zh()

    def _load_zh(self):
        p = os.path.join(self.data_dir, 'dimension_map.json')
        if not os.path.exists(p):
            return {}
        with open(p, encoding='utf-8') as f:
            return {e['label']: e['zh'] for e in json.load(f)}

    # ---------------- 取值 -> 程度短语 ----------------
    LEVEL = {'Very high': '非常强', 'High': '较强', 'Average': None,
             'Low': '较弱', 'Very low': '非常弱'}
    LEVEL_BEHAV = {'Very high': '非常多', 'High': '较多', 'Average': None,
                   'Low': '很少', 'Very low': '几乎没有'}
    LEVEL_ENERGY = {'Very high': '非常充沛', 'High': '充沛', 'Average': None,
                    'Low': '不足', 'None': '很差'}
    ATTITUDE = {'Enthusiast': '十分热衷', 'Positive': '持正面态度', 'Neutral': None,
                'Skeptical': '持怀疑态度', 'Opposed': '持反对态度'}
    TRAIT = {'Signature': '非常突出', 'Strong': '比较突出', 'Moderate': None,
             'Slight': '比较弱', 'Absent': '几乎没有'}
    VALUE = {'Core value': 'core', 'Important': 'imp', 'Moderate': None,
             'Minor': 'minor', 'Irrelevant': 'irrelevant'}
    FREQ = {'Daily': '每天', 'Weekly': '每周', 'Monthly': None,
            'Rarely': '偶尔', 'Never': '从不'}
    MBTI = {'INTJ — Architect': 'INTJ 建筑师型', 'INTP — Logician': 'INTP 逻辑学家型',
            'ENTJ — Commander': 'ENTJ 指挥官型', 'ENTP — Debater': 'ENTP 辩论家型',
            'INFJ — Advocate': 'INFJ 提倡者型', 'INFP — Mediator': 'INFP 调停者型',
            'ENFJ — Protagonist': 'ENFJ 主人公型', 'ENFP — Campaigner': 'ENFP 竞选者型',
            'ISTJ — Logistician': 'ISTJ 物流师型', 'ISFJ — Defender': 'ISFJ 守卫者型',
            'ESTJ — Executive': 'ESTJ 总经理型', 'ESFJ — Consul': 'ESFJ 执政官型',
            'ISTP — Virtuoso': 'ISTP 鉴赏家型', 'ISFP — Adventurer': 'ISFP 探险家型',
            'ESTP — Entrepreneur': 'ESTP 企业家型', 'ESFP — Entertainer': 'ESFP 表演者型'}

    # ---------------- 特殊维度：取值 -> 完整短语 ----------------
    SPECIAL = {
        'Dominant trait': {'High openness': '性格开放，乐于接受新事物',
                           'High conscientiousness': '性格尽责，做事有条理',
                           'High extraversion': '性格外向，喜欢与人交往',
                           'High agreeableness': '性格随和，容易相处',
                           'High neuroticism': '性格上比较容易焦虑、情绪波动',
                           'Balanced': None},
        'Risk tolerance': {'Risk-averse': '非常厌恶风险', 'Cautious': '行事谨慎',
                           'Balanced': None, 'Risk-tolerant': '能承受一定风险',
                           'Risk-seeking': '喜欢冒险'},
        'Decision style': {'Analytical': '决策理性，讲究分析', 'Intuitive': '决策凭直觉',
                           'Consensus-driven': '决策喜欢听取大家意见',
                           'Directive': '决策果断直接', 'Deliberative': '决策反复权衡、比较慎重'},
        'Core value': {'Achievement': '把成就看得最重', 'Security': '把安稳看得最重',
                       'Autonomy': '把自由自主看得最重', 'Community': '把社区归属看得最重',
                       'Novelty': '把新鲜体验看得最重', 'Tradition': '把传统看得最重'},
        'Sleep schedule': {'Early bird': '习惯早起，是典型的晨型人', 'Night owl': '作息偏晚，是典型的夜猫子',
                           'Irregular': '睡眠习惯不规律', 'Flexible': '作息灵活，不固定',
                           'Shift-based': '作息随轮班走'},
        'Work schedule': {'9-to-5': '朝九晚五上班', 'Flexible hours': '弹性工时', 'Shift work': '轮班制工作',
                          'On-call': '随时待命', 'Freelance': '自由职业，时间灵活', 'Unemployed': '目前没有工作'},
        'Commute mode': {'Car': '开车通勤', 'Public transit': '乘坐公共交通通勤', 'Bike': '骑车通勤',
                         'Walk': '步行通勤', 'Remote': '远程办公，不用通勤', 'Rideshare': '打车通勤'},
        'Diet type': {'Omnivore': None, 'Flexitarian': '弹性素食，以素为主偶尔吃肉',
                      'Vegetarian': '吃素', 'Vegan': '纯素食', 'Pescatarian': '吃鱼素',
                      'Keto/low-carb': '低碳水/生酮饮食'},
        'Shopping style': {'Researcher': '买东西前会做足功课', 'Impulse buyer': '容易冲动消费',
                           'Bargain hunter': '爱淘便宜货', 'Brand loyal': '认准熟悉的品牌',
                           'Minimalist': '崇尚极简，很少购物'},
        'Tidiness': {'Spotless': '家里一尘不染', 'Tidy': '收拾得整整齐齐', 'Lived-in': None,
                     'Cluttered': '家里有点乱', 'Chaotic': '比较邋遢'},
        'Spending vs saving': {'Frugal saver': '很节俭，喜欢存钱', 'Balanced': None,
                               'Spender': '花钱比较大手大脚', 'Splurger': '挥霍型消费'},
        'Social battery': {'Strong introvert': '非常内向', 'Introvert': '偏内向', 'Ambivert': None,
                           'Extrovert': '偏外向', 'Strong extrovert': '非常外向，爱社交'},
        'Daily screen time': {'<2 hrs': '每天屏幕时间少于 2 小时', '2-4 hrs': '每天屏幕时间 2-4 小时',
                              '4-8 hrs': '每天屏幕时间 4-8 小时', '8+ hrs': '每天屏幕时间超过 8 小时'},
        'Morning routine': {'Highly structured': '晨间安排非常规律', 'Loosely structured': '晨间比较随性',
                            'Rushed': '早上总是匆匆忙忙', 'Slow': '早上节奏很慢', 'None': None},
        'Punctuality': {'Always early': '总是提前到', 'On time': '很守时', 'Usually late': '经常迟到',
                        'Unpredictable': '时早时晚，说不准'},
        'Caffeine intake': {'None': '不喝咖啡因饮品', 'Low': '咖啡因摄入很少', 'Moderate': None,
                            'High': '咖啡因摄入较多'},
        'Alcohol use': {'Never': '滴酒不沾', 'Rarely': '很少喝酒', 'Socially': '只在社交场合喝酒',
                        'Regularly': '经常喝酒', 'Heavily': '饮酒量比较大'},
        'Smoking / vaping': {'Never': '不吸烟', 'Former': '以前吸烟，现已戒掉', 'Occasional': '偶尔抽烟',
                             'Regular': '有规律吸烟习惯'},
        'Cooking frequency': {'Daily': '每天自己做饭', 'Weekly': '每周做几次饭', 'Monthly': None,
                              'Rarely': '很少做饭', 'Never': '从不做饭'},
        'Travel frequency': {'Frequent flyer': '经常旅行', 'A few trips/yr': '一年旅行几次',
                             'Occasional': '偶尔旅行', 'Rare': '很少旅行', 'Homebody': '不爱出门，宅家为主'},
        'Pet ownership': {'Dog': '养狗', 'Cat': '养猫', 'Multiple pets': '养了好几只宠物',
                          'Other': '养宠物', 'None': None},
        'Planning horizon': {'Day-to-day': '只看眼前，不做长远打算', 'Weekly': '会做一周左右的规划',
                             'Monthly': '会做月度规划', 'Yearly': '会做年度规划', 'Multi-year': '喜欢做长期规划'},
        'News consumption': {'Constant': '时刻关注新闻', 'Daily': '每天看新闻', 'Weekly': '每周看几次新闻',
                             'Rarely': '很少看新闻', 'Avoids news': '刻意回避新闻'},
        'Streaming hours/week': {'0-2': '每周看 0-2 小时剧/视频', '3-7': '每周看 3-7 小时剧/视频',
                                 '8-15': '每周看 8-15 小时剧/视频', '16+': '每周看 16 小时以上的剧/视频'},
        'Coffee ritual': {'Home brew': '习惯在家自己冲咖啡', 'Café regular': '常去咖啡馆',
                          'Office coffee': '喝办公室咖啡', 'Tea instead': '不喝咖啡，喝茶', 'None': None},
        'Investment style': {'Index investor': '稳健的指数基金投资者', 'Active trader': '喜欢主动交易',
                             'Crypto-heavy': '重仓加密货币', 'Real estate': '偏好房产投资',
                             'Cash saver': '只存钱不投资', 'None': None},
        'Banking style': {'Traditional bank': '用传统银行', 'Neobank': '用数字银行',
                          'Credit union': '用信用合作社', 'Mostly cash': '基本用现金',
                          'Unbanked': '没有银行账户'},
        'Payment preference': {'Credit card': '习惯用信用卡支付', 'Debit card': '习惯用借记卡支付',
                               'Mobile wallet': '习惯用手机支付', 'Cash': '习惯用现金',
                               'BNPL': '习惯先买后付', 'Crypto': '习惯用加密货币支付'},
        'Primary social platform': {'Instagram': '常用 Instagram', 'TikTok': '常用 TikTok',
                                    'X / Twitter': '常用 X（推特）', 'Facebook': '常用 Facebook',
                                    'LinkedIn': '常用 LinkedIn', 'YouTube': '常用 YouTube',
                                    'Reddit': '常用 Reddit', 'None': None},
        'Economic motivation': {'Cost-sensitive': '对价格非常敏感', 'Value-driven': '看重性价比',
                                'Premium-seeking': '追求高品质，愿意多花钱', 'Indifferent': None},
        'Fitness level': {'Athlete': '体能非常好，像运动员', 'Fit': '体能不错', 'Average': None,
                          'Sedentary': '久坐不动，体能较差'},
        'Sleep quality': {'Excellent': '睡眠质量很好', 'Good': '睡眠质量不错', 'Fair': None,
                          'Poor': '睡眠质量差'},
        'Mental health': {'Thriving': '心理状态非常好', 'Stable': '心理状态稳定', 'Struggling': '心理上有些挣扎',
                          'In crisis': '心理状态不佳'},
        'Political lean': {'Left': '政治倾向偏左', 'Center-left': '政治倾向中偏左', 'Center': None,
                           'Center-right': '政治倾向中偏右', 'Right': '政治倾向偏右', 'Apolitical': '不关心政治'},
        'Religiosity': {'Secular': '不信教', 'Spiritual': '相信灵性但不属于特定宗教',
                        'Observant': '有宗教生活', 'Devout': '非常虔诚', 'Prefer not to say': None},
        'Emotional state': {'Calm': None, 'Curious': '情绪上比较好奇', 'Frustrated': '有些烦躁',
                            'Anxious': '有些焦虑', 'Excited': '情绪比较高涨', 'Skeptical': '带有怀疑',
                            'Urgent': '处于紧迫状态'},
        'Hobby intensity': {'Obsessive': '对爱好非常痴迷', 'Dedicated': '爱好投入度很高', 'Casual': None,
                            'Dabbler': '什么爱好都浅尝辄止', 'None': None},
        'Charitable giving': {'Regular donor': '定期捐款做慈善', 'Occasional': '偶尔捐款',
                              'Rare': '很少捐款', 'Never': None},
        'Volunteering': {'Daily': '几乎天天做志愿服务', 'Weekly': '每周做志愿服务', 'Monthly': None,
                         'Rarely': '偶尔做志愿服务', 'Never': None},
        'Myers-Briggs type': {},
        'General health': {'Excellent': '身体健康状况很好', 'Good': '身体健康', 'Fair': '身体一般',
                           'Poor': '身体不太好'},
        'Chronic condition': {'None': None, 'Managed': '有慢性病，控制得不错',
                              'Multiple': '有多种慢性病', 'Undiagnosed concerns': '有些未确诊的健康问题'},
        'Chronic pain': {'None': None, 'Mild': '有轻度慢性疼痛', 'Moderate': '有中度慢性疼痛',
                         'Severe': '有严重的慢性疼痛'},
        'Medication use': {'None': None, 'Occasional': '偶尔需要吃药', 'Daily': '每天吃药',
                           'Multiple daily': '每天要吃好几种药'},
        'Dietary restriction': {'None': None, 'Allergy': '有食物过敏', 'Religious': '有宗教饮食限制',
                                'Medical': '有医疗饮食限制', 'Ethical': '有伦理饮食限制'},
        'Caregiver status': {'Not a caregiver': None, 'Child caregiver': '在照顾孩子',
                             'Elder caregiver': '在照顾老人', 'Both': '既要照顾孩子也要照顾老人'},
        'Insurance status': {'Comprehensive': '医保很全面', 'Basic': '有基础医保',
                             'Minimal': '医保覆盖很少', 'Uninsured': '没有医保'},
        'Neurodivergence': {'Neurotypical': None, 'ADHD': '有 ADHD（多动症）', 'Autistic': '有自闭症谱系特质',
                            'Dyslexic': '有阅读障碍', 'Other': '有神经多样性特质'},
        'Attention condition': {'None': None, 'Mild': '注意力略有困难', 'Diagnosed': '有注意力相关诊断'},
        'Mobility': {'Full': None, 'Mild limitation': '行动能力略有受限',
                     'Moderate limitation': '行动能力中度受限', 'Uses mobility aid': '需要行动辅助工具'},
        'Vision': {'Normal': None, 'Corrected': '视力需要矫正', 'Low vision': '视力较差', 'Blind': '失明'},
        'Hearing': {'Normal': None, 'Mild loss': '听力轻度下降', 'Moderate loss': '听力中度下降',
                    'Deaf / hard of hearing': '有听力障碍'},
        'Manual dexterity': {'Full': None, 'Reduced': '手部灵活度下降', 'Limited': '手部灵活度受限',
                             'Assistive needed': '手部需要辅助工具'},
        'Exercise frequency': {'Daily': '每天锻炼', 'Weekly': '每周锻炼', 'Monthly': None,
                               'Rarely': '很少锻炼', 'Never': '从不锻炼'},
        'Energy level': {'Very high': '精力非常充沛', 'High': '精力充沛', 'Moderate': None,
                         'Low': '精力不足', 'None': '经常没精神'},
        'Stress level': {'Very high': '压力非常大', 'High': '压力较大', 'Moderate': None,
                         'Low': '压力较小', 'None': '几乎没压力'},
        'Health literacy': {'Very high': '健康知识很丰富', 'High': '健康知识较丰富', 'Moderate': None,
                            'Low': '健康知识较少', 'None': '对健康知识了解很少'},
        'Cognitive load capacity': {'Very high': '能同时处理很多事情', 'High': '处理多任务能力较强',
                                    'Moderate': None, 'Low': '处理多任务能力较弱', 'None': '很难同时处理多件事'},
        'Assistive technology': {'None': None, 'Screen reader': '使用屏幕阅读器',
                                 'Switch control': '使用开关控制设备', 'Voice control': '使用语音控制',
                                 'Magnifier': '使用放大工具'},
        'Tech savviness': {'Digital native': '科技素养很高，数字原住民', 'Comfortable': '用科技产品很顺手',
                           'Cautious adopter': '对新技术比较谨慎', 'Reluctant': '不太愿意接触新技术',
                           'Avoidant': '回避新技术'},
        'Trust level': {'Trusting': '对人比较信任', 'Verifying': '习惯先验证再相信',
                        'Skeptical': '对人不轻易信任', 'Hostile': '对他人戒备心强'},
        'Safety sensitivity': {'Benign': None, 'Sensitive personal': '对个人敏感信息很谨慎',
                               'High-stakes (medical/legal/financial)': '对医疗/法律/财务等高危场景特别谨慎',
                               'Potentially harmful': '对潜在危害很警觉', 'Dual-use': '对双用途风险敏感'},
    }

    # 与用电/消费/社会行为相关的态度（core 模式输出；full 模式全部态度都输出）
    ATTITUDE_CORE = {
        'Attitude: Renewable energy': '可再生能源', 'Attitude: Electric vehicles': '电动汽车',
        'Attitude: Nuclear energy': '核能', 'Attitude: Climate action': '气候行动',
        'Attitude: New technology': '新技术', 'Attitude: Risk-taking': '冒险',
        'Attitude: Homeownership': '买房置业', 'Attitude: Taking on debt': '举债',
        'Attitude: Consumerism': '消费主义', 'Attitude: Minimalism': '极简主义',
        'Attitude: Fast fashion': '快时尚', 'Attitude: Subscription services': '订阅服务',
        'Attitude: Working from office': '办公室办公', 'Attitude: Remote work': '远程办公',
        'Attitude: Public transit': '公共交通', 'Attitude: Urban density': '城市密度',
        'Attitude: Privacy vs security': '隐私与安全的权衡', 'Attitude: Data privacy': '数据隐私',
        'Attitude: Free markets': '自由市场', 'Attitude: Government regulation': '政府监管',
    }

    # 分组顺序与引导语
    SECTIONS = [
        ('personality', '你的性格与行为风格：'),
        ('values', '你的价值观：'),
        ('attitude', '你对事物的态度：'),
        ('lifestyle', '你的生活习惯：'),
        ('health', '你的健康状况：'),
        ('habits', '你的日常习惯：'),
    ]

    def _section_of(self, label):
        if label in ('Dominant trait', 'Risk tolerance', 'Decision style', 'Core value',
                     'Myers-Briggs type', 'Political lean', 'Religiosity', 'Emotional state',
                     'Trust level', 'Safety sensitivity', 'Tech savviness',
                     'Social battery', 'Planned vs spontaneous', 'Routine vs variety',
                     'Stability vs change', 'Novelty vs familiarity', 'Indoor vs outdoor',
                     'Early vs late adopter', 'Lead vs follow', 'Competition vs collaboration',
                     'Logic vs intuition', 'Speed vs accuracy', 'Quality vs quantity',
                     'Brief vs full detail', 'Big group vs one-on-one', 'Texting vs calling',
                     'Save vs spend', 'City vs nature', 'Team vs solo work', 'Office vs remote',
                     'Need for Cognition', 'Need for Closure', 'Attachment Anxiety',
                     'Attachment Avoidance', 'Interpersonal Agency/Dominance',
                     'Interpersonal Communion/Warmth'):
            return 'personality'
        if label.startswith('Character:') or label.startswith(('BFI-2', 'Big Five')) or label in (
                'Imagination', 'Artistic interest', 'Emotionality', 'Adventurousness', 'Intellect',
                'Liberalism', 'Self-efficacy', 'Orderliness', 'Dutifulness', 'Achievement-striving',
                'Self-discipline', 'Cautiousness', 'Friendliness', 'Gregariousness', 'Assertiveness',
                'Activity level', 'Excitement-seeking', 'Cheerfulness', 'Trust', 'Morality',
                'Altruism', 'Cooperation', 'Modesty', 'Sympathy', 'Anxiety', 'Anger', 'Depression',
                'Self-consciousness', 'Immoderation', 'Vulnerability'):
            return 'personality'
        if label.startswith('Value:') or label.startswith('Schwartz') or label.startswith('SDT'):
            return 'values'
        if label.startswith('Attitude:') or label.startswith('Moral Foundation') or label.startswith('DOSPERT'):
            return 'attitude'
        if label.startswith('Habit:'):
            return 'habits'
        if label in ('Sleep schedule', 'Work schedule', 'Commute mode', 'Diet type', 'Exercise frequency',
                     'Alcohol use', 'Smoking / vaping', 'Caffeine intake', 'Cooking frequency',
                     'Shopping style', 'Travel frequency', 'Pet ownership', 'Daily screen time',
                     'Planning horizon', 'Punctuality', 'Tidiness', 'Spending vs saving',
                     'Charitable giving', 'News consumption', 'Reading frequency', 'Gaming frequency',
                     'Streaming hours/week', 'Music listening', 'Podcast listening',
                     'Primary social platform', 'Primary messenger', 'Device ecosystem',
                     'Primary browser', 'Payment preference', 'Banking style', 'Investment style',
                     'Active subscriptions', 'Coffee ritual', 'Fashion sense', 'Hobby intensity',
                     'Vacation style', 'Morning routine', 'Volunteering', 'Economic motivation'):
            return 'lifestyle'
        if label.startswith(('General health', 'Chronic', 'Mobility', 'Vision', 'Hearing', 'Color vision',
                             'Manual dexterity', 'Mental health', 'Stress level', 'Energy level',
                             'Sleep quality', 'Chronic pain', 'Medication use', 'Dietary restriction',
                             'Neurodivergence', 'Caregiver', 'Health literacy', 'Insurance status',
                             'Fitness level', 'Cognitive load', 'High-contrast', 'Large-text',
                             'Assistive', 'Motion sensitivity', 'Attention condition')):
            return 'health'
        return None

    def _phrase(self, label, value, mode):
        if not value:
            return None
        # MBTI
        if label == 'Myers-Briggs type':
            return self.MBTI.get(value)
        # 特殊短语
        if label in self.SPECIAL:
            return self.SPECIAL[label].get(value)
        # 态度
        if label.startswith('Attitude:'):
            sub = label[len('Attitude: '):]
            if mode == 'core' and label not in self.ATTITUDE_CORE:
                return None
            zh = self.ATTITUDE_CORE.get(label, self.zh_map.get(label, sub).replace('态度：', ''))
            att = self.ATTITUDE.get(value)
            if att is None:
                return None
            return '对%s%s' % (zh, att)
        # 价值观
        if label.startswith('Value:'):
            zh = self.zh_map.get(label, label).replace('价值观：', '')
            v = self.VALUE.get(value)
            if v is None:
                return None
            if mode == 'core' and v not in ('core', 'imp'):
                return None
            return {'core': '把%s视为核心价值' % zh, 'imp': '比较重视%s' % zh,
                    'minor': '不太在意%s' % zh, 'irrelevant': '完全不在意%s' % zh}[v]
        # 施瓦茨/SDT/道德/风险等等级制
        if label.startswith(('Schwartz', 'SDT', 'Moral Foundation', 'DOSPERT', 'Attachment',
                             'Interpersonal', 'Need for')):
            lv = self.LEVEL.get(value)
            if lv is None:
                return None
            if mode == 'core' and lv == '较强':
                return None
            zh = self.zh_map.get(label, label)
            zh = zh.replace('施瓦茨价值观：', '').replace('自我决定需求：', '').replace('道德基础：', '').replace('风险容忍：', '')
            if label.startswith('SDT'):
                return '对%s%s' % (zh, lv)
            if label.startswith('Schwartz'):
                return '对%s的需求%s' % (zh, lv)
            return '%s%s' % (zh, lv)
        # 大五 / BFI-2 / VIA
        if label.startswith(('BFI-2', 'Big Five')) or label.startswith('Character:') or label in (
                'Imagination', 'Artistic interest', 'Emotionality', 'Adventurousness', 'Intellect',
                'Liberalism', 'Self-efficacy', 'Orderliness', 'Dutifulness', 'Achievement-striving',
                'Self-discipline', 'Cautiousness', 'Friendliness', 'Gregariousness', 'Assertiveness',
                'Activity level', 'Excitement-seeking', 'Cheerfulness', 'Trust', 'Morality',
                'Altruism', 'Cooperation', 'Modesty', 'Sympathy', 'Anxiety', 'Anger', 'Depression',
                'Self-consciousness', 'Immoderation', 'Vulnerability'):
            lv = self.LEVEL.get(value)
            if lv is None:
                return None
            if mode == 'core' and lv in ('较强', '较弱'):
                return None
            zh = self.zh_map.get(label, label)
            zh = zh.replace('大五人格分面：', '').replace('BFI-2：', '').replace('品格优势：', '')
            if label.startswith('Character:'):
                return '%s%s' % (zh, lv)
            return '%s%s' % (zh, lv)
        # 频率类（阅读/游戏/播客/音乐等）
        if label in ('Reading frequency', 'Gaming frequency', 'Music listening',
                     'Podcast listening', 'Active subscriptions', 'Volunteering',
                     'Charitable giving', 'Exercise frequency'):
            fr = self.FREQ.get(value)
            if fr is None:
                return None
            if mode == 'core' and fr == '偶尔':
                return None
            zh = {'Reading frequency': '阅读', 'Gaming frequency': '打游戏',
                  'Music listening': '听音乐', 'Podcast listening': '听播客',
                  'Active subscriptions': None, 'Volunteering': '做志愿服务',
                  'Charitable giving': '捐款', 'Exercise frequency': '锻炼'}[label]
            if zh is None:
                return None
            return '%s%s' % (fr, zh)
        # 兜底：无匹配
        return None

    def render(self, row, mode='core'):
        groups = {name: [] for name, _ in self.SECTIONS}
        for label, value in row.items():
            sec = self._section_of(label)
            if sec is None:
                continue
            ph = self._phrase(label, value, mode)
            if ph:
                groups[sec].append(ph)
        text_parts = []
        for name, lead in self.SECTIONS:
            items = groups[name]
            if not items:
                continue
            text_parts.append(lead + '；'.join(items))
        return '。'.join(text_parts) + '。'


if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from sampler import PersonaSampler
    ps = PersonaSampler()
    r = PersonaRenderer()
    for seed in (42, 7):
        p = ps.sample_persona(seed=seed)
        print('===== seed=%d core 模式 =====' % seed)
        print(r.render(p))
        print()
