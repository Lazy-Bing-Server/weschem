# 创世神原理图管理器

**创造模式增强插件工坊** 第二弹

 [英语(English)](https://github.com/ra1ny-yuki/weschem/tree/git_test) | **简体中文**

 一个用于获取同一机器上其他子服务器创世神原理图的MCDR插件。
 
 本分支是本插件的**早期预览版本**，可能会包含一些不稳定功能和烦人的虫。
 
## 依赖
- [MCDReforged](https://github.com/Fallen-Breath/MCDReforged/) >= 1.0.0
- [WorldEdit](https://www.curseforge.com/minecraft/mc-mods/worldedit)
- [Gitpython](https://pypi.org/project/GitPython/) (在系统命令行中输入`pip install gitpython`以快速安装)

## 配置小贴士
- 初次加载插件生成配置后别忘了改，配置文件在MCDR工作目录下的`config/WESchem.json`

- 如需要可在插件本体中修改插件指令前缀和插件默认配置文件位置。

## 指令帮助
插件的指令前缀是`!!wes` 和 `!!weschem`，直接输入以在客户端内直接获取帮助信息

以下将使用`<Prefix>`替代上述两个指令前缀。

1. `<Prefix> list` 
列出插件可以访问原理图的所有子服列表。

2. `<Prefix> list <sub-server>`
列出玩家要求的子服务器中的所有原理图。

3. `<Prefix> fetch <sub-server> <schematic>`
将另一子服中的原理图复制到当前子服中，或者你可以将本地共享仓库里的原理图拿过来。

4. `<Prefix> send <sub-server> <schematic>`
将当前子服中的原理图复制到另一子服中，或者你可以把这个子服里的原理图扔到本地共享仓库里。

5. `<Prefix> reload`
  重载本插件配置文件`config/WESchem.json`。

6. `<Prefix> push`
  自本地共享仓库向远程仓库推送更改。

7. `<Prefix> pull`
   自远程仓库向本地共享仓库拉取更改。

8. `<prefix> clear`

   清理你的本地共享仓库，这会保留Markdown文件和文件夹。
   
## 预览版更新日志
**1.2.0-alpha3** 新增清理本地临时git仓库功能

**1.2.0-alpha2** 修复了一系列问题

**1.2.0-alpha1** 新增利用git向远程仓库同步原理图功能
