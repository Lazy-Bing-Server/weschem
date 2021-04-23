# WorldEdit Schematic Manager

**Project Creative Enchancer Workshop** #2

  **English** | [简体中文(Simplified Chinese)](https://github.com/ra1ny-yuki/weschem/blob/git_test/README_zh.md)

  A MCDR plugin to fetch WorldEdit Schematics in the other sub-server on the same server.
  
  This branch is the **early preview version** for this plugin, may contain some unstable fuctions and annoying bugs.
  
## Preview Versions Changelog
  
**1.2.0-alpha3** Added clearing local git repo.

**1.2.0-alpha2** Fixed several issues.

**1.2.0-alpha1** Added syncing schematic to remote repo with git.

## Requirement
- [MCDReforged](https://github.com/Fallen-Breath/MCDReforged/) >= 1.0.0
- [WorldEdit](https://www.curseforge.com/minecraft/mc-mods/worldedit)
- [Gitpython](https://pypi.org/project/GitPython/) (You can simply install it with `pip install gitpython` in your system shell. )

## Configuration Tips
- Don't forget to confirgurate the config file `config/WESchem.json` in your MCDR working directory after generating config file when plugin is loaded for the first time.

- You can have your config file and command prefixes changed in the plugin file if needed.

## Command help
`!!wes` or `!!weschem` are the command prefixes, they can also be used to call the help message out.

In the rest of this guide, `<Prefix>` refer to the two command prefixes.

1. `<Prefix> list` 
List all the sub-servers that this plugin can access.

2. `<Prefix> list <sub-server>`
List all the schematics in the sub-server you input.

3. `<Prefix> fetch <sub-server> <schematic>`
  Copy the schematic you want in one another sub-server to the sub-server you are currently in.

   Or you can fetch schematic from local share reposity, which is named as `git` in game.

4. `<Prefix> send <sub-server> <schematic>`
  Copy the schematic you want in the sub-server you're currently in to one another sub-server.

   Or you can send schematic to local share reposity.

5. `<Prefix> reload`
  Reload the configuration file `config/WESchem.json`.

6. `<Prefix> push`
  Push your changes from local share reposity to the remote reposity.

7. `<Prefix> pull`
   Pull your changes from the remote reposity to the local share reposity.

8. `<prefix> clear`

   Clear your local share reposity. Folders and markdown files will be kept.

