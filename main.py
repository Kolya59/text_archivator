class Tree:
    def __init__(self, left, right, symbol: str, probability: float):
        self.left = left
        self.right = right
        self.symbol = symbol
        self.probability = probability

    def __str__(self):
        return '({%s} | %s | %s)' % (str(self.left), str(self.symbol), str(self.right))


def unpack(data: bytes, tree: Tree) -> str:
    return parse_code(bytes_to_code(data), tree)


def pack(data: str, tree: Tree) -> bytes:
    res = ''
    for i, el in enumerate(data):
        code = find_code(el, tree)
        res += code
        print('On iter: ' + str(i) + ' Element ' + el + ' has code: ' + code + '\n')
    return code_to_bytes(res)


def bytes_to_code(data: bytes) -> str:
    ints = []
    for _, b in enumerate(data):
        ints += int.from_bytes(b, byteorder='big')
    s = ''
    for _, i in enumerate(ints):
        s += '{0:b}'.format(i)
    return s


def parse_code(code: str, tree: Tree) -> str:
    tmp_tree = tree
    res = ''
    for _, b in enumerate(code):
        if len(tmp_tree.symbol) <= 1:
            res += tmp_tree.symbol
            tmp_tree = tree
            continue
        tmp_tree = tmp_tree.left if b == 0 else tmp_tree.right
    return res


def code_to_bytes(code: str) -> bytes:
    b = []
    for i in range(0, len(code), 8):
        packet = code[i:i+8]
        b += int(packet, 2)
    # TODO: Check last byte
    if len(code[i:len(code)]) > 0:
        b += code[i:len(code)]
    return bytes(b)


def find_code(symbol: str, tree: Tree) -> str:
    if tree.left is not None and symbol in tree.left.symbol:
        return '0' + find_code(symbol, tree.left)
    if tree.right is not None and symbol in tree.right.symbol:
        return '1' + find_code(symbol, tree.right)
    return ''


def list_to_tree(data: [(str, float)]) -> Tree:
    source = []
    for _, el in enumerate(data):
        source.append(Tree(None, None, el[0], el[1]))

    while len(source) != 1:
        new = Tree(None, None, '', 0.0)
        fst = min(source, key=lambda x: x.probability)
        source.remove(fst)
        snd = min(source, key=lambda x: x.probability)
        if fst == snd:
            snd = None
        else:
            source.remove(snd)
        new.left = fst
        new.right = snd
        new.symbol = fst.symbol + snd.symbol
        new.probability = fst.probability + snd.probability
        source.append(new)
    return source[0]


if __name__ == '__main__':
    # Get data
    source = open('./freq.txt', newline='\n', encoding='utf-16').read()
    data: [str, float] = [('\n', 0.0152592971737005), (' ', 0.190767000311362)]
    for _, elem in enumerate(source.split('\r\n')):
        sp = elem.split(' ')
        symbol = sp[0]
        prob = float(sp[1])
        data.append((symbol, prob))

    tree = list_to_tree(data)
    original = open('./original.txt', 'r').read()
    packed = pack(original, tree)
    packed_file = open('./packed.txt', 'w').write(packed)
    unpacked = unpack(packed, tree)
    unpacked_file = open('./unpacked.txt', 'w').write(unpacked)
    if original == unpacked:
        print('All is ok')
    else:
        print('All is not ok')
