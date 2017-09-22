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
import yaml
import logging
import logging.handlers

__author__ = 'Iago Mosquera'

FILE_SETTINGS = "settings_librarian.yml"
FILE_LOG = "librarian.log"
ENCODING = "utf-8"

settings = {}
log = ""


def loadData(path):
    return yaml.safe_load(open(path, 'r', encoding='utf-8'))


def moverArchivos(lista, destino):
    if len(lista) >= 1:
        for line in lista:
            subprocess.call(['mv', '-n', line, destino])
            log.info("Moviendo archivo: {0}".format(line))


def clasificarPorRegex(regex):
    trastero = settings['dir_boxroom']
    result = subprocess.check_output([
        'find',
        trastero,
        '-maxdepth', '1',
        '-type', 'f',
        '-regextype', 'posix-awk',
        '-iregex', regex
        ])
    
    return result.decode(ENCODING).split('\n')


# def comprimirBackup(nombre_arch, destino="/cygdrive/e/archived/Packages/", *entradas):
#     fuentes = ""
#     for arch in entradas:
#         fuentes = fuentes + " " + arch
        
#     cmd = "zip " + "-FSr " + destino + nombre_arch + " " + fuentes
    
#     os.system(cmd)


def getBoxPath(boxname):
    trastero = settings['dir_boxroom']

    return os.path.join(trastero, boxname)


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
        if not os.path.exists(path):
            os.makedirs(path)
            log.info("Creando directorio: {0}".format(path))


def moveVaultToBoxroom():
    vault = settings['dir_vault']
    trastero = settings['dir_boxroom']
    white_dirs = settings['white_dirs']
    dir_descargas = settings['dir_dls']

    dias_antig = "+" + str(settings['days_old'])

    if os.listdir(vault):
        result = subprocess.check_output(['find', vault, '-maxdepth', '1'])
        mover = result.decode(ENCODING).split('\n')
        if "" in mover:
            mover.remove("")
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
        mover = result.decode(ENCODING).split('\n')
        if "" in mover:
            mover.remove("")
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
        mover = result.decode(ENCODING).split('\n')
        if "" in mover:
            mover.remove("")
        if dir_descargas in mover:
            mover.remove(dir_descargas)
        for d in white_dirs:
            if os.path.join(dir_descargas, d) in mover:
                mover.remove(os.path.join(dir_descargas, d))
        moverArchivos(mover, vault)


def sortBoxroom():
    boxroom = settings['boxroom']
    trastero = settings['dir_boxroom']
    white_dirs = settings['white_dirs']

    for set in boxroom:
        box = getBoxPath(set['name'])
        regex = ".*\.("
        for ext in set['filetypes'][:-1]:
            regex = regex + ext + "|"
        regex = regex + set['filetypes'][-1] + ")"
        log.debug("Using regex: {0}".format(regex))
        fileList = clasificarPorRegex(regex)
        if fileList:
            if "" in fileList:
                fileList.remove("")
            moverArchivos(fileList, box)

    box = getBoxPath(settings['box_misc'])
    result = subprocess.check_output([
        'find',
        trastero,
        '-maxdepth', '1',
        '-type', 'f',
        ])
    if result:
        mover = result.decode(ENCODING).split('\n')
        if "" in mover:
            mover.remove("")
        moverArchivos(mover, box)

    result = subprocess.check_output([
        'find',
        trastero,
        '-maxdepth', '1',
        '-type', 'd',
        ])

    if result:
        mover = result.decode(ENCODING).split('\n')
        if "" in mover:
            mover.remove("")
        if trastero in mover:
            mover.remove(trastero)
        for d in white_dirs:
            if os.path.join(trastero, d) in mover:
                mover.remove(os.path.join(trastero, d))
        moverArchivos(mover, box)


def deleteTmp():
    dir_tmp = settings['dir_tmp']
    subprocess.call(['rm', '-rf', dir_tmp])


# def makeArchives():
#     dir_packages = settings['dir_packages']

#     for set in settings['archives']:
#         # using * to unpack the list into args
#         comprimirBackup(set['name'], dir_packages, *set['paths'])


def main():
    global settings
    global log

    settings = loadData(FILE_SETTINGS)
    log = setupLogger(FILE_LOG)

    createBoxroomDirs()
    moveVaultToBoxroom()
    # Backup would go here <-
    sortBoxroom()
    deleteTmp()
    # makeArchives()

    log.info("Librarian - ejecución finalizada")


if __name__ == '__main__':
    main()
