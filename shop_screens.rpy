
# position constants
define SHOP_START_XPOS = 190
define SHOP_START_YPOS = 370 #328

define SHOP_XSPACING = 16
define SHOP_YSPACING = 58

define SHOP_ITEM_SIZE = 111

# what shop sells what and for what price
default shops_items = {
    "bob":[{'hat':5,'soda':3,'coin':1,'hat2':5,'soda2':3,'coin2':1,'hat3':5,'soda3':3},{'coin3':1},{},{}], 
    "candyclub":[{'CRINGE':1, 'Bugz':1, 'skites':1, 'gumballz':1, 'gopstoppers':1, 'salspageti':1, 'pollos':1},{'nutzag':1},{},{}]
}
default shop_items_values = {
    "bob":{'hat':5,'soda':3,'coin':1,'hat2':5,'soda2':3,'coin2':1,'hat3':5,'soda3':3,'coin3':1}, 
    "candyclub":{'CRINGE':1, 'Bugz':1, 'skites':1, 'gumballz':1, 'gopstoppers':1, 'salspageti':1, 'pollos':1,'nutzag':1}
}

# what shop buys what and for what price
default shop_buy_items = {
    "bob":{'soda':3,'soda2':3,'soda3':3,'soda4':3}, 
    "candyclub":{'CRINGE':1, 'Bugz':1, 'skites':1, 'gumballz':1, 'gopstoppers':1, 'salspageti':1, 'pollos':1, 'nutzag':1}
}

default shop_prev_transaction = []
default shop_shelfs_current_offsets = [0,0,0,0]

default current_sell_item = ""
default current_buy_item = ""
init python:
    # sell item logic
    # remove 1 from inventory and give the money
    def sell_item_func(item_name):
        if (item_name in store.inventory):
            if (store.inventory[item_name] > 0):
                value = store.shop_buy_items[store.shop_name][item_name]
                store.player_money += value
                store.inventory[item_name] = max(0, inventory[item_name]-1)
                if (not store.shop_prev_transaction):
                    store.shop_prev_transaction = ["sell", item_name, value]
        return
    def buy_item_func(item_name):
        value = store.shop_items_values[store.shop_name][item_name]
        store.player_money -= value
        if (item_name in store.inventory):
            store.inventory[item_name] += 1
        else:
            store.inventory[item_name] = 1
        if (not store.shop_prev_transaction):
            store.shop_prev_transaction = ["buy", item_name, value]
        return

    # cancel previous interaction
    def reset_buy_item_func():
        store.player_money += shop_prev_transaction[2]
        store.inventory[shop_prev_transaction[1]] = max(0, inventory[shop_prev_transaction[1]]-1)
        store.shop_prev_transaction = []
        return
    def reset_sell_item_func():
        store.player_money -= shop_prev_transaction[2]
        store.inventory[shop_prev_transaction[1]] += 1
        store.shop_prev_transaction = []
        return


# try to sell item label
label sell_item(item_name):
    #$ current_sell_item = item_name
    if (item_name in shop_buy_items[shop_name].keys()):
        $ renpy.music.play("sfx/shop_transaction_success.mp3", channel="sound")
        #call screen confirm(message="Sell [item_name]?", yes_action=[sell_item_func,Return()] , no_action=Return())
        $ sell_item_func(item_name)
        if renpy.has_label(shop_name+"_"+item_name+"_sell"):
            call expression(shop_name+"_"+item_name+"_sell") from _call_expression
        $ inventory_draggable = True
        $ renpy.block_rollback()
        return
    else:
        $ renpy.music.play("sfx/shop_transaction_cancel.mp3", channel="sound")
        $ inventory_draggable = True
        $ renpy.block_rollback()
        return

# try to buy and item
label buy_item(item_name):
    #$ current_buy_item = item_name
    if (shop_items_values[shop_name][item_name] <= player_money):
        $ renpy.music.play("sfx/shop_transaction_success.mp3", channel="sound")
        #call screen confirm(message="Buy [item_name]?", yes_action=[buy_item_func,Return()] , no_action=Return())
        $ buy_item_func(item_name)
        if renpy.has_label(shop_name+"_"+item_name+"_buy"):
            call expression(shop_name+"_"+item_name+"_buy") from _call_expression_1
        
        $ inventory_draggable = True
        $ renpy.block_rollback()
        return
    else:
        $ renpy.music.play("sfx/shop_transaction_cancel.mp3", channel="sound")
        if renpy.has_label(shop_name+"_insufficientFunds"):
            call expression(shop_name+"_insufficientFunds") from _call_expression_2
        $ inventory_draggable = True
        $ renpy.block_rollback()
        return
    
label shop_drop_outside_area():
    $ inventory_draggable = True
    return
    

# the generic screen, the input shop_name to decide which shop
screen shop_screen(_active=True):
    #zorder 1

    # shop text
    add "gui/shop/shop_sign_"+shop_name+".png":
        xpos 120
        ypos 25

    # shop shelf
    add "gui/shop/shop_shelf.png":
        xpos 30
        ypos 300
    # arrows
    # left
    for i in range (4):
        imagebutton auto 'gui/shop/shelf_arrow_l_%s.png':
            #insensitive "gui/inventory/inventory_use_area_transparent.png"
            idle 'gui/shop/shelf_arrow_l_idle.png'
            hover 'gui/shop/shelf_arrow_l_hover.png'
            sensitive 0 < shop_shelfs_current_offsets[i-1] and _active
            action SetDict(shop_shelfs_current_offsets, i-1, shop_shelfs_current_offsets[i-1]-1)
            xpos 100 #INVENTORY_BOTTOM_XPOS + INVENTORY_SLOT_XSIZE - 45
            ypos 380 + i*170
    for i in range (4):
        imagebutton: 
            #insensitive "gui/inventory/inventory_use_area_transparent.png"
            idle 'gui/shop/shelf_arrow_r_idle.png'
            hover 'gui/shop/shelf_arrow_r_hover.png'
            sensitive (shop_shelfs_current_offsets[i-1] < len(shops_items[shop_name][i])-5) and _active
            action SetDict(shop_shelfs_current_offsets, i-1, shop_shelfs_current_offsets[i-1]+1)
            xpos 830 #INVENTORY_BOTTOM_XPOS + INVENTORY_SLOT_XSIZE - 45
            ypos 380 + (i)*170

    # character 
    #add "gui/shop/shop_character_"+shop_name+".png":
    #    xpos 1120
    #    ypos 150

    # current funds 
    add "gui/shop/current_funds_plate.png":
        xpos 1440
        ypos 750
    text "$" + str(player_money) + ".00":
        color "#000"
        size 40
        xpos 1580
        xalign 0.5
        ypos 900
    if (shop_prev_transaction):
        #if ((shop_prev_transaction[0] == "sell" and player_money > shop_prev_transaction[2]) or shop_prev_transaction[0] == "buy")
        textbutton "cancel previous":
            #color "#000"
            text_size 40
            xpos 1580
            xalign 0.5
            ypos 700
            if (shop_prev_transaction[0] == "sell"):
                action Function(reset_sell_item_func)
            else:
                action Function(reset_buy_item_func)

    if _active:
        imagebutton:
            #sensitive renpy.get_screen("inventory_button")
            idle "gui/shop/back_idle.png"
            hover "gui/shop/back_hover.png"
            action Return("shop_complete")#[Hide("inventory_button"), Hide("inventory_screen"), Return()]
            xpos 1700
            ypos 60

    add "gui/shop/shop_bottom.png":
        xalign 0.5
        yalign 1.0 
    
    # shop use area graphic
    add "gui/inventory/inventory_use_area_shop.png":
        xalign 0.9
        yalign 0.7

    # draggable elements at the top layer 

    #$ y_itr = 0
    $ x_itr = 0
    $ temp_x = SHOP_START_XPOS
    $ temp_y = SHOP_START_YPOS
    draggroup:
        $ first_item = True
        for y_itr in range(4):
            $ shelf_x_counter = 0 
            $ items_to_skip = shop_shelfs_current_offsets[y_itr-1]
            for item_name, price in shops_items[shop_name][y_itr].iteritems():
                if (0 < items_to_skip):
                    $ items_to_skip = items_to_skip - 1
                    #continue
                else:
                    if (shelf_x_counter < 5):
                        #if (shop_shelfs_current_offsets[y_itr-1] == 0): 
                        #    if (shelf_x_counter == 0):
                        #    $ current_shop_positions[item_name] = (temp_x, temp_y)
                        #    else:
                        #        $ current_shop_positions[item_name] = (temp_x, temp_y)
                        #else:
                        #   $ current_shop_positions[item_name] = (temp_x + (127), temp_y)
                        $ current_shop_positions[item_name] = (temp_x, temp_y)
                        drag:
                            drag_offscreen False
                            droppable False
                            drag_name item_name
                            child "gui/shop/shop_icons/inventory_%s.png"%(item_name)
                            xpos temp_x
                            ypos temp_y
                            dragged shop_drag_buy_item
                            draggable inventory_draggable and _active#True
                            # TODO: tooltips for this?
                            tooltip inventory_tooltips[item_name]
                        #if x_itr == 4:
                        #    $ x_itr = 0
                        #    $ temp_x = SHOP_START_XPOS
                        #    $ temp_y = temp_y + SHOP_YSPACING + SHOP_ITEM_SIZE
                        #else:
                        $ shelf_x_counter += 1
                        $ x_itr += 1
                        $ temp_x += SHOP_XSPACING + SHOP_ITEM_SIZE
                    
                
                    
            $ x_itr = 0
            $ temp_x = SHOP_START_XPOS
            $ temp_y = temp_y + SHOP_YSPACING + SHOP_ITEM_SIZE
            
            
            

            # use area
            drag:
                drag_name 'inventory_use_area'
                draggable False
                droppable True
                child "gui/inventory/inventory_use_area_transparent_shop.png"
                xalign 0.9
                yalign 0.7

    # tooltip
    $ tooltip = GetTooltip()
    if tooltip:
        $ topic,contents = tooltip.split('SEPARATOR')
        vbox:
            xpos 0.5
            xalign 0.5
            ypos 0.3
            xsize 400
            style_prefix "tooltip"
            text topic
            text contents

## Tooltip style
style tooltip_text is gui_text

style tooltip_text:
                color gui.text_color
                outlines [(absolute(4), "#ffffff88", absolute(0), absolute(0)), (absolute(2), "#000", absolute(0), absolute(0))]
                xalign 0.5
