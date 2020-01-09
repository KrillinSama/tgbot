import html
import json
import random
import telegram
from datetime import datetime
from typing import Optional, List
from io import BytesIO
from time import sleep
import time
import requests
import os
from telegram import TelegramError, Message, Chat, Update, Bot, MessageEntity, ParseMode, User
from telegram.ext import CommandHandler, run_async, Filters, MessageHandler
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown, mention_html
from telegram.error import BadRequest

from axel_kassemsyr import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS, BAN_STICKER, LOGGER
from axel_kassemsyr.__main__ import STATS, USER_INFO, GDPR
from axel_kassemsyr.modules.disable import DisableAbleCommandHandler
from axel_kassemsyr.modules.helper_funcs.extraction import extract_user
from axel_kassemsyr.modules.helper_funcs.filters import CustomFilters
from axel_kassemsyr.modules.helper_funcs.chat_status import is_user_ban_protected
import axel_kassemsyr.modules.sql.users_sql as sql

from geopy.geocoders import Nominatim
from telegram import Location

RUN_STRINGS = (
    "Where do you think you're going?",
    "Huh? what? did they get away?",
    "ZZzzZZzz... Huh? what? oh, just them again, nevermind.",
    "Get back here!",
    "Not so fast...",
    "Look out for the wall!",
    "Don't leave me alone with them!!",
    "You run, you die.",
    "Jokes on you, I'm everywhere",
    "You're gonna regret that...",
    "You could also try /kickme, I hear that's fun.",
    "Go bother someone else, no-one here cares.",
    "You can run, but you can't hide.",
    "Is that all you've got?",
    "I'm behind you...",
    "You've got company!",
    "We can do this the easy way, or the hard way.",
    "You just don't get it, do you?",
    "Yeah, you better run!",
    "Please, remind me how much I care?",
    "I'd run faster if I were you.",
    "That's definitely the droid we're looking for.",
    "May the odds be ever in your favour.",
    "Famous last words.",
    "And they disappeared forever, never to be seen again.",
    "\"Oh, look at me! I'm so cool, I can run from a bot!\" - this person",
    "Yeah yeah, just tap /kickme already.",
    "Here, take this ring and head to Mordor while you're at it.",
    "Legend has it, they're still running...",
    "Unlike Harry Potter, your parents can't protect you from me.",
    "Fear leads to anger. Anger leads to hate. Hate leads to suffering. If you keep running in fear, you might "
    "be the next Vader.",
    "Multiple calculations later, I have decided my interest in your shenanigans is exactly 0.",
    "Legend has it, they're still running.",
    "Keep it up, not sure we want you here anyway.",
    "You're a wiza- Oh. Wait. You're not Harry, keep moving.",
    "NO RUNNING IN THE HALLWAYS!",
    "Hasta la vista, baby.",
    "Who let the dogs out?",
    "It's funny, because no one cares.",
    "Ah, what a waste. I liked that one.",
    "Frankly, my dear, I don't give a damn.",
    "My milkshake brings all the boys to yard... So run faster!",
    "You can't HANDLE the truth!",
    "A long time ago, in a galaxy far far away... Someone would've cared about that. Not anymore though.",
    "Hey, look at them! They're running from the inevitable banhammer... Cute.",
    "Han shot first. So will I.",
    "What are you running after, a white rabbit?",
    "As The Doctor would say... RUN!",
)

SLAP_TEMPLATES = (
    "{user1} {hits} {user2} with *{item}*. {emoji}",
    "{user1} {hits} {user2} in the face with *{item}*. {emoji}",
    "{user1} {hits} {user2} around a bit with *{item}*. {emoji}",
    "{user1} {throws} *{item}* at {user2}. {emoji}",
    "{user1} grabs *{item}* and {throws} it at {user2}'s face. {emoji}",
    "{user1} launches *{item}* in {user2}'s general direction. {emoji}",
    "{user1} starts slapping {user2} silly with *{item}*. {emoji}",
    "{user1} pins {user2} down and repeatedly {hits} them with *{item}*. {emoji}",
    "{user1} grabs up *{item}* and {hits} {user2} with it. {emoji}",
    "{user1} ties {user2} to a chair and {throws} *{item}* at them. {emoji}",
)

PUNCH_TEMPLATES = (
    "{user1} {punches} {user2} to assert dominance.",
    "{user1} {punches} {user2} to see if they shut the fuck up for once.",
    "{user1} {punches} {user2} because they were asking for it.",
    "It's over {user2}, they have the high ground.",
    "{user1} performs a superman punch on {user2}, {user2} is rekt now.",
    "{user1} kills off {user2} with a T.K.O",
    "{user1} attacks {user2} with a billiard cue. A bloody mess.",
    "{user1} disintegrates {user2} with a MG.",
    "A hit and run over {user2} performed by {user1}",
    "{user1} punches {user2} into the throat. Warning, choking hazard!",
    "{user1} drops a piano on top of {user2}. A harmonical death.",
    "{user1} throws rocks at {user2}",
    "{user1} forces {user2} to drink chlorox. What a painful death.",
    "{user2} got sliced in half by {user1}'s katana.",
    "{user1} makes {user2} fall on their sword. A stabby death lol.",
    "{user1} kangs {user2} 's life energy away.",
    "{user1} shoot's {user2} into a million pieces. Hasta la vista baby.",
    "{user1} drop's the frigde on {user2}. Beware of crushing.",
    "{user1} engage's a guerilla tactic on {user2}",
    "{user1} ignite's {user2} into flames. IT'S LIT FAM.",
    "{user1} pulls a loaded 12 gauge on {user2}.",
    "{user1} throws a Galaxy Note7 into {user2}'s general direction. A bombing massacre.",
    "{user1} walks with {user2} to the end of the world, then pushes him over the edge.",
    "{user1} performs a Stabby McStabby on {user2} with a butterfly.",
    "{user1} cut's {user2}'s neck off with a machete. A blood bath.",
    "{user1} secretly fills in {user2}'s cup with Belle Delphine's Gamer Girl Bathwater instead of water. Highly contagious herpes.",
    "{user1} is tea cupping on {user2} after a 1v1, to assert their dominance.",
    "{user1} ask's for {user2}'s last words. {user2} is ded now.",
    "{user1} let's {user2} know their position.",
    "{user1} makes {user2} to his slave. What is your bidding? My Master.",
    "{user1} forces {user2} to commit suicide.",
    "{user1} shout's 'it's garbage day' at {user2}.",
    "{user1} throws his axe at {user2}.",
    "{user1} is now {user2}'s grim reaper.",
)

PUNCH = (
    "punches",
    "RKOs",
    "smashes the skull of",
    "throws a pipe wrench at",
)

ITEMS = (
    "a Samsung J5 2017",
    "a Samsung S10+",
    "an iPhone XS MAX",
    "a Note 9",
    "a Note 10+",
    "knox 0x0",
    "OneUI 2.0",
    "OneUI 69.0",
    "TwoUI 1.0",
    "Secure Folder",
    "Samsung Pay",
    "prenormal RMM state",
    "prenormal KG state",
    "a locked bootloader",
    "payment lock",
    "stock rom",
    "good rom",
    "Good Lock apps",
    "Q port",
    "Pie port",
    "8.1 port",
    "Pie port",
    "Pie OTA",
    "Q OTA",
    "LineageOS 16",
    "LineageOS 17",
    "a bugless rom",
    "a kernel",
    "a kernal",
    "a karnal",
    "a karnel",
    "official TWRP",
    "VOLTE",
    "kanged rom",
    "an antikang",
    "audio fix",
    "hwcomposer fix",
    "mic fix",
    "random reboots",
    "bootloops",
    "unfiltered logs",
    "a keylogger",
    "120FPS",
    "a download link",
    "168h uptime",
    "a paypal link",
    "treble support",
    "EVO-X gsi",
    "Q gsi",
    "Q beta",
    "a Rom Control",
    "a hamburger",
    "a cheeseburger",
    "a Big-Mac",
)

THROW = (
    "throws",
    "flings",
    "chucks",
    "hurls",
)

HIT = (
    "hits",
    "whacks",
    "slaps",
    "smacks",
    "spanks",
    "bashes",
)
EMOJI = (
    "\U0001F923",
    "\U0001F602",
    "\U0001F922",
    "\U0001F605",
    "\U0001F606",
    "\U0001F609",
    "\U0001F60E",
    "\U0001F929",
    "\U0001F623",
    "\U0001F973",
    "\U0001F9D0",
    "\U0001F632",
)

SFW_STRINGS = (
    "Owww ... Such a stupid idiot.",
    "Don't drink and type.",
    "I think you should go home or better a mental asylum.",
    "Command not found. Just like your brain.",
    "Do you realize you are making a fool of yourself? Apparently not.",
    "You can type better than that.",
    "Bot rule 544 section 9 prevents me from replying to stupid humans like you.",
    "Sorry, we do not sell brains.",
    "Believe me you are not normal.",
    "I bet your brain feels as good as new, seeing that you never use it.",
    "If I wanted to kill myself I'd climb your ego and jump to your IQ.",
    "Zombies eat brains... you're safe.",
    "You didn't evolve from apes, they evolved from you.",
    "Come back and talk to me when your I.Q. exceeds your age.",
    "I'm not saying you're stupid, I'm just saying you've got bad luck when it comes to thinking.",
    "What language are you speaking? Cause it sounds like bullshit.",
    "Stupidity is not a crime so you are free to go.",
    "You are proof that evolution CAN go in reverse.",
    "I would ask you how old you are but I know you can't count that high.",
    "As an outsider, what do you think of the human race?",
    "Brains aren't everything. In your case they're nothing.",
    "Ordinarily people live and learn. You just live.",
    "I don't know what makes you so stupid, but it really works.",
    "Keep talking, someday you'll say something intelligent! (I doubt it though)",
    "Shock me, say something intelligent.",
    "Your IQ's lower than your shoe size.",
    "Alas! Your neurotransmitters are no more working.",
    "Are you crazy you fool.",
    "Everyone has the right to be stupid but you are abusing the privilege.",
    "I'm sorry I hurt your feelings when I called you stupid. I thought you already knew that.",
    "You should try tasting cyanide.",
    "Your enzymes are meant to digest rat poison.",
    "You should try sleeping forever.",
    "Pick up a gun and shoot yourself.",
    "You could make a world record by jumping from a plane without parachute.",
    "Stop talking BS and jump in front of a running bullet train.",
    "Try bathing with Hydrochloric Acid instead of water.",
    "Try this: if you hold your breath underwater for an hour, you can then hold it forever.",
    "Go Green! Stop inhaling Oxygen.",
    "God was searching for you. You should leave to meet him.",
    "give your 100%. Now, go donate blood.",
    "Try jumping from a hundred story building but you can do it only once.",
    "You should donate your brain seeing that you never used it.",
    "Volunteer for target in an firing range.",
    "Head shots are fun. Get yourself one.",
    "You should try swimming with great white sharks.",
    "You should paint yourself red and run in a bull marathon.",
    "You can stay underwater for the rest of your life without coming back up.",
    "How about you stop breathing for like 1 day? That'll be great.",
    "Try provoking a tiger while you both are in a cage.",
    "Have you tried shooting yourself as high as 100m using a canon.",
    "You should try holding TNT in your mouth and igniting it.",
    "Try playing catch and throw with RDX its fun.",
    "I heard phogine is poisonous but i guess you wont mind inhaling it for fun.",
    "Launch yourself into outer space while forgetting oxygen on Earth.",
    "You should try playing snake and ladders, with real snakes and no ladders.",
    "Dance naked on a couple of HT wires.",
    "Active Volcano is the best swimming pool for you.",
    "You should try hot bath in a volcano.",
    "Try to spend one day in a coffin and it will be yours forever.",
    "Hit Uranium with a slow moving neutron in your presence. It will be a worthwhile experience.",
    "You can be the first person to step on sun. Have a try.",
)

HBD_STRINGS = (
    "Happy birthday ",
    "HBD 😍 ",
    "HBD :) ",
    "Heppi burfdey ",
    "Hep burf ",
    "Happy day of birthing ",
    "Sadn't deathn't-day ",
    "Oof, you were born today ",
)

GMAPS_LOC = "https://maps.googleapis.com/maps/api/geocode/json"
GMAPS_TIME = "https://maps.googleapis.com/maps/api/timezone/json"


SMACK_STRING = """[smack my beach up!!](https://vimeo.com/31482159)"""

@run_async
def runs(bot: Bot, update: Update):
    running = update.effective_message
    if running.reply_to_message:
        update.effective_message.reply_to_message.reply_text(random.choice(RUN_STRINGS))
    else:
        update.effective_message.reply_text(random.choice(RUN_STRINGS))
        
@run_async
def insult(bot: Bot, update: Update):
    inst = update.effective_message
    if inst.reply_to_message:
        update.effective_message.reply_to_message.reply_text(random.choice(SFW_STRINGS))
    else:
        update.effective_message.reply_text(random.choice(SFW_STRINGS))        

@run_async
def birthday(bot: Bot, update: Update, args: List[str]):
    if args:
        username = str(",".join(args))
    for i in range(5):
        bdm = random.choice(HBD_STRINGS)
        update.effective_message.reply_text(bdm + username)
        
@run_async
def smack(bot: Bot, update: Update):
    msg = update.effective_message
    if msg.reply_to_message:
        update.effective_message.reply_to_message.reply_text(SMACK_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    else:
        update.effective_message.reply_text(SMACK_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

@run_async
def slap(bot: Bot, update: Update, args: List[str]):
    msg = update.effective_message  # type: Optional[Message]

    # reply to correct message
    reply_text = msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text

    # get user who sent message
    if msg.from_user.username:
        curr_user = "@" + escape_markdown(msg.from_user.username)
    else:
        curr_user = "[{}](tg://user?id={})".format(msg.from_user.first_name, msg.from_user.id)

    user_id = extract_user(update.effective_message, args)
    if user_id == bot.id or user_id == 777000:
        user1 = "[{}](tg://user?id={})".format(bot.first_name, bot.id)
        user2 = curr_user
    elif user_id:
        slapped_user = bot.get_chat(user_id)
        user1 = curr_user
        if slapped_user.username:
            user2 = "@" + escape_markdown(slapped_user.username)
        else:
            user2 = "[{}](tg://user?id={})".format(slapped_user.first_name,
                                                   slapped_user.id)

    # if no target found, bot targets the sender
    else:
        user1 = "[{}](tg://user?id={})".format(bot.first_name, bot.id)
        user2 = curr_user

    temp = random.choice(SLAP_TEMPLATES)
    item = random.choice(ITEMS)
    hit = random.choice(HIT)
    throw = random.choice(THROW)
    emoji = random.choice(EMOJI)

    repl = temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw, emoji=emoji)

    reply_text(repl, parse_mode=ParseMode.MARKDOWN)

@run_async
def punch(bot: Bot, update: Update, args: List[str]):
    msg = update.effective_message  # type: Optional[Message]

    # reply to correct message
    reply_text = msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text

    # get user who sent message
    if msg.from_user.username:
        curr_user = "@" + escape_markdown(msg.from_user.username)
    else:
        curr_user = "[{}](tg://user?id={})".format(msg.from_user.first_name, msg.from_user.id)

    user_id = extract_user(update.effective_message, args)
    if user_id == bot.id or user_id == 777000:
        user1 = "[{}](tg://user?id={})".format(bot.first_name, bot.id)
        user2 = curr_user
    elif user_id:
        slapped_user = bot.get_chat(user_id)
        user1 = curr_user
        if slapped_user.username:
            user2 = "@" + escape_markdown(slapped_user.username)
        else:
            user2 = "[{}](tg://user?id={})".format(slapped_user.first_name,
                                                   slapped_user.id)

    # if no target found, bot targets the sender
    else:
        user1 = "[{}](tg://user?id={})".format(bot.first_name, bot.id)
        user2 = curr_user

    temp = random.choice(PUNCH_TEMPLATES)
    punch = random.choice(PUNCH)

    repl = temp.format(user1=user1, user2=user2, punches = punch)

    reply_text(repl, parse_mode=ParseMode.MARKDOWN)

@run_async
def get_id(bot: Bot, update: Update, args: List[str]):
    user_id = extract_user(update.effective_message, args)
    if user_id:
        if update.effective_message.reply_to_message and update.effective_message.reply_to_message.forward_from:
            user1 = update.effective_message.reply_to_message.from_user
            user2 = update.effective_message.reply_to_message.forward_from
            update.effective_message.reply_text(
                "The original sender, {}, has an ID of `{}`.\nThe forwarder, {}, has an ID of `{}`.".format(
                    escape_markdown(user2.first_name),
                    user2.id,
                    escape_markdown(user1.first_name),
                    user1.id),
                parse_mode=ParseMode.MARKDOWN)
        else:
            user = bot.get_chat(user_id)
            update.effective_message.reply_text("{}'s id is `{}`.".format(escape_markdown(user.first_name), user.id),
                                                parse_mode=ParseMode.MARKDOWN)
    else:
        chat = update.effective_chat  # type: Optional[Chat]
        if chat.type == "private":
            update.effective_message.reply_text("Your id is `{}`.".format(chat.id),
                                                parse_mode=ParseMode.MARKDOWN)

        else:
            update.effective_message.reply_text("This group's id is `{}`.".format(chat.id),
                                                parse_mode=ParseMode.MARKDOWN)

@run_async
def info(bot: Bot, update: Update, args: List[str]):
    msg = update.effective_message  # type: Optional[Message]
    user_id = extract_user(update.effective_message, args)

    if user_id and int(user_id) != 777000:
        user = bot.get_chat(user_id)
    
    elif user_id and int(user_id) == 777000:
        msg.reply_text("This is Telegram. Unless you manually entered this reserved account's ID, it is likely a broadcast from a linked channel.")
        return
      
    elif not msg.reply_to_message and not args:
        user = msg.from_user

    elif not msg.reply_to_message and (not args or (
            len(args) >= 1 and not args[0].startswith("@") and not args[0].isdigit() and not msg.parse_entities(
        [MessageEntity.TEXT_MENTION]))):
        msg.reply_text("I can't extract a user from this.")
        return
    else:
        return

    text = "<b>User info</b>:" \
           "\nID: <code>{}</code>" \
           "\nFirst Name: {}".format(user.id, html.escape(user.first_name))

    if user.last_name:
        text += "\nLast Name: {}".format(html.escape(user.last_name))

    if user.username:
        text += "\nUsername: @{}".format(html.escape(user.username))

    text += "\nPermanent user link: {}".format(mention_html(user.id, "link"))

    if user.id == OWNER_ID:
        text += "\n\nThis person is my owner - I would never do anything against them!"
    else:
        if user.id in SUDO_USERS:
            text += "\nThis person is one of my sudo users! " \
                    "Nearly as powerful as my owner - so watch it."
        else:
            if user.id in SUPPORT_USERS:
                text += "\nThis person is one of my support users! " \
                        "Not quite a sudo user, but can still gban you off the map."

            if user.id in WHITELIST_USERS:
                text += "\nThis person has been whitelisted! " \
                        "That means I'm not allowed to ban/kick them."

    for mod in USER_INFO:
        mod_info = mod.__user_info__(user.id).strip()
        if mod_info:
            text += "\n\n" + mod_info

    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

@run_async
def get_time(bot: Bot, update: Update, args: List[str]):
    location = " ".join(args)
    if location.lower() == bot.first_name.lower():
        update.effective_message.reply_text("Its always banhammer time for me!")
        bot.send_sticker(update.effective_chat.id, BAN_STICKER)
        return

    res = requests.get(GMAPS_LOC, params=dict(address=location))

    if res.status_code == 200:
        loc = json.loads(res.text)
        if loc.get('status') == 'OK':
            lat = loc['results'][0]['geometry']['location']['lat']
            long = loc['results'][0]['geometry']['location']['lng']

            country = None
            city = None

            address_parts = loc['results'][0]['address_components']
            for part in address_parts:
                if 'country' in part['types']:
                    country = part.get('long_name')
                if 'administrative_area_level_1' in part['types'] and not city:
                    city = part.get('long_name')
                if 'locality' in part['types']:
                    city = part.get('long_name')

            if city and country:
                location = "{}, {}".format(city, country)
            elif country:
                location = country

            timenow = int(datetime.utcnow().timestamp())
            res = requests.get(GMAPS_TIME, params=dict(location="{},{}".format(lat, long), timestamp=timenow))
            if res.status_code == 200:
                offset = json.loads(res.text)['dstOffset']
                timestamp = json.loads(res.text)['rawOffset']
                time_there = datetime.fromtimestamp(timenow + timestamp + offset).strftime("%H:%M:%S on %A %d %B")
                update.message.reply_text("It's {} in {}".format(time_there, location))

@run_async
def echo(bot: Bot, update: Update):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message
    if message.reply_to_message:
        message.reply_to_message.reply_text(args[1])
    else:
        message.reply_text(args[1], quote=False)
    message.delete()
         
MARKDOWN_HELP = """
Markdown is a very powerful formatting tool supported by telegram. {} has some enhancements, to make sure that \
saved messages are correctly parsed, and to allow you to create buttons.
- <code>_italic_</code>: wrapping text with '_' will produce italic text
- <code>*bold*</code>: wrapping text with '*' will produce bold text
- <code>`code`</code>: wrapping text with '`' will produce monospaced text, also known as 'code'
- <code>[sometext](someURL)</code>: this will create a link - the message will just show <code>sometext</code>, \
and tapping on it will open the page at <code>someURL</code>.
EG: <code>[test](example.com)</code>
- <code>[buttontext](buttonurl:someURL)</code>: this is a special enhancement to allow users to have telegram \
buttons in their markdown. <code>buttontext</code> will be what is displayed on the button, and <code>someurl</code> \
will be the url which is opened.
EG: <code>[This is a button](buttonurl:example.com)</code>
If you want multiple buttons on the same line, use :same, as such:
<code>[one](buttonurl://example.com)
[two](buttonurl://google.com:same)</code>
This will create two buttons on a single line, instead of one button per line.
Keep in mind that your message <b>MUST</b> contain some text other than just a button!
""".format(dispatcher.bot.first_name)


@run_async
def markdown_help(bot: Bot, update: Update):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text("Try forwarding the following message to me, and you'll see!")
    update.effective_message.reply_text("/save test This is a markdown test. _italics_, *bold*, `code`, "
                                        "[URL](example.com) [button](buttonurl:github.com) "
                                        "[button2](buttonurl://google.com:same)")


@run_async
def stats(bot: Bot, update: Update):
	update.effective_message.reply_text("*Current stats:*\n" + "\n".join([mod.__stats__() for mod in STATS]),
                                                parse_mode=ParseMode.MARKDOWN)



def gps(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message
    if len(args) == 0:
        update.effective_message.reply_text("That was a funny joke, but no really, put in a location")
    try:
        geolocator = Nominatim(user_agent="hades")
        location = " ".join(args)
        geoloc = geolocator.geocode(location)  
        chat_id = update.effective_chat.id
        lon = geoloc.longitude
        lat = geoloc.latitude
        the_loc = Location(lon, lat) 
        gm = "https://www.google.com/maps/search/{},{}".format(lat,lon)
        bot.send_location(chat_id, location=the_loc)
        update.message.reply_text("Open with: [Google Maps]({})".format(gm), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    except AttributeError:
        update.message.reply_text("I can't find that")
        
@run_async
def getlink(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = int(args[0])
    else:
        update.effective_message.reply_text("You don't seem to be referring to a chat")
    for chat_id in args:
        try:
            chat = bot.getChat(chat_id)
            bot_member = chat.get_member(bot.id)
            if bot_member.can_invite_users:
                invitelink = bot.exportChatInviteLink(chat_id)
                update.effective_message.reply_text("Invite link for: " + chat_id + "\n" + invitelink)
            else:
                update.effective_message.reply_text("I don't have access to the invite link.")
        except BadRequest as excp:
                update.effective_message.reply_text(excp.message + " " + str(chat_id))
        except TelegramError as excp:
                update.effective_message.reply_text(excp.message + " " + str(chat_id))

@run_async
def slist(bot: Bot, update: Update):
    message = update.effective_message
    text1 = "My sudo users are:"
    text2 = "My support users are:"
    for user_id in SUDO_USERS:
        try:
            user = bot.get_chat(user_id)
            name = "[{}](tg://user?id={})".format(user.first_name + (user.last_name or ""), user.id)
            if user.username:
                name = escape_markdown("@" + user.username)
            text1 += "\n - {}".format(name)
        except BadRequest as excp:
            if excp.message == 'Chat not found':
                text1 += "\n - ({}) - not found".format(user_id)
    for user_id in SUPPORT_USERS:
        try:
            user = bot.get_chat(user_id)
            name = "[{}](tg://user?id={})".format(user.first_name + (user.last_name or ""), user.id)
            if user.username:
                name = escape_markdown("@" + user.username)
            text2 += "\n - {}".format(name)
        except BadRequest as excp:
            if excp.message == 'Chat not found':
                text2 += "\n - ({}) - not found".format(user_id)
    message.reply_text(text1 + "\n", parse_mode=ParseMode.MARKDOWN)
    message.reply_text(text2 + "\n", parse_mode=ParseMode.MARKDOWN)
    
# /ip is for private use
__help__ = """
Some random modules (extras).

*Owner Only*
 - /getlink <group id>: Gets invite link for a specific chat.
 - /supromote <id>: Promote user to sudo.
 - /sudemote <id>: Demote sudo user.
 
 *Sudo users*
 - /sulist : Gets sudo users list.
 
 *Avaliable commands*
 - /id: get the current group id. If used by replying to a message, gets that user's id.
 - /runs: reply a random string from an array of replies.
 - /spank: same as /slap but nastier.
 - /slap: slap a user, or get slapped if not a reply.
 - /insult : replay a random insult string.
 - /birthday <username> : spam user with birthday messages.
 - /info: get information about a user. 
 - /markdownhelp: quick summary of how markdown works in telegram - can only be called in private chats.
"""

__mod_name__ = "Misc"

ID_HANDLER = DisableAbleCommandHandler("id", get_id, pass_args=True)

TIME_HANDLER = CommandHandler("time", get_time, pass_args=True)

RUNS_HANDLER = DisableAbleCommandHandler("runs", runs)
INST_HANDLER = DisableAbleCommandHandler("insult", insult)
HBD_HANDLER = DisableAbleCommandHandler("birthday", birthday, pass_args=True, filters=Filters.group)
SMACK_HANDLER = DisableAbleCommandHandler("smack", smack)
SLAP_HANDLER = DisableAbleCommandHandler("slap", slap, pass_args=True)
PUNCH_HANDLER = DisableAbleCommandHandler("punch", punch, pass_args=True)
SPANK_HANDLER = DisableAbleCommandHandler("spank", slap, pass_args=True)
INFO_HANDLER = DisableAbleCommandHandler("info", info, pass_args=True)
ECHO_HANDLER = CommandHandler("echo", echo, filters=Filters.user(OWNER_ID))
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, filters=Filters.private)
GETLINK_HANDLER = CommandHandler("getlink", getlink, pass_args=True, filters=Filters.user(OWNER_ID))
SLIST_HANDLER = CommandHandler("sulist", slist, filters=CustomFilters.sudo_filter)


STATS_HANDLER = CommandHandler("stats", stats, filters=CustomFilters.sudo_filter)
GPS_HANDLER = DisableAbleCommandHandler("gps", gps, pass_args=True)

dispatcher.add_handler(ID_HANDLER)
# dispatcher.add_handler(TIME_HANDLER)
dispatcher.add_handler(RUNS_HANDLER)
dispatcher.add_handler(SMACK_HANDLER)
dispatcher.add_handler(SLAP_HANDLER)
dispatcher.add_handler(PUNCH_HANDLER)
dispatcher.add_handler(SPANK_HANDLER)
dispatcher.add_handler(INFO_HANDLER)
dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(STATS_HANDLER)
dispatcher.add_handler(GPS_HANDLER)
dispatcher.add_handler(INST_HANDLER)
dispatcher.add_handler(HBD_HANDLER)
dispatcher.add_handler(GETLINK_HANDLER)
dispatcher.add_handler(SLIST_HANDLER)
