#!/usr/bin/env python3

import os
import sys
import json
import requests
import concurrent.futures


def wget(url, target):
    """Download the file at `url` and write it into `target`.

    @param[in] url      file url to download
    @param[in] target   write file into target
    """
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(target, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)


def download_mod(mod, into):
    """Download a mod into a directory.

    @param[in] mod      dict of the mod extracted from the minecraftinstance.json
    @param[in] into     target download directory
    """
    modfile = mod["installedFile"]
    modfilename = modfile["FileNameOnDisk"]
    filename = os.path.join(into, modfilename)
    fileurl = modfile["downloadUrl"]
    if os.path.exists(filename):
        return
    if os.path.exists(filename + ".disabled"):
        os.rename(filename + ".disabled", filename)
        return
    print(f"Mod {modfilename} not found, downloading it")
    wget(url=fileurl, target=filename)


def download_mods(mods, into):
    """Download all mods from minecraftinstance.json concurrently.

    @param[in] mods     addons dict extracted from the minecraftinstance.json
    @param[in] into     target download directory
    """
    print("Download any missing mod")
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        for mod in mods:
            executor.submit(download_mod, mod, into)


def delete_removed_mods(mods, dir):
    """Delete files in `dir` mod folder not present in minecraftinstance.json.

    @param[in] mods     addons dict extracted from the minecraftinstance.json
    @param[in] dir      mods directory
    """
    print("Delete any removed mods")
    modfiles = [mod["installedFile"]["FileNameOnDisk"] for mod in mods]
    files = [file for file in os.listdir(dir)
             if file not in modfiles and not os.path.isdir(file)]
    for file in files:
        print(f"Found removed mod {os.path.join(dir, file)}, deleting it")
        os.remove(os.path.join(dir, file))


def sync_instance():
    """Synchronize the Twitch instance.

    Reads the mod list in minecraftinstance.json, then downloads any mods
    not present locally, and remove local mods not in the list.
    """
    cwd = os.getcwd()
    print(f"Running in {cwd}")

    modsdir = os.path.join(cwd, "mods")
    instancefile = os.path.join(cwd, "minecraftinstance.json")

    if not os.path.exists(modsdir):
        print(f"{modsdir} does not exist, creating it")
        os.mkdir(modsdir)

    if not os.path.isdir(modsdir):
        raise IOError(f"{modsdir} exists but is not a directory")

    with open(instancefile, "r") as f:
        print(f"Found {instancefile} file")
        instance = json.load(f)
        mods = instance['installedAddons']
        print(f"Instance loaded, has {len(mods)} mods")

    download_mods(mods, into=modsdir)

    delete_removed_mods(mods, dir=modsdir)


if __name__ == "__main__":
    try:
        sync_instance()
    except Exception as err:
        print(f"Error: {err}, aborting", file=sys.stderr)
        sys.exit(1)
