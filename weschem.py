PLUGIN_ID = 'weschem'
PLUGIN_NAME_SHORT = '§lWES§rchem Manager'
PLUGIN_METADATA = {
	'id': PLUGIN_ID,
	'version': '1.1.1',
	'name': '§lW§rorld§lE§rdit §lS§rchematic §lM§ranager',
	'description': 'Manage WE schematic files in a group of servers',
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
	"current_subserver": "qmirror",
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
§7{Prefix} send§r §e<Sub-server> <Schematic>§r  将指定原理图投送至另一子服
'''.strip()
configFile = 'config/WESchem.json'
config = defaultConfig

def get_config():
	if not os.path.exists(configFile):  
		with open(configFile, 'w+', encoding='UTF-8') as f:
			f.write(defaultConfig)
	with open(configFile, 'r', encoding='UTF-8') as f:
		global config
		config = json.load(f, encoding='UTF-8')

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
	source_path_list = config['servers']
	try:
		source_path = os.path.join(source_path_list[sub_server], schematic)
		if not os.path.exists(source_path):
			call_list = command_run('§a点此§r', '点此查看原理图列表', f'{Prefix} list {sub_server}')
			print_message(source, '§c原理图不存在!§r ' + call_list + f'查看该子服的原理图列表')
			return
		destination = os.path.join(config['current_path'], schematic)
		excute_copy(source, source_path, destination)
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
def excute_copy(source: CommandSource, source_path: os.path, destination: os.path, fetch = True, target_server = 'current'):
	if fetch:
		part_1 = '获取'
	else:
		part_1 = '投送'
	dest_transfered = anti_overwrite(source, destination)
	if not dest_transfered == destination:
		print_message(source, f'同名原理图已存在，目标原理图另存为§b{os.path.split(dest_transfered)[1]}§r', True, '')
	try:
		shutil.copyfile(source_path, dest_transfered)
	except Exception as e:
		print_message(source, f'{part_1}原理图§c失败§r, 原因：§4{e}§r', tell = True, prefix = '')

	else:
		schematic_name = str(os.path.split(destination)[1])
		if fetch:
			part_3 = command_run(f'§a点此§r', f'点此加载{schematic_name}', f'//schem load {schematic_name}') + '加载此原理图'
		else:
			part_3 = command_run(f'§a点此§r', f'点此跳转到{target_server}', f'/server {target_server}') + '跳转到目标子服'
		print_message(source, f'{part_1}原理图§a成功§r, ' + part_3, tell = True, prefix = '')

@new_thread(PLUGIN_METADATA['id'])
def list_schematic(source: CommandSource, sub_server: str):
	if sub_server == config['current_subserver']:
		list_schematic_current(source, config)
	else: 
		target_path_list = config['servers']
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
def list_schematic_current(source: CommandSource, config, target_server = None):
	try:
		source_path = os.path.join(config['current_path'])
		if target_server == None:
			print_message(source, '当前服务器可投送的原理图如下: ')
		else:
			print_message(source, f'您将投送原理图至子服§6{target_server}§r')
			print_message(source, '当前服务器可投送到目标子服的原理图如下: ', True, '')
			
		number = 0
		if target_server == None:
			for file in os.listdir(source_path):
				number = number + 1
				rfile = command_run(f'§b{file}§r', f'点击将原理图§l{file}§r投送到其他子服', f'{Prefix} send to_be_determined {file}')
				print_message(source, rfile, True, f'[{number}]')
		else:
			for file in os.listdir(source_path):
				number = number + 1
				rfile = command_run(f'§b{file}§r', f'点击将原理图§l{file}§r投送到§l{target_server}§r', f'{Prefix} send {target_server} {file}')
				print_message(source, rfile, True, f'[{number}]')
	except Exception as e:
		print_message(source, f'§c出现错误:{e}§r如有疑问请联系服务器管理员。')
	

@new_thread(PLUGIN_METADATA['id'])
def list_sub_server_to_send(source: CommandSource, schematic: str):
	print_message(source, f'您选择了原理图§d{schematic}§r\n请选择投送目标子服:')
	server_list = config['servers']
	number = 0
	for servers in server_list.keys():
		number = number + 1
		server_name = command_run(f'§b{servers}§r', f'将原理图§l{schematic}§r投送到{servers}', f'{Prefix} send {servers} {schematic}')
		print_message(source, server_name, True, f'[{str(number)}]')

@new_thread(PLUGIN_METADATA['id'])
def send_schematic(source: CommandSource, sub_server: str, schematic):
	if sub_server == 'to_be_determined':
		list_sub_server_to_send(source, schematic)
	else:
		print_message(source, '正在投送原理图...')
		target_path_list = config['servers']
		source_path = os.path.join(config['current_path'], schematic)
		try:
			destination = os.path.join(target_path_list[sub_server], schematic)
			if not os.path.exists(source_path):
				call_list = command_run('§a点此§r', '点此查看原理图列表', f'{Prefix} list current')
				print_message(source, '§c原理图不存在!§r ' + call_list + f'查看当前子服原理图列表')
				return
			excute_copy(source, source_path, destination, False, sub_server)
		except:
			call_help = command_run(f'§a点此§r', '点此查看有效子服列表', f'{Prefix} list')
			print_message(source, '§c没有找到子服! ' + call_help + '查看有效子服列表')

	
@new_thread(PLUGIN_METADATA['id'])
def list_sub_server(source: CommandSource):
	server_list = config['servers']
	print_message(source, '本插件可访问的子服如下：')
	prefix_current = command_run('§a[L]§r ', '点击显示该服务器的原理图列表', f'{Prefix} list current')
	print_message(source, '当前子服('+ config['current_subserver'] + ')', True, prefix_current)
	for servers in server_list.keys():
		prefix = command_run('§a[F]§r ', '点击显示该服务器可获取的原理图列表', f'{Prefix} list {servers}') + command_run('§6[S]§r ', '点击显示可投送到该服务器的原理图列表', f'{Prefix} list current {servers}')
		print_message(source, servers, True, prefix)

def reload(source: CommandSource):
	try:
		get_config()
		print_message(source, '配置文件重载§a成功§r')
	except Exception as e:
		print_message(source, '配置文件重载§a失败§r, 原因:{}'.format(e))
		
def on_load(server: ServerInterface, prev_module):
	get_config()
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
		then(Literal('send').then(QuotableText('sub_server').then(GreedyText('schematic').
				runs(lambda src, ctx: send_schematic(src, ctx['sub_server'], ctx['schematic']))
			))).
		then(
			Literal('list').
				runs(lambda src: list_sub_server(src)).
					then(Literal('current').runs(lambda src: list_schematic_current(src, config)).
						then(QuotableText('target_server').runs(lambda src, ctx: list_schematic_current(src, config, ctx['target_server']))).
					then(GreedyText('sub_server').
						runs(lambda src, ctx: list_schematic(src, ctx['sub_server']))
			))).
		then(
			Literal('reload').runs(lambda src: reload(src))
		)
	)
	server.register_help_message(Prefix, '从指定子服处获取WorldEdit原理图至本服')
