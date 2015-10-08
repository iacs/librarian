#!/usr/bin/env python
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
#from subprocess import call

__author__ = 'Iago Mosquera'

syncfile = "sync.txt"
exclfile = "excl.txt"
logfile = "/cygdrive/e/data/logs/librarian.log"
logpath = "/cygdrive/e/data/logs/"
synclog = "/cygdrive/e/data/logs/rsync.log"

dir_descargas = "/cygdrive/e/Downloads"  # directorio de descargas
baul = "/cygdrive/e/Downloads/baul"      # directorio donde guardar temporalmente archivos viejos
trastero = "/cygdrive/e/trastero"        # directorio de almacenamiento de archivos viejos
origin = "/cygdrive/e/"
destination = "/cygdrive/f/backup2"
dir_packages = "/cygdrive/e/archived/Packages/"

# Directorios protegidos que no deben moverse
white_dirs = [
    "video",
    "img",
    "audio",
    "archff",
    "binaries",
    "data",
    "clasificar",
    "baul",
    "torrent",
    "jdl"
]

#
# Funciones
#


def clasificarPorRegex(regex):
    result = subprocess.check_output([
        'find',
        trastero,
        '-maxdepth', '1',
        '-type', 'f',
        '-regextype', 'posix-awk',
        '-iregex', regex
        ])
    
    return result.split('\n')

 
def moverArchivos(lista, destino):
    if len(lista) > 1:
        for line in lista:
            subprocess.call(['mv', '-n', line, destino])
            print "moviendo", line


def comprimirBackup(nombre_arch, destino="/cygdrive/e/archived/Packages/", *entradas):
    fuentes = ""
    for arch in entradas:
        fuentes = fuentes + " " + arch
        
    cmd = "zip " + "-FSr " + destino + nombre_arch + " " + fuentes
    
    os.system(cmd)


def logline():
    with open(logfile, "a") as logfd:
        line = datetime.now().strftime("[%Y-%m-%d] @ %I:%M:%S %p - Librarian executed\n")
        logfd.write(line)

#
# Setup
#

# Load preferences

# Logging
if not (os.path.exists(logpath)):
    os.makedirs(logpath)
log = logging.getLogger('librarian')
formatter = logging.Formatter(fmt='{asctime} [{levelname}] - {message}', style='{')
fileHandler = logging.handlers.RotatingFileHandler(os.path.join(logpath, "librarian.log"),
    'a', 1048576, 10)
fileHandler.setFormatter(formatter)
log.setLevel(logging.INFO)
log.addHandler(fileHandler)

t_video = trastero + "/video"
t_img = trastero + "/img"
t_audio = trastero + "/audio"
t_archive = trastero + "/archff"
t_bin = trastero + "/binaries"
t_data = trastero + "/data"
t_mess = trastero + "/clasificar"

dirs = [t_video, t_img, t_audio, t_archive, t_bin, t_data, t_mess]

for dirname in dirs:
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        #print "creando", dirname
        log.info("creando directorio: {}", dirname)


#
# Copia de seguridad
#

# Ejecutar comando de copia de seguridad
#rsync -avrh --delete-after --files-from=$LISTASYNC --log-file=$LOGFILE $OGDIR/d $BKDIR

#
# Limpieza de archivos
#


# Si el baúl no está vacío, mover al trastero
if os.listdir(baul):
    #result = subprocess.check_output(['ls', '-1', baul])
    result = subprocess.check_output(['find', baul, '-maxdepth', '1'])
    mover = result.split('\n')
    if baul in mover:
        mover.remove(baul)
    #for f in mover: print(f)
    moverArchivos(mover, trastero)
    #subprocess.call(['mv', baul + '/*', trastero])
else:
    print("Baul vacío. Nada que mover")
    
# Mover descargas antiguas
# Mover archivos
result = subprocess.check_output([
                'find',
                dir_descargas,
                '-maxdepth', '1',
                '-type', 'f',
                '-mtime', '+15',
                ])
#print(result)
if result:
    mover = result.split('\n')
    for line in mover:
        subprocess.call(['mv', line, baul])
        print "moviendo", line
        
# Mover directorios
result = subprocess.check_output([
                'find',
                dir_descargas,
                '-maxdepth', '1',
                '-type', 'd',
                '-mtime', '+15',
                ])

if result:
    mover = result.split('\n')
    if "" in mover:
        mover.remove("")
    if dir_descargas in mover:
        mover.remove(dir_descargas)
        #print("eliminado descargas")
    for d in white_dirs:
        #print(dir_descargas + "/" + d)
        if dir_descargas + "/" + d in mover:
            mover.remove(dir_descargas + "/" + d)
            #print("eliminado " + d)
    for line in mover:
        subprocess.call(['mv', line, baul])
        print "moviendo", line

# Clasificar trastero
lista_archivos = clasificarPorRegex(".*\.(avi|mpg|mp4|wmv|mkv|flv|webm)")
moverArchivos(lista_archivos, t_video)

lista_archivos = clasificarPorRegex(".*\.(jpg|jpeg|png|gif)")
moverArchivos(lista_archivos, t_img)

lista_archivos = clasificarPorRegex(".*\.(mp3|m4a|flac|ogg)")
moverArchivos(lista_archivos, t_audio)

lista_archivos = clasificarPorRegex(".*\.(zip|rar|7z|gz|bz2|iso)")
moverArchivos(lista_archivos, t_archive)

lista_archivos = clasificarPorRegex(".*\.(exe|msi|msu|deb|rpm)")
moverArchivos(lista_archivos, t_bin)

lista_archivos = clasificarPorRegex(".*\.(pdf|txt|doc|docx)")
moverArchivos(lista_archivos, t_data)

# Archivar directorios
result = subprocess.check_output([
                'find',
                trastero,
                '-maxdepth', '1',
                '-type', 'd',
                ])

if result:
    mover = result.split('\n')
    if "" in mover:
        mover.remove("")
    if trastero in mover:
        mover.remove(trastero)
    for d in white_dirs:
        #print(dir_descargas + "/" + d)
        if trastero + "/" + d in mover:
            mover.remove(trastero + "/" + d)
            #print("eliminado " + d)
    for line in mover:
        subprocess.call(['mv', line, t_mess])
        print "moviendo", line

#
# Borrar archivos temporales
#

dir_tmp = "/cygdrive/e/tmp/*"

print("Eliminando archivos temporales...")
subprocess.call(['rm', '-rf', dir_tmp])

#
# Crear archivos comprimidos
#

print("Comprimiendo archivos extra...")

comprimirBackup('st3_pack-master', dir_packages, "/cygdrive/c/Users/Iago\ Mosquera/AppData/Roaming/Sublime\ Text\ 3/Packages/")

# Self-backup
comprimirBackup('librarian', dir_packages,
                "/cygdrive/e/data/src/scripts/librarian/librarian.py",
                "/cygdrive/e/data/src/scripts/librarian/settings_librarian.yml",
                "/home/Iago\ Mosquera/sync.txt",
                "/home/Iago\ Mosquera/excl.txt")

#
# Sincronizar copia de seguridad
#

# print("Sincronizando copia de seguridad...")

# subprocess.call([
#     'rsync',
#     '-avprh',
#     '--delete-after',
#     '--modify-window=3',
#     '--files-from=' + syncfile,
#     '--exclude-from=' + exclfile,
#     '--log-file=' + synclog,
#     origin,
#     destination
#     ])

#
# Escribir en el log
#

logline()

#
# Fin
#

print("Copia de seguridad terminada.")
