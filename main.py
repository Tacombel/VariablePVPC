# Python 3.8

import os
import csv
import requests
import json

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


def precios_PVPC(dia):
    url = 'https://api.esios.ree.es/archives/70/download_json'
    params = dict(
        locale='es',
        date=dia[2] + '-' + dia[1] + '-' + dia[0]
    )
    resp = requests.get(url=url, params=params)
    data = resp.json()
    datos = {}
    for e in data['PVPC']:
        hora = e['Hora']
        hora = hora[3:]
        hora = hora.lstrip('0')
        datos[hora] = float(e['PCB'].replace(',', '.')) / 1000
    return datos


if __name__ == '__main__':
    potencia_instalada = float(input('Introducir potencia pico solar en kW a considerar (0 si no se desea) >>'))
    f = open('PV_2016_1kW.json')
    data = json.load(f)
    hourly = data['outputs']['hourly']
    PV = {}
    for e in hourly:
        PV[e['time']] = float(e['P']) / 1000

    consumo_periodo = 0
    compra_energia = 0
    compra_energia_sin_solar = 0
    venta_energia_maxima = 0
    date_PVPC = 'vacio'
    date_autoconsumo = 'vacio'
    consultas_API = 0
    lineas = 0
    dias = 0
    energia_consumida = 0
    energia_generada = 0
    energía_importada = 0
    energía_exportada = 0

    opciones = menu()
    for opcion in opciones:
        with open(opcion) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    dia = row[1].split('/')
                    hora = row[2]
                    hora = str(int(hora) - 1)
                    if len(hora) == 1:
                        hora = '0' + hora
                    else:
                        hora = hora
                    date_PV = '2016' + dia[1] + dia[0] + ':' + hora + '10'
                    consumo_linea = row[3]
                    consumo_linea = float(consumo_linea.replace(',', '.'))
                    energia_consumida += consumo_linea
                    consumo_comprado = consumo_linea - PV[date_PV] * potencia_instalada
                    energia_generada += PV[date_PV] * potencia_instalada
                    if consumo_comprado < 0:
                        energía_exportada += consumo_comprado * (-1)
                        consumo_comprado = 0
                    else:
                        energía_importada += consumo_comprado
                    if date_PVPC == 'vacio' or date_PVPC != row[1]:
                        precios_horarios = {}
                        date_PVPC = row[1]
                        precios_horarios = precios_PVPC(dia)
                        consultas_API += 1
                    compra_energia += consumo_comprado * precios_horarios[row[2]]
                    if potencia_instalada > 0:
                        compra_energia_sin_solar += consumo_linea * precios_horarios[row[2]]
                    line_count += 1
        lineas += line_count
        dias += (line_count - 1) / 24

    print(f'Lineas: {lineas}')
    print(f'Días considerados: {int(dias)}')
    print(f'Consultas al API: {consultas_API}')
    print(f'----------------------------------------------------------------------------------------------------------')
    print(f'Energía consumida: {energia_consumida:.3f} kWh')
    if potencia_instalada > 0:
        print(f'Energía generada: {energia_generada:.3f} kWh')
        print(f'Energía importada: {energía_importada:.3f} kWh')
        print(f'Energía exportada gratuitamente: {energía_exportada:.3f} kWh')
    print(f'Coste de la energía: {compra_energia:.2f}€')
    if potencia_instalada > 0:
            print(f'Ahorro: {compra_energia_sin_solar - compra_energia:.2f}€')
    print(f'Consumo medio diario de la red: {energía_importada / dias:.3f} kWh/dia')
    print(f'Precio medio de la energía: {compra_energia / energía_importada:.2f} €/kWh. Sin costes fijos ni impuestos.')
