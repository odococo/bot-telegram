from typing import Dict


class Code:
    def __init__(self, n: int):
        self.n = n  # number of digits
        self.codes = {}
        self.code = [[str(c) for c in range(0, 10)] for i in range(0, n)]
        print(self.code)

    def test(self, code: str, giuste: int, presenti: int):
        sbagliate = self.n - giuste - presenti
        self.codes[code] = {
            'yes': giuste,
            'ok': presenti,
            'no': sbagliate
        }

        self.crack()
        #self.solutions()

    def crack(self):
        for code, value in self.codes.items():
            self.compare(code, value)
        print(self.code)

    def compare(self, code: str, value: Dict):
        for c, v in self.codes.items():
            if code != c:
                differences = {}
                for i in range(0, self.n):  # confronto ciascun carattere
                    if (c[i] != code[i]):
                        differences['num'][i] = {
                            'old': c[i],
                            'new': code[i]
                        }
                differences['yes'] = {
                    'old': v['yes'],
                    'new': v['yes']
                }
                differences['ok'] = {
                    'old': v['ok'],
                    'new': v['ok']
                }
                if differences['yes']['old'] + differences['ok']['old'] > differences['yes']['new'] + differences['ok']['new']


    def solutions(self):
        if sum([len(c) for c in self.code]) <= self.n * self.n:
            self._iter(0, '')

    def _iter(self, i: int, code: str):
        if i == self.n:
            print(code)
        else:
            for c in self.code[i]:
                self._iter(i + 1, code + c)


def test():
    c = Code(6)
    c.test('123456', 0, 5)
    c.test('123457', 1, 4)  # 7 nel posto giusto e 6 numero papabile ==> i 6 numeri sono in 1234567
    c.test('123458', 0, 4)  # 8 non c'e'
    c.test('123459', 0, 4)  # 9 non c'e'
    c.test('123450', 0, 4)  # 0 non c'e'
    c.test('123476', 0, 5)  # 5 c'e'
    c.test('123756', 0, 5)  # 4 c'e'
    c.test('126456', 0, 5)  # 3 c'e'
    c.test('173456', 0, 5)  # 2 c'e' ==> 1 non c'e'
    c.test('234567', 1, 5)
    c.test('243567', 2, 4)  # 4 nel posto giusto
    c.test('342567', 2, 4)
    c.test('542367', 3, 3)  # 5 o 3 nel posto giusto
    c.test('543267', 4, 2)  # 5  e 2 nel posto giusto
    c.test('546237', 6, 0)  # soluzione


if __name__ == '__main__':
    test()
