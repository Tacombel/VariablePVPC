# Python 3.8

import os
import csv
import requests

def menu():
    path = './'
    counter = 1
    opciones = []
    # r=root, d=directories, f = files
    for f1 in os.walk(path):
        for file1 in f1[2]:
            if 'consumo' in file1:
                opciones.append(file1)
                print(counter, ': ', file1)
                counter += 1
        print(f'0 :  procesar todos los ficheros')
        opcion_menu = input("Elije un fichero >> ")
        if opcion_menu == '0':
            print(f'Procesaremos todos los ficheros y daremos un resultado agregado')
        else:
            print('Procesaremos el fichero:', opciones[int(opcion_menu) - 1])
            elegido = opciones[int(opcion_menu) - 1]
            opciones = []
            opciones.append(elegido)
        return opciones


if __name__ == '__main__':
    consumo_mes = 0
    gasto_mes = 0
    date = 'vacio'
    consultas_al_api = 0
    lineas = 0
    dias = 0

    opciones = menu()
    for opcion in opciones:
        with open(opcion) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    consumo = row[3]
                    consumo = consumo.replace(',', '.')
                    consumo = float(consumo)
                    consumo_mes = consumo_mes + consumo
                    # print(f'{row[1]} {row[2]} {consumo} - {consumo_mes}')
                    if date == 'vacio' or date != row[1]:
                        consultas_al_api += 1
                        date = row[1]
                        # print(f'Descargando {date}')
                        dia = date.split('/')
                        url = 'https://api.esios.ree.es/archives/70/download_json'
                        params = dict(
                            locale='es',
                            date=dia[2] + '-' + dia[1] + '-' + dia[0]
                        )
                        resp = requests.get(url=url, params=params)
                        data = resp.json()
                        precios_horarios = {}
                        for e in data['PVPC']:
                            hora = e['Hora']
                            hora = hora[3:]
                            hora = hora.lstrip('0')
                            precio = e['PCB']
                            precio = precio.replace(',', '.')
                            precios_horarios[hora] = float(precio) / 1000
                    gasto_mes = gasto_mes + (float(consumo) * precios_horarios[row[2]])
                    line_count += 1
        lineas += line_count
        dias += (line_count - 1) / 24

    print(f'Lineas: {lineas}')
    print(f'Días considerados: {int(dias)}')
    print(f'Consultas a la API: {consultas_al_api}')
    print(f'Consumo: {consumo_mes:.3f} KWh')
    print(f'Coste de la energía: {gasto_mes:.2f}€')
    print(f'Consumo medio diario: {consumo_mes/ (line_count - 1) * 24:.3f} kWh/dia')
    print(f'Precio medio de la energía: {gasto_mes/consumo_mes:.2f} €/kWh. Sin termino fijo y antes de impuestos.')
