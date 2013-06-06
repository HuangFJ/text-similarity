# coding: utf-8
import copy

def print_list(l):
    '''
    打印list对象
    '''
    if l:
        s = ''
        for i in l:
            s += str(i) + ','
        
        return s[:-1]
    else:
        return ''

class Atom(object):
    
    def __init__(self, part=None):
        # ~^ 在 义原 或者 符号之前
        self.logic = None
        # 关系义原英文部分
        self.rel_primitive = None
        # #%$*+&@?! 关系符号
        self.rel_symbol = None
        # 义原英文部分
        self.eng = None
        # 义原中文部分
        self.chi = None
        # 具体词
        self.is_concrete = False
        
        if part is not None: self.parse(part)
        
    def parse(self, part):
        #具体词
        if part[0] == '(':
            part = part[1:-1].strip()
            self.is_concrete = True
        #逻辑符号
        if part[0] in "~^":
            self.logic = part[0]
            part = part[1:].strip()
        #关系符号
        if part[0] in "#%$*+&@?!":
            self.rel_symbol = part[0]
            part = part[1:].strip()
            
        pair_r = part.split('|')
        
        self.eng = pair_r[0].strip()
        if len(pair_r) > 1:
            self.chi = pair_r[1].strip()
            
    def __str__(self):
        part = ''
        if self.rel_primitive:
            part += self.rel_primitive + '='
        if self.logic:
            part += self.logic
        if self.rel_symbol:
            part += self.rel_symbol
        
        part += self.eng
        
        if self.chi:
            part += '|' + self.chi
            
        if self.is_concrete:
            part = '(' + part + ')'
            
        part = '"' + part + '"'
        return part
        

class Word(object):
    
    def __init__(self):
        #中文词
        self.word = ''
        #词性标注
        self.type = ''
        #该词是否是虚词
        self.is_structural = False
        #第一基本义原
        self.first_primitive = None
        #其他基本义原集合
        self.other_primitives = []
        #关系义原集合
        self.relational_primitives = {}
        #关系符号义原集合
        self.symbol_primitives = {}
    
    def add_primitive(self, atom):
        if atom.rel_primitive is not None:
            self.add_relational_primitive(atom.rel_primitive, atom)
        elif atom.rel_symbol is not None:
            key = (atom.logic or '') + atom.rel_symbol
            self.add_symbol_primitive(key, atom)
        else:
            self.add_other_primitive(atom)
        
    def add_other_primitive(self, atom):
        self.other_primitives.append(atom)
        
    def add_relational_primitive(self, key, atom):
        if self.relational_primitives.get(key) is None:
            self.relational_primitives[key] = []
            
        self.relational_primitives[key].append(atom)
        
    def add_symbol_primitive(self, key, atom):
        if self.symbol_primitives.get(key) is None:
            self.symbol_primitives[key] = []
        
        self.symbol_primitives[key].append(atom)
    
    def __str__(self):
        op = '[' + print_list(self.other_primitives) + ']'
        
        rp = ''
        for k in self.relational_primitives:
            rp += k + ':[' + print_list(self.relational_primitives[k]) + '],'
        if rp: rp = rp[:-1]
        
        sp = ''
        for k in self.symbol_primitives:
            sp += k + ':[' + print_list(self.symbol_primitives[k]) + '],'
        if sp: sp = sp[:-1]
        
        word_t = '实'
        if self.is_structural:
            word_t = '虚'
            
        return "%s, %s, %s, %s, %s, %s, %s" % \
            (self.word, self.type, word_t, self.first_primitive, op, '{' + rp + '}', '{' + sp + '}')
       
class Primitive(object):
    #所有中文词与其义原属性的对照表
    all_words = None
    #义原ID与义原的对照表
    all_primitives = None
    #义原英文与义原ID的对照表
    primitives_id = None
    
    @classmethod
    def init(cls):
        '''
        加载数据
        '''
        if cls.all_primitives is None:
            cls.all_primitives = {}
            cls.primitives_id = {}
            with open('data/WHOLE.DAT') as f:
                for line in f:
                    line_arr = line.strip().split()
                    
                    primitive = cls()
                    primitive.id = int(line_arr[0])
                    primitive.parent_id = int(line_arr[2])
                    
                    words = line_arr[1].split('|')
                    primitive.eng = words[0]
                    primitive.chi = words[1]
                    
                    cls.all_primitives[primitive.id] = primitive
                    cls.primitives_id[primitive.eng] = primitive.id
        
        if cls.all_words is None:
            cls.all_words = {}
            with open('data/glossary.dat') as f:
                for line in f:
                    word = cls.parse_word(line.strip())
                    
                    if cls.all_words.get(word.word) is None:
                        cls.all_words[word.word] = []
                        
                    cls.all_words[word.word].append(word)
                    
    @classmethod
    def parse_word(cls, line):
        word = Word()
        line_arr = line.split(None,2)
        word.word = line_arr[0]
        word.type = line_arr[1]
        
        parts = line_arr[2].strip()
        
        #虚词
        if parts[0] == '{':
            word.is_structural = True
            parts = parts[1:-1].strip()
        #分割属性
        parts_r = parts.split(',', 1)
        first = True
        while len(parts_r) > 0:
            cur_part = parts_r[0].strip()
            #实词的第一义原
            if first:
                word.first_primitive = Atom(cur_part)
            #关系义原
            else:
                if '=' in cur_part:
                    atom = Atom()
                    if cur_part[0] == '(':
                        atom.is_concrete = True
                        cur_part = cur_part[1:-1].strip()
                    relational_primitive = cur_part.split('=')
                    tmp = Atom(relational_primitive[0].strip())
                    atom.parse(relational_primitive[1].strip())
                    atom.rel_primitive = tmp.eng
                else:
                    atom = Atom(cur_part)
                
                word.add_primitive(atom)
            
            first = False
            if len(parts_r) > 1:
                parts_r = parts_r[1].strip().split(',', 1)
            else:
                parts_r = []
                
        return word
                    
    def __init__(self):
        self.id = 0
        self.parent_id = 0
        self.eng = None
        self.chi = None
        
    def is_top(self):
        '''
        此义原是顶级义原
        '''
        return self.id == self.parent_id
    
    def get_parents(self, primitive_eng):
        '''
        获取义原树
        '''
        result = []
        primitive_id = Primitive.primitives_id.get(primitive_eng)
        
        if primitive_id is not None:
            result.append(primitive_id)
            primitive_obj = Primitive.all_primitives.get(primitive_id)
            
            while not primitive_obj.is_top():
                parent_id = primitive_obj.parent_id
                result.append(parent_id)
                primitive_obj = Primitive.all_primitives.get(parent_id)
                
        return result
    
    def similar(self, primitive1_eng, primitive2_eng):
        '''
        义原相似度
        '''
        p = Primitive()
        l1 = p.get_parents(primitive1_eng)
        l2 = p.get_parents(primitive2_eng)
        for i,item1 in enumerate(l1):
            if item1 in l2:
                j = l2.index(item1)
                return alpha / (i + j + alpha)
        #两个无关义原之间的默认距离20
        return alpha / (20 + alpha)
    
Primitive.init()

WordType = {
    'PREFIX':0,
    'PREP':1,
    'ECHO':2,
    'EXPR':3,
    'SUFFIX':4,
    'PUNC':5,
    'N':6,
    'ADV':7,
    'CLAS':8,
    'COOR':9,
    'CONJ':10,
    'V':11,
    'STRU':12,
    'PP':13,
    'P':14,
    'ADJ':15,
    'PRON':16,
    'AUX':17,
    'NUM':18
}

#sim(p1,p2) = alpha/(d+alpha)
alpha = 1.6
#基本义原权重
beta1 = 0.5
#其他义原权重
beta2 = 0.2
#关系义原权重
beta3 = 0.17
#关系符号义原权重
beta4 = 0.13
#具体词与义原的相似度一律处理为一个比较小的常数. 具体词和具体词的相似度，如果两个词相同，则为1，否则为0
gamma = 0.2
#将任一非空值与空值的相似度定义为一个比较小的常数
delta = 0.2


def similar_inner(atom1, atom2):
    '''
    内部比较两个词，可能是为具体词，也可能是义原
    '''
    p = Primitive()
    
    #义原
    if not atom1.is_concrete and not atom2.is_concrete:
        return p.similar(atom1.eng, atom2.eng)
    #具体词
    if atom1.is_concrete and atom2.is_concrete:
        if atom1.chi == atom2.chi:
            return 1.0
        else:
            return 0.0
        
    #义原和具体词的相似度, 默认为gamma=0.2
    return gamma


def similar_list(l1_readonly, l2_readonly):
    l1 = copy.deepcopy(l1_readonly)
    l2 = copy.deepcopy(l2_readonly)
    '''
    比较两个集合的相似度
    '''
    l1_len = len(l1)
    l2_len = len(l2)
    if l1_len < 1 and l2_len < 1:
        return 1
    
    count = 0
    similar_sum = 0.0
    while count < min(l1_len, l2_len):
        similar_max = 0.0
        rm_item1 = rm_item2 = None
        for atom1 in l1:
            for atom2 in l2:
                similar = similar_inner(atom1, atom2)
                if similar > similar_max:
                    rm_item1 = atom1
                    rm_item2 = atom2
                    similar_max = similar
        
        similar_sum += similar_max
        if rm_item1 is not None: l1.remove(rm_item1)
        if rm_item2 is not None: l2.remove(rm_item2)
        count += 1
    
    return (similar_sum + delta * abs(l1_len - l2_len)) / max(l1_len, l2_len)
    
    
def similar_map(m1, m2):
    m1_len = len(m1)
    m2_len = len(m2)
    total = m1_len + m2_len
    
    if m1_len < 1 and m2_len < 1:
        return 1
    
    similar = 0.0
    count = 0
    for key1,l1 in m1.items():
        l2 = m2.get(key1)
        if l2 is not None:
            similar += similar_list(l1, l2)
            count += 1
    
    return (similar + delta * (total - 2 * count)) / (total - count)


def _similar_word(w1, w2):
    #虚词和实词的相似度为零
    if w1.is_structural != w2.is_structural:
        return 0.0
    #同虚词或同实词
    else:
        p = Primitive()
        #基本义原相似度
        product = p.similar(w1.first_primitive.eng, w2.first_primitive.eng)
        #其他基本义原相似度
        similar_op = similar_list(w1.other_primitives, w2.other_primitives)
        #关系义原相似度
        similar_rp = similar_map(w1.relational_primitives, w2.relational_primitives)
        #关系符号相似度
        similar_sp = similar_map(w1.symbol_primitives, w2.symbol_primitives)
        
        similar_sum = beta1 * product
        
        product *= similar_op
        similar_sum += beta2 * product;
        
        product *= similar_rp
        similar_sum += beta3 * product;
        
        product *= similar_sp
        similar_sum += beta4 * product;
        
        return similar_sum
    
def similar_word(w1_str, w2_str):
    w1_list = Primitive.all_words.get(w1_str)
    w2_list = Primitive.all_words.get(w2_str)
    if w1_list and w2_list:
        similar_max = 0
        for w1 in w1_list:
            for w2 in w2_list:
                similar = _similar_word(w1, w2)
                similar_max = max(similar_max, similar)
        
        return similar_max
    
if __name__ == '__main__':
#    for w in Primitive.all_words:
#        for t in Primitive.all_words.get(w):
#            print t
    print similar_word('男人','女人')#0.861
    print similar_word('男人','父亲')#1.0
    print similar_word('男人','母亲')#0.861
    print similar_word('男人','和尚')#0.861
    print similar_word('男人','经理')#0.63
    print similar_word('男人','高兴')#0.048
    print similar_word('男人','收音机')#0.112
    print similar_word('男人','鲤鱼')#0.209
    print similar_word('男人','苹果')#0.171
    print similar_word('男人','工作')#0.112
    print similar_word('男人','责任')#0.126
    print '====================='
    print similar_word('工人','教师')#0.722
    print similar_word('工人','科学家')#0.576
    print similar_word('工人','农民')#0.722
    print similar_word('工人','运动员')#0.722
    print '====================='
    print similar_word('教师','科学家')#0.576
    print similar_word('教师','农民')#0.722
    print similar_word('教师','运动员')#0.722
    print '====================='
    print similar_word('科学家','农民')#0.576
    print similar_word('科学家','运动员')#0.6
    print '====================='
    print similar_word('农民','运动员')#0.722
    print '====================='
    print similar_word('中国','美国')#0.936
    print similar_word('中国','欧洲')#0.0.733
    print similar_word('中国','联合国')#0.136
    print '====================='
    print similar_word('粉红','红')#1
    print similar_word('粉红','红色')#1
    print similar_word('粉红','绿')#0.861
    print similar_word('粉红','颜色')#0.059
