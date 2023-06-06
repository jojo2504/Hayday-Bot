import pyautogui
import time
import win32api, win32con
import keyboard
import threading
import sys

def click(x,y, second_sleep = 1):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
    time.sleep(second_sleep)

def mouse_drag(start_x, start_y, drag_distance_x, drag_distance_y, drag_duration, sleep_duration=1):
    pyautogui.moveTo(start_x, start_y)
    pyautogui.mouseDown(button='left')
    pyautogui.moveRel(drag_distance_x, drag_distance_y, duration=drag_duration)
    pyautogui.mouseUp(button='left')
    time.sleep(sleep_duration)

def scrolldown(iteration):
    pyautogui.scroll(iteration)

def reset_camera_fov():
    pyautogui.keyDown('ctrlleft')
    scrolldown(-2000)
    pyautogui.keyUp('ctrlleft')
    time.sleep(1)

def locateOnScreen(needle, confidence_threshold, x=400, y=200, width=1100, height=600):
    return pyautogui.locateOnScreen(needle, region=(x, y, width, width), grayscale=True, confidence=confidence_threshold)

###############################
#                             #
#        HARVESTING           #
#                             #
###############################

def detect_harvestable_wheat():
    harvest_wheat_result = locateOnScreen('images/wheat.png', confidence_threshold=.80)
    if harvest_wheat_result != None:
        x =  harvest_wheat_result.left + 20
        y =  harvest_wheat_result.top + 15
        print(f"I see a harvestable wheat {x, y}")
        return (x,y)
    else:
        print("I don't see any harvestable wheat")
        return None

def use_scythe():
    scythe_result = locateOnScreen('images/scytheV2.png', confidence_threshold=.80)
    if scythe_result != None:
        scythe_x = scythe_result.left - 120
        scythe_y = scythe_result.top - 20
        print(f"I see a scythe at {scythe_x, scythe_y}, may move (waiting for camera stabilization...)")

        time.sleep(1.7)
        pyautogui.moveTo(scythe_x, scythe_y)
        pyautogui.mouseDown(button='left')
        return True, (scythe_x, scythe_y)
    else:
        print(f"I don't see any scythe")
        return False, None

def harvest_wheat():
    harvest_wheat_result = locateOnScreen('images/wheat.png', confidence_threshold=.80)
    if harvest_wheat_result != None:
        harvest_wheat_x =  harvest_wheat_result.left + 20
        harvest_wheat_y =  harvest_wheat_result.top + 15
        print(f"I see a harvestable wheat {harvest_wheat_x, harvest_wheat_y}")
        click(harvest_wheat_x, harvest_wheat_y, second_sleep=1)

        scythe = use_scythe()
        if scythe[0] == True:
            if scythe[1][0] > harvest_wheat_x or (scythe[1][1] - harvest_wheat_y) in range(100): #comparing x values
                print("scythe not well picked, restarting the function...")
                time.sleep(.5)
                harvest_wheat()
            else:
                processed_set = set()
                while True:
                    try:
                        harvestable_wheat_x, harvestable_wheat_y = detect_harvestable_wheat()
                        if (harvestable_wheat_x, harvestable_wheat_y) in processed_set:
                            pyautogui.mouseUp(button='left')
                            print("Debugging loop (harvest)")
                            mouse_drag(1000, 1000, -200, .5, 1)
                            return False
                        else:
                            processed_set.add((harvestable_wheat_x, harvestable_wheat_y))
                            pyautogui.moveTo(harvestable_wheat_x, harvestable_wheat_y, duration=0.01)
                            print("harvested a wheat")
                    except TypeError:
                        print("No more possible harvest.")
                        pyautogui.mouseUp(button='left')
                        break
        else:
            return False
    else:
        print("I don't any harvestable wheat")
        return None


###############################
#                             #
#        PLANTATION           #
#                             #
###############################

def use_seed(): 
    planting_wheat_result = locateOnScreen('images/planting_wheat.png', confidence_threshold=.80)
    if planting_wheat_result != None:
        x =  planting_wheat_result.left
        y =  planting_wheat_result.top
        print(f"I see a planting wheat at {x, y}")
        pyautogui.moveTo(x,y)
        pyautogui.mouseDown(button='left')
        return (x,y)
    else:
        print(f"I don't see any planting seed")
        return None

def detect_empty_farmland():
    empty_farmland_result = locateOnScreen('images/farmland.png', confidence_threshold=.90)

    if empty_farmland_result != None:
        x =  empty_farmland_result.left + 15
        y =  empty_farmland_result.top + 15

        print(f"I see a farmland at {x, y}")
        return (x,y)
    else:
        print(f"I don't see any farmland")
        return False

def first_crop_initialization():
    first_crop_result = locateOnScreen('images/initialization_crop.png', confidence_threshold=.90)
    if first_crop_result != None:
        first_crop_x = first_crop_result.left # offset x
        first_crop_y = first_crop_result.top # offset y
        pyautogui.moveTo(first_crop_x, first_crop_y)
        print("First seed planted..")
        return True
    else:
        print("First crop not detected")
        return False

def planting_wheat():
    planting_wheat_result = locateOnScreen('images/farmland.png', confidence_threshold=.90)

    if planting_wheat_result != None:
        x =  planting_wheat_result.left + 15
        y =  planting_wheat_result.top + 15

        print(f"I see a farmland at {x, y}")
        click(x,y)
        time.sleep(1)
        if use_seed() != None:
            if first_crop_initialization() == True:
                processed_set = set()
                while True:
                    try:
                        plantable_wheat_x, plantable_wheat_y = detect_empty_farmland()
                        if (plantable_wheat_x, plantable_wheat_y) in processed_set:
                            pyautogui.mouseUp(button='left')
                            print("Debugging loop (planting), proceeding to restart the planting function")
                            planting_wheat()
                        else:
                            processed_set.add((plantable_wheat_x, plantable_wheat_y))
                            pyautogui.moveTo(plantable_wheat_x, plantable_wheat_y, duration=0.01)
                            print("wheat planted")
                    except TypeError:
                        print("No more possible planting")
                        pyautogui.mouseUp(button='left')
                        break
            return False # This event should never triggers
        return False
    else:
        print("I don't see any farmland")

###############################
#                             #
#             SHOP            #
#                             #
###############################

def exit_shop() -> None:
    print("Exiting shop...")
    click(1655, 150)

def recolt_money(): 
    selled_result = locateOnScreen('images/selled.png', confidence_threshold=.90, x=0, y=0, width=1980, height=1080)
    if selled_result != None:
        selled_item_x = selled_result.left
        selled_item_y = selled_result.top
        print("Recolting items in shop")
        click(selled_item_x, selled_item_y, 0.05)
        return True
    else:
        print("There is nothing to recolt")
        return False

def end_list():
    end_list_result = locateOnScreen('images/end_list_shop.png', confidence_threshold=.90, x=0, y=0, width=1980, height=1080)
    if end_list_result != None:
        return True
    else:
        print("Still need to drag to the right...")
        return False

def publish_item() -> None:
    possible_publish_result = locateOnScreen('images/free_publication.png', confidence_threshold=.90, x=0, y=0, width=1980, height=1080)
    if possible_publish_result != None:
        publish_x = possible_publish_result.left
        publish_y = possible_publish_result.top
        print("Publishing items")
        click(1165, 520, .1)
        click(970, 760, .1)
    else:
        print("Can't publish")

def item_publishable():
    item_publishable_result = locateOnScreen('images/unpublished_wheat.png', confidence_threshold=.90, x=0, y=0, width=1980, height=1080)
    if item_publishable_result != None:
        item_publishable_x = item_publishable_result.left + 100
        item_publishable_y = item_publishable_result.top + 120
        print("Publishing wheats")
        click(item_publishable_x, item_publishable_y, 1)
        publish_item()
    else:
        print("Can't publish")

def published_state(publish_flag):
    item_publishable_result = locateOnScreen('images/published_wheat.png', confidence_threshold=1, x=0, y=0, width=1980, height=1080)
    if item_publishable_result != None:
        print("------------- Some items are already published -------------")
        publish_flag = 1
        return publish_flag
    else:
        return publish_flag

def put_on_sell(publish_flag):
    while True:
        if not recolt_money():
            break
    if end_list() == True:
        if publish_flag == 0:
            item_publishable()
        exit_shop()
    else:
        publish_flag = published_state(publish_flag)
        possible_sell_slot_result = locateOnScreen('images/new_sell.png', confidence_threshold=.90, x=0, y=0, width=1980, height=1080)
        if possible_sell_slot_result != None:
            sell_slot_x = possible_sell_slot_result.left
            sell_slot_y = possible_sell_slot_result.top

            print("Selling..")
            click(sell_slot_x, sell_slot_y, 0.05)

            print("Silo category selected..")
            click(270, 350, 0.05) # Selecting Silo category  

            wheat_item_sell_result = locateOnScreen('images/wheat_item_sell.png', confidence_threshold=.80, x=0, y=0, width=1980, height=1080)
            if wheat_item_sell_result != None:
                wheat_item_x = wheat_item_sell_result.left
                wheat_item_y = wheat_item_sell_result.top
                print("Wheat item selected..")
                click(wheat_item_x, wheat_item_y, 0.05)
            else:
                print("No wheat available") # this event should never trigger 
                return None

            click(1500,540, 0.05) # set max money price
            #publish_item() # free every 5 minutes

            click(1400,1000, 0.05) # put in sell
            put_on_sell(publish_flag)
        else:
            print("I can't put anything on sell.")
            x = 1200 # randomly take
            y = 750 # randomly take
            mouse_drag(x, y, -200, 0, .01, .01)
            put_on_sell(publish_flag)

def detect_shop():
    shop_result = locateOnScreen('images/shop.png', confidence_threshold=.70, x=0, y=0, width=1980, height=1080)
    if shop_result != None:
        shop_x = shop_result.left + 30 # offset x 
        shop_y = shop_result.top + 20 # offset y 
        print("Shop detected")
        time.sleep(2)
        click(shop_x, shop_y)
        return True
    else:
        print("Shop not detected... searching...")
        time.sleep(0.3)
        x = 1000 # randomly picked
        y = 1000 # randomly picked
        #click(x,y, 1)
        mouse_drag(x, y, 300, 0, .5, 2)
        detect_shop()

def exit_full_silo_warning():
    full_silo_result = locateOnScreen('images/full_silo.png', confidence_threshold=.90, x=0, y=0, width=1980, height=1080)
    if full_silo_result != None:
        print('Exit full silo warning')
        time.sleep(0.5)
        click(1600, 100, 0.2)
        return True
    else:
        #print("No warning silo detected")
        return False


###############################
#                             #
#        ENVIRONMENT          #
#                             #
###############################

def get_environment():
    shop_presence_result = locateOnScreen('images/shop_presence.png', confidence_threshold=.90, x=0, y=0, width=1980, height=1080)
    if shop_presence_result != None:
        environment_section = """
###############################
#                             #
#             SHOP            #
#                             #
###############################
            """
        print(environment_section)
        return "SHOP"
    else:
        environment_section = """
###############################
#                             #
#             FARM            #
#                             #
###############################
            """
        print(environment_section)
        return "FARM"

def fix_wtf_camera():
    boat_result = locateOnScreen('images/WTF ARE WE DOING HERE.png', confidence_threshold=.90, x=0, y=0, width=1980, height=1080)
    if boat_result != None:
        print("Fixing the camera")
        mouse_drag(1000, 1000, -300, -300, .5)

###############################
#                             #
#            MAIN             #
#                             #
###############################

stop_program = False  # Flag variable to indicate whether to stop the program

def check_key_press():
    global stop_program
    while True:
        if keyboard.is_pressed("q"):
            pyautogui.mouseUp(button='left')
            print("\n" + "=" * 50)
            print("Program Stopping...")
            print("=" * 50)
            environment = get_environment()
            if environment == "FARM":
                pyautogui.keyDown('ctrlleft')
                scrolldown(2000)
                pyautogui.keyUp('ctrlleft')
                time.sleep(1)
            stop_program = True
            sys.exit()

def main():
    for i in range(1, 4):
        print("Initialization of the Game" + "." * i, end='\r')
        time.sleep(.6)
    print("Initialization of the Game...")

    key_thread = threading.Thread(target=check_key_press)
    key_thread.start()

    while not stop_program:
        environment = get_environment()
        if environment == "FARM":
            fix_wtf_camera()
            planting_wheat()
            time.sleep(2)
            harvest_wheat()

            if exit_full_silo_warning():
                time.sleep(2)
                planting_wheat()
                if detect_shop():
                    time.sleep(1)
        else:
            put_on_sell(publish_flag=0)
        pyautogui.mouseUp(button='left')

if __name__ == '__main__':
    main()