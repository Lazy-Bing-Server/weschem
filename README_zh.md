# 创世神原理图获取

**创造模式插件增强合集计划第二弹**

 [英语(English)](https://github.com/ra1ny-yuki/weschem) | **简体中文**

 一个用于获取同一机器上其他子服务器创世神原理图的MCDR插件。

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
将另一子服中的原理图复制到当前子服中。
