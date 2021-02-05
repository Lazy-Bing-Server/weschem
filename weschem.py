PLUGIN_ID = 'weschem'
PLUGIN_NAME_SHORT = '§lWES§rchem Fetcher'
PLUGIN_METADATA = {
	'id': PLUGIN_ID,
	'version': '1.0.0',
	'name': '§lW§rorldEdit §lS§rchematic §lF§retcher',
	'description': 'A backup and restore backup plugin, with multiple backup slots',
	'author': [
		'Ra1ny_Yuki'
	],
	'link': 'https://github.com/ra1ny-yuki/weschem',
	'dependencies': {
		'mcdreforged': '>=1.0.0',
	}
}

import json
import os
import re
import shutil
from mcdreforged.api.all import *

defaultConfig = '''
{
	"current_path": "server/config/worldedit/schematics",
    "servers": {
        "creative": "/home/creative/server/config/worldedit/schematics",
        "mirror": "/home/mirror/server/config/worldedit/schematics"
    }
}
'''
Prefix = '!!weschem'
Prefix_short = '!!wes'
helpMsg = f'''------ MCDR {PLUGIN_NAME_SHORT} v{PLUGIN_METADATA['version']} ------
各创造子服间WE原理图快速投送插件。
§d【指令帮助】§r
指令前缀§7{Prefix}§r可缩写为§7{Prefix_short}§r
§7{Prefix}§r 显示本插件帮助。
§7{Prefix} list§r §e<Sub-server>§r 显示指定子服的原理图列表
§7{Prefix} fetch§r §e<Sub-server> <Schematic>§r  获取另一子服的指定原理图
'''.strip()
configFile = 'config/WESchem.json'

def get_config(): 
    if not os.path.exists(configFile):  
        with open(configFile, 'w+', encoding='UTF-8') as f:
            f.write(defaultConfig)
    with open(configFile, 'r', encoding='UTF-8') as f:
        config = json.load(f, encoding='UTF-8')
    return config

def print_message(source: CommandSource, msg: str, tell = True, prefix = '[WESchem] '):
    msg = prefix + msg
    if source.is_player and not tell:
        source.get_server().say(msg)
    else:
        source.reply(msg)

def command_run(message: str, text: str, command: str):
	return RText(message).set_hover_text(text).set_click_event(RAction.run_command, command)

def command_suggest(message: str, text: str, command: str):
	return RText(message).set_hover_text(text).set_click_event(RAction.suggest_command, command)

def show_help(source: CommandSource):
	for line in helpMsg.splitlines():
		prefix = re.search(r'(?<=§7){}[\w ]*(?=§)'.format(Prefix), line)
		if prefix is not None:
			print_message(source, command_suggest(line, '点击补全命令', prefix.group()), True, '')
		else:
			print_message(source, line, True, '')

@new_thread(PLUGIN_METADATA['id'])
def fetch_schematic(source: CommandSource, sub_server: str, schematic: str):
	print_message(source, '正在获取原理图...')
	config = get_config()
	source_path_list = config['servers']
	try:
		source_path = os.path.join(source_path_list[sub_server], schematic)
		if not os.path.exists(source_path):
			call_list = command_run('§a点此§r', '点此查看原理图列表', f'{Prefix} list {sub_server}')
			print_message(source, '§c原理图不存在!§r ' + call_list + f'查看该子服的原理图列表')
			return
		destination = os.path.join(config['current_path'], schematic)
		excute_fetch(source, source_path, destination)
	except:
		call_help = command_run(f'§a点此§r', '点此查看有效子服列表', f'{Prefix} list')
		print_message(source, '§c没有找到子服! ' + call_help + '查看有效子服列表')

def anti_overwrite(source, dest_path: os.path):
	if os.path.exists(dest_path):
		dest_path_raw = os.path.splitext(dest_path)[0]
		dest_path_transfered = os.path.join(dest_path_raw + '1.schem')
		return anti_overwrite(source, dest_path_transfered)
	return dest_path

@new_thread(PLUGIN_METADATA['id'])
def excute_fetch(source: CommandSource, source_path: os.path, destination: os.path):
	dest_transfered = anti_overwrite(source, destination)
	if not dest_transfered == destination:
		print_message(source, f'同名原理图已存在，目标原理图另存为§b{os.path.split(dest_transfered)[1]}§r', True, '')
	try:
		shutil.copyfile(source_path, dest_transfered)
	except Exception as e:
		print_message(source, f'获取原理图§c失败§r，原因：§4{e}§r', tell = True, prefix = '')
	else:
		print_message(source, '获取原理图§a成功§r', tell = True, prefix = '')

@new_thread(PLUGIN_METADATA['id'])
def list_schematic(source: CommandSource, sub_server: str):
	target_path_list = get_config()['servers']
	try:
		target_path = os.path.join(target_path_list[sub_server])
		print_message(source, f'子服§l{sub_server}§r中的原理图如下：')
		number = 0
		for file in os.listdir(target_path):
			number = number + 1
			rfile = command_run(f'§b{file}§r', f'点击获取原理图§l{file}§r', f'{Prefix} fetch {sub_server} {file}')
			print_message(source, rfile, tell = True, prefix = f' [{number}] ')
	except:
		call_help = command_run(f'§a点此§r', '点此查看有效子服列表', f'{Prefix} list')
		print_message(source, '§c没有找到子服! ' + call_help + '查看有效子服列表')
	
@new_thread(PLUGIN_METADATA['id'])
def list_sub_server(source: CommandSource):
	server_list = get_config()['servers']
	print_message(source, '本插件可获取原理图的子服如下：')
	for servers in server_list.keys():
		prefix = command_run('§a[L]§r ', '点击显示该服务器的原理图列表', f'{Prefix} list {servers}')
		print_message(source, servers, True, prefix)
	
		
def register_command(server: ServerInterface):
	rprefix = command_run(f'§7{Prefix}§f', '点我获取帮助', Prefix)
	def print_error_msg(source):
		print_message(source, '§c指令错误! §r请输入§7' + rprefix + '§r以获取插件帮助')
	server.register_command(
		Literal({Prefix, Prefix_short}).
		runs(lambda src: show_help(src)).
		on_error(UnknownArgument, lambda src: print_error_msg(src), handled = True).
		then(
			Literal('fetch').then(QuotableText('sub_server').then(GreedyText('schematic').
				runs(lambda src, ctx: fetch_schematic(src, ctx['sub_server'], ctx['schematic']))
			))).
		then(
			Literal('list').
				runs(lambda src: list_sub_server(src)).
					then(GreedyText('sub_server').
						runs(lambda src, ctx: list_schematic(src, ctx['sub_server']))
			)
		)
	)

def on_load(server: ServerInterface, prev_module):
	get_config()
	register_command(server)
	server.register_help_message(Prefix, '从指定子服处获取WorldEdit原理图至本服')
