import html
import json
import logging
import traceback
from enum import Enum, auto, unique

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

import app.models

from ..config import Config
from . import resources

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:",
                 exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_msg = context.error.__traceback__ if context.error is not None else None
    tb_list = traceback.format_exception(None, context.error, tb_msg)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    # max message size 4096
    await context.bot.send_message(
        chat_id=Config.developer_chat_id, text=message[:4000], parse_mode=ParseMode.HTML
    )


@unique
class WeightConversationState(Enum):
    CHINCHILA = auto()
    WEIGHT = auto()
    FINISH = auto()


async def sc_start(update: Update, _) -> None:
    logger.debug("sc_start %s", update)
    if update.message is None or update.message.text is None:
        logger.warning("sc_start with message/text None")
        return

    await update.message.reply_text(resources.SC_START_TEXT)
    await update.message.reply_text(resources.HELP_TEXT)


async def sc_add_weight(update: Update, _) -> WeightConversationState:
    logger.debug("sc_add_weight %s", update)

    chinchilas_inlines = []
    for chinchila in app.models.Chinchilla.all():
        chinchilas_inlines.append(
            InlineKeyboardButton(chinchila.name,
                                 callback_data=f'{resources.SC_ADD_WEIGHT_CHINCHILA_DATA_PREFIX}_{chinchila.id}'
                                 )
        )

    sc_select_chinchila_markup = InlineKeyboardMarkup([chinchilas_inlines])

    await update.message.reply_text(resources.SC_ADD_WEIGHT_CHINCHILA_TEXT, reply_markup=sc_select_chinchila_markup)
    return WeightConversationState.CHINCHILA


async def sc_select_chinchila(update: Update, context: ContextTypes.DEFAULT_TYPE) -> WeightConversationState:
    logger.encoding = "UTF-8"
    logger.debug("sc_select_chinchila %s", update)

    if update.callback_query is None or update.callback_query.data is None or update.callback_query.message is None:
        logger.error("sc_select_chinchila with callback_query/data/message None")
        return WeightConversationState.CHINCHILA
    assert context.chat_data is not None

    prefix, ch_id = update.callback_query.data.split('_')
    if prefix != resources.SC_ADD_WEIGHT_CHINCHILA_DATA_PREFIX:
        logger.error("sc_select_chinchila with wrong callback_query.data")
        return WeightConversationState.CHINCHILA
    try:
        ch = app.models.Chinchilla.find(int(ch_id))
    except ValueError:
        logger.error("sc_select_chinchila failed to find chinchilla")
        return WeightConversationState.CHINCHILA

    context.chat_data['last_ch_id'] = ch.id

    text = resources.SC_ADD_WEIGHT_WEIGHT_TEXT % ch.name
    await update.callback_query.message.edit_text(text)

    return WeightConversationState.WEIGHT


async def sc_enter_weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> WeightConversationState:
    logger.debug("sc_enter_weight %s", update)

    if update.message is None or update.message.text is None:
        logger.error("sc_enter_weight with message/text None")
        return WeightConversationState.WEIGHT

    assert context.chat_data is not None

    try:
        weight = int(update.message.text)
    except ValueError:
        await update.message.reply_text(resources.SC_ADD_WEIGHT_WEIGHT_ERROR % update.message.text)
        return WeightConversationState.WEIGHT

    context.chat_data['last_ch_weight'] = weight

    ch = app.models.Chinchilla.find(int(context.chat_data['last_ch_id']))

    text = resources.SC_ADD_WEIGHT_FINISH_TEXT % (ch.name, weight)
    await update.message.reply_text(text, reply_markup=resources.SC_ADD_WEIGHT_FINISH_MARKUP)
    return WeightConversationState.FINISH


async def sc_save_weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> WeightConversationState | int:
    logger.debug("sc_save_weight %s", update)

    if update.callback_query is None or update.callback_query.message is None:
        logger.error("sc_save_weight with message/text None")
        return WeightConversationState.FINISH
    assert context.chat_data is not None

    try:
        db_weight = app.models.Weight()
        db_weight.chinchilla_id = int(context.chat_data['last_ch_id'])
        db_weight.weight = int(context.chat_data['last_ch_weight'])
        db_weight.save()
    except Exception as ex:
        logger.error("sc_save_weight failed %s", ex)

        text = resources.SC_ADD_WEIGHT_SAVE_ERROR % (db_weight.get_chinchilla().name, db_weight.weight)
        await update.callback_query.message.edit_text(text)
        return ConversationHandler.END

    context.chat_data['last_ch_id'] = None
    context.chat_data['last_ch_weight'] = None

    text = resources.SC_ADD_WEIGHT_SAVE_OK % (db_weight.get_chinchilla().name, db_weight.weight)
    await update.callback_query.message.edit_text(text)
    return ConversationHandler.END


async def sc_reset_weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> WeightConversationState | int:
    logger.debug("sc_reset_weight %s", update)

    if update.callback_query is None or update.callback_query.message is None:
        logger.error("sc_reset_weight with callback_query/message None")
        return WeightConversationState.FINISH
    assert context.chat_data is not None

    context.chat_data['last_ch_id'] = None
    context.chat_data['last_ch_weight'] = None

    await update.callback_query.message.edit_text(resources.SC_ADD_WEIGHT_RESET)
    return ConversationHandler.END


async def help_cmd(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.debug("help_cmd %s", update)

    if update.message is None:
        logger.error("help_cmd with message None")
        return

    await update.message.reply_text(resources.HELP_TEXT)
