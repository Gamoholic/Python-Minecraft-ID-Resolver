#!/usr/bin/env python
import re, os, sys
from operator import itemgetter


SCAN = ""


rootdir = 'config'
configs = []

# Use these 2 to add special cases
configs_exclude = ['EE3.cfg']
configs_include = ['TinkersWorkshop.txt']

# Super mega sexy file list generator
for root, subFolders, files in os.walk(rootdir):
    for x in files:
        if x not in configs_exclude:
            if x.endswith('cfg') or x.endswith('conf'):
                configs.append(os.path.join(root, x))
            if x in configs_include:
                configs.append(os.path.join(root, x))




def build_list(regex_string, open_file, config_name):
    regex = regex_string + ' \{.*?\}'
    
    # Find the "block" or "item" section
    # re.DOTALL ignores newlines
    list_search = re.search(regex, open_file, re.DOTALL)
    if list_search != None:
        list_search_group = list_search.group()
        list_findall = re.findall('I\:.*', list_search_group)
        
        # Split the IDs into name and ID number
        # Example: ["I:ID.BioFuel.Still", "2063"]
        list_split = [s.split('=') for s in list_findall]
        list_int = []
        
        # Change the datatype for the ID numbers to, well, numbers :P
        for x in list_split:
            temp_list = [x[0], int(x[1])]
            list_int.append(temp_list)
        list_append = []
        
        # Add the config name to keep track of which items belong to which config
        for s in list_int:
            s.append(config_name)
            list_append.append(s)
        return list_append
    else:
        print regex_string, config_name
        return []




def replace_ids(object_name, buffer_amount, round_amount, id_object, this_config):
    if object_name != []:
        
        # Avoid vanilla music discs. They conflict for some reason.
        while id_object in range(2256, 2268):
            id_object += 1
        
        # Iterate over either blocks or items, sorted by ID number
        for x in sorted(object_name, key=itemgetter(1)):
            original = x[0] + '=' + str(x[1])
            replacement = x[0] + '=' + str(id_object)
            
            ''' Example:
                    original:
                        I:ID.BioFuel.Still=2063
                    replacement:
                        I:ID.BioFuel.Still=5000
            '''
            this_config = re.sub(original, replacement, this_config)
            id_object += 1
        
        # Add a buffer to pad for the unexpected
        id_object += buffer_amount
        
        # Round the ID number
        while id_object % round_amount != 0:
            id_object += 1
    return this_config, id_object




blocks = []
items = []
range_list = []

# These 2 control where the IDs start
id_block = 1000
id_item = 10000

# These 2 control how much padding is added after each config
buffer_block = 20
buffer_item = 255

# These 2 control what the IDs are rounded to
round_block = 20
round_item = 100

print "Configs to check:"
print

# The Main Loop
for config in sorted(configs):
    the_open_config = open(config, 'rU')
    open_config = the_open_config.read()
    special_names = {}
    
    # The Exceptions
    # I plan to clean this up soon. Any ideas are very welcome
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
        special_names = {'"equipables"': "i", '""paterns and misc""': "i",
            '""tool parts""': "i", '"tools"': "i"}
    elif config == "config/Reika/RotaryCraft.cfg":
        special_names = {'""crafting item ids""': "i", '""item ids""': "i", 
            '""itemblock ids""': "i", '""resource item ids""': "i", 
            '""tool item ids""': "i", '""extra block ids""': "b",
            '""machine blocks""': "b"}
    elif config == "config/Reika/ReactorCraft.cfg":
        special_names = {'"item ids"': "i", '"reactor blocks"': "b"}
    elif config == "config/Reika/GeoStrata.cfg":
        # Some consistancy would be amazing Reika!!!
        special_names = {'"item ids"': "i", '"rock blocks"': "b"}
    
    # Build the ID lists
    else:
        blocks = build_list("block", open_config, config)
        items = build_list("item", open_config, config)
    
    # This handles configs that have multiple ID sections
    if special_names != {}:
        for special_name in special_names:
            for special_list in build_list(special_name, open_config, config):
                if special_names[special_name] == "i":
                    items.append(special_list)
                else:
                    blocks.append(special_list)
    
    id_block_start = id_block
    id_item_start = id_item
    
    # Replace the IDs
    # Includes special logic to prevent Pam's mods from eating all the IDs
    if blocks != []:
        if config.startswith("config/PamHC"):
            open_config, id_block = replace_ids(blocks, 1, 
                1, id_block, open_config)
        else:
            open_config, id_block = replace_ids(blocks, buffer_block, 
                round_block, id_block, open_config)
    if items != []:
        if config.startswith("config/PamHC"):
            open_config, id_item = replace_ids(items, 1, 
                1, id_item, open_config)
        else:
            open_config, id_item = replace_ids(items, buffer_item, 
                round_item, id_item, open_config)
    
    # Build the ID range lists
    if id_block_start == id_block:
        range_list_block = ""
    else:
        range_list_block = str(id_block_start) + '-' + str(id_block)
    if id_item_start == id_item:
        range_list_item = ""
    else:
        range_list_item = str(id_item_start) + '-' + str(id_item)
    
    # Build the CSV-ready range list section    
    range_list.append(config + ', ' + range_list_block + ', ' + range_list_item)
    
    # Write the updated config
    if SCAN != '--scan':
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

