# 创世神原理图管理器

**创造模式增强插件工坊** 第二弹

 [英语(English)](https://github.com/ra1ny-yuki/weschem/tree/git_test) | **简体中文**

 一个用于获取同一机器上其他子服务器创世神原理图的MCDR插件。

 本分支是本插件的**早期预览版本**，可能会包含一些不稳定功能和烦人的虫。

 戳[这里](https://github.com/Lazy-Bing-Server/weschem)查看当前稳定版本。

## 依赖
- [MCDReforged](https://github.com/Fallen-Breath/MCDReforged/) >= 1.0.0
- [WorldEdit](https://www.curseforge.com/minecraft/mc-mods/worldedit)
- [Git](https://git-scm.com/)

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

**1.2.0-beta2** 抓虫

**1.2.0-beta1** 大量用户体验提升修改以及日常抓虫

**1.2.0-alpha8** 修复了某些POSIX操作系统上找不到git指令的问题，此外允许指定git路径了

**1.2.0-alpha7** 修改了git同步原理图功能，不再依赖gitpython，细化了git报错处理

**1.2.0-alpha6** 修改了清理仓库功能，理论上现在它应如设计时预想的一般工作

**1.2.0-alpha5** 修复了某些愚蠢的错误

**1.2.0-alpha4** 现在仓库提交日志中的服务端控制台名称可以修改了

**1.2.0-alpha3** 新增清理本地临时git仓库功能

**1.2.0-alpha2** 修复了一系列问题

**1.2.0-alpha1** 新增利用git向远程仓库同步原理图功能