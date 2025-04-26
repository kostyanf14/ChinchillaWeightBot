from telegram import InlineKeyboardButton, InlineKeyboardMarkup

SC_START_TEXT = "Hi!"

SC_ADD_WEIGHT_CHINCHILA_TEXT = "Select chinchila"

SC_ADD_WEIGHT_CHINCHILA_DATA_PREFIX = "c8hd"

SC_ADD_WEIGHT_WEIGHT_TEXT = "Enter weight for chinchila %s"

SC_ADD_WEIGHT_WEIGHT_ERROR = "Failed to parse weight '%s' - must be integer. Try again."

SC_ADD_WEIGHT_FINISH_TEXT = '''Chinchila %s, weight: %s

if everything is correct - click 'Save' to continue. If an error occurred - click 'Reset' to start again.'''

SC_ADD_WEIGHT_FINISH_MARKUP = InlineKeyboardMarkup([[
    InlineKeyboardButton('Save', callback_data='save'),
    InlineKeyboardButton('Reset', callback_data='reset'),
]])

SC_ADD_WEIGHT_SAVE_OK = "[OK]: Chinchila %s, weight: %s saved"

SC_ADD_WEIGHT_SAVE_ERROR = "[FAILED}: Chinchila %s, weight: %s not saved"

SC_ADD_WEIGHT_RESET = "Ok, forget everything"

HELP_TEXT = '''
/add_weight - add chinchila weight
/cancel - cancel current action
/help - get this text
'''
