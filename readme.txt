Utilidad para comparar lo facturado con lo consumido, teniendo em cuenta los precios horarios, para tarifa PVPC
Solo es valido para consumos a partir de los cambios tarifarios de junio de 2021
Para empezar hay que bajar el fichero consumo_facturado* de tu distribuidor y colocarlo en el directorio de main.py
En mi caso es i-DE (Iberdrola distribución) www.i-de.es
Al ejecutar el programa la cifra en euros que da es el total de la parte correspondiente a energía, antes de impuestos.
En el caso de Curenergía es la suma de:
  Total peaje de transporte y distribución energía
  Total cargos energía
  Coste de la energía
Hay algún tema de redondeos por ahí, por que la cifra discrepa en algunos céntimos de la de la factura.
La razón principal de este ejercicio era comprobar que lo de llano, valle y punta no tiene ya ningún significado
Al aplicarse los precios horarios resulta perfectamente posible que una hora valle sea mas cara que una hora punta
Como ejemplo en https://www.esios.ree.es/es/pvpc compara el precio de un sábado a las 20 horas con un dia entre
semana a las 13 horas y veras que divertido.
O un día cualquiera, compara el precio a las 7 y a las 15.

Hay tambien un cálculo básico de ahorros con energía solar. Para usarlo hay que bajarse el fichero de datos de aqui
https://re.jrc.ec.europa.eu/pvg_tools/es/#PVP marcando en el mapa la ubicación de la instalación, eligiendo 2016 como
ño inicial y final y tecleando una potencia pico de 1
Hay que descargar los datos en formato json, renombrar el fichero PV_2016_1kW.json y ponerlo en el mismo directorio de
main.py
