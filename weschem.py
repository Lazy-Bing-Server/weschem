PLUGIN_ID = 'weschem'
PLUGIN_NAME_SHORT = '§lWES§rchem Manager'
PLUGIN_METADATA = {
	'id': PLUGIN_ID,
	'version': '1.2.0-alpha6',
	'name': '§lW§rorld§lE§rdit §lS§rchematic §lM§ranager',
	'description': 'Manage WE schematic files in a group of servers',
	'author': [
		'Ra1ny_Yuki'
	],
	'link': 'https://github.com/Lazy-Bing-Server/weschem',
	'dependencies': {
		'mcdreforged': '>=1.0.0',
	}
}

import json
import os
import re
import shutil
from mcdreforged.api.all import *
import datetime
import git

defaultConfig = '''
{
	"current_subserver": "qmirror",
	"current_path": "server/config/worldedit/schematics",
    "servers": {
        "creative": "/home/creative/server/config/worldedit/schematics",
        "mirror": "/home/mirror/server/config/worldedit/schematics",
		"git": "/home/LBS-Schematics-Library"
    },
	"console_name": "-Console",
	"remote_reposity": "https://github.com/Lazy-Bing-Server/LBS-Schematics-Library.git",
	"permission":
	{
		"clear": 2,
		"fetch": 1,
		"send": 1,
		"list": 0,
		"push": 1,
		"pull": 1
	}
}
'''
Prefix = '!!weschem'
Prefix_short = '!!wes'
helpMsg = f'''---- MCDR {PLUGIN_NAME_SHORT} v§7{PLUGIN_METADATA['version']}§r ----
各创造子服间WE原理图快速投送插件，并可将原理图上传至Github供下载
§d【指令帮助】§r
指令前缀§7{Prefix}§r可缩写为§7{Prefix_short}§r
§7{Prefix}§r 显示本插件帮助。
§7{Prefix} list§r §e<Sub-server>§r 显示指定子服的原理图列表
§7{Prefix} fetch§r §e<Sub-server> <Schematic>§r  获取另一子服的指定原理图
§7{Prefix} send§r §e<Sub-server> <Schematic>§r  将指定原理图投送至另一子服
§7{Prefix} push§r 向Github公用仓库提交改动
§7{Prefix} pull§r 自Github公用仓库拉取改动
§7{Prefix} clear§r 清理本地临时仓库
§d【上传&下载原理图】§r
将原理图复制到list中名为git的本地仓库后使用push指令可上传至Github仓库
将原理图提交到Github仓库后可从git子服(仓库)中获取提交的原理图
关于Github仓库的访问方式请询问管理员
'''.strip()
configFile = 'config/WESchem.json'
logFile = 'logs/WESchem.log'
config = defaultConfig
clear_flag = False

class Logger:
    def __init__(self, log_path: str):
        self.path = os.path.join(log_path)
        if not os.path.isfile(self.path):
            with open(self.path, 'w+', encoding = 'utf-8') as f:
                f.write('')
    
    def info(self, msg: str):
        msg = msg.replace('§r', '').replace('§d', '').replace('§c', '').replace('§6', '').replace('§e', '').replace('§a', '')
        self.save(msg)
        self.show(msg)

    def warning(self, msg: str):
        msg = msg.replace('§r', '').replace('§d', '').replace('§c', '').replace('§6', '').replace('§e', '').replace('§a', '')
        self.save(msg, True)
        self.show(msg, True)
    
    def save(self, msg = '', warn = False):
        warn_section = ''
        if warn:
            warn_section = 'WARNING!!!'
        with open(self.path, 'a+') as log:
            log.write(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]") + warn_section + msg + '\n')

    def show(self, msg: str, warn = False):
        warn_section = '32mINFO'
        if warn:
            warn_section = '33mWARNING'
        print("[MCDR] " + datetime.datetime.now().strftime("[%H:%M:%S]") + ' [{}/\033[1;{}\033[0m] '.format(PLUGIN_ID, warn_section) + msg)

logger = Logger(logFile)

def get_config():
	if not os.path.exists(configFile):
		logger.info('Configuration file doesn\'t exists! Regenerated.')
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
	msg = ''
	for line in helpMsg.splitlines():
		if not msg == '':
			msg = msg + '\n'
		prefix = re.search(r'(?<=§7){}[\w ]*(?=§)'.format(Prefix), line)
		if prefix is not None:
			line_converted = command_suggest(line, '点击补全命令', prefix.group())
		else:
			line_converted = line
		msg = msg + line_converted
	print_message(source, msg, True, '')
		

def src_to_name(source: CommandSource): 
	if source.is_player:
		src_name = source.player
	else:
		src_name = config['console_name']
	return src_name

@new_thread(PLUGIN_ID)
def fetch_schematic(source: CommandSource, sub_server: str, schematic: str):
	print_message(source, '正在获取原理图...')
	source_path_list = config['servers']
	src_name = src_to_name(source)
	try:
		source_path = os.path.join(source_path_list[sub_server], schematic)
		if not os.path.exists(source_path):
			call_list = command_run('§a点此§r', '点此查看原理图列表', f'{Prefix} list {sub_server}')
			print_message(source, '§c原理图不存在!§r ' + call_list + f'查看该子服的原理图列表')
			return
		destination = os.path.join(config['current_path'], schematic)
		excute_copy(source, source_path, 'fetch', destination)		
		logger.info(src_name + ' successfully fetched schematic ' + schematic + ' from ' + sub_server)
	except:
		call_help = command_run(f'§a点此§r', '点此查看有效子服列表', f'{Prefix} list')
		logger.warning(src_name + f' failed fetching schematic {schematic} from {sub_server}. Does the specified sub-server exist?')
		print_message(source, '§c没有找到子服! ' + call_help + '查看有效子服列表')

def anti_overwrite(source, dest_path: os.path):
	if os.path.exists(dest_path):
		dest_path_raw = os.path.splitext(dest_path)[0]
		dest_path_transfered = os.path.join(dest_path_raw + '1.schem')
		return anti_overwrite(source, dest_path_transfered)
	return dest_path

@new_thread(PLUGIN_ID)
def send_schematic(source: CommandSource, sub_server: str, schematic):
	src_name = src_to_name(source)
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
			operation = 'send'
			if sub_server == ('git'):
				operation = 'push'	
			excute_copy(source, source_path, destination, operation, sub_server)
			logger.info(src_name + ' successfully sent schematic ' + schematic + ' to ' + sub_server)
		except:
			call_help = command_run(f'§a点此§r', '点此查看有效子服列表', f'{Prefix} list')
			print_message(source, '§c没有找到子服! ' + call_help + '查看有效子服列表')
			logger.warning(src_name + f' failed sending schematic {schematic} from {sub_server}. Does the specified sub-server exist?')

@new_thread(PLUGIN_ID)
def excute_copy(source: CommandSource, source_path: os.path, destination: os.path, opration: str, target_server = 'current'):
	if opration == 'fetch':
		part_1 = '获取'
	else:
		part_1 = '投送'
	dest_transfered = anti_overwrite(source, destination)
	if not dest_transfered == destination:
		print_message(source, f'同名原理图已存在，目标原理图另存为§b{os.path.split(dest_transfered)[1]}§r', True, '')
		logger.info('Schematic with the same name exists already! The newer one is rename as {}'.format(os.path.split(dest_transfered)[1]))
	try:
		shutil.copyfile(source_path, dest_transfered)
	except Exception as e:
		print_message(source, f'{part_1}原理图§c失败§r, 原因：§4{e}§r', tell = True, prefix = '')

	else:
		schematic_name = str(os.path.split(dest_transfered)[1])
		part_3 = ''
		if opration == 'fetch':
			part_3 = command_run(f', §a点此§r', f'点此加载{schematic_name}', f'//schem load {schematic_name}') + '加载此原理图'
		elif opration == 'send':
			part_3 = command_run(f', §a点此§r', f'点此跳转到{target_server}', f'/server {target_server}') + '跳转到目标子服'
		print_message(source, f'{part_1}原理图§a成功§r' + part_3, tell = True, prefix = '')
		if opration == 'push':
			git_add_commit(source, schematic_name)
			
		

@new_thread(PLUGIN_ID)
def git_add_commit(source: CommandSource, schematic: str):
	src_name = src_to_name(source)
	try:
		repo.index.add(schematic)
		repo.index.commit(f'{src_name} committed {schematic}.')
		result = '§a成功§r, ' + command_run(f'§a点此§r', f'向在线仓库推送改动', '!!wes push') + '向Github仓库推送改动'
		logger.info('{} commited §b{}§r to local reposities successfully.'.format(src_name, schematic))
	except Exception as e:
		result = '§c失败§r, 原因: ' + str(e)
		logger.info('{} failed commiting §b{}§r to local reposities, reason: {}'.format(src_name, schematic, e))
	print_message(source, '向本地仓库提交原理图§b'+ schematic + result)

@new_thread(PLUGIN_ID)
def git_push(source: CommandSource):
	src_name = src_to_name(source)
	try:
		repo.remote().push()
		result = '§a成功§r, ' + RText('点此').set_click_event(RAction.open_url, config['remote_reposity']).set_color(RColor.green) + '查看'
		logger.info('{} pushed changes to online reposities successfully.'.format(src_name))
	except Exception as e:
		result = '§c失败§r, 原因: ' + str(e)
		logger.info('{} failed pushing changes to online reposities, reason: {}'.format(src_name, e))
	print_message(source, '向公用仓库推送改动' + result)
	

@new_thread(PLUGIN_ID)
def git_pull(source: CommandSource):
	src_name = src_to_name(source)
	try:
		repo.remote().pull()
		result = '§a成功§r'
		logger.info('{} pulled changes from online reposities successfully.'.format(src_name))
	except Exception as e:
		result = '§c失败§r, 原因: ' + e
		logger.info('{} failed pulling changes from online reposities, reason: {}'.format(src_name, e))
	print_message(source, '自公用仓库拉取改动' + result)

@new_thread(PLUGIN_ID)
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

@new_thread(PLUGIN_ID)
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
	

@new_thread(PLUGIN_ID)
def list_sub_server_to_send(source: CommandSource, schematic: str):
	print_message(source, f'您选择了原理图§d{schematic}§r\n请选择投送目标子服:')
	server_list = config['servers']
	number = 0
	for servers in server_list.keys():
		number = number + 1
		server_name = command_run(f'§b{servers}§r', f'将原理图§l{schematic}§r投送到{servers}', f'{Prefix} send {servers} {schematic}')
		print_message(source, server_name, True, f'[{str(number)}]')
	
@new_thread(PLUGIN_ID)
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

@new_thread(PLUGIN_ID)
def request_clear(source: CommandSource):
	global clear_flag
	clear_flag = True
	print_message(source, '已要求清空本地仓库, ' + 
	'输入' + command_run('!!wes confirm', '点此确认清理', '!!wes confirm').set_color(RColor.gray) + '以§a确认§r清空' + 
	'输入' + command_run('!!wes abort', '点此取消清理', '!!wes abort') + '以§c取消§r清空')
	

@new_thread(PLUGIN_ID)
def clear_local_repo(source: CommandSource, abort = False):
	if abort and clear_flag:
		print_message(source, '已§c取消§r清理')
	elif clear_flag and not abort:
		global clear_flag
		clear_flag = False
		for file in os.listdir(config['servers']['git']):
			file_path = os.path.join(config['servers']['git'], file)
			if os.path.isfile(file_path) and not file.endswith('.md'):
				repo.index.remove(file_path)
		src_name = src_to_name(source)
		repo.index.commit(f'{src_name} cleared local reposity.')
		print_message(source, '已§A完成§r清理')
	else:
		print_message(source, '没要求清理啊rue')


		
def on_load(server: ServerInterface, prev_module):
	get_config()
	global repo
	repo = git.Repo(config['servers']['git'])
	rprefix = command_run(f'§7{Prefix}§f', '点我获取帮助', Prefix)

	def print_error_msg(source: CommandSource):
		print_message(source, '§c指令错误! §r请输入§7' + rprefix + '§r以获取插件帮助')

	def permed_literal(literal: str):
		lvl = config['permission'].get(literal, 0)
		return Literal(literal).requires(lambda src: src.has_permission(lvl), failure_message_getter = lambda: f'§f[WESchem] §c权限不足, 你想桃子呢, 需要{lvl}§r')

	server.register_command(
		Literal({Prefix, Prefix_short}).
		runs(lambda src: show_help(src)).
		on_error(UnknownArgument, lambda src: print_error_msg(src), handled = True).
		then(
			permed_literal('fetch').then(QuotableText('sub_server').then(GreedyText('schematic').
				runs(lambda src, ctx: fetch_schematic(src, ctx['sub_server'], ctx['schematic']))
			))).
		then(permed_literal('send').then(QuotableText('sub_server').then(GreedyText('schematic').
				runs(lambda src, ctx: send_schematic(src, ctx['sub_server'], ctx['schematic']))
			))).
		then(
			permed_literal('list').
				runs(lambda src: list_sub_server(src)).
					then(Literal('current').runs(lambda src: list_schematic_current(src, config)).
						then(QuotableText('target_server').runs(lambda src, ctx: list_schematic_current(src, config, ctx['target_server']))).
					then(GreedyText('sub_server').
						runs(lambda src, ctx: list_schematic(src, ctx['sub_server']))
			))).
		then(
			permed_literal('push').runs(lambda src: git_push(src))
		).
		then(
			permed_literal('pull').runs(lambda src: git_pull(src))
		).
		then(
			permed_literal('clear').runs(lambda src: request_clear(src))
		).
		then(
			permed_literal('confirm').runs(lambda src: clear_local_repo(src))
		).
		then(
			permed_literal('abort').runs(lambda src: clear_local_repo(src, True))
		).
		then(
			permed_literal('reload').runs(lambda src: reload(src))
		)
	)
	server.register_help_message(Prefix, '从指定子服处获取WorldEdit原理图至本服')
