import requests
import json
import pandas
import warnings

warnings.filterwarnings('ignore')

# #################Выгрузка данных о вакансиях с HH.RU######################
"""
Вакансии брались по ключевой фразе "Специалист по ИБ"
Данные о вакансиях выгружались в csv-файл
Столбцы в csv-файле: название вакансии (name), минимальная ЗП (from),
    максимальная ЗП (to), валюта (currency)
"""
vacancy = 'Специалист по информационной безопасности'


# Функция для открытия страниц hh.ru с вакансиями
def getVacancies():
    URL = 'https://api.hh.ru/vacancies'
    par = {'text': vacancy,
           'area': 2,  # регион: Санкт-Петербург
           'page': i,
           'per_page': 100}
    response = requests.get(URL, par)
    response.close()
    return response

# Считываем со страниц hh.ru первые 5000 вакансий
file1_name = 'IB_SPB.csv'  # файл, в который будут записаны выгруженные данные
info_list = []

for i in range(0, 50):
    info_json = getVacancies().json()
    info_list.append(info_json)
    root_keys = ['name']  # ключи json "верхнего уровня", выборка для csv-файла
    salary_keys = ['from', 'to', 'currency']  # ключи salary, выборка для csv

    # датафрейм 1 - название вакансии
    df1 = pandas.DataFrame(columns=list(root_keys))
    count = 0
    for i in range(len(info_list)):
        for j in range(len(info_list[i]['items'])):
            df1.loc[count] = info_list[i]['items'][j]
            count += 1

    # датафрейм 2 - зарплата
    df2 = pandas.DataFrame(columns=list(salary_keys))
    count = 0
    for i in range(len(info_list)):
        for j in range(len(info_list[i]['items'])):
            df2.loc[count] = info_list[i]['items'][j]['salary']
            count += 1

    if (info_json['pages'] - i) <= 1:  # если страниц меньше 50, прерываем цикл
        break

df3 = df1.join(df2)  # объединяем датафреймы
df3.to_csv(file1_name)  # создаем файл csv с выгруженными данными о вакансиях
print ('\nCоздан файл', file1_name, 'с выгруженными данными о вакансиях')


# ######################Расчет средней зарплаты ##############################
"""
Там где указывался диапазон ЗП, бралось среднее значение
В выгружнных данных ЗП указывалась в рублях и в долларах
Доллары переводились в рубли, итоговая средняя считалась в рублях
"""

dollar_cource = 83.35  # курс доллара к рублю
data = pandas.read_csv(file1_name)
df = pandas.DataFrame(data)

# Заполнение null-значений в ячейках
salary_from = pandas.DataFrame(df['from'].fillna(df['to']))
salary_to = pandas.DataFrame(df['to'].fillna(df['from']))
salary_cur = pandas.DataFrame(df['currency'])
salary_all = salary_from.join(salary_to).join(salary_cur)

# Выборка строк с рублями и долларами
rubles = salary_all.loc[salary_all['currency'] == 'RUR']
dollars = salary_all.loc[salary_all['currency'] == 'USD']

# Расчет средней ЗП
a1 = ((rubles['from']+rubles['to'])/2).sum()  # сумма всех рубевых ЗП
# сумма всех долларовых ЗП, переведенная в рубли:
a2 = (((dollars['from']+dollars['to'])/2).sum()) * dollar_cource
b = len(rubles.index)+len(dollars.index)  # количество вакансий
avg_salary = round((a1+a2)/b, 0)  # средняя зарплата

# Запись данных о средней зарплате в txt-файл
file2_name = 'otchet.txt'
region = 'Санкт-Петербург'
file = open('otchet.txt', 'w')
file.write('Регион: ' + region + '\n')
file.write('Тип вакансий: ' + vacancy + '\n')
file.write('Количество вакансий: ' + str(len(df.index)) + '\n')
file.write('Cредняя зарплата (в рублях): ' + str(avg_salary) + ' руб.')
file.close()
print('\nCоздан файл', file2_name, 'с данными по средней зарплате')
