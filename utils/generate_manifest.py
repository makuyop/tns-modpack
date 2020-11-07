#!/usr/bin/env python3

import json
import argparse


def generate_manifest(version: str):
    """Generate a manifest.json from a minecraftinstance.json.

    Generate the manifest.json file contained in a Twitch Minecraft modpack
    from the minecraftinstance.json file describing a Twitch game instance
    and from a user-supplied modpack version number.

    @param[in] version  modpack version number
    """

    # Open minecraftinstance.json and load its content into instance dict
    with open("minecraftinstance.json") as instance_file:
        instance = json.load(instance_file)

    # Create manifest dict from the data of instance dict
    manifest = {
        "name": instance["name"],
        "author": instance["customAuthor"],
        "version": version,
        "manifestType": "minecraftModpack",
        "manifestVersion": 1,
        "overrides": "overrides",
        "files": [
            {
                "projectID": addon["addonID"],
                "fileID": addon["installedFile"]["id"],
                "required": True
            }
            for addon in instance["installedAddons"]
        ],
        "minecraft": {
            "version": instance["gameVersion"],
            "modLoaders": [
                {
                    "id": instance["baseModLoader"]["name"],
                    "primary": True
                }
            ]
        }
    }

    # Dump the manifest dict content into manifest.json
    with open("manifest.json", "w") as manifest_file:
        json.dump(manifest, manifest_file, sort_keys=True, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=generate_manifest.__doc__.splitlines()[0])
    parser.add_argument("version", type=str, help="modpack version number")
    args = parser.parse_args()
    generate_manifest(args.version)
