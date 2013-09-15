#!/usr/bin/env python
import re, os
from operator import itemgetter



rootdir = 'config'
configs = []

# Super mega sexy file list generator
for root, subFolders, files in os.walk(rootdir):
    for x in files:
        if x.endswith('cfg') or x.endswith('conf'):
            configs.append(os.path.join(root, x))
configs.append("config/TinkersWorkshop.txt")
configs.remove("config/EE3/EE3.cfg")



def build_list(regex_string, open_file, config_name):
    regex = regex_string + ' \{.*?\}'
    list_search = re.search(regex, open_file, re.DOTALL)
    if list_search != None:
        list_search_group = list_search.group()
        list_findall = re.findall('I\:.*', list_search_group)
        list_split = [s.split('=') for s in list_findall]
        list_int = []
        for x in list_split:
            temp_list = [x[0], int(x[1])]
            list_int.append(temp_list)
        list_append = []
        for s in list_int:
            s.append(config_name)
            list_append.append(s)
        return list_append
    else:
        print regex_string, config_name
        return []




def replace_ids(object_name, buffer_amount, id_object, this_config):
    if object_name != []:
        for x in sorted(object_name, key=itemgetter(1)):
            original = x[0] + '=' + str(x[1])
            replacement = x[0] + '=' + str(id_object)
            if original.endswith("4000"): print original, replacement
            this_config = re.sub(original, replacement, this_config)
            id_object += 1
        if id_object % buffer_amount == 0:
            id_object += 1
        while id_object % buffer_amount != 0:
            id_object += 1
    return this_config, id_object




blocks = []
items = []
id_block = 1000
id_item = 10000
buffer_block = 20
buffer_item = 100
range_list = []

print "Configs to check:"
print

for config in sorted(configs, key=itemgetter(2)):
    the_open_config = open(config, 'rU')
    open_config = the_open_config.read()
    
    if config == "config/OpenPeripheral.cfg":
        blocks = build_list("blocks", open_config, config)
        items = build_list("items", open_config, config)
    elif config == "config/JAKJ_RedstoneInMotion.cfg":
        blocks = build_list("BlockIds", open_config, config)
        items = build_list("\"Item IDs\"", open_config, config)
    elif config.startswith("config/Metallurgy3"):
        blocks = build_list("block", open_config, config)
        items = build_list("\"\#item ids\"", open_config, config)
    elif config == "config/AdvancedSolarPanel.cfg":
        blocks = build_list("block", open_config, config)
        items = build_list("items", open_config, config)
    elif config == "config/TinkersWorkshop.txt":
        blocks = build_list("block", open_config, config)
        items = build_list("item", open_config, config)
        for equipable in build_list("equipables", open_config, config):
            items.append(equipable)
        for pattern in build_list("\"patterns and misc\"", open_config, config):
            items.append(pattern)
        for tool_part in build_list("\"tool parts\"", open_config, config):
            items.append(tool_part)
        for tool in build_list("tools", open_config, config):
            items.append(tool)
    else:
        blocks = build_list("block", open_config, config)
        items = build_list("item", open_config, config)
    
    id_block_start = id_block
    id_item_start = id_item
    
    if blocks != []:
        open_config, id_block = replace_ids(blocks, buffer_block, id_block, open_config)
    if items != []:
        open_config, id_item = replace_ids(items, buffer_item, id_item, open_config)
    
    if id_block_start == id_block:
        range_list_block = ""
    else:
        range_list_block = str(id_block_start) + '-' + str(id_block)
    if id_item_start == id_item:
        range_list_item = ""
    else:
        range_list_item = str(id_item_start) + '-' + str(id_item)
        
    range_list.append(config + ', ' + range_list_block + ', ' + range_list_item)
    the_open_config.close()
    config_to_write = open(config, 'w')
    config_to_write.write(open_config)
    config_to_write.close()

print
print "ID Ranges:"
for x in range_list:
    print x
print
print "Last block ID used:", id_block
print "Last item ID used: ", id_item
    
