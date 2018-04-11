from functools import reduce

count = int(input('Введите количество предприятий: '))
data = dict()


for i in range(count):
    data[input('Введите название {} предприятия: '.format(str(i + 1)))] = \
        int(input('Введите квартальную прибыль {} предприятия: '.format(str(i + 1))))

mid = (reduce(lambda x, y: x + y, data.values())) / len(data)
good = []
bad = []

for k, v in data.items():
    if v > mid:
        good.append(k)
    elif v < mid:
        bad.append(k)

print('Прибыль выше среднего: ', end='')
for i in good:
    print(i, ' ', end='')

print('\nПрибыль ниже среднего: ', end='')
for i in bad:
    print(i, ' ', end='')
