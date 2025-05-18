"""
    Speedbuilder Hotbar Remapper

    Copyright (C) 2025 dontcareism a.k.a ClearColdWater (1697088220@qq.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import time
import re
import json

def follow(filename):
    file = None
    last_inode = None
    last_position = 0
    buffer = ''

    while True:
        try:
            stat = os.stat(filename)
        except FileNotFoundError:
            print(f"日志文件 '{filename}' 未找到，等待重试...")
            time.sleep(10)
            continue

        current_inode = stat.st_ino
        current_size = stat.st_size

        if current_inode != last_inode:
            if file:
                file.close()
            try:
                file = open(filename, 'rb')
            except IOError:
                time.sleep(1)
                continue
            
            last_inode = current_inode
            buffer = ''
            file.seek(0, os.SEEK_END)
            last_position = file.tell()
            continue

        if current_size < last_position:
            buffer = ''
            last_position = 0
            file.seek(0)

        elif current_size > last_position:
            file.seek(last_position)
            data = file.read(current_size - last_position)
            last_position = file.tell()

            try:
                buffer += data.decode('ansi')
            except UnicodeDecodeError:
                buffer += data.decode('ansi', errors='replace')

            lines = buffer.split('\n')
            buffer = lines[-1]

            for line in lines[:-1]:
                yield line

        time.sleep(0.1)

key_binds = ''

def map_hotbar(hotbar):
    global key_binds
    
    time.sleep(0.1)
    with open('map.ahk', 'w') as file:
        for i in range(hotbar.size()):
            file.write(key_binds[i] + '::' + hotbar[i] + '\n')
    
    os.system('map.ahk')

swap_file = None
vis = None
hotbar = ''
filler_str = 'aaa'
offhand_key = ''


def dfs(num):
    global swap_file, key_binds, filler_str
    
    nxt = int(hotbar[num - 1])
    if vis[num]:
        return
    
    vis[num] = True
    dfs(nxt)
    swap_file.write(key_binds[num - 1] + filler_str + offhand_key + filler_str)
    
def swap_hotbar():
    global swap_file, vis, key_binds, filler_str
    
    vis = [False] * (len(hotbar) + 1)
    swap_file = open('swap.ahk', 'w')
    swap_file.write("Send, a")
    
    for i in range(1, len(hotbar)):
        if not vis[i] and i != int(hotbar[i - 1]):
            swap_file.write(key_binds[i - 1] + filler_str + offhand_key + filler_str)
            dfs(i)
    
    swap_file.close()
    os.system('swap.ahk')

if __name__ == "__main__":
    line_content = ''
    build_name = ''
    log_file = ''
    map_swap_ind = 0

    build_key_table = dict()

    print('Speedbuilder Hotbar Remapper Copyright (C) 2025 dontcareism a.k.a ClearColdWater (1697088220@qq.com)\n\
    This program comes with ABSOLUTELY NO WARRANTY. \n\
    This is free software, and you are welcome to redistribute it \n\
    under certain conditions. Check LICENSE in the directory for more information.')

    
    while True:
        try:
            with open('build-key-table.cfg', 'r') as file:
                for line in file:
                    words = line.strip().split(':')
                    build_key_table[words[0]] = words[1]
            break
            
        except IOError:
            print("建筑键位重映射配置文件缺失或打开失败，等待重试...")
            time.sleep(10)

    while True:
        try:
            with open('config.cfg', 'r') as file:
                config_str = file.read()
                
                print("正在使用如下配置:")
                print(build_key_table)
                print(config_str)
                
                config_dict = json.loads(config_str)
                key_binds = config_dict['hotbar_key_binds']
                log_file = config_dict['log_file_name']
                filler_str = config_dict['filler_string']
                offhand_key = config_dict['offhand_key']
            break
        except IOError:
            print("您似乎是第一次使用此脚本，请按照提示完成配置，按回车键确认输入，有疑问请参考目录下的 README 文件:")

            while True:
                print("请输入您的快捷栏键位（例如:1234rcvfg）:")
                key_binds = input()
                if len(key_binds) != 9:
                    print("快捷栏键位数量不为9，输入无效")
                    continue
                break
            
            print("请输入您希望修改键位的我的世界游戏日志文件地址:（网易所有我的世界服务器日志文件都在同一地址下，输入0自动改为该地址）:")
            log_file = input()
            if log_file == '0':
                log_file = 'C:\MCLDownload\Game\.minecraft\logs\latest.log'
                
            print("请输入您的副手键位:")
            offhand_key = input()
            
            print("使用键盘重映射修改键位（显示仍错误，实际按键键位正确）请输入1，使用副手切换方块位置（显示和实际都正确）请输入2，按回车键确认（如果不知道这是什么，请输入2；所有不为1的输入都会被默认更正为2）:")
            map_swap_ind = int(input())
            if map_swap_ind != 1:
                map_swap_ind = 2

            config_dict = dict()
            config_dict['hotbar_key_binds'] = key_binds
            config_dict['log_file_name'] = log_file
            config_dict['filler_string'] = filler_str
            config_dict['offhand_key'] = offhand_key
            config_str = json.dumps(config_dict)
            
            with open('config.cfg', 'w') as file:
                file.write(config_str)

    while True:
        for line in follow(log_file):
            try:
                line_content = line.split(':')[-2]
                if line_content[:8] != ' [CHAT] ' or ('>' in line_content or '?' in line_content or '=' in line_content or 'TOP' in line_content or '回合' in line_content or '恭' in line_content or '-' in line_content or line_content == '') or (not '您' in line_content): 
                    continue
                build_name = line_content[8:].split('您')[0][:-1]
            except IndexError:
                continue

            if build_name in build_key_table:
                print('识别到建筑:' + build_name)
                hotbar = build_key_table[build_name]
                
                if map_swap_ind == 1:
                    map_hotbar()
                else:
                    swap_hotbar()
            else:
                print('未找到建筑:' + build_name)
