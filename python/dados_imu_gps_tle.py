# -*- coding: utf-8 -*-
"""Dados IMU/GPS TLE.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bcNQBUEfh_fwnw039FwXUMqK3InUEiIY

## sgp4 --
Para a propagação dos TLE, a biblioteca sgp4 obtem a posição e velocidade do satélite. Esses dados serão utilizados para simular as medições do GPS e IMU, usaremos as mudanças na posição e velocidade para calcular as acelerações e rotações.
"""

pip install sgp4

"""## Simulação dos dados IMU/GPS

Dados com ruídos dos sensores incluídos
"""

import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta

# Constantes
G = 6.67430e-11  # Constante gravitacional
M_terra = 5.972e24  # Massa da Terra em kg

# IMU MEMS MPU-6050
# Parâmetros de ruído para MEMS
ACELEROMETRO_RUIDO_BRANCO = 0.098  # m/s^2
ACELEROMETRO_BIAS = 0.49  # m/s^2
ACELEROMETRO_DERIVA = 0.001  # m/s^2 por segundo

GIROSCOPIO_RUIDO_BRANCO = 0.01  # graus/segundo
GIROSCOPIO_BIAS = 0.01  # graus/segundo
GIROSCOPIO_DERIVA = 0.0001  # graus/segundo por segundo

# GPS UBlox NEO-6M
GPS_RUIDO = 3.0  # Desvio padrão do ruído do GPS em metros

def calcular_aceleracao_gravitacional(pos):
    """ Calcula a aceleração gravitacional na posição dada. """
    r = np.linalg.norm(pos)
    return -G * M_terra / r**3 * pos

def adicionar_ruído(dados, desvio_padrão):
    """ Adiciona ruído gaussiano aos dados. """
    return dados + np.random.normal(0, desvio_padrão, dados.shape)

def simular_dados(tle_line1, tle_line2, dt_seconds=10, duration_minutes=10):
    satellite = Satrec.twoline2rv(tle_line1, tle_line2)
    start_time = datetime.utcnow()
    time_step = timedelta(seconds=dt_seconds)
    duration = timedelta(minutes=duration_minutes)

    times = []
    positions = []
    velocities = []

    current_time = start_time
    while current_time < start_time + duration:
        jd, fr = jday(current_time.year, current_time.month, current_time.day,
                      current_time.hour, current_time.minute, current_time.second + current_time.microsecond * 1e-6)
        e, r, v = satellite.sgp4(jd, fr)
        if e == 0:
            times.append(current_time)
            positions.append(r)
            velocities.append(v)
        else:
            print("Error propagating TLE: ", e)
        current_time += time_step

    positions = np.array(positions)
    velocities = np.array(velocities)

    # Calcular acelerações (incluindo gravidade)
    accelerations = []
    for i in range(1, len(velocities) - 1):
        a_orbital = (velocities[i + 1] - velocities[i - 1]) / (2 * dt_seconds)
        a_gravitational = calcular_aceleracao_gravitacional(positions[i])
        a_total = a_orbital + a_gravitational
        accelerations.append(a_total)

    accelerations = np.array(accelerations)

    # Adicionar ruído ao acelerômetro
    acelerometro_bias = np.random.normal(0, ACELEROMETRO_BIAS, accelerations.shape[1])
    acelerometro_ruido = adicionar_ruído(accelerations, ACELEROMETRO_RUIDO_BRANCO)
    acelerometro_deriva = np.cumsum(np.random.normal(0, ACELEROMETRO_DERIVA, accelerations.shape), axis=0)
    accelerations = acelerometro_ruido + acelerometro_bias + acelerometro_deriva

    # Calcular rotações (omegas)
    omegas = []
    for i in range(1, len(positions) - 1):
        v1 = velocities[i]
        v2 = velocities[i + 1]
        omega = np.cross(v1, v2) / np.linalg.norm(v1)
        omegas.append(omega)
    omegas = np.array(omegas)

    # Adicionar ruído ao giroscópio
    giroscopio_bias = np.random.normal(0, GIROSCOPIO_BIAS, omegas.shape[1])
    giroscopio_ruido = adicionar_ruído(omegas, GIROSCOPIO_RUIDO_BRANCO)
    giroscopio_deriva = np.cumsum(np.random.normal(0, GIROSCOPIO_DERIVA, omegas.shape), axis=0)
    omegas = giroscopio_ruido + giroscopio_bias + giroscopio_deriva

    # Adicionar ruído aos dados de GPS
    positions = adicionar_ruído(positions, GPS_RUIDO)

    return times[1:-1], positions[1:-1], velocities[1:-1], accelerations, omegas

# Exemplo de uso
tle_line1 = "1 25544U 98067A   20356.91754743  .00016717  00000-0  10270-3 0  9008"
tle_line2 = "2 25544  51.6431  21.3564 0000368  93.0661 287.0303 15.49182665261367"

times, positions, velocities, accelerations, omegas = simular_dados(tle_line1, tle_line2)

# Exibição dos dados simulados com ruído
print(f"Times: {times}\n")
print(f"Positions: {positions}\n")
print(f"Velocities: {velocities}\n")
print(f"Accelerations: {accelerations}\n")
print(f"Omegas: {omegas}")

"""Dados gerados sem os ruídos totais inseridos"""

import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta

def simular_dados(tle_line1, tle_line2, dt_seconds=10, duration_minutes=10):
    satellite = Satrec.twoline2rv(tle_line1, tle_line2)
    start_time = datetime.utcnow()
    time_step = timedelta(seconds=dt_seconds)
    duration = timedelta(minutes=duration_minutes)

    times = []
    positions = []
    velocities = []

    current_time = start_time
    while current_time < start_time + duration:
        jd, fr = jday(current_time.year, current_time.month, current_time.day,
                      current_time.hour, current_time.minute, current_time.second + current_time.microsecond * 1e-6)
        e, r, v = satellite.sgp4(jd, fr)
        if e == 0:
            times.append(current_time)
            positions.append(r)
            velocities.append(v)
        else:
            print("Error propagating TLE: ", e)
        current_time += time_step

    positions = np.array(positions)
    velocities = np.array(velocities)

    # Calcular acelerações
    accelerations = np.diff(velocities, axis=0) / dt_seconds

    # Calcular rotações (omegas)
    omegas = []
    for i in range(1, len(positions) - 1):
        v1 = velocities[i]
        v2 = velocities[i + 1]
        omega = np.cross(v1, v2) / np.linalg.norm(v1)
        omegas.append(omega)
    omegas = np.array(omegas)

    return times[:-1], positions[:-1], velocities[:-1], accelerations, omegas

# Insirir o TLE do Celestrak
tle_line1 = "1 25544U 98067A   20356.91754743  .00016717  00000-0  10270-3 0  9008"
tle_line2 = "2 25544  51.6431  21.3564 0000368  93.0661 287.0303 15.49182665261367"

times, positions, velocities, accelerations, omegas = simular_dados(tle_line1, tle_line2)

print(f"Times: {times}\n")
print(f"Positions: {positions}\n")
print(f"Velocities: {velocities}\n")
print(f"Accelerations: {accelerations}\n")
print(f"Omegas: {omegas}\n")