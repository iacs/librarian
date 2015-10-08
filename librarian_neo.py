#!/usr/bin/env python3
# coding: utf-8
#
#  __     ______     ______     __  __     ______
# /\ \   /\  __ \   /\  ___\   /\ \/\ \   /\  ___\
# \ \ \  \ \  __ \  \ \ \____  \ \ \_\ \  \ \___  \
#  \ \_\  \ \_\ \_\  \ \_____\  \ \_____\  \/\_____\
#   \/_/   \/_/\/_/   \/_____/   \/_____/   \/_____/
#
# Librarian 3.0.0
# SN: 151008
#
# Iago Mosquera
# Script para automatizar tareas de mantenimiento
# * Comprimir paquetes de archivos
# * Clasificación de archivos
# * Limpieza de archivos temporales
#
# Versión python.
# Configurado para cygwin
#

import os
import subprocess
import logging
from datetime import datetime, date, time

__author__ = 'Iago Mosquera'

FILE_SETTINGS = "librarian_config.yml"
FILE_LOG = "librarian.log"

settings = {}
log

def loadData(path):
    return yaml.safe_load(file.open(path, 'r', encoding='utf-8'))

def moverArchivos(lista, destino):
    if len(lista) > 1:
        for line in lista:
            subprocess.call(['mv', '-n', line, destino])
            log.info("Moviendo al trastero: {}", line)

def setupLogger(logFileName):
    dir_logs = settings['dir_logs']

    if not (os.path.exists(dir_logs)):
        os.makedirs(dir_logs)

    log = logging.getLogger('librarian')
    formatter = logging.Formatter(fmt='{asctime} [{levelname}] - {message}', style='{')
    fileHandler = logging.handlers.RotatingFileHandler(os.path.join(dir_logs, logFileName),
                                                       'a', 1048576, 10)

    fileHandler.setFormatter(formatter)
    log.setLevel(logging.INFO)
    log.addHandler(fileHandler)

    return log

def createBoxroomDirs():
    dir_boxroom = settings['dir_boxroom']

    for box in settings['boxroom']:
        path = os.path.join(dir_boxroom, box['name'])
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            log.info("Creando directorio: {}", dirname)

def moveVaultToBoxroom():
    vault = settings['dir_vault']
    trastero = settings['dir_boxroom']
    white_dirs = settings['white_dirs']
    dir_descargas = settings['dir_descargas']

    dias_antig = "+" + settings['days_old']

    if os.listdir(vault):
        result = subprocess.check_output(['find', vault, '-maxdepth', '1'])
        mover = result.split('\n')
        if vault in mover:
            mover.remove(vault)
        moverArchivos(mover, trastero)
    else:
        log.info("Baul vacío. Nada que mover")

    # Mover descargas antiguas
    result = subprocess.check_output([
                    'find',
                    dir_descargas,
                    '-maxdepth', '1',
                    '-type', 'f',
                    '-mtime', dias_antig,
                    ])

    if result:
        mover = result.split('\n')
        # for line in mover:
        #     subprocess.call(['mv', line, vault])
        #     print "moviendo", line
        moverArchivos(mover, vault)
            
    # Mover directorios
    result = subprocess.check_output([
                    'find',
                    dir_descargas,
                    '-maxdepth', '1',
                    '-type', 'd',
                    '-mtime', dias_antig,
                    ])

    if result:
        mover = result.split('\n')
        if "" in mover:
            mover.remove("")
        if dir_descargas in mover:
            mover.remove(dir_descargas)
        for d in white_dirs:
            # if dir_descargas + "/" + d in mover:
            if os.path.join(dir_descargas, d) in mover:
                mover.remove(os.path.join(dir_descargas, d))
        moverArchivos(mover, vault)


def main():
    global settings
    global log

    settings = loadData(FILE_SETTINGS)
    log = setupLogger(FILE_LOG)

    createBoxroomDirs()
    moveVaultToBoxroom()


if __name__ == '__main__':
    main()