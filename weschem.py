PLUGIN_ID = 'weschem'
PLUGIN_NAME_SHORT = '§lWES§rchem Manager'
PLUGIN_METADATA = {
	'id': PLUGIN_ID,
	'version': '1.2.0-beta3',
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
from json.decoder import JSONDecodeError
import os
import re
import shutil
from mcdreforged.api.all import *
import datetime
from subprocess import check_output, CalledProcessError
from threading import Lock

defaultConfig = {
	'cmd_prefix': '!!weschem',
	'cmd_prefix_short': '!!wes',
	'log_path': 'logs/WESchem.log',
	'current_subserver': 'mirror',
	'current_path': 'server/config/worldedit/schematics',
    'servers': {
        'creative': '/content/creative/server/config/worldedit/schematics',
		'git': '/content/git_library'
    },
	'console_name': '-Console',
	'enable_git': False,
	'timeout': 30,
	'remote_reposity': 'https://github.com/for_example/example.git',
	'git_command': 'git', 
	'permission':
	{
		'clear': 2,
		'fetch': 1,
		'send': 1,
		'list': 0,
		'push': 1,
		'pull': 1
	}
}

Prefix = '!!weschem'
Prefix_short = '!!wes'
configFile = 'config/WESchem.json'
clear_flag = False
enableGit = True
action_progressing = Lock()

class Config:
	def __init__(self, config_path: str) -> None:
		self.path = os.path.join(config_path)
		self.index = defaultConfig
		self.logger = None
	
	@new_thread(PLUGIN_ID)
	def load(self, server: ServerInterface):
		if self.logger is None:
			self.logger = server.logger
		self.index = defaultConfig
		if not os.path.isfile(self.path):
			with open(self.path, 'w+', encoding = 'UTF-8') as f:
				f.write('')
		self.index = defaultConfig
		with open(self.path, 'r', encoding = 'UTF-8') as f:
			try:
				data = json.load(f, encoding = 'UTF-8')
			except JSONDecodeError:
				data = {}
				self.logger.info('Regenerated invalid config file.')
		for key, value in data.items():
			self.index[key] = value
		if list(defaultConfig.keys() - data.keys()) != []:
			js = json.dumps(self.index).split(',')
			content = ''
			for item in js:
				if content != '':
					content += ',\n'
				content += item
			with open(self.path, 'w+', encoding = 'UTF-8') as file:
				file.write(content)
			server.say('[WESchem] 插件加载过程中重新生成了配置中无效的键值, 请通知服务器管理员检查配置文件')
			self.logger.info('Regenerated invalid keys with their default value: '+ str(list(defaultConfig.keys() - data.keys())).strip('[]'))
		self.logger = Logger(self.index['log_path'])
		global Prefix, Prefix_short, enableGit, repo, logger
		Prefix = self.index['cmd_prefix']
		Prefix_short = self.index['cmd_prefix_short']
		enableGit = self.index['enable_git']
		logger = self.logger
		try:
			repo = Repo(config['servers']['git'])
		except KeyError:
			enableGit = False
	
	def __getitem__(self, key):
		return self.index[key]		
config = Config(configFile)

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

class Repo:
	def __init__(self, local_path: str) -> None:
		self.local_path = os.path.join(local_path)
		self.arg_list = [config['git_command']]

	def add(self, file: str):
		args = self.arg_list.copy() + ['add', file]
		self.excute(args)

	def remove(self, file: str):
		args = self.arg_list.copy() + ['rm', file]
		self.excute(args)
		
	def commit(self, text: str):
		args = self.arg_list.copy() + ['commit', '-am', f"{text}"]
		self.excute(args)

	def push(self, additonal_arg = None, remote_branch = 'main', local_branch = 'main', remote_address = 'origin'):
		args = self.arg_list.copy() + ['push', remote_address, f'{local_branch}:{remote_branch}']
		if additonal_arg:
			args.append(additonal_arg)
		self.excute(args)
	
	def pull(self, additonal_arg = None, remote_branch = 'main', local_branch = 'main', remote_address = 'origin'):
		args = self.arg_list.copy() + ['pull', remote_address, f'{remote_branch}:{local_branch}']
		if additonal_arg:
			args.append(additonal_arg)
		self.excute(args)
	
	def excute(self, command: list):
		check_output(command, timeout = config['timeout'], cwd = self.local_path)

def print_message(source: CommandSource, msg: str, tell = True, prefix = '[WESchem] '):
    msg = prefix + msg
    if source.is_player and not tell:
        source.get_server().say(msg)
    else:
        source.reply(msg)

def command_run(message: str, text: str, command: str):
	return RText(message).set_hover_text(text).set_click_event(RAction.run_command, command)
rprefix = command_run(f'§7{Prefix}§f', '点我获取帮助', Prefix)

def command_suggest(message: str, text: str, command: str):
	return RText(message).set_hover_text(text).set_click_event(RAction.suggest_command, command)

def show_help(source: CommandSource, git = False):
	if not git:
		helpMsg = f'''---- MCDR {PLUGIN_NAME_SHORT} v§7{PLUGIN_METADATA['version']}§r ----
各创造子服间WE原理图快速投送插件，并可将原理图上传至远程仓库供下载
§d【指令帮助】§r
指令前缀§7{Prefix}§r可缩写为§7{Prefix_short}§r
§7{Prefix}§r 显示本插件帮助。
§7{Prefix} list§r §e<Sub-server>§r 显示指定子服的原理图列表
§7{Prefix} fetch§r §e<Sub-server> <Schematic>§r  获取另一子服的指定原理图
§7{Prefix} send§r §e<Sub-server> <Schematic>§r  将指定原理图投送至另一子服
§7{Prefix} push§r 向远程仓库提交改动
§7{Prefix} pull§r 自远程仓库拉取改动
§7{Prefix} clear§r 清理本地临时仓库
§d【上传&下载原理图】§r
将原理图复制到list中名为git的本地仓库后使用push指令可上传至远程仓库
将原理图提交到远程仓库后可pull后从git子服(仓库)中获取提交的原理图
push和pull无法自动合并时可在这两个指令后附加§5-h§r参数查阅帮助
关于远程仓库的访问方式请询问管理员
'''.strip()
	else:
		helpMsg = f'''§epush指令具有以下参数：§r
§7{Prefix} push -h§r 显示本指令帮助
§7{Prefix} push -f§r 强制推送, 覆盖远程仓库的改动
    §epull指令具有以下参数:§r
§7{Prefix} pull -h§r 显示本指令帮助
§7{Prefix} pull -r§r 重定基拉取, 合并再推送后可在远程仓库中查询历史改动
§7{Prefix} pull -f§r 强制拉取, 覆盖本地仓库的改动
§c强制拉取可能导致数据丢失!!!§r'''.strip()
	msg = ''
	for line in helpMsg.splitlines():
		if not msg == '':
			msg = msg + '\n'
		prefix = re.search(r'(?<=§7){}[\S ]*(?=§)'.format(Prefix), line)
		if prefix is not None:
			line_converted = command_suggest(line, '点击填入§7' + prefix.group() + '§r', prefix.group())
		else:
			line_converted = line
		msg = msg + line_converted
	msgPrefix = ''
	if git:
		msgPrefix = '[WESchem] '
	print_message(source, msg, True, msgPrefix)

def src_to_name(source: CommandSource): 
	if source.is_player:
		src_name = source.player
	else:
		src_name = config['console_name']
	return src_name

@new_thread(PLUGIN_ID)
def fetch_schematic(source: CommandSource, sub_server: str, schematic: str):
	action_progressing.acquire(blocking = True)
	print_message(source, '正在获取原理图...')
	source_path_list = config['servers']
	src_name = src_to_name(source)
	if not schematic.endswith('.schem') and not schematic.endswith('.schematic'):
		schematic += '.schem'
	try:
		source_path = os.path.join(source_path_list[sub_server], schematic)
		if not os.path.exists(source_path):
			call_list = command_run('§7点此§r', '点此查看原理图列表', f'{Prefix} list {sub_server}')
			print_message(source, '§c原理图不存在!§r ' + call_list + f'查看该子服的原理图列表')
			return
		destination = os.path.join(config['current_path'], schematic)
		excute_copy(source, source_path, destination, 'fetch')		
		logger.info(src_name + ' successfully fetched schematic ' + schematic + ' from ' + sub_server)
	except:
		call_help = command_run(f'§7点此§r', '点此查看有效子服列表', f'{Prefix} list')
		logger.warning(src_name + f' failed fetching schematic {schematic} from {sub_server}. Does the specified sub-server exist?')
		print_message(source, '§c没有找到子服! ' + call_help + '查看有效子服列表')
	action_progressing.release()

def anti_overwrite(source, dest_path: os.path):
	if os.path.exists(dest_path):
		dest_path_raw = os.path.splitext(dest_path)[0]
		dest_path_transfered = os.path.join(dest_path_raw + '1.schem')
		return anti_overwrite(source, dest_path_transfered)
	return dest_path

@new_thread(PLUGIN_ID)
def send_schematic(source: CommandSource, sub_server: str, schematic: str):
	global action_progressing
	src_name = src_to_name(source)
	if not schematic.endswith('.schem') and not schematic.endswith('.schematic'):
		schematic += '.schem'
	if sub_server == 'to_be_determined':
		list_sub_server_to_send(source, schematic)
	else:
		action_progressing.acquire(blocking = True)
		print_message(source, '正在投送原理图...')
		target_path_list = config['servers']
		source_path = os.path.join(config['current_path'], schematic)
		try:
			destination = os.path.join(target_path_list[sub_server], schematic)
			if not os.path.exists(source_path):
				call_list = command_run('§7点此§r', '点此查看原理图列表', f'{Prefix} list current')
				print_message(source, '§c原理图不存在!§r ' + call_list + f'查看当前子服原理图列表')
				return
			operation = 'send'
			if sub_server == ('git'):
				operation = 'push'	
			excute_copy(source, source_path, destination, operation, sub_server)
			logger.info(src_name + ' successfully sent schematic ' + schematic + ' to ' + sub_server)
		except:
			call_help = command_run(f'§7点此§r', '点此查看有效子服列表', f'{Prefix} list')
			print_message(source, '§c没有找到子服! ' + call_help + '查看有效子服列表')
			logger.warning(src_name + f' failed sending schematic {schematic} from {sub_server}. Does the specified sub-server exist?')
		action_progressing.release()

@new_thread(PLUGIN_ID)
def excute_copy(source: CommandSource, source_path: str, destination: str, operation: str, target_server = 'current'):
	operation_dict = {'fetch': '获取', 'send': '投送', 'push': '投送'}
	dest_transfered = anti_overwrite(source, destination)
	if not dest_transfered == destination:
		print_message(source, f'同名原理图已存在，目标原理图另存为§b{os.path.split(dest_transfered)[1]}§r', True, '')
		logger.info('Schematic with the same name exists already! The newer one is rename as {}'.format(os.path.split(dest_transfered)[1]))
	try:
		logger.info(source_path + ' ' + dest_transfered)
		shutil.copyfile(source_path, dest_transfered)
	except Exception as e:
		print_message(source, f'{operation_dict[operation]}原理图§c失败§r, 原因：§4{e}§r', tell = True, prefix = '')
	else:
		schematic_name = str(os.path.split(dest_transfered)[1])
		result_list = {'fetch': command_run(f', §7点此§r', f'点此加载{schematic_name}', f'//schem load {schematic_name}') + '加载此原理图', 
						'send': command_run(f', §7点此§r', f'点此跳转到{target_server}', f'/server {target_server}') + '跳转到目标子服', 'push': ''}
		print_message(source, f'{operation_dict[operation]}原理图§a成功§r' + result_list[operation], tell = True, prefix = '')
		if operation == 'push' and enableGit:
			git_add_commit(source, schematic_name)		

@new_thread(PLUGIN_ID)
def git_add_commit(source: CommandSource, schematic: str):
	src_name = src_to_name(source)
	try:
		repo.add(schematic)
		repo.commit(f"{src_name} committed {schematic} from {config['current_subserver']}.")
		result = '§a成功§r, ' + command_run(f'§7点此§r', f'向在线仓库推送改动', '!!wes push') + '向远程仓库推送改动'
		logger.info('{} commited §b{}§r to local reposities successfully.'.format(src_name, schematic))
	except Exception as e:
		result = '§c失败§r, 原因: ' + str(e)
		logger.info('{} failed commiting §b{}§r to local reposities, reason: {}'.format(src_name, schematic, e))
	print_message(source, '向本地仓库提交原理图§b'+ schematic + result)

@new_thread(PLUGIN_ID)
def git_push(source: CommandSource, add_args = None):
	if not enableGit:
		print_message(source, 'git推送功能未启用, 请联系管理员启用')
		return
	action_progressing.acquire(blocking = True)
	src_name = src_to_name(source)
	try:
		if add_args == None:
			repo.push()
		elif add_args == '-f':
			repo.push('--force')
		elif add_args == '-h':
			show_help(source, True)
			action_progressing.release()
			return
		else:
			raise RuntimeError
		result = '§a成功§r, ' + RText('点此').set_click_event(RAction.open_url, config['remote_reposity']).set_color(RColor.gray) + '查看远程仓库'
		logger.info('{} pushed changes to remote reposities successfully.'.format(src_name))
	except TimeoutError:
		result = '§c失败§r, 操作执行§c超时§r, 请告知管理员检查网络'
		logger.info(f'{src_name} failed pushing changes to remote reposities, time out.')
	except CalledProcessError:
		result = '§c失败§r, git无法执行这种合并, ' + command_run('点此', '拉取未合并的改动', '!!wes pull').set_color(RColor.gray) + '拉取这些改动后方可再行推送, 若无效' + command_run('点此', '获取参数帮助', '!!wes push -h').set_color(RColor.gray) + '查看额外参数以执行其他形式合并'
		logger.info(f'{src_name} failed pushing changes to remote reposities, the remote contains work that you do not have locally or invaild connection to your remote repo.')
	except RuntimeError:
		result = f'§c失败§r, 参数§4{add_args}§r无效, §7' + command_run('点此', '获取参数帮助', '!!wes push -h') + '§r以获取本指令参数帮助'
	except Exception as e:
		result = '§c失败§r, 发生意外错误, 原因: §c' + str(e)
		logger.info('{} failed pushing changes to remote reposities, reason: {}'.format(src_name, e))
	print_message(source, '向公用仓库推送改动' + result)
	action_progressing.release()
	

@new_thread(PLUGIN_ID)
def git_pull(source: CommandSource, add_args = None):
	if not enableGit:
		print_message(source, 'git拉取功能未启用, 请联系管理员启用')
		return
	action_progressing.acquire(blocking = True)
	src_name = src_to_name(source)
	try:
		if add_args == None:
			repo.pull()
		elif add_args == '-f':
			repo.pull('--force')
		elif add_args == '-r':
			repo.pull('--rebase')
		elif add_args == '-h':
			show_help(source, True)
			action_progressing.release()
			return
		else:
			raise RuntimeError
		result = '§a成功§r, ' + command_run('点此', '查看本地仓库', '!!wes list git').set_color(RColor.gray) + '查看本地仓库'
		logger.info('{} pulled changes from remote reposities successfully.'.format(src_name))
	except TimeoutError:
		result = '§c失败§r, 操作执行§c超时§r, 请告知管理员检查网络'
		logger.info(f'{src_name} failed pushing changes to remote reposities, time out.')
	except CalledProcessError:
		result = '§c失败§r, git无法执行这种合并, ' + command_run('点此', '获取参数帮助', '!!wes pull -h').set_color(RColor.gray) + '查看额外参数以执行其他形式合并'
		logger.info(f'{src_name} failed pushing changes to remote reposities, invaild connection to your remote repo.')
	except RuntimeError:
		result = f'§c失败§r, 参数§4{add_args}§r无效, §7' + command_run('点此', '获取参数帮助', '!!wes pull -h') + '§r以获取本指令参数帮助'
	except Exception as e:
		result = '§c失败§r, 发生意外错误, 原因: §c' + str(e)
		logger.info('{} failed pulling changes from remote reposities, reason: {}'.format(src_name, e))
	print_message(source, '自公用仓库拉取改动' + result)
	action_progressing.release()

@new_thread(PLUGIN_ID)
def list_schematic(source: CommandSource, sub_server: str, fetch = False):
	if sub_server == config['current_subserver']:
		list_schematic_current(source)
	else: 
		target_path_list = config['servers']
		try:
			target_path = os.path.join(target_path_list[sub_server])
			number = 0
			if fetch:
				content = f'您未选定要从子服§l{sub_server}§r获取的原理图, 请选择: '
			else:
				content = f'子服§l{sub_server}§r中的原理图如下: '
			for file in os.listdir(target_path):
				if file.endswith('.schem') or file.endswith('.schematic'):
					number = number + 1
					rfile = f'\n[{number}] ' + command_run(f'§b{file}§r', f'点击获取原理图§l{file}§r', f'{Prefix} fetch {sub_server} {file}')
					content += rfile
			print_message(source, content)
		except:
			call_help = command_run(f'§7点此§r', '点此查看有效子服列表', f'{Prefix} list')
			print_message(source, '§c没有找到子服! ' + call_help + '查看有效子服列表')

@new_thread(PLUGIN_ID)
def list_schematic_current(source: CommandSource, target_server = None):
	try:
		source_path = os.path.join(config['current_path'])
		if target_server == None:
			content = '当前服务器可投送的原理图如下: '
		else:
			content = f'您将投送原理图至子服§6{target_server}§r\n当前服务器可投送到目标子服的原理图如下: '			
		number = 0
		for file in os.listdir(source_path):
			if file.endswith('.schem') or file.endswith('.schematic'):
				number = number + 1
				if target_server == None:
					rfile = f'\n[{number}] ' + command_run(f'§b{file}§r', f'点击将原理图§l{file}§r投送到其他子服', f'{Prefix} send to_be_determined {file}')
				else:
					rfile = f'\n[{number}] ' + command_run(f'§b{file}§r', f'点击将原理图§l{file}§r投送到§l{target_server}§r', f'{Prefix} send {target_server} {file}')
				content += rfile
		print_message(source, content)
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

@new_thread(PLUGIN_ID)
def reload(source: CommandSource):
	action_progressing.acquire(blocking = True)
	try:
		print_message(source, '重载插件§a完成§r')
		source.get_server().reload_plugin(PLUGIN_ID)
	except Exception as e:
		print_message(source, '重载§a失败§r, 原因:{}'.format(e))
	action_progressing.release()

@new_thread(PLUGIN_ID)
def request_clear(source: CommandSource):
	if not enableGit:
		print_message(source, 'Git仓库管理功能未启用，请联系管理员启用')
	global clear_flag
	clear_flag = True
	print_message(source, '已要求清空本地仓库, ' + 
	'输入' + command_run('!!wes confirm', '点此确认清理', '!!wes confirm').set_color(RColor.gray) + '以§a确认§r清空, ' + 
	'输入' + command_run('!!wes abort', '点此取消清理', '!!wes abort').set_color(RColor.gray) + '以§c取消§r清空')

@new_thread(PLUGIN_ID)
def clear_local_repo(source: CommandSource, abort = False):
	global clear_flag
	if abort and clear_flag and enableGit:
		print_message(source, '已§c取消§r清理')
	elif clear_flag and not abort and enableGit:
		action_progressing.acquire(blocking = True)
		clear_flag = False
		for file in os.listdir(config['servers']['git']):
			file_path = os.path.join(config['servers']['git'], file)
			if os.path.isfile(file_path) and not file.endswith('.md'):
				try:
					repo.remove(file_path)
				except:
					os.remove(file_path)
		src_name = src_to_name(source)
		repo.commit(f'{src_name} cleared local reposity.')
		print_message(source, '已§a完成§r清理')
		action_progressing.release()
	else:
		print_message(source, '没要求清理啊rue')
		
def on_load(server: ServerInterface, prev_module):
	config.load(server)
	def print_error_msg(source: CommandSource, error_type = 'cmd'):
		error_msg = {'arg': '未知参数!', 'cmd': '指令错误!'}
		print_message(source, f'§c{error_msg[error_type]} §r请输入§7' + rprefix + '§r以获取插件帮助')

	def permed_literal(literal: str):
		lvl = config['permission'].get(literal, 0)
		return Literal(literal).requires(lambda src: src.has_permission(lvl), failure_message_getter = lambda: f'§f[WESchem] §c权限不足, 你想桃子呢, 需要权限等级{lvl}§r')
	server.register_command(
		Literal({Prefix, Prefix_short}).on_error(UnknownArgument, lambda src: print_error_msg(src, 'arg'), handled = True).
		runs(lambda src: show_help(src)).
		then(
			permed_literal('fetch').on_error(UnknownCommand, lambda src: print_error_msg(src), handled = True).
			then(QuotableText('sub_server').runs(lambda src, ctx: list_schematic(src, ctx['sub_server'], True)).
			then(GreedyText('schematic').runs(lambda src, ctx: fetch_schematic(src, ctx['sub_server'], ctx['schematic']))
			))).
		then(permed_literal('send').on_error(UnknownCommand, lambda src: print_error_msg(src), handled = True).
			then(QuotableText('sub_server').runs(lambda src, ctx: list_schematic_current(src, ctx['sub_server'])).
			then(GreedyText('schematic').
				runs(lambda src, ctx: send_schematic(src, ctx['sub_server'], ctx['schematic']))
			))).
		then(
			permed_literal('list').
				runs(lambda src: list_sub_server(src)).
					then(Literal('current').runs(lambda src: list_schematic_current(src)).
						then(QuotableText('target_server').runs(lambda src, ctx: list_schematic_current(src, config, ctx['target_server'])))).
					then(GreedyText('sub_server').
						runs(lambda src, ctx: list_schematic(src, ctx['sub_server']))
			)).
		then(
			permed_literal('push').runs(lambda src: git_push(src)).
				then(QuotableText('arg').on_error(UnknownArgument, lambda src: print_error_msg(src, 'arg'), handled = True).runs(lambda src, ctx: git_push(src, ctx['arg'])))
		).
		then(
			permed_literal('pull').runs(lambda src: git_pull(src)).
				then(QuotableText('arg').on_error(UnknownArgument, lambda src: print_error_msg(src, 'arg'), handled = True).runs(lambda src, ctx: git_pull(src, ctx['arg'])))
		).
		then(
			permed_literal('clear').on_error(UnknownArgument, lambda src: print_error_msg(src, 'arg'), handled = True).runs(lambda src: request_clear(src))
		).
		then(
			permed_literal('confirm').on_error(UnknownArgument, lambda src: print_error_msg(src, 'arg'), handled = True).runs(lambda src: clear_local_repo(src))
		).
		then(
			permed_literal('abort').on_error(UnknownArgument, lambda src: print_error_msg(src, 'arg'), handled = True).runs(lambda src: clear_local_repo(src, True))
		).
		then(
			permed_literal('reload').on_error(UnknownArgument, lambda src: print_error_msg(src, 'arg'), handled = True).runs(lambda src: reload(src))
		)
	)
	server.register_help_message(Prefix, '从指定子服处获取WorldEdit原理图至本服')
