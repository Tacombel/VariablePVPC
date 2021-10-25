# Python 3.8

import os
import csv
import requests
import json
from secrets import *

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


def precio_autoconsumo(principio, fin):
    url = 'https://api.esios.ree.es/indicators/1739'
    headers = {
        'Accept':'application/json; application/vnd.esios-api-v1+json',
        'Content-Type':'application/json',
        'Host':'api.esios.ree.es',
        'Authorization':'Token token=' + esios_token
    }
    params = dict(
        start_date= principio,
        end_date= fin
    )
    resp = requests.get(url=url, headers=headers, params=params)
    data = resp.json()
    return data


def formatear_hora(row):
    dia = row[1].split('/')
    hora = row[2]
    hora = str(int(hora) - 1)
    if len(hora) == 1:
        hora = '0' + hora
    else:
        hora = hora
    return dia[2] + dia[1] + dia[0] + 'T' + hora + ':00'


if __name__ == '__main__':
    potencia_instalada = float(input('Introducir potencia pico solar en kW a considerar (0 si no se desea) >>'))
    if potencia_instalada > 0:
        f = open('PV_2016_1kW.json')
        data = json.load(f)
        hourly = data['outputs']['hourly']
        PV = {}
        for e in hourly:
            PV[e['time']] = float(e['P']) / 1000

    consumo_periodo = 0
    compra_energia = 0
    compra_energia_sin_solar = 0
    venta_energia_total = 0
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
            rows = list(csv_reader)
            print(f'Primera fecha: {formatear_hora(rows[1])}')
            print(f'Primera fecha: {formatear_hora(rows[-1])}')
            precios_autoconsumo = precio_autoconsumo(formatear_hora(rows[1]), formatear_hora(rows[-1]))['indicator']['values']
            precios_autoconsumo_dict = {}
            for e in precios_autoconsumo:
                precios_autoconsumo_dict[e['datetime']] = e['value']
            for row in rows:
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
                    consumo_comprado = consumo_linea
                    if potencia_instalada > 0:
                        consumo_comprado = consumo_linea - PV[date_PV] * potencia_instalada
                        energia_generada += PV[date_PV] * potencia_instalada
                    if consumo_comprado < 0:
                        energía_exportada += consumo_comprado * (-1)
                        date_AC = f'{dia[2]}-{dia[1]}-{dia[0]}T{hora}:00:00.000+02:00'
                        venta_energia_total += consumo_comprado * precios_autoconsumo_dict[date_AC] / 1000 * (-1)
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
        print(f'Energía exportada: {energía_exportada:.3f} kWh')
    print(f'Compra de energía: {compra_energia:.2f}€')
    if potencia_instalada > 0:
        print(f'Venta de energía: {venta_energia_total:.2f}€')
        if venta_energia_total > compra_energia:
            venta_energia_total = compra_energia
        print(f'Coste facturado: {compra_energia - venta_energia_total:.2f}€')
        print(f'Ahorro: {compra_energia_sin_solar - compra_energia + venta_energia_total:.2f}€')
    print(f'Sin costes fijos ni impuestos.')
