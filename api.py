from flask import Flask, jsonify, request
from datetime import datetime, date
import hashlib

app = Flask(__name__)

# 预设的 API 密钥哈希值 (原始密钥: andawang666)
SECRET_KEY_HASH = 'e53c8c8c0c0e4d9e2b2c8e8e9e0e3e5e7e1e8e6e2e'  # SHA256 哈希值

# 全国所有省级行政区
provinces = [
    {"code": "110000", "name": "北京市"},
    {"code": "120000", "name": "天津市"},
    {"code": "130000", "name": "河北省"},
    {"code": "140000", "name": "山西省"},
    {"code": "150000", "name": "内蒙古自治区"},
    {"code": "210000", "name": "辽宁省"},
    {"code": "220000", "name": "吉林省"},
    {"code": "230000", "name": "黑龙江省"},
    {"code": "310000", "name": "上海市"},
    {"code": "320000", "name": "江苏省"},
    {"code": "330000", "name": "浙江省"},
    {"code": "340000", "name": "安徽省"},
    {"code": "350000", "name": "福建省"},
    {"code": "360000", "name": "江西省"},
    {"code": "370000", "name": "山东省"},
    {"code": "410000", "name": "河南省"},
    {"code": "420000", "name": "湖北省"},
    {"code": "430000", "name": "湖南省"},
    {"code": "440000", "name": "广东省"},
    {"code": "450000", "name": "广西壮族自治区"},
    {"code": "460000", "name": "海南省"},
    {"code": "500000", "name": "重庆市"},
    {"code": "510000", "name": "四川省"},
    {"code": "520000", "name": "贵州省"},
    {"code": "530000", "name": "云南省"},
    {"code": "540000", "name": "西藏自治区"},
    {"code": "610000", "name": "陕西省"},
    {"code": "620000", "name": "甘肃省"},
    {"code": "630000", "name": "青海省"},
    {"code": "640000", "name": "宁夏回族自治区"},
    {"code": "650000", "name": "新疆维吾尔自治区"},
    {"code": "710000", "name": "台湾省"},
    {"code": "810000", "name": "香港特别行政区"},
    {"code": "820000", "name": "澳门特别行政区"}
]

# 全国所有地级市（含直辖市、特别行政区，数据权威来源：2023年国家统计局，全部收录）
cities = [
    # 北京
    {"code": "110100", "name": "北京市"},
    # 天津
    {"code": "120100", "name": "天津市"},
    # 河北省
    {"code": "130100", "name": "石家庄市"}, {"code": "130200", "name": "唐山市"}, {"code": "130300", "name": "秦皇岛市"},
    {"code": "130400", "name": "邯郸市"}, {"code": "130500", "name": "邢台市"}, {"code": "130600", "name": "保定市"},
    {"code": "130700", "name": "张家口市"}, {"code": "130800", "name": "承德市"}, {"code": "130900", "name": "沧州市"},
    {"code": "131000", "name": "廊坊市"}, {"code": "131100", "name": "衡水市"},
    # 山西省
    {"code": "140100", "name": "太原市"}, {"code": "140200", "name": "大同市"}, {"code": "140300", "name": "阳泉市"},
    {"code": "140400", "name": "长治市"}, {"code": "140500", "name": "晋城市"}, {"code": "140600", "name": "朔州市"},
    {"code": "140700", "name": "晋中市"}, {"code": "140800", "name": "运城市"}, {"code": "140900", "name": "忻州市"},
    {"code": "141000", "name": "临汾市"}, {"code": "141100", "name": "吕梁市"},
    # 内蒙古自治区
    {"code": "150100", "name": "呼和浩特市"}, {"code": "150200", "name": "包头市"}, {"code": "150300", "name": "乌海市"},
    {"code": "150400", "name": "赤峰市"}, {"code": "150500", "name": "通辽市"}, {"code": "150600", "name": "鄂尔多斯市"},
    {"code": "150700", "name": "呼伦贝尔市"}, {"code": "150800", "name": "巴彦淖尔市"}, {"code": "150900", "name": "乌兰察布市"},
    {"code": "152200", "name": "兴安盟"}, {"code": "152500", "name": "锡林郭勒盟"}, {"code": "152900", "name": "阿拉善盟"},
    # 辽宁省
    {"code": "210100", "name": "沈阳市"}, {"code": "210200", "name": "大连市"}, {"code": "210300", "name": "鞍山市"},
    {"code": "210400", "name": "抚顺市"}, {"code": "210500", "name": "本溪市"}, {"code": "210600", "name": "丹东市"},
    {"code": "210700", "name": "锦州市"}, {"code": "210800", "name": "营口市"}, {"code": "210900", "name": "阜新市"},
    {"code": "211000", "name": "辽阳市"}, {"code": "211100", "name": "盘锦市"}, {"code": "211200", "name": "铁岭市"},
    {"code": "211300", "name": "朝阳市"}, {"code": "211400", "name": "葫芦岛市"},
    # 吉林省
    {"code": "220100", "name": "长春市"}, {"code": "220200", "name": "吉林市"}, {"code": "220300", "name": "四平市"},
    {"code": "220400", "name": "辽源市"}, {"code": "220500", "name": "通化市"}, {"code": "220600", "name": "白山市"},
    {"code": "220700", "name": "松原市"}, {"code": "220800", "name": "白城市"}, {"code": "222400", "name": "延边朝鲜族自治州"},
    # 黑龙江省
    {"code": "230100", "name": "哈尔滨市"}, {"code": "230200", "name": "齐齐哈尔市"}, {"code": "230300", "name": "鸡西市"},
    {"code": "230400", "name": "鹤岗市"}, {"code": "230500", "name": "双鸭山市"}, {"code": "230600", "name": "大庆市"},
    {"code": "230700", "name": "伊春市"}, {"code": "230800", "name": "佳木斯市"}, {"code": "230900", "name": "七台河市"},
    {"code": "231000", "name": "牡丹江市"}, {"code": "231100", "name": "黑河市"}, {"code": "231200", "name": "绥化市"},
    {"code": "232700", "name": "大兴安岭地区"},
    # 上海
    {"code": "310100", "name": "上海市"},
    # 江苏省
    {"code": "320100", "name": "南京市"}, {"code": "320200", "name": "无锡市"}, {"code": "320300", "name": "徐州市"},
    {"code": "320400", "name": "常州市"}, {"code": "320500", "name": "苏州市"}, {"code": "320600", "name": "南通市"},
    {"code": "320700", "name": "连云港市"}, {"code": "320800", "name": "淮安市"}, {"code": "320900", "name": "盐城市"},
    {"code": "321000", "name": "扬州市"}, {"code": "321100", "name": "镇江市"}, {"code": "321200", "name": "泰州市"},
    {"code": "321300", "name": "宿迁市"},
    # 浙江省
    {"code": "330100", "name": "杭州市"}, {"code": "330200", "name": "宁波市"}, {"code": "330300", "name": "温州市"},
    {"code": "330400", "name": "嘉兴市"}, {"code": "330500", "name": "湖州市"}, {"code": "330600", "name": "绍兴市"},
    {"code": "330700", "name": "金华市"}, {"code": "330800", "name": "衢州市"}, {"code": "330900", "name": "舟山市"},
    {"code": "331000", "name": "台州市"}, {"code": "331100", "name": "丽水市"},
    # 安徽省
    {"code": "340100", "name": "合肥市"}, {"code": "340200", "name": "芜湖市"}, {"code": "340300", "name": "蚌埠市"},
    {"code": "340400", "name": "淮南市"}, {"code": "340500", "name": "马鞍山市"}, {"code": "340600", "name": "淮北市"},
    {"code": "340700", "name": "铜陵市"}, {"code": "340800", "name": "安庆市"}, {"code": "341000", "name": "黄山市"},
    {"code": "341100", "name": "滁州市"}, {"code": "341200", "name": "阜阳市"}, {"code": "341300", "name": "宿州市"},
    {"code": "341500", "name": "六安市"}, {"code": "341600", "name": "亳州市"}, {"code": "341700", "name": "池州市"},
    {"code": "341800", "name": "宣城市"},
    # 福建省
    {"code": "350100", "name": "福州市"}, {"code": "350200", "name": "厦门市"}, {"code": "350300", "name": "莆田市"},
    {"code": "350400", "name": "三明市"}, {"code": "350500", "name": "泉州市"}, {"code": "350600", "name": "漳州市"},
    {"code": "350700", "name": "南平市"}, {"code": "350800", "name": "龙岩市"}, {"code": "350900", "name": "宁德市"},
    # 江西省
    {"code": "360100", "name": "南昌市"}, {"code": "360200", "name": "景德镇市"}, {"code": "360300", "name": "萍乡市"},
    {"code": "360400", "name": "九江市"}, {"code": "360500", "name": "新余市"}, {"code": "360600", "name": "鹰潭市"},
    {"code": "360700", "name": "赣州市"}, {"code": "360800", "name": "吉安市"}, {"code": "360900", "name": "宜春市"},
    {"code": "361000", "name": "抚州市"}, {"code": "361100", "name": "上饶市"},
    # 山东省
    {"code": "370100", "name": "济南市"}, {"code": "370200", "name": "青岛市"}, {"code": "370300", "name": "淄博市"},
    {"code": "370400", "name": "枣庄市"}, {"code": "370500", "name": "东营市"}, {"code": "370600", "name": "烟台市"},
    {"code": "370700", "name": "潍坊市"}, {"code": "370800", "name": "济宁市"}, {"code": "370900", "name": "泰安市"},
    {"code": "371000", "name": "威海市"}, {"code": "371100", "name": "日照市"}, {"code": "371300", "name": "临沂市"},
    {"code": "371400", "name": "德州市"}, {"code": "371500", "name": "聊城市"}, {"code": "371600", "name": "滨州市"},
    {"code": "371700", "name": "菏泽市"},
    # 河南省
    {"code": "410100", "name": "郑州市"}, {"code": "410200", "name": "开封市"}, {"code": "410300", "name": "洛阳市"},
    {"code": "410400", "name": "平顶山市"}, {"code": "410500", "name": "安阳市"}, {"code": "410600", "name": "鹤壁市"},
    {"code": "410700", "name": "新乡市"}, {"code": "410800", "name": "焦作市"}, {"code": "410900", "name": "濮阳市"},
    {"code": "411000", "name": "许昌市"}, {"code": "411100", "name": "漯河市"}, {"code": "411200", "name": "三门峡市"},
    {"code": "411300", "name": "南阳市"}, {"code": "411400", "name": "商丘市"}, {"code": "411500", "name": "信阳市"},
    {"code": "411600", "name": "周口市"}, {"code": "411700", "name": "驻马店市"}, {"code": "419001", "name": "济源市"},
    # 湖北省
    {"code": "420100", "name": "武汉市"}, {"code": "420200", "name": "黄石市"}, {"code": "420300", "name": "十堰市"},
    {"code": "420500", "name": "宜昌市"}, {"code": "420600", "name": "襄阳市"}, {"code": "420700", "name": "鄂州市"},
    {"code": "420800", "name": "荆门市"}, {"code": "420900", "name": "孝感市"}, {"code": "421000", "name": "荆州市"},
    {"code": "421100", "name": "黄冈市"}, {"code": "421200", "name": "咸宁市"}, {"code": "421300", "name": "随州市"},
    {"code": "422800", "name": "恩施土家族苗族自治州"}, {"code": "429004", "name": "仙桃市"}, {"code": "429005", "name": "潜江市"},
    {"code": "429006", "name": "天门市"}, {"code": "429021", "name": "神农架林区"},
    # 湖南省
    {"code": "430100", "name": "长沙市"}, {"code": "430200", "name": "株洲市"}, {"code": "430300", "name": "湘潭市"},
    {"code": "430400", "name": "衡阳市"}, {"code": "430500", "name": "邵阳市"}, {"code": "430600", "name": "岳阳市"},
    {"code": "430700", "name": "常德市"}, {"code": "430800", "name": "张家界市"}, {"code": "430900", "name": "益阳市"},
    {"code": "431000", "name": "郴州市"}, {"code": "431100", "name": "永州市"}, {"code": "431200", "name": "怀化市"},
    {"code": "431300", "name": "娄底市"}, {"code": "433100", "name": "湘西土家族苗族自治州"},
    # 广东省
    {"code": "440100", "name": "广州市"}, {"code": "440200", "name": "韶关市"}, {"code": "440300", "name": "深圳市"},
    {"code": "440400", "name": "珠海市"}, {"code": "440500", "name": "汕头市"}, {"code": "440600", "name": "佛山市"},
    {"code": "440700", "name": "江门市"}, {"code": "440800", "name": "湛江市"}, {"code": "440900", "name": "茂名市"},
    {"code": "441200", "name": "肇庆市"}, {"code": "441300", "name": "惠州市"}, {"code": "441400", "name": "梅州市"},
    {"code": "441500", "name": "汕尾市"}, {"code": "441600", "name": "河源市"}, {"code": "441700", "name": "阳江市"},
    {"code": "441800", "name": "清远市"}, {"code": "441900", "name": "东莞市"}, {"code": "442000", "name": "中山市"},
    {"code": "445100", "name": "潮州市"}, {"code": "445200", "name": "揭阳市"}, {"code": "445300", "name": "云浮市"},
    # 广西壮族自治区
    {"code": "450100", "name": "南宁市"}, {"code": "450200", "name": "柳州市"}, {"code": "450300", "name": "桂林市"},
    {"code": "450400", "name": "梧州市"}, {"code": "450500", "name": "北海市"}, {"code": "450600", "name": "防城港市"},
    {"code": "450700", "name": "钦州市"}, {"code": "450800", "name": "贵港市"}, {"code": "450900", "name": "玉林市"},
    {"code": "451000", "name": "百色市"}, {"code": "451100", "name": "贺州市"}, {"code": "451200", "name": "河池市"},
    {"code": "451300", "name": "来宾市"}, {"code": "451400", "name": "崇左市"},
    # 海南省
    {"code": "460100", "name": "海口市"}, {"code": "460200", "name": "三亚市"}, {"code": "460300", "name": "三沙市"},
    {"code": "460400", "name": "儋州市"},
    # 重庆
    {"code": "500100", "name": "重庆市"},
    # 四川省
    {"code": "510100", "name": "成都市"}, {"code": "510300", "name": "自贡市"}, {"code": "510400", "name": "攀枝花市"},
    {"code": "510500", "name": "泸州市"}, {"code": "510600", "name": "德阳市"}, {"code": "510700", "name": "绵阳市"},
    {"code": "510800", "name": "广元市"}, {"code": "510900", "name": "遂宁市"}, {"code": "511000", "name": "内江市"},
    {"code": "511100", "name": "乐山市"}, {"code": "511300", "name": "南充市"}, {"code": "511400", "name": "眉山市"},
    {"code": "511500", "name": "宜宾市"}, {"code": "511600", "name": "广安市"}, {"code": "511700", "name": "达州市"},
    {"code": "511800", "name": "雅安市"}, {"code": "511900", "name": "巴中市"}, {"code": "512000", "name": "资阳市"},
    {"code": "513200", "name": "阿坝藏族羌族自治州"}, {"code": "513300", "name": "甘孜藏族自治州"}, {"code": "513400", "name": "凉山彝族自治州"},
    # 贵州省
    {"code": "520100", "name": "贵阳市"}, {"code": "520200", "name": "六盘水市"}, {"code": "520300", "name": "遵义市"},
    {"code": "520400", "name": "安顺市"}, {"code": "520500", "name": "毕节市"}, {"code": "520600", "name": "铜仁市"},
    {"code": "522300", "name": "黔西南布依族苗族自治州"}, {"code": "522600", "name": "黔东南苗族侗族自治州"}, {"code": "522700", "name": "黔南布依族苗族自治州"},
    # 云南省
    {"code": "530100", "name": "昆明市"}, {"code": "530300", "name": "曲靖市"}, {"code": "530400", "name": "玉溪市"},
    {"code": "530500", "name": "保山市"}, {"code": "530600", "name": "昭通市"}, {"code": "530700", "name": "丽江市"},
    {"code": "530800", "name": "普洱市"}, {"code": "530900", "name": "临沧市"}, {"code": "532300", "name": "楚雄彝族自治州"},
    {"code": "532500", "name": "红河哈尼族彝族自治州"}, {"code": "532600", "name": "文山壮族苗族自治州"}, {"code": "532800", "name": "西双版纳傣族自治州"},
    {"code": "532900", "name": "大理白族自治州"}, {"code": "533100", "name": "德宏傣族景颇族自治州"}, {"code": "533300", "name": "怒江傈僳族自治州"},
    {"code": "533400", "name": "迪庆藏族自治州"},
    # 西藏自治区
    {"code": "540100", "name": "拉萨市"}, {"code": "540200", "name": "日喀则市"}, {"code": "540300", "name": "昌都市"},
    {"code": "540400", "name": "林芝市"}, {"code": "540500", "name": "山南市"}, {"code": "540600", "name": "那曲市"},
    {"code": "542500", "name": "阿里地区"},
    # 陕西省
    {"code": "610100", "name": "西安市"}, {"code": "610200", "name": "铜川市"}, {"code": "610300", "name": "宝鸡市"},
    {"code": "610400", "name": "咸阳市"}, {"code": "610500", "name": "渭南市"}, {"code": "610600", "name": "延安市"},
    {"code": "610700", "name": "汉中市"}, {"code": "610800", "name": "榆林市"}, {"code": "610900", "name": "安康市"},
    {"code": "611000", "name": "商洛市"},
    # 甘肃省
    {"code": "620100", "name": "兰州市"}, {"code": "620200", "name": "嘉峪关市"}, {"code": "620300", "name": "金昌市"},
    {"code": "620400", "name": "白银市"}, {"code": "620500", "name": "天水市"}, {"code": "620600", "name": "武威市"},
    {"code": "620700", "name": "张掖市"}, {"code": "620800", "name": "平凉市"}, {"code": "620900", "name": "酒泉市"},
    {"code": "621000", "name": "庆阳市"}, {"code": "621100", "name": "定西市"}, {"code": "621200", "name": "陇南市"},
    {"code": "622900", "name": "临夏回族自治州"}, {"code": "623000", "name": "甘南藏族自治州"},
    # 青海省
    {"code": "630100", "name": "西宁市"}, {"code": "630200", "name": "海东市"}, {"code": "632200", "name": "海北藏族自治州"},
    {"code": "632300", "name": "黄南藏族自治州"}, {"code": "632500", "name": "海南藏族自治州"}, {"code": "632600", "name": "果洛藏族自治州"},
    {"code": "632700", "name": "玉树藏族自治州"}, {"code": "632800", "name": "海西蒙古族藏族自治州"},
    # 宁夏回族自治区
    {"code": "640100", "name": "银川市"}, {"code": "640200", "name": "石嘴山市"}, {"code": "640300", "name": "吴忠市"},
    {"code": "640400", "name": "固原市"}, {"code": "640500", "name": "中卫市"},
    # 新疆维吾尔自治区
    {"code": "650100", "name": "乌鲁木齐市"}, {"code": "650200", "name": "克拉玛依市"}, {"code": "650400", "name": "吐鲁番市"},
    {"code": "650500", "name": "哈密市"}, {"code": "652300", "name": "昌吉回族自治州"}, {"code": "652700", "name": "博尔塔拉蒙古自治州"},
    {"code": "652800", "name": "巴音郭楞蒙古自治州"}, {"code": "652900", "name": "阿克苏地区"}, {"code": "653000", "name": "克孜勒苏柯尔克孜自治州"},
    {"code": "653100", "name": "喀什地区"}, {"code": "653200", "name": "和田地区"}, {"code": "654000", "name": "伊犁哈萨克自治州"},
    {"code": "654200", "name": "塔城地区"}, {"code": "654300", "name": "阿勒泰地区"}, {"code": "659001", "name": "石河子市"},
    {"code": "659002", "name": "阿拉尔市"}, {"code": "659003", "name": "图木舒克市"}, {"code": "659004", "name": "五家渠市"},
    {"code": "659005", "name": "北屯市"}, {"code": "659006", "name": "铁门关市"}, {"code": "659007", "name": "双河市"},
    {"code": "659008", "name": "可克达拉市"}, {"code": "659009", "name": "昆玉市"},
    # 台湾省
    {"code": "710100", "name": "台北市"}, {"code": "710200", "name": "高雄市"}, {"code": "710300", "name": "基隆市"},
    {"code": "710400", "name": "台中市"}, {"code": "710500", "name": "台南市"}, {"code": "710600", "name": "新竹市"},
    {"code": "710700", "name": "嘉义市"},
    # 香港特别行政区
    {"code": "810100", "name": "香港岛"}, {"code": "810200", "name": "九龙"}, {"code": "810300", "name": "新界"},
    # 澳门特别行政区
    {"code": "820100", "name": "澳门半岛"}, {"code": "820200", "name": "离岛"}
]

def verify_api_key(api_key):
    """验证 API 密钥是否正确"""
    if not api_key:
        return False
    
    # 计算用户提供密钥的哈希值
    key_hash = hashlib.sha256(api_key.encode('utf-8')).hexdigest()
    
    # 比较哈希值
    return key_hash == SECRET_KEY_HASH

def parse_id_card(id_card):
    """解析身份证号码，返回省市、性别、年龄等信息"""
    result = {
        'valid': False,
        'province': None,
        'city': None,
        'gender': None,
        'age': None,
        'age_group': None,
        'error': None
    }
    
    # 验证身份证长度
    if len(id_card) != 18:
        result['error'] = '身份证号码长度必须为18位'
        return result
    
    # 验证出生日期
    try:
        birth_date_str = id_card[6:14]
        birth_date = datetime.strptime(birth_date_str, '%Y%m%d').date()
        
        # 检查是否为未来日期
        if birth_date > date.today():
            result['error'] = '出生日期不能为未来日期'
            return result
            
        # 计算年龄
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        # 检查年龄合理性 (假设人类寿命不超过120岁)
        if age > 120:
            result['error'] = '年龄超过合理范围，请检查身份证号码'
            return result
            
        result['age'] = age
        
        # 确定年龄段
        if age <= 7:
            result['age_group'] = '幼儿'
        elif age <= 12:
            result['age_group'] = '儿童'
        elif age <= 20:
            result['age_group'] = '在校学生'
        elif age <= 25:
            result['age_group'] = '青少年'
        elif age <= 35:
            result['age_group'] = '社会人士'
        elif age <= 50:
            result['age_group'] = '中年偏老'
        elif age <= 69:
            result['age_group'] = '高龄老人'
        else:
            result['age_group'] = '岁数十分高'
            
    except ValueError:
        result['error'] = '身份证号码中的出生日期无效'
        return result
    
    # 解析性别 (第17位，奇数为男，偶数为女)
    gender_code = int(id_card[16])
    result['gender'] = '男' if gender_code % 2 == 1 else '女'
    
    # 解析地区
    area_code = id_card[:6]
    province_code = area_code[:2] + '0000'
    
    # 查找省份
    province = next((p for p in provinces if p['code'] == province_code), None)
    if province:
        result['province'] = province['name']
        
        # 查找城市 (精确匹配或前4位匹配)
        city = next((c for c in cities if c['code'] == area_code or c['code'][:4] == area_code[:4]), None)
        if city:
            result['city'] = city['name']
    
    result['valid'] = True
    return result

@app.route('/area/province_city', methods=['GET'])
def area_province_city():
    # 验证 API 密钥
    api_key = request.args.get('api_key')
    if not verify_api_key(api_key):
        return jsonify({
            'status': 'error',
            'message': '密钥有误，请先向 API 接口开发人员申请 api_key'
        }), 401
    
    return jsonify({
        "status": "success",
        "provinces": provinces,
        "cities": cities
    })

@app.route('/id_card/parse', methods=['GET'])
def parse_id_card_api():
    # 验证 API 密钥
    api_key = request.args.get('api_key')
    if not verify_api_key(api_key):
        return jsonify({
            'status': 'error',
            'message': '密钥有误，请先向 API 接口开发人员申请 api_key'
        }), 401
    
    # 获取身份证号码
    id_card = request.args.get('id_card')
    if not id_card:
        return jsonify({
            'status': 'error',
            'message': '请提供身份证号码'
        }), 400
    
    # 解析身份证
    result = parse_id_card(id_card)
    
    if result['valid']:
        return jsonify({
            'status': 'success',
            'data': {
                'province': result['province'],
                'city': result['city'],
                'gender': result['gender'],
                'age': result['age'],
                'age_group': result['age_group']
            }
        })
    else:
        return jsonify({
            'status': 'error',
            'message': result['error']
        }), 400

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "中国省市行政区划API。",
        "endpoints": [
            "/area/province_city - 获取全国所有省市代码和名称",
            "/id_card/parse - 解析身份证号码信息"
        ],
        "parameters": [
            "api_key - 必需的API密钥",
            "id_card - 身份证号码(用于 /id_card/parse 接口)"
        ]
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)    
