
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

# from constants.privileges import PRIVILEGES
from constants.messages import MESSAGES


def make_keyboard(permList, guest=False, now=True):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=False)

    accept =  "Btn_" #Дефис клавиш

    #print( "make_keyboard perms_now:", permList )

    if not permList:
        #print("return none Not Perms!")
        return ReplyKeyboardRemove()
    
    all_void = True
    for action in permList:

        if accept in action:
            all_void = False
            
            button = KeyboardButton( MESSAGES[action] ) #Держать все стандартные клавиши в стандартном МЕСАГЕ!!
            keyboard.add(button)
        # else:
            #print(action)

    if all_void: 
        #print("return none all Perms void!")
        return ReplyKeyboardRemove()


    #print("return Done!")
    return keyboard