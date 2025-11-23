from otree.api import *
from .configmanager import ConfigManager
from .mk import *
import time
import random
import json

doc = """
Continuous double auction market oTree 5 project with Ambiguous assets, including both SSW market and single-period market.
"""

SINGLE_ASSET_NAME = 'A'


class C(BaseConstants):
    NAME_IN_URL = 'market_ambiguity'
    PLAYERS_PER_GROUP = 9
    NUM_ROUNDS = 10
    random_seed = time.time()

    # list of capital letters A..Z
    asset_names = [chr(i) for i in range(65, 91)]
    config_fields = {
        'round_number': int,
        'period_length': int,
        'num_assets': int,
        'num_states': int,
        'asseta_endowments': str,
        'assetb_endowments': str,
        'assetc_endowments': str,
        'assetd_endowments': str,
        'cash_endowment': str,
        'practice': bool,
        'a1': int,
        'a2': int,
        'a3': int,
        'b1': int,
        'b2': int,
        'b3': int,
        'c1': int,
        'c2': int,
        'c3': int,
        'd1': int,
        'd2': int,
        'd3': int,
        'p1': float,
        'p2': float,
        'p3': float,
        'p0': float,
        'state_independent': bool,
        'ssw_inherit': bool,
        'treatment': str,
    }


def creating_session(self):
    config_addr = 'market_ambiguity/configs/' + \
                  self.session.config['config_file']
    config_manager = ConfigManager(config_addr)
    self.num_rounds = config_manager.num_rounds
    if self.round_number > self.num_rounds:
        return

    self.set_properties(config_manager.get_round_dict(
        self.round_number, C.config_fields))
    for p in self.get_players():
        p.set_endowments()
    return


class Subsession(BaseSubsession):
    period_length = models.IntegerField()
    num_assets = models.IntegerField()
    num_states = models.IntegerField()
    asseta_endowments = models.StringField()
    assetb_endowments = models.StringField()
    assetc_endowments = models.StringField()
    assetd_endowments = models.StringField()

    cash_endowment = models.StringField()
    practice = models.BooleanField()

    a1 = models.IntegerField()
    a2 = models.IntegerField()
    a3 = models.IntegerField()

    b1 = models.IntegerField()
    b2 = models.IntegerField()
    b3 = models.IntegerField()

    c1 = models.IntegerField()
    c2 = models.IntegerField()
    c3 = models.IntegerField()

    d1 = models.IntegerField()
    d2 = models.IntegerField()
    d3 = models.IntegerField()

    p1 = models.FloatField()
    p2 = models.FloatField()
    p3 = models.FloatField()
    p0 = models.FloatField()

    state_independent = models.BooleanField()
    ssw_inherit = models.BooleanField()
    treatment = models.StringField()

    state_a = models.IntegerField()
    state_b = models.IntegerField()
    state_c = models.IntegerField()
    state_d = models.IntegerField()

    num_rounds = models.IntegerField()

    # 第一页结果存储
    round_selected_player_id_page1 = models.IntegerField(default=-1)
    round_selected_color_page1 = models.StringField(default="")
    round_selected_color_css_page1 = models.StringField(default="")

    # 第二页结果存储
    round_selected_player_id_page2 = models.IntegerField(default=-1)
    round_selected_color_page2 = models.StringField(default="")
    round_selected_color_css_page2 = models.StringField(default="")

    # 控制是否跳过第二页的标记
    skip_page2 = models.BooleanField(default=False)
    
    def color_to_state(self):
        """根据最终结果返回对应状态"""
        if self.skip_page2:
            # 第一页结果有效（黑色）
            color_map = {'黑色': 0}  # 黑色对应状态0
            return color_map.get(self.round_selected_color_page1, 0)
        else:
            # 第二页结果有效（红/黄/蓝）
            color_map = {'红色': 1, '黄色': 2, '蓝色': 3}  # 对应状态1-3
            return color_map.get(self.round_selected_color_page2, 0)

    def asset_names(self):
        return C.asset_names[:self.num_assets]

    def get_state(self, r):
        if r < self.p0:
            return 0
        elif r - self.p0 < self.p1:
            return 1
        elif r - self.p0 - self.p1 < self.p2:
            return 2
        else:
            return 3

    def get_asset_return(self, asset, group):
        """状态0（黑色）→ 所有资产不付息"""
        if not group:
            return 0
        try:
            current_state = group.color_to_state()
            # 强制状态0时返回0（不付息）
            if current_state == 0:
                return 0
            current_state = current_state if isinstance(current_state, int) and 1 <= current_state <= 3 else 0
        except Exception:
            return 0  # 异常情况也不付息

        # 资产A的股息（从CSV的a1/a2/a3读取，对应状态1-3）
        if asset == 'A':
            # 状态0：CSV中无a0，暂设为0（若有实际值，替换为对应字段）
            if current_state == 0:
                return 0  # 或 self.a0（若CSV有a0列）
            # 状态1→a1，状态2→a2，状态3→a3（严格对应CSV预设）
            elif current_state == 1:
                return self.a1
            elif current_state == 2:
                return self.a2
            elif current_state == 3:
                return self.a3
                # 资产B的股息（若需要，参考资产A逻辑，从CSV的b1/b2/b3读取）
        elif asset == 'B':
            if current_state == 0:
                return 0  # 或 self.b0
            elif current_state == 1:
                return self.b1
            elif current_state == 2:
                return self.b2
            elif current_state == 3:
                return self.b3
        # if asset == 'A':
        #     if self.state_a == 0:
        #         return 0
        #     elif self.state_a == 1:
        #         return self.a1
        #     elif self.state_a == 2:
        #         return self.a2
        #     else:
        #         return self.a3

        # if asset == 'B':
        #     if self.state_b == 0:
        #         return 0
        #     elif self.state_b == 1:
        #         return self.b1
        #     elif self.state_b == 2:
        #         return self.b2
        #     else:
        #         return self.b3

        # if asset == 'C':
        #     if self.state_c == 0:
        #         return 0
        #     elif self.state_c == 1:
        #         return self.c1
        #     elif self.state_c == 2:
        #         return self.c2
        #     else:
        #         return self.c3

        # if asset == 'D':
        #     if self.state_d == 0:
        #         return 0
        #     elif self.state_d == 1:
        #         return self.d1
        #     elif self.state_d == 2:
        #         return self.d2
        #     else:
        #         return self.d3

    def set_properties(self, round_dict):

        '''
        Set params for the round using round_dict
        '''
        self.period_length = round_dict['period_length']
        self.num_assets = round_dict['num_assets']
        self.num_states = round_dict['num_states']
        self.asseta_endowments = round_dict['asseta_endowments']
        self.assetb_endowments = round_dict['assetb_endowments']
        self.assetc_endowments = round_dict['assetc_endowments']
        self.assetd_endowments = round_dict['assetd_endowments']
        self.cash_endowment = round_dict['cash_endowment']
        self.practice = round_dict['practice']

        self.a1 = round_dict['a1']
        self.a2 = round_dict['a2']
        self.a3 = round_dict['a3']

        self.b1 = round_dict['b1']
        self.b2 = round_dict['b2']
        self.b3 = round_dict['b3']

        self.c1 = round_dict['c1']
        self.c2 = round_dict['c2']
        self.c3 = round_dict['c3']

        self.d1 = round_dict['d1']
        self.d2 = round_dict['d2']
        self.d3 = round_dict['d3']

        self.p1 = round_dict['p1']
        self.p2 = round_dict['p2']
        self.p3 = round_dict['p3']
        self.p0 = round_dict['p0']

        self.state_independent = round_dict['state_independent']
        self.ssw_inherit = round_dict['ssw_inherit']
        self.treatment = round_dict['treatment']

        # Use the current system time as the seed
        # random.seed()
        # r1 = random.random()
        # r2 = random.random() if self.state_independent else r1
        # r3 = random.random() if self.state_independent else r1
        # r4 = random.random() if self.state_independent else r1
        # self.state_a = self.get_state(r1)
        # self.state_b = self.get_state(r2)
        # self.state_c = self.get_state(r3)
        # self.state_d = self.get_state(r4)


class Group(BaseGroup):
    trader_state = models.LongStringField(default="{}")
    trader_state_history = models.LongStringField(default="{}")

    # 核心字段：带明确默认值，避免 None
    round_selected_player_id_page1 = models.IntegerField(default=-1)
    round_selected_color_page1 = models.StringField(default="")
    round_selected_color_css_page1 = models.StringField(default="")
    
    round_selected_player_id_page2 = models.IntegerField(default=-1)
    round_selected_color_page2 = models.StringField(default="")
    round_selected_color_css_page2 = models.StringField(default="")
    
    skip_page2 = models.BooleanField(default=False)  # 布尔字段默认 False，无 null 参数
    
    def color_to_state(self):
        """终极兼容：处理所有可能的 None/空值情况"""
        # 逐层兜底，确保不触发 AttributeError
        skip_page2 = getattr(self, 'skip_page2', False)
        skip_page2 = skip_page2 if skip_page2 is not None else False
        
        color_page1 = getattr(self, 'round_selected_color_page1', "")
        color_page1 = color_page1 if color_page1 is not None else ""
        
        color_page2 = getattr(self, 'round_selected_color_page2', "")
        color_page2 = color_page2 if color_page2 is not None else ""

        if skip_page2:
            return 0 if color_page1.strip() == '黑色' else 0
        else:
            color_map = {'红色': 1, '黄色': 2, '蓝色': 3}
            return color_map.get(color_page2.strip(), 0)

    def period_length(self):
        return self.subsession.period_length

class Player(BasePlayer):

    time = models.FloatField()

    final_selected_round = models.IntegerField(default=-1)

    settled_assets = models.LongStringField(default="{}")
    initial_assets = models.LongStringField(default="{}")
    initial_cash = models.LongStringField(default="{}")
    settled_cash = models.StringField()

    # 第一页点击信息
    clicked_index_page1 = models.IntegerField(default=-1)  # 点击索引
    clicked_color_page1 = models.StringField(default="")    # 点击颜色（中文）

    # 第二页点击信息
    clicked_index_page2 = models.IntegerField(default=-1)
    clicked_color_page2 = models.StringField(default="")

    question_1 = models.IntegerField(
        label="为购买额外一单位资产A，你最多愿意支付多少钱？")
    question_2 = models.IntegerField(
        label="为出售额外一单位资产A，你最少愿意接受多少钱？")
    question_3 = models.IntegerField(
        label="为购买额外一单位资产B，你最多愿意支付多少钱？")
    question_4 = models.IntegerField(
        label="为出售额外一单位资产A，你最少愿意接受多少钱？")

    name = models.StringField(label='姓名')
    gender = models.StringField(
        choices=[['男', '男'], ['女', '女'], ['其他', '其他']],
        label='性别'
    )
    phone_id = models.StringField(
        label='手机号')
    part_id = models.StringField(
        label='座位号')
    venmo_id = models.StringField(label='支付宝账号ID')
    comments = models.LongStringField(
        label='实验的哪些部分让你感到困惑？请列举')
    strategy = models.LongStringField(
        label='请简单介绍你在市场资产交易游戏中的交易策略')

    total_payoff = models.CurrencyField()

    def asset_endowment(self):
        asset_names = self.subsession.asset_names()
        pid = self.id_in_group
        endowments_a = [int(e) for e in self.subsession.asseta_endowments.split(' ') if e]
        endowments_b = [int(e) for e in self.subsession.assetb_endowments.split(' ') if e]
        endowments_c = [int(e) for e in self.subsession.assetc_endowments.split(' ') if e]
        endowments_d = [int(e) for e in self.subsession.assetd_endowments.split(' ') if e]
        assert C.PLAYERS_PER_GROUP == len(
            endowments_a), 'invalid config. number of players and asset length must match'

        endowments = 0
        if len(asset_names) >= 1:
            endowments = [endowments_a[pid - 1]]
        if len(asset_names) >= 2:
            endowments = [endowments_a[pid - 1], endowments_b[pid - 1]]
        if len(asset_names) >= 3:
            endowments = [endowments_a[pid - 1], endowments_b[pid - 1], endowments_c[pid - 1]]
        if len(asset_names) >= 4:
            endowments = [endowments_a[pid - 1], endowments_b[pid - 1], endowments_c[pid - 1], endowments_d[pid - 1]]

        return dict(zip(asset_names, endowments))


    def cash_endowment(self):
        pid = self.id_in_group
        endowments_cash = [int(e) for e in self.subsession.cash_endowment.split(' ') if e]
        endowments = endowments_cash[pid - 1]
        return endowments


    def set_endowments(self):
        '''sets all of this player's cash and asset endowments'''

        asset_endowment = self.asset_endowment()
        if not isinstance(asset_endowment, dict):
            asset_endowment = {SINGLE_ASSET_NAME: asset_endowment}

        self.settled_assets = json.dumps(asset_endowment)
        self.available_assets = json.dumps(asset_endowment)

        cash_endowment = self.cash_endowment()

        self.settled_cash = cash_endowment
        self.available_cash = cash_endowment




class DividendPage1(Page):
    """第一页：显示第一个矩阵+第三个矩阵（黑白逻辑）"""
    form_model = 'player'
    form_fields = ['clicked_index_page1', 'clicked_color_page1']

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds

    def vars_for_template(self):
        treatment = self.subsession.treatment
        parts = treatment.split("_")
        part1 = parts[0] if len(parts) >= 1 else ""

        total_cells = 12 * 12  # 12×12矩阵
        total_rows = 12
        matrix1_original = []  # 第一个矩阵原始数据（0=白，1=黑）
        matrix1_hide_rows = []  # 遮挡行（仅ambi时有效）
        matrix3_data = []       # 第三矩阵数据（基于第一个矩阵）

        # 固定种子确保同轮数据一致
        seed = hash(f"{self.round_number}_{treatment}_page1") % (2**32 - 1)
        random.seed(seed)

        # 生成第一个矩阵
        if part1 == "risk":
            # risk：前3行黑，后9行白（计算概率，作为局部变量）
            black_count = 3 * 12  # 3行×12列=36个黑色
            white_count = total_cells - black_count  # 144-36=108个白色
            # 计算概率（百分比，直接定义为局部变量，不绑定到self）
            black_prob = (black_count / total_cells) * 100  # 25%
            white_prob = (white_count / total_cells) * 100  # 75%
            # 生成矩阵数据
            for i in range(total_cells):
                row = i // 12
                matrix1_original.append(1 if row < 3 else 0)
        else:  # ambi
            # ambi：25%黑，75%白，随机6行遮挡（无需概率）
            matrix1_original = [1 if random.random() < 0.25 else 0 for _ in range(total_cells)]
            matrix1_hide_rows = random.sample(range(total_rows), 6)

        # 乱序第一个矩阵
        shuffled_matrix1 = DividendPage1.shuffle_array(matrix1_original)

        # 第三矩阵：直接使用乱序后的第一个矩阵（1=黑，0=白）
        matrix3_data = shuffled_matrix1

        # 玩家ID（组内唯一ID）
        player_id = self.id_in_group

        # 返回变量（part1=risk时包含概率）
        vars_dict = {
            "part1": part1,
            "matrix1_original": matrix1_original,
            "matrix1_hide_rows": matrix1_hide_rows,
            "matrix3_data": matrix3_data,
            "player_id": player_id,
        }
        # 仅当risk时添加概率变量（直接用局部变量）
        if part1 == "risk":
            vars_dict["black_prob"] = black_prob
            vars_dict["white_prob"] = white_prob

        return vars_dict

    @staticmethod
    def shuffle_array(arr):
        """打乱数组"""
        shuffled = arr.copy()
        random.shuffle(shuffled)
        return shuffled


class WaitAfterPage1(WaitPage):
    """第一页等待页面：抽到黑色时强制设 skip_page2=True"""
    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds

    def after_all_players_arrive(self):
        group = self.group
        color_css_map = {'黑色': 'black', '白色': 'white'}
        
        valid_players = []
        for p in group.get_players():
            if (hasattr(p, 'clicked_index_page1') and p.clicked_index_page1 != -1
                and hasattr(p, 'clicked_color_page1') and p.clicked_color_page1.strip()):
                valid_players.append(p)

        if valid_players:
            selected = random.choice(valid_players)
            selected_color = selected.clicked_color_page1.strip()
            group.round_selected_player_id_page1 = selected.id_in_group
            group.round_selected_color_page1 = selected_color
            group.round_selected_color_css_page1 = color_css_map.get(selected_color, 'gray')
            # 核心：抽到黑色 → 跳过第二页（不付息）
            group.skip_page2 = (selected_color == '黑色')
        else:
            # 无有效玩家时，默认不跳过（或根据需求设为 True）
            group.round_selected_color_page1 = ""
            group.skip_page2 = False  # 明确赋值，避免 None


class DividendPage2(Page):
    """第二页：显示第二个矩阵+第三个矩阵（红黄蓝逻辑）"""
    form_model = 'player'
    form_fields = ['clicked_index_page2', 'clicked_color_page2']

    def is_displayed(self):
        group = self.group
        # 严谨判断：仅当 skip_page2 明确为 False 时才显示
        skip_page2 = getattr(group, 'skip_page2', False)
        skip_page2 = skip_page2 if skip_page2 is not None else False
        return not skip_page2  # skip_page2=True 时不显示
    def vars_for_template(self):
        treatment = self.subsession.treatment
        parts = treatment.split("_")
        part2 = parts[1] if len(parts) >= 2 else ""

        total_cells = 12 * 12  # 12×12=144个单元格
        total_rows = 12
        matrix2_original = []  # 第二个矩阵原始数据（0=红，1=黄，2=蓝）
        matrix2_hide_rows = []  # 遮挡行（仅ambi时有效）
        matrix3_data = []       # 第三矩阵数据（基于第二个矩阵）

        # 固定种子确保同轮数据一致
        seed = hash(f"{self.round_number}_{treatment}_page2") % (2**32 - 1)
        random.seed(seed)

        # 生成第二个矩阵
        if part2 == "risk":
            # risk：前4行红，中4行黄，后4行蓝（计算概率）
            # 每种颜色占4行×12列=48个单元格
            red_count = 4 * 12
            yellow_count = 4 * 12
            blue_count = 4 * 12
            # 计算概率（百分比，保留2位小数）
            red_prob = (red_count / total_cells) * 100  # 33.33%
            yellow_prob = (yellow_count / total_cells) * 100  # 33.33%
            blue_prob = (blue_count / total_cells) * 100  # 33.34%（四舍五入）
            # 生成矩阵数据
            for i in range(total_cells):
                row = i // 12
                if row < 4:
                    matrix2_original.append(0)  # 红
                elif row < 8:
                    matrix2_original.append(1)  # 黄
                else:
                    matrix2_original.append(2)  # 蓝
        else:  # ambi
            # ambi：红/黄/蓝各1/3，随机6行遮挡（无需概率）
            matrix2_original = [random.randint(0, 2) for _ in range(total_cells)]
            matrix2_hide_rows = random.sample(range(total_rows), 6)

        # 乱序第二个矩阵
        shuffled_matrix2 = DividendPage2.shuffle_array(matrix2_original)

        # 第三矩阵：直接使用乱序后的第二个矩阵
        matrix3_data = shuffled_matrix2

        # 玩家ID
        player_id = self.id_in_group

        # 返回变量（part2=risk时包含概率）
        vars_dict = {
            "part2": part2,
            "matrix2_original": matrix2_original,
            "matrix2_hide_rows": matrix2_hide_rows,
            "matrix3_data": matrix3_data,
            "player_id": player_id,
        }
        # 仅当risk时添加概率变量（局部变量，不绑定到self）
        if part2 == "risk":
            vars_dict["red_prob"] = round(red_prob, 2)
            vars_dict["yellow_prob"] = round(yellow_prob, 2)
            vars_dict["blue_prob"] = round(blue_prob, 2)

        return vars_dict

    @staticmethod
    def shuffle_array(arr):
        shuffled = arr.copy()
        random.shuffle(shuffled)
        return shuffled


class WaitAfterPage2(WaitPage):
    """第二页等待页面：仅当未抽到黑色时执行"""
    def is_displayed(self):
        group = self.group
        # 容错判断：避免 skip_page2 为 None 导致判断失效
        skip_page2 = getattr(group, 'skip_page2', False)
        skip_page2 = skip_page2 if skip_page2 is not None else False
        # 仅当 skip_page2=False 且当前轮次有效时显示
        return self.round_number <= self.subsession.num_rounds and (not skip_page2)

    def after_all_players_arrive(self):
        group = self.group
        color_css_map = {'红色': 'red', '黄色': 'yellow', '蓝色': 'blue'}
        
        valid_players = []
        for p in group.get_players():
            if (hasattr(p, 'clicked_index_page2') and p.clicked_index_page2 != -1
                and hasattr(p, 'clicked_color_page2') and p.clicked_color_page2.strip()):
                valid_players.append(p)

        if valid_players:
            selected = random.choice(valid_players)
            group.round_selected_player_id_page2 = selected.id_in_group
            group.round_selected_color_page2 = selected.clicked_color_page2.strip()
            group.round_selected_color_css_page2 = color_css_map.get(selected.clicked_color_page2.strip(), 'gray')
        else:
            group.round_selected_color_page2 = ""


class WelcomePage(Page):
    def is_displayed(self):
        return self.round_number == 1


class Instruction(Page):
    def is_displayed(self):
        self.initial_assets = self.settled_assets
        self.initial_cash = self.settled_cash
        return self.round_number == 1

    def vars_for_template(self):

        return {
            'state_independent': self.subsession.state_independent,
            'num_states': self.subsession.num_states,
            'num_assets': self.subsession.num_assets
        }


# If ssw_inherit is True, override this round's endowments with last round's settled holdings
def inherit_endowments_from_previous_round(subsession):
    """
    Overwrite this round's starting endowments with last round's final holdings.
    Called after all players in all groups arrive at WaitStart.
    """
    if subsession.ssw_inherit and subsession.round_number > 1:
        for p in subsession.get_players():
            prev_p = p.in_round(subsession.round_number - 1)

            # Cash
            p.settled_cash = prev_p.settled_cash
            p.initial_cash = prev_p.settled_cash

            # Assets
            p.settled_assets = prev_p.settled_assets
            p.initial_assets = prev_p.settled_assets


class WaitStart(WaitPage):
    body_text = 'Waiting for all players to be ready'
    wait_for_all_groups = True

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds

    after_all_players_arrive = inherit_endowments_from_previous_round


class Market(Page):
    def get_timeout_seconds(self):
        return self.group.period_length()

    def is_displayed(self):
        self.time = time.time()

        return self.round_number <= self.subsession.num_rounds

    def vars_for_template(self):
        # 从treatment中提取part1（与DividendPage1逻辑一致）
        treatment = self.subsession.treatment
        parts = treatment.split("_")
        part1 = parts[0] if len(parts) >= 1 else ""
        part2 = parts[1] if len(parts) >= 2 else ""
        # 新增：计算black_prob和white_prob（与DividendPage1保持一致）
        black_prob = None
        white_prob = None
        if part1 == "risk":
            # 3行黑色（12列），总单元格12×12=144
            black_count = 3 * 12
            total_cells = 12 * 12
            black_prob = (black_count / total_cells) * 100  # 25%
            white_prob = 100 - black_prob  # 75%
        # 2. 新增：计算红黄蓝概率（与DividendPage2逻辑一致）
        red_prob = None
        yellow_prob = None
        blue_prob = None
        if part2 == "risk":
            # 每种颜色4行（12列），总单元格12×12=144
            color_count = 4 * 12  # 48个单元格/颜色
            total_cells = 12 * 12
            # 计算概率（保留2位小数，处理四舍五入误差）
            base_prob = (color_count / total_cells) * 100  # 33.333...%
            red_prob = round(base_prob, 2)
            yellow_prob = round(base_prob, 2)
            # 蓝色概率微调，确保总和为100%（解决浮点误差）
            blue_prob = round(base_prob, 2)
        return {
            'round_number': self.round_number,
            'number_of_player': len(self.group.get_players()),
            'p1': self.subsession.p1 * 100,
            'p2': self.subsession.p2 * 100,
            'p3': self.subsession.p3 * 100,
            'p0': self.subsession.p0 * 100,
            'assets': ["A", "B", "C", "D"][:self.subsession.num_assets],
            'settled_assets': self.settled_assets,
            'asset_a_return_1': self.subsession.a1,
            'asset_a_return_2': self.subsession.a2,
            'asset_a_return_3': self.subsession.a3,
            'asset_b_return_1': self.subsession.b1,
            'asset_b_return_2': self.subsession.b2,
            'asset_b_return_3': self.subsession.b3,
            'asset_c_return_1': self.subsession.c1,
            'asset_c_return_2': self.subsession.c2,
            'asset_c_return_3': self.subsession.c3,
            'asset_d_return_1': self.subsession.d1,
            'asset_d_return_2': self.subsession.d2,
            'asset_d_return_3': self.subsession.d3,

            'num_states': self.subsession.num_states,
            'num_assets': self.subsession.num_assets,
            'is_practice': self.subsession.practice,
            'state_independent': self.subsession.state_independent,
            'trader_state': self.group.trader_state,
            'trader_states': self.group.trader_state_history,
            'settled_cash': self.settled_cash,

            'part1': part1,
            'part2': part2,
            # 新增：仅在part1为risk时传递概率变量
            'black_prob': black_prob,
            'white_prob': white_prob,
            # 新增：红黄蓝概率（与DividendPage2保持一致）
            'red_prob': red_prob,
            'yellow_prob': yellow_prob,
            'blue_prob': blue_prob

        }

    #  'bbc': self.asset_endowment()
    @staticmethod
    def live_method(player, data):
        import uuid
        # 获取当前时间戳
        timestamp = time.time() - player.time

        # 添加时间戳到payload中
        data['payload']['timestamp'] = timestamp

        # 获取玩家所在的 group
        group = player.group

        trader_state, trader_state_hisoty = get_trader_state(group)

        # 检查消息类型
        if data['channel'] == 'enter':

            # 处理出价或询价逻辑
            flag = is_valid_bid_ask(trader_state, data['payload'], player.settled_cash, player.settled_assets)

            if flag == 1:
                return {player.id_in_group: {"channel": 'messages',
                                             "data": 'Cannot enter a bid that crosses your own ask.'}}

            if flag == 2:
                return {player.id_in_group: {"channel": 'messages',
                                             "data": 'Cannot enter an ask that crosses your own bid.'}}

            if flag == 3:
                return {
                    player.id_in_group: {"channel": 'messages', "data": 'Order rejected: insufficient available cash.'}}

            if flag == 4:
                return {player.id_in_group: {"channel": 'messages',
                                             "data": f'Order rejected: insufficient available amount of asset {data["payload"]["asset_name"]}.'}}

            # 分配唯一的 order_id
            data['payload']['order_id'] = str(uuid.uuid4())

            update_trader_state(trader_state, trader_state_hisoty, data)
            # 对trades列表按价格和时间排序
            trader_state['trades'].sort(key=lambda x: (int(x['timestamp'])))
            trader_state_hisoty['trades'].sort(key=lambda x: (int(x['timestamp'])))
            # 确认是否匹配交易
            bids, asks = match_trades(trader_state, trader_state_hisoty, player.time)
            if bids != "":
                group.trader_state = json.dumps(trader_state).replace('True', 'true').replace('False', 'false')
                group.trader_state_history = json.dumps(trader_state_hisoty).replace('True', 'true').replace('False',
                                                                                                             'false')
                return {0: {"channel": 'confirm_trade',
                            "payload": {"asset_name": data['payload']['asset_name'], "making_orders": bids,
                                        "taking_order": asks}}}

            group.trader_state = json.dumps(trader_state).replace('True', 'true').replace('False', 'false')
            group.trader_state_history = json.dumps(trader_state_hisoty).replace('True', 'true').replace('False',
                                                                                                         'false')
            return {0: {"channel": 'confirm_enter', "payload": data['payload']}}


        elif data['channel'] == 'cancel':
            # 处理取消订单逻辑
            payload = data['payload']
            remove_order(trader_state, trader_state_hisoty, payload)
            group.trader_state = json.dumps(trader_state).replace('True', 'true').replace('False', 'false')
            group.trader_state_history = json.dumps(trader_state_hisoty).replace('True', 'true').replace('False',
                                                                                                         'false')
            return {0: {"channel": 'confirm_cancel', "payload": data['payload']}}

        elif data['channel'] == 'accept':
            # 处理用户确认的交易
            payload = data['payload']
            messages = process_trade(trader_state, trader_state_hisoty, payload, player)
            group.trader_state = json.dumps(trader_state).replace('True', 'true').replace('False', 'false')
            group.trader_state_history = json.dumps(trader_state_hisoty).replace('True', 'true').replace('False',
                                                                                                         'false')
            return messages

        # 保存更新后的交易状态
        group.trader_state = json.dumps(trader_state).replace('True', 'true').replace('False', 'false')

        # 返回更新后的交易状态给所有玩家
        return {0: trader_state}

#处理最后的结算金额
def payofff(group):
    stats = {}
    # 旧版本兼容：容错解析 JSON
    try:
        trader_state = getattr(group, 'trader_state', "{}") or "{}"
        data = json.loads(trader_state.strip()) if trader_state.strip() else {}
    except Exception:
        data = {}
    subsession = group.subsession

    # 安全初始化 skip_page2（避免 None）
    if getattr(group, 'skip_page2', None) is None:
        group.skip_page2 = False

    # 遍历当前组内玩家（仅9人）
    for p in group.get_players():
        # 容错处理玩家字段
        try:
            settled_assets_str = getattr(p, 'settled_assets', "{}") or "{}"
            settled_assets = json.loads(settled_assets_str.strip()) if settled_assets_str.strip() else {}
        except Exception:
            settled_assets = {}
        
        settled_cash = getattr(p, 'settled_cash', "0") or "0"
        try:
            settled_cash = int(settled_cash.strip())
        except Exception:
            settled_cash = 0

        # 计算基础收益（强制传入 group，确保组内独立）
        asset_a_return = subsession.get_asset_return('A', group)
        asset_a_holdings = settled_assets.get('A', 0)
        base_payoff = settled_cash + (asset_a_return * asset_a_holdings)

        # 多资产处理
        if subsession.num_assets >= 2:
            asset_b_return = subsession.get_asset_return('B', group)
            asset_b_holdings = settled_assets.get('B', 0)
            base_payoff += (asset_b_return * asset_b_holdings)
        if subsession.num_assets >= 3:
            asset_c_return = subsession.get_asset_return('C', group)
            asset_c_holdings = settled_assets.get('C', 0)
            base_payoff += (asset_c_return * asset_c_holdings)
        if subsession.num_assets >= 4:
            asset_d_return = subsession.get_asset_return('D', group)
            asset_d_holdings = settled_assets.get('D', 0)
            base_payoff += (asset_d_return * asset_d_holdings)

        p.payoff = base_payoff

    # 处理组内交易记录
    if not data or "trades" not in data:
        return

    for trade in data["trades"]:
        buyer_id = trade["buyer_id"]
        seller_id = trade["seller_id"]
        price = trade["price"]
        asset_name = trade["asset_name"]

        # 统计买家交易
        if buyer_id not in stats:
            stats[buyer_id] = {"count": {}, "amount": 0}
        stats[buyer_id]["count"][asset_name] = stats[buyer_id]["count"].get(asset_name, 0) + 1
        stats[buyer_id]["amount"] -= price

        # 统计卖家交易
        if seller_id not in stats:
            stats[seller_id] = {"count": {}, "amount": 0}
        stats[seller_id]["count"][asset_name] = stats[seller_id]["count"].get(asset_name, 0) - 1
        stats[seller_id]["amount"] += price

    # 更新玩家资产和现金
    for p in group.get_players():
        p_id_str = str(p.id_in_group)
        if p_id_str not in stats:
            continue

        # 更新现金
        current_cash = getattr(p, 'settled_cash', "0") or "0"
        try:
            current_cash = int(current_cash.strip())
        except Exception:
            current_cash = 0
        new_cash = current_cash + int(stats[p_id_str]["amount"])
        p.settled_cash = str(new_cash)

        # 更新资产
        try:
            settled_assets_str = getattr(p, 'settled_assets', "{}") or "{}"
            settled_assets = json.loads(settled_assets_str.strip()) if settled_assets_str.strip() else {}
        except Exception:
            settled_assets = {}
        for asset_name in settled_assets.keys():
            settled_assets[asset_name] += stats[p_id_str]["count"].get(asset_name, 0)
        p.settled_assets = json.dumps(settled_assets)

        # 重新计算最终收益
        final_asset_a_return = subsession.get_asset_return('A', group)
        final_asset_a_holdings = settled_assets.get('A', 0)
        final_payoff = new_cash + (final_asset_a_return * final_asset_a_holdings)

        if subsession.num_assets >= 2:
            final_asset_b_return = subsession.get_asset_return('B', group)
            final_asset_b_holdings = settled_assets.get('B', 0)
            final_payoff += (final_asset_b_return * final_asset_b_holdings)
        if subsession.num_assets >= 3:
            final_asset_c_return = subsession.get_asset_return('C', group)
            final_asset_c_holdings = settled_assets.get('C', 0)
            final_payoff += (final_asset_c_return * final_asset_c_holdings)
        if subsession.num_assets >= 4:
            final_asset_d_return = subsession.get_asset_return('D', group)
            final_asset_d_holdings = settled_assets.get('D', 0)
            final_payoff += (final_asset_d_return * final_asset_d_holdings)

        p.payoff = final_payoff


class Wait(WaitPage):
    body_text = 'Waiting for all players to be ready'

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds

    after_all_players_arrive = payofff


class RoundResults(Page):
    """本轮结果页面：变量名完全匹配模板，组内独立显示"""

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds

    def get_timeout_seconds(self):
        return 60

    def vars_for_template(self):
        player = self
        group = self.group
        subsession = self.subsession
        # 判断是否付息（状态0=不付息）
        current_state = group.color_to_state() if group else 0
        is_interest_paid = (current_state != 0)  # 状态0→不付息

        # 容错处理所有字段，避免模板变量缺失
        try:
            settled_assets_str = getattr(player, 'settled_assets', "{}") or "{}"
            settled_assets = json.loads(settled_assets_str.strip()) if settled_assets_str.strip() else {}
        except Exception:
            settled_assets = {}
        
        settled_cash = getattr(player, 'settled_cash', "0") or "0"
        try:
            settled_cash = int(settled_cash.strip())
        except Exception:
            settled_cash = 0

        num_assets = getattr(subsession, 'num_assets', 1)
        group_id = getattr(group, 'id_in_subsession', 1)

        # --------------------------
        # 1. 计算各资产回报（组内独立）
        # --------------------------
        # 资产A（必选）
        try:
            asset_a_return = subsession.get_asset_return('A', group)
        except Exception:
            asset_a_return = 0
        asset_a_unit = settled_assets.get('A', 0)
        asset_a_total_return = asset_a_unit * asset_a_return

        # 资产B（可选）
        asset_b_unit = asset_b_return = asset_b_total_return = 0
        if num_assets >= 2:
            try:
                asset_b_return = subsession.get_asset_return('B', group)
            except Exception:
                asset_b_return = 0
            asset_b_unit = settled_assets.get('B', 0)
            asset_b_total_return = asset_b_unit * asset_b_return

        # 资产C（可选）
        asset_c_unit = asset_c_return = asset_c_total_return = 0
        if num_assets >= 3:
            try:
                asset_c_return = subsession.get_asset_return('C', group)
            except Exception:
                asset_c_return = 0
            asset_c_unit = settled_assets.get('C', 0)
            asset_c_total_return = asset_c_unit * asset_c_return

        # 资产D（可选）
        asset_d_unit = asset_d_return = asset_d_total_return = 0
        if num_assets >= 4:
            try:
                asset_d_return = subsession.get_asset_return('D', group)
            except Exception:
                asset_d_return = 0
            asset_d_unit = settled_assets.get('D', 0)
            asset_d_total_return = asset_d_unit * asset_d_return

        # 总收益
        total_payoff = settled_cash + asset_a_total_return + asset_b_total_return + asset_c_total_return + asset_d_total_return

        # --------------------------
        # 2. 读取组内抽取结果（变量名匹配模板：selected_player_id）
        # --------------------------
        # 第一页结果
        round1_selected_player_id = getattr(group, 'round_selected_player_id_page1', -1)
        round1_selected_player_id = round1_selected_player_id if round1_selected_player_id != -1 else '无'
        round1_selected_color = getattr(group, 'round_selected_color_page1', '') or '无'
        round1_selected_color_css = getattr(group, 'round_selected_color_css_page1', 'gray')

        # 最终结果（模板中用 selected_player_id，所以这里直接返回该键名）
        skip_page2 = getattr(group, 'skip_page2', False)
        skip_page2 = skip_page2 if skip_page2 is not None else False

        if skip_page2:
            selected_player_id = round1_selected_player_id  # 匹配模板变量名
            selected_color = round1_selected_color
            selected_color_css = round1_selected_color_css
        else:
            round2_selected_player_id = getattr(group, 'round_selected_player_id_page2', -1)
            selected_player_id = round2_selected_player_id if round2_selected_player_id != -1 else '无'  # 匹配模板变量名
            selected_color = getattr(group, 'round_selected_color_page2', '') or '无'
            selected_color_css = getattr(group, 'round_selected_color_css_page2', 'gray')

        # --------------------------
        # 3. 组装模板变量（确保所有模板用到的变量都存在）
        # --------------------------
        return {
            # 组信息
            'group_id': group_id,
            'group_size': len(group.get_players()) if group else 9,

            # 资产数据（模板可能用到的变量）
            'asset_a_unit': asset_a_unit,
            'asset_a_return': asset_a_return,
            'asset_a_total_return': asset_a_total_return,
            'asset_b_unit': asset_b_unit,
            'asset_b_return': asset_b_return,
            'asset_b_total_return': asset_b_total_return,
            'asset_c_unit': asset_c_unit,
            'asset_c_return': asset_c_return,
            'asset_c_total_return': asset_c_total_return,
            'asset_d_unit': asset_d_unit,
            'asset_d_return': asset_d_return,
            'asset_d_total_return': asset_d_total_return,

            # 现金与收益
            'settled_cash': settled_cash,
            'payoff': total_payoff,
            'num_assets': num_assets,

            # 抽取结果（核心：变量名完全匹配模板）
            'selected_player_id': selected_player_id,  # 修复：模板中用的是这个变量名
            'selected_color': selected_color,
            'selected_color_css': selected_color_css,

            # 第一页结果（如果模板也用到）
            'round1_selected_player_id': round1_selected_player_id,
            'round1_selected_color': round1_selected_color,
            'round1_selected_color_css': round1_selected_color_css,

            'is_interest_paid': is_interest_paid,  # 新增：是否付息标记

            # 其他辅助变量
            'has_round2': not skip_page2,
            'timeout_seconds': 60
        }


class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds

    def vars_for_template(self):
        import random
        round_payer = None
        r = None
        flag = True
        while flag:
            r = random.randint(1, self.subsession.num_rounds)
            round_payer = self.in_round(r)
            flag = round_payer.subsession.practice
        self.final_selected_round = r
        # self.participant.vars['mpl_payoff'] = 10
        self.total_payoff = round_payer.payoff / 9 + Currency(self.participant.vars['mpl_payoff'] * 4) + 10
        return {
            'selected_round': r,
            'mpl_payoff': self.participant.vars['mpl_payoff'],
            'salience_payoff': round_payer.payoff,
            'total_payoff': self.total_payoff
        }


class Questionnaire(Page):
    form_model = 'player'
    form_fields = ['question_1', 'question_2', 'question_3', 'question_4']

    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds


class Demographic(Page):
    form_model = 'player'
    form_fields = ['name', 'gender', 'phone_id', 'part_id',
                   'venmo_id', 'comments', 'strategy']

    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds


# , FinalResults
page_sequence = [
    Instruction, 
    WaitStart, 
    Market, 
    Wait, 
    DividendPage1,       # 第一页矩阵
    WaitAfterPage1,      # 第一页后等待判断
    DividendPage2,       # 第二页矩阵（条件显示）
    WaitAfterPage2,      # 第二页后等待
    RoundResults,        # 结算页面
    Questionnaire, 
    Demographic, 
    FinalResults
]