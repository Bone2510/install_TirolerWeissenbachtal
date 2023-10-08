#!/usr/bin/env python

import requests
import tempfile
from pathlib import Path
import sys
import zipfile
import shutil
import os
import distutils.dir_util
from lxml import etree as et
from termcolor import colored

#    Tiroler_Weißenbachtal installer

#    Script to make installation of the LS22 Tiroler_Weißenbachtal map easier
#
#    @author: 	[LSFM] Bone2510
#    @date: 	08.10.2023
#    @version:	1.0
#
#    History:	v1.0 @08.10.2023 - Initial implementation
#                --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def download(url, file):
    r = requests.get(url, allow_redirects=True, stream=True)
    f = open(file, "wb")

    total_length = r.headers.get('content-length')
    dl = 0
    total_length = int(total_length)
    for data in r.iter_content(chunk_size=4096):
        dl += len(data)
        f.write(data)
        done = int(50 * dl / total_length)
        sys.stdout.write("\rFortschritt: [%s%s]" % ('=' * done, ' ' * (50 - done)))
        sys.stdout.flush()

    f.close()
    return file

def main():
    print("Tiroler Weißenbachtal v1.0 installer by [LSFM] Bone2510")
    print("\nLade FS22_Tiroler_Weißenbachtal von https://www.heimahd.com herunter...")

    temp_dir = Path(tempfile.mkdtemp())

    #print("Temp Path: " + temp_dir.__str__())

    url="https://www.heimahd.com/assets/downloads/FS22_Tiroler_Weissenbachtal.zip?"
    mapPath = download(url, temp_dir / "FS22_Tiroler_Weissenbachtal.zip")

    selectValid = False
    url2 = None
    while not selectValid:
        print("\n")
        print("Welche Fahrzeuge möchtest du verwenden?")
        print("\t 1. Standard LS22 Fahrzeuge")
        print("\t 2. Hay and Forage Fahrzeuge (Hay and Forage DLC wird benötigt)")

        defaultVehicleIndex = int(input("Auswahl: "))

        if defaultVehicleIndex > 0 and defaultVehicleIndex < 3:
            selectValid = True

            if defaultVehicleIndex == 1:
                url2="https://cloud.bayerngamers.de/index.php/s/Q9Y3xGt4gZK5RrC/download/placeables_vehicles.zip"

            elif defaultVehicleIndex == 2:
                url2 = "https://cloud.bayerngamers.de/index.php/s/tiwz5qD4cH385j5/download/placeables_vehicles_Hey_and_forage.zip"

    if url2 is None:
        print("Fehler: URL für defaultVehicle.xml nicht gesetzt!")

    print("\nDownloading defaultVehicle.xml.")
    defaultVehiclePath = download(url2, temp_dir / "defaultVehicles.zip")

    mapDir = temp_dir / "FS22_Tiroler_Weissenbachtal"
    defaultVehicleDir = temp_dir / "defaultVehicles"

    print("\nEnt-zippe Dateien. Bite warten... ")

    with zipfile.ZipFile(mapPath, 'r') as mapFile:
        mapFile.extractall(temp_dir / "FS22_Tiroler_Weissenbachtal")

    with zipfile.ZipFile(defaultVehiclePath, 'r') as defaultVehicleFile:
        defaultVehicleFile.extractall(temp_dir / "defaultVehicles")

    print("Fertig!")

    #os.listdir(defaultVehicleDir)
    #shutil.copytree(defaultVehicleDir, mapDir)
    distutils.dir_util.copy_tree(defaultVehicleDir.__str__(), mapDir.__str__())

    print("\nZippe FS22_Tiroler_Weissenbachtal. Bitte warten... ", end="")

    newMapFile = temp_dir / "out" / "FS22_Tiroler_Weissenbachtal.zip"
    shutil.make_archive(newMapFile.__str__().replace(".zip", ""), "zip", mapDir)

    print("Fertig!")

    print("\nLade FS22_Stepa_Crane herunter...")
    craneURL = "https://cloud.bayerngamers.de/index.php/s/Xj8RTyS9y3LwRXW/download/FS22_Stepa_Crane.zip"
    cranePath = download(craneURL, temp_dir / "FS22_Stepa_Crane.zip")

    userPath = os.path.expanduser('~')
    gameSettingsPath = os.path.join(userPath, "Documents", "My Games", "FarmingSimulator2022", "gameSettings.xml")

    file = open(gameSettingsPath, "rb")
    tree = et.parse(file)
    root = tree.getroot()

    modsDirOverride = root.find("modsDirectoryOverride")
    modsPath = Path(os.path.join(userPath, "Documents", "My Games", "FarmingSimulator2022", "mods"))

    if modsDirOverride is not None:
        customModsPathEnabled = modsDirOverride.get("active") == "true"
        if customModsPathEnabled == True:
            modsPath = Path(modsDirOverride.get("directory"))

    print(f"\nVerschiebe Dateien in Modordner: {modsPath}")

    shutil.move(cranePath, modsPath / "FS22_Stepa_Crane.zip")
    shutil.move(newMapFile, modsPath / "FS22_Tiroler_Weissenbachtal.zip")

    file.close()
    input("Drücke ENTER zum beenden...")
    shutil.rmtree(temp_dir)


if __name__ == '__main__':
    main()

