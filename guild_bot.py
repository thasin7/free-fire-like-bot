import threading
import jwt
import random
import json
import requests
import google.protobuf
from datetime import datetime, date
import base64
import logging
import re
import socket
import os
import binascii
import sys
import psutil
import time
from important_zitado import *
from time import sleep
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.json_format import MessageToJson
from protobuf_decoder.protobuf_decoder import Parser
from threading import Thread
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import httpx
import urllib3
import MajorLoginRes_pb2
import jwt_generator_pb2

# Load bot configuration dynamically
def load_bot_config():
    """Load bot configuration from command line argument or default file"""
    # Auto-detect config file based on script name
    script_name = os.path.basename(__file__)  # e.g., "bot_1_guild_bot.py"
    if "_guild_bot.py" in script_name:
        bot_name = script_name.replace("_guild_bot.py", "")  # e.g., "bot_1"
        config_file = f"{bot_name}.txt"  # e.g., "bot_1.txt"
    else:
        config_file = "guild_bot.txt"  # Default fallback
    
    # Check if config file is passed as command line argument
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    print(f"Loading config from: {config_file}")
    
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            return config_data
    except FileNotFoundError:
        print(f"Config file {config_file} not found!")
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in {config_file}")
        return {}

# Load bot-specific data from account.json
def load_bot_data_from_account():
    """Load bot data from account.json based on config file name"""
    try:
        # Auto-detect config file based on script name
        script_name = os.path.basename(__file__)  # e.g., "bot_1_guild_bot.py"
        if "_guild_bot.py" in script_name:
            bot_name = script_name.replace("_guild_bot.py", "")  # e.g., "bot_1"
            config_file = f"{bot_name}.txt"  # e.g., "bot_1.txt"
        else:
            config_file = "guild_bot.txt"  # Default fallback
        
        # Check if config file is passed as command line argument
        if len(sys.argv) > 1:
            config_file = sys.argv[1]
        
        # Extract bot name from config file name (e.g., "bot_1.txt" -> "bot_1")
        bot_name = config_file.replace('.txt', '')
        
        with open('account.json', 'r') as f:
            account_data = json.load(f)
            
        # Find the bot data for this specific bot
        for bot in account_data.get('bots', []):
            if bot['bot_name'] == bot_name:
                return bot
                
        print(f"Bot data not found for {bot_name}")
        return {}
    except Exception as e:
        print(f"Error loading bot data: {e}")
        return {}

# Load configuration
BOT_CONFIG = load_bot_config()
BOT_DATA = load_bot_data_from_account()

# Set bot-specific values
BOT_UID = BOT_DATA.get('uid')  # Default fallback
BOT_CLAN_ID = BOT_DATA.get('clan_id')  # Default fallback  
BOT_CLAN_KEY = BOT_DATA.get('clan_key')  # Default fallback

# Global variables to store dynamically loaded clan data
DYNAMIC_CLAN_ID = None
DYNAMIC_CLAN_KEY = None

print(f"Bot loaded with UID: {BOT_UID}, Initial Clan ID: {BOT_CLAN_ID}")

def extract_clan_data_from_response(response_data):
    """Extract clan ID and clan key from server response"""
    global DYNAMIC_CLAN_ID, DYNAMIC_CLAN_KEY
    
    try:
        json_result = get_available_room(response_data)
        parsed_data = json.loads(json_result)
        
        # Extract clan ID from field 20
        if "20" in parsed_data and "data" in parsed_data["20"]:
            DYNAMIC_CLAN_ID = str(parsed_data["20"]["data"])
            print(f"Loaded dynamic clan ID: {DYNAMIC_CLAN_ID}")
        
        # Extract clan key from field 55
        if "55" in parsed_data and "data" in parsed_data["55"]:
            DYNAMIC_CLAN_KEY = parsed_data["55"]["data"]
            print(f"Loaded dynamic clan key: {DYNAMIC_CLAN_KEY}")
            
        return DYNAMIC_CLAN_ID, DYNAMIC_CLAN_KEY
        
    except Exception as e:
        print(f"Error extracting clan data: {e}")
        return None, None

def get_current_clan_id():
    """Get current clan ID (dynamic if available, otherwise fallback)"""
    return DYNAMIC_CLAN_ID if DYNAMIC_CLAN_ID else BOT_CLAN_ID

def get_current_clan_key():
    """Get current clan key (dynamic if available, otherwise fallback)"""
    return DYNAMIC_CLAN_KEY if DYNAMIC_CLAN_KEY else BOT_CLAN_KEY


LIKE_LIMIT_FILE = 'like_limits.json'
DAILY_LIKE_LIMIT = 5

OWNER_UID = '6500846368' 
like_limit_lock = threading.Lock()


tempid = None
sent_inv = False
start_par = False
pleaseaccept = False
nameinv = "none"
idinv = 0
senthi = False
statusinfo = False
tempdata1 = None
tempdata = None
leaveee = False
leaveee1 = False
data22 = None
isroom = False
isroom2 = False
paylod_token1 = "3a07312e3131342e32aa01026172b201203535656437353966636639346638353831336535376232656338343932663563ba010134ea0140366662376664656638363538666430333137346564353531653832623731623231646238313837666130363132633865616631623633616136383766316561659a060134a2060134ca03203734323862323533646566633136343031386336303461316562626665626466"
freefire_version = "ob50"
client_secret = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
chat_ip = "202.81.106.78"
chat_port = 39698
keys = "jifat" # this is a temp key 

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# --- NEW: Function to manage daily like limits ---
def check_and_update_like_limit(user_uid):

    if str(user_uid) == OWNER_UID:
        return True  # Owner has no limits

    today_str = str(date.today())
    
    with like_limit_lock:
        try:
            with open(LIKE_LIMIT_FILE, 'r') as f:
                limits_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            limits_data = {}

   
        if today_str not in limits_data:
            limits_data = {today_str: {}}

       
        requests_made = limits_data[today_str].get(str(user_uid), 0)

        if requests_made < DAILY_LIKE_LIMIT:
           
            limits_data[today_str][str(user_uid)] = requests_made + 1
            with open(LIKE_LIMIT_FILE, 'w') as f:
                json.dump(limits_data, f, indent=4)
            return True
        else:
           
            return False
# --- END NEW ---

def encrypt_packet(plain_text, key, iv):
    plain_text = bytes.fromhex(plain_text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()
    
def gethashteam(hexxx):
    a = zitado_get_proto(hexxx)
    if not a:
        raise ValueError("Invalid hex format or empty response from zitado_get_proto")
    data = json.loads(a)
    return data['5']['7']
def getownteam(hexxx):
    a = zitado_get_proto(hexxx)
    if not a:
        raise ValueError("Invalid hex format or empty response from zitado_get_proto")
    data = json.loads(a)
    return data['5']['1']

def get_player_status(packet):
    json_result = get_available_room(packet)
    parsed_data = json.loads(json_result)

    if "5" not in parsed_data or "data" not in parsed_data["5"]:
        return "OFFLINE"

    json_data = parsed_data["5"]["data"]

    if "1" not in json_data or "data" not in json_data["1"]:
        return "OFFLINE"

    data = json_data["1"]["data"]

    if "3" not in data:
        return "OFFLINE"

    status_data = data["3"]

    if "data" not in status_data:
        return "OFFLINE"

    status = status_data["data"]

    if status == 1:
        return "SOLO"
    
    if status == 2:
        if "9" in data and "data" in data["9"]:
            group_count = data["9"]["data"]
            countmax1 = data["10"]["data"]
            countmax = countmax1 + 1
            return f"INSQUAD ({group_count}/{countmax})"

        return "INSQUAD"
    
    if status in [3, 5]:
        return "INGAME"
    if status == 4:
        return "IN ROOM"
    
    if status in [6, 7]:
        return "IN SOCIAL ISLAND MODE .."

    return "NOTFOUND"
def get_idroom_by_idplayer(packet):
    json_result = get_available_room(packet)
    parsed_data = json.loads(json_result)
    json_data = parsed_data["5"]["data"]
    data = json_data["1"]["data"]
    idroom = data['15']["data"]
    return idroom
def get_leader(packet):
    json_result = get_available_room(packet)
    parsed_data = json.loads(json_result)
    json_data = parsed_data["5"]["data"]
    data = json_data["1"]["data"]
    leader = data['8']["data"]
    return leader
def fix_num(num):
    fixed = ""
    count = 0
    num_str = str(num)

    for char in num_str:
        if char.isdigit():
            count += 1
        fixed += char
        if count == 3:
            fixed += "[c]"
            count = 0  
    return fixed


def fix_word(num):
    fixed = ""
    count = 0
    
    for char in num:
        if char:
            count += 1
        fixed += char
        if count == 3:
            fixed += "[c]"
            count = 0  
    return fixed
def rrrrrrrrrrrrrr(number):
    if isinstance(number, str) and '***' in number:
        return number.replace('***', '106')
    return number
####################################

#Clan-info-by-clan-id
def Get_clan_info(clan_id):
    try:
        url = f"https://get-clan-info.vercel.app/get_clan_info?clan_id={clan_id}"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            msg = f""" 
[11EAFD][b][c]
°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
▶▶▶▶GUILD DETAILS◀◀◀◀
Achievements: {data['achievements']}\n\n
Balance : {fix_num(data['balance'])}\n\n
Clan Name : {data['clan_name']}\n\n
Expire Time : {fix_num(data['guild_details']['expire_time'])}\n\n
Members Online : {fix_num(data['guild_details']['members_online'])}\n\n
Regional : {data['guild_details']['regional']}\n\n
Reward Time : {fix_num(data['guild_details']['reward_time'])}\n\n
Total Members : {fix_num(data['guild_details']['total_members'])}\n\n
ID : {fix_num(data['id'])}\n\n
Last Active : {fix_num(data['last_active'])}\n\n
Level : {fix_num(data['level'])}\n\n
Rank : {fix_num(data['rank'])}\n\n
Region : {data['region']}\n\n
Score : {fix_num(data['score'])}\n\n
Timestamp1 : {fix_num(data['timestamp1'])}\n\n
Timestamp2 : {fix_num(data['timestamp2'])}\n\n
Welcome Message: {data['welcome_message']}\n\n
XP: {fix_num(data['xp'])}\n\n
°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
[FFB300][b][c]BOT MADE BY PRO BOT BY RIFAT
            """
            return msg
        else:
            msg = """
[11EAFD][b][c]
°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
Failed to get info, please try again later!!

°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
[FFB300][b][c]BOT MADE BY PRO BOT BY RIFAT
            """
            return msg
    except:
        pass
#GET INFO BY PLAYER ID
def get_player_info(player_id):
    url = f"https://like2.vercel.app/player-info?uid={uid}&server=BD&key={keys}"
    response = requests.get(url)    
    if response.status_code == 200:
        try:
            r = response.json()
            return {
                "Account Booyah Pass": f"{r.get('booyah_pass_level', 'N/A')}",
                "Account Create": f"{r.get('createAt', 'N/A')}",
                "Account Level": f"{r.get('level', 'N/A')}",
                "Account Likes": f" {r.get('likes', 'N/A')}",
                "Name": f"{r.get('nickname', 'N/A')}",
                "UID": f" {r.get('accountId', 'N/A')}",
                "Account Region": f"{r.get('region', 'N/A')}",
                }
        except ValueError as e:
            pass
            return {
                "error": "Invalid JSON response"
            }
    else:
        pass
        return {
            "error": f"Failed to fetch data: {response.status_code}"
        }
#CHAT WITH AI
def talk_with_ai(question):
    url = f"https://gemini-api-api-v2.vercel.app/prince/api/v1/ask?key=prince&ask={question}" # use you gemini api
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        msg = data["message"]["content"]
        return msg
    else:
        return "An error occurred while connecting to the server."
#SPAM REQUESTS
def spam_requests(player_id):
    # This URL now correctly points to the Flask app you provided
    url = f"https://like2.vercel.app/send_requests?uid={player_id}&key={keys}&server=BD"
    try:
        res = requests.get(url, timeout=20) # Added a timeout
        if res.status_code == 200:
            data = res.json()
            # Return a more descriptive message based on the API's JSON response
            return f"API Status: Success [{data.get('success_count', 0)}] Failed [{data.get('failed_count', 0)}]"
        else:
            # Return the error status from the API
            return f"API Error: Status {res.status_code}"
    except requests.exceptions.RequestException as e:
        # Handle cases where the API isn't running or is unreachable
        print(f"Could not connect to spam API: {e}")
        return "Failed to connect to spam API."
####################################

# ** NEW INFO FUNCTION using the new API **
def newinfo(uid):
    # Base URL without parameters
    url = "https://like2.vercel.app/player-info"
    # Parameters dictionary - this is the robust way to do it
    params = {
        'uid': uid,
        'server': 'bd', # Hardcoded to bd as requested
        'key': keys, 
    }
    try:
        # Pass the parameters to requests.get()
        response = requests.get(url, params=params, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            # Check if the expected data structure is in the response
            if "basicInfo" in data:
                return {"status": "ok", "data": data}
            else:
                # The API returned 200, but the data is not what we expect (e.g., error message in JSON)
                return {"status": "error", "message": data.get("error", "Invalid ID or data not found.")}
        else:
            # The API returned an error status code (e.g., 404, 500)
            try:
                # Try to get a specific error message from the API's response
                error_msg = response.json().get('error', f"API returned status {response.status_code}")
                return {"status": "error", "message": error_msg}
            except ValueError:
                # If the error response is not JSON
                return {"status": "error", "message": f"API returned status {response.status_code}"}

    except requests.exceptions.RequestException as e:
        # Handle network errors (e.g., timeout, no connection)
        return {"status": "error", "message": f"Network error: {str(e)}"}
    except ValueError: 
        # Handle cases where the response is not valid JSON
        return {"status": "error", "message": "Invalid JSON response from API."}

	
#ADDING-100-LIKES-IN-24H
import requests

def send_likes(uid):
    try:
        likes_api_response = requests.get(
            f"https://like2.vercel.app/like?uid={uid}&server=bd&key={keys}",
            timeout=30
        )

        if likes_api_response.status_code == 200:
            api_json_response = likes_api_response.json()

            player_name = api_json_response.get('player', 'Unknown')
            likes_before = api_json_response.get('likes_before', 0)
            likes_after = api_json_response.get('likes_after', 0)
            likes_added = api_json_response.get('likes_added', 0)
            status = api_json_response.get('status', 0)

            if likes_added > 0 and likes_after > likes_before:
                return f"""
[C][B][11EAFD]‎━━━━━━━━━━━━
[FFFFFF]Likes Status:

[00FF00]Likes Sent Successfully!

[FFFFFF]Player Name : [00FF00]{player_name}  
[FFFFFF]Likes Added : [00FF00]{likes_added}  
[FFFFFF]Likes Before : [00FF00]{likes_before}  
[FFFFFF]Likes After : [00FF00]{likes_after}  
[C][B][11EAFD]‎━━━━━━━━━━━━
[C][B][FFB300]Credits: [FFFFFF]FALCON X64[00FF00] RIFAT!!
                """
            elif likes_before == likes_after:
                return f"""
[C][B][FF0000]━━━━━━━━━━━━

[FFFFFF]No Likes Sent!

[FF0000]You have already taken likes with this UID.
Try again after 24 hours.

[FFFFFF]Player Name : [FF0000]{player_name}  
[FFFFFF]Likes Before : [FF0000]{likes_before}  
[FFFFFF]Likes After : [FF0000]{likes_after}  
[C][B][FF0000]━━━━━━━━━━━━
"""
            else:
                return f"""
[C][B][FF0000]━━━━━━━━━━━━
[FFFFFF]Unexpected Response!
Something went wrong.

Please try again or contact support.
━━━━━━━━━━━━
"""
        else:
            return f"""
[C][B][FF0000]━━━━━
[FFFFFF]Like API Error!
Status Code: {likes_api_response.status_code}
Please check if the API is running correctly.
━━━━━
"""

    except requests.exceptions.RequestException:
        return """
[C][B][FF0000]━━━━━
[FFFFFF]Like API Connection Failed!
Is the API server (app.py) running?
━━━━━
"""
    except Exception as e:
        return f"""
[C][B][FF0000]━━━━━
[FFFFFF]An unexpected error occurred:
[FF0000]{str(e)}
━━━━━
"""
####################################
#CHECK ACCOUNT IS BANNED
def check_banned_status(player_id):
    url = f"https://checkban-vf40.onrender.com/ban?uid={player_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 200 and data.get('msg') == 'id_found':
                is_banned = data.get('data', {}).get('is_banned', '0')
                nickname = data.get('data', {}).get('nickname', 'N/A')
                return {
                    'status': 'BANNED' if is_banned == '1' else 'NOT BANNED',
                    'data.nickname': nickname
                }
            return {"error": "Player not found or invalid response"}
        else:
            return {"error": f"Failed to fetch data. Status code: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
####################################
def Encrypt(number):
    try:
        number = int(number)
        encoded_bytes = []
        while True:
            byte = number & 0x7F
            number >>= 7
            if number:
                byte |= 0x80
            encoded_bytes.append(byte)
            if not number:
                break
        return bytes(encoded_bytes).hex()
    except:
        restart_program()
#############CLASS RANDOM###########
def  generate_random_word():
    word_list = [
        "XNXXX", "ZBI", "PRO BOT BY RIFAT", "NIKMOK",
        "PUSSY", "FUCK YOU", "fuke_any_team", "FUCK_YOUR_MOM", "PORNO",
        "FUCK YOUR MOTHER", "FUCK_YOUR_SISTER", "MOROCCO", "kissss omkk", "YOUR_MOM_PINK_PUSSY",
        "WAAA DAK W9", "ZAMLLL", "YANA9CH", "9WAD", "YOUR_ASS_IS_BIG",
        "PUSSY", "I_FUCK_YOU", "SIT_DOWN_PIMP", "AHHH", "DIMA RAJA",
        "FAILED_STREAMER", "PRO BOT BY RIFAT", "GAY", "YOUR_ASS_IS_PINK", "YOUR_PUSSY_IS_BEAUTIFUL",
        "HAHAHAHAHAHA", "YOUR_PUSSY_IS_PINK", "I_WILL_FUCK_YOU", "EAT_IT_PIMP", "HEY_BITCH",
        "MY_DICK", "STRONG_PUSSY", "PUSSY", "GO_FUCK_YOURSELF", "LOSER",
        "HEY_WHORE", "MY_BITCH", "PUSSY", "FUCK_YOU_UP", "YOUR_PUSSY",
        "LOSER", "FUCK_YOU", "FUCK_YOUR_MOM_SLANG", "FUCK_YOUR_MOM_SLANG2", "I_WILL_JERK_OFF_ON_YOU", "LICKER", " PRO BOT BY RIFAT", "TELEGRAM:@S_DD_F"
    ]

    return random.choice(word_list)
def generate_random_color():
	color_list = [
    "[00FF00][b][c]",
    "[FFDD00][b][c]",
    "[3813F3][b][c]",
    "[FF0000][b][c]",
    "[0000FF][b][c]",
    "[FFA500][b][c]",
    "[DF07F8][b][c]",
    "[11EAFD][b][c]",
    "[DCE775][b][c]",
    "[A8E6CF][b][c]",
    "[7CB342][b][c]",
    "[FF0000][b][c]",
    "[FFB300][b][c]",
    "[90EE90][b][c]",
    "[FF4500][b][c]",
    "[FFD700][b][c]",
    "[32CD32][b][c]",
    "[87CEEB][b][c]",
    "[9370DB][b][c]",
    "[FF69B4][b][c]",
    "[8A2BE2][b][c]",
    "[00BFFF][b][c]",
    "[1E90FF][b][c]",
    "[20B2AA][b][c]",
    "[00FA9A][b][c]",
    "[008000][b][c]",
    "[FFFF00][b][c]",
    "[FF8C00][b][c]",
    "[DC143C][b][c]",
    "[FF6347][b][c]",
    "[FFA07A][b][c]",
    "[FFDAB9][b][c]",
    "[CD853F][b][c]",
    "[D2691E][b][c]",
    "[BC8F8F][b][c]",
    "[F0E68C][b][c]",
    "[556B2F][b][c]",
    "[808000][b][c]",
    "[4682B4][b][c]",
    "[6A5ACD][b][c]",
    "[7B68EE][b][c]",
    "[8B4513][b][c]",
    "[C71585][b][c]",
    "[4B0082][b][c]",
    "[B22222][b][c]",
    "[228B22][b][c]",
    "[8B008B][b][c]",
    "[483D8B][b][c]",
    "[556B2F][b][c]",
    "[800000][b][c]",
    "[008080][b][c]",
    "[000080][b][c]",
    "[800080][b][c]",
    "[808080][b][c]",
    "[A9A9A9][b][c]",
    "[D3D3D3][b][c]",
    "[F0F0F0][b][c]"
]
	random_color = random.choice(color_list)
	return  random_color
def get_random_avatar():
    avatar_list = [
        '902000061', '902000060', '902000064', '902000065', '902000066', 
        '902000074', '902000075', '902000077', '902000078', '902000084', 
        '902000085', '902000087', '902000091', '902000094', '902000306','902000091','902000208','902000209','902000210','902000211','902047016','902047016','902000347'
    ]
    return random.choice(avatar_list)
def rrrrrrrrrrrrrr(number):
    if isinstance(number, str) and '***' in number:
        return number.replace('***', '106')
    return number
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class FF_CLIENT(threading.Thread):
    def __init__(self, id, password):
        self.id = id
        self.password = password
        self.key = None
        self.iv = None
        self.get_tok()
    def connect(self, tok, host, port, packet, key, iv):
        global clients
        clients = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = int(port)
        clients.connect((host, port))
        clients.send(bytes.fromhex(tok))

        while True:
            data = clients.recv(9999)
            if data == b"":
                print("Connection closed by remote host")
                restart_program()
                break           
#GET AVAILABLE ROOM
def get_available_room(input_text):
    try:
        parsed_results = Parser().parse(input_text)
        parsed_results_objects = parsed_results
        parsed_results_dict = parse_results(parsed_results_objects)
        json_data = json.dumps(parsed_results_dict)
        return json_data
    except Exception as e:
        print(f"error {e}")
        return None
#PARSE RESULTS
def parse_results(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {}
        field_data["wire_type"] = result.wire_type
        if result.wire_type == "varint":
            field_data["data"] = result.data
        if result.wire_type == "string":
            field_data["data"] = result.data
        if result.wire_type == "bytes":
            field_data["data"] = result.data
        elif result.wire_type == "length_delimited":
            field_data["data"] = parse_results(result.data.results)
        result_dict[result.field] = field_data
    return result_dict
#DECODE TO HEX
def dec_to_hex(ask):
    ask_result = hex(ask)
    final_result = str(ask_result)[2:]
    if len(final_result) == 1:
        final_result = "0" + final_result
    return final_result
#ENCODE MESSAGE
def encrypt_message(plaintext):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(plaintext, AES.block_size)
    encrypted_message = cipher.encrypt(padded_message)
    return binascii.hexlify(encrypted_message).decode('utf-8')
#ENCODE API
def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()
####################################
def extract_jwt_from_hex(hex):
    byte_data = binascii.unhexlify(hex)
    message = jwt_generator_pb2.Garena_420()
    message.ParseFromString(byte_data)
    json_output = MessageToJson(message)
    token_data = json.loads(json_output)
    return token_data
def format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
####################################
def restart_program():
    try:
        p = psutil.Process(os.getpid())
        # Try to close open files, but don't fail if we can't get them
        try:
            open_files = p.open_files()
            for handler in open_files:
                try:
                    os.close(handler.fd)
                except (OSError, AttributeError):
                    pass
        except (RuntimeError, psutil.AccessDenied, psutil.NoSuchProcess):
            pass  # Skip if we can't get open files or process is gone
            
        # Try to close network connections
        try:
            connections = p.connections()
            for conn in connections:
                try:
                    if hasattr(conn, 'close'):
                        conn.close()
                except Exception:
                    pass
        except (RuntimeError, psutil.AccessDenied, psutil.NoSuchProcess):
            pass  # Skip if we can't get connections or process is gone
            
    except Exception as e:
        print(f"Error during cleanup: {e}")
    
    # Restart the script
    python = sys.executable
    os.execl(python, python, *sys.argv)
    python = sys.executable
    os.execl(python, python, *sys.argv)
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class FF_CLIENT(threading.Thread):
    def __init__(self, id, password):
        super().__init__()
        self.id = id
        self.password = password
        self.key = None
        self.iv = None
        self.get_tok()

    def parse_my_message(self, serialized_data):
        try:
            MajorLogRes = MajorLoginRes_pb2.MajorLoginRes()
            MajorLogRes.ParseFromString(serialized_data)
            key = MajorLogRes.ak
            iv = MajorLogRes.aiv
            if isinstance(key, bytes):
                key = key.hex()
            if isinstance(iv, bytes):
                iv = iv.hex()
            self.key = key
            self.iv = iv
            print(f"Key: {self.key} | IV: {self.iv}")
            return self.key, self.iv
        except Exception as e:
            print(f"{e}")
            return None, None

    def nmnmmmmn(self, data):
        key, iv = self.key, self.iv
        try:
            key = key if isinstance(key, bytes) else bytes.fromhex(key)
            iv = iv if isinstance(iv, bytes) else bytes.fromhex(iv)
            data = bytes.fromhex(data)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            cipher_text = cipher.encrypt(pad(data, AES.block_size))
            return cipher_text.hex()
        except Exception as e:
            print(f"Error in nmnmmmmn: {e}")

    def spam_room(self, idroom, idplayer):
        fields = {
        1: 78,
        2: {
            1: int(idroom),
            2: f"{generate_random_color()}{generate_random_word()}",
            4: 330,
            5: 6000,
            6: 201,
            10: int(get_random_avatar()),
            11: int(idplayer),
            12: 1
        }
        }
        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0E15000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "0E1500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "0E150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0E15000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def send_squad(self, idplayer):
        fields = {
            1: 33,
            2: {
                1: int(idplayer),
                2: "bd",
                3: 1,
                4: 1,
                7: 330,
                8: 19459,
                9: 100,
                12: 1,
                16: 1,
                17: {
                2: 94,
                6: 11,
                8: "1.109.5",
                9: 3,
                10: 2
                },
                18: 201,
                23: {
                2: 1,
                3: 1
                },
                24: int(get_random_avatar()),
                26: {},
                28: {}
            }
        }
        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def start_autooo(self):
        fields = {
        1: 9,
        2: {
            1: 10853443433
        }
        }
        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def invite_skwad(self, idplayer):
        fields = {
        1: 2,
        2: {
            1: int(idplayer),
            10: int(get_random_avatar()),
            2: "bd",
            4: 1
        }
        }
        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def request_skwad(self, idplayer):
        fields = {
        1: 33,
        2: {
            1: int(idplayer),
            2: "bd",
            3: 1,
            4: 1,
            7: 330,
            8: 19459,
            9: 100,
            12: 1,
            16: 1,
            17: {
            2: 94,
            6: 11,
            8: "1.109.5",
            9: 3,
            10: 2
            },
            18: 201,
            23: {
            2: 1,
            3: 1
            },
            24: int(get_random_avatar()),
            26: {},
            28: {}
        }
        }
        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def skwad_maker(self):
        fields = {
        1: 1,
        2: {
            2: "\u0001",
            3: 1,
            4: 1,
            5: "en",
            9: 1,
            11: 1,
            13: 1,
            14: {
            2: 5756,
            6: 11,
            8: "1.109.5",
            9: 3,
            10: 2
            },
        }
        }

        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def changes(self, num):
        fields = {
        1: 17,
        2: {
            1: 11516784163,
            2: 1,
            3: int(num),
            4: 62,
            5: "\u001a",
            8: 5,
            13: 329
        }
        }

        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
   
    def leave_s(self):
        fields = {
        1: 7,
        2: {
            1: 10853443433
        }
        }

        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def leave_room(self, idroom):
        fields = {
        1: 6,
        2: {
            1: int(idroom)
        }
        }

        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0E15000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "0E1500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "0E150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0E15000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def stauts_infoo(self, idd):
        fields = {
        1: 7,
        2: {
            1: 10853443433
        }
        }

        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)






    def GenResponsMsg(self, Msg):
        # Use fallback values if BOT_UID or clan data is None
        bot_uid = BOT_UID if BOT_UID is not None else 6500846368
        clan_id = get_current_clan_id() if get_current_clan_id() is not None else 123456789
        
        fields = {
        1: 1,
        2: {
            1: int(bot_uid),#bot account id
            2: int(clan_id),#clan id
            3: 1,
            4: str(Msg),
            5: int(datetime.now().timestamp()),
            9: {
            1: "fo",
            2: int(get_random_avatar()),
            4: 330,
            8: "OK",
            10: 1,
            11: 1
            },
            10: "en",
            13: {
            1: "https://lh3.googleusercontent.com/a/ACg8ocL7eKRT-gDmquqmXjHGRbWqFBQmcNgB_nTfeicGt61c-PndxQ=s96-c",
            2: 1,
            3: 1
            },
            14: {}
        }
        }
        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "1215000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "121500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "12150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "1215000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def createpacketinfo(self, idddd):
        ida = Encrypt(idddd)
        packet = f"080112090A05{ida}1005"
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0F15000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "0F1500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "0F150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0F15000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)

        
                
                        
                                
                                                
    def accept_sq(self, hashteam, idplayer, ownerr):
        fields = {
        1: 4,
        2: {
            1: int(ownerr),
            3: int(idplayer),
            4: "\u0001\u0007\t\n\u0012\u0019\u001a ",
            8: 1,
            9: {
            2: 1393,
            4: "wW_T",
            6: 11,
            8: "1.109.5",
            9: 3,
            10: 2
            },
            10: hashteam,
            12: 1,
            13: "en",
            16: "OR"
        }
        }

        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def info_room(self, idrooom):
        fields = {
        1: 1,
        2: {
            1: int(idrooom),
            3: {},
            4: 1,
            6: "en"
        }
        }

        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0E15000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "0E1500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "0E150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0E15000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)

        
                
                                
    def joinclanchat(self):
        fields = {
            1: 3,
            2: {
                1: int(get_current_clan_id()),#clan id
                2: 1,
                4: str(get_current_clan_key()),#clan key
            }
        }
        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "1215000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "121500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "12150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "1215000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)




    def joinclanchat1(self):
        fields = {
        1: 3,
        2: {
            2: 5,
            3: "en"
        }
        }
        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "1215000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "121500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "12150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "1215000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)

    def sockf1(self, tok, host, port, packet, key, iv):
        global socket_client
        global sent_inv
        global tempid
        global start_par
        global clients
        global pleaseaccept
        global tempdata1
        global nameinv
        global idinv
        global senthi
        global statusinfo
        global tempdata
        global data22
        global leaveee
        global isroom
        global isroom2
        socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = int(port)

        socket_client.connect((host,port))
        print(f" Con port {port} Host {host} ")
        print(tok)
        socket_client.send(bytes.fromhex(tok))
        while True:
            data2 = socket_client.recv(9999)
            print(data2)
            if "0500" in data2.hex()[0:4] and len(data2.hex()) > 30:
                if sent_inv == True:
                    accept_packet = f'08{data2.hex().split("08", 1)[1]}'
                    print(accept_packet)
                    print(tempid)
                    aa = gethashteam(accept_packet)
                    ownerid = getownteam(accept_packet)
                    print(ownerid)
                    print(aa)
                    ss = self.accept_sq(aa, tempid, int(ownerid))
                    socket_client.send(ss)
                    sleep(1)
                    startauto = self.start_autooo()
                    socket_client.send(startauto)
                    start_par = False
                    sent_inv = False
            if data2 == b"":                
                print("Connection closed by remote host")
                restart_program()

            if "0600" in data2.hex()[0:4] and len(data2.hex()) > 700:
                    accept_packet = f'08{data2.hex().split("08", 1)[1]}'
                    kk = get_available_room(accept_packet)
                    parsed_data = json.loads(kk)
                    print(parsed_data)
                    idinv = parsed_data["5"]["data"]["1"]["data"]
                    nameinv = parsed_data["5"]["data"]["3"]["data"]
                    senthi = True
            if "0f00" in data2.hex()[0:4]:
                packett = f'08{data2.hex().split("08", 1)[1]}'
                print(packett)
                kk = get_available_room(packett)
                parsed_data = json.loads(kk)
                
                asdj = parsed_data["2"]["data"]
                tempdata = get_player_status(packett)
                if asdj == 15:
                    if tempdata == "-OFFLINE":
                        tempdata = f"-THE ID IS {tempdata}"
                    else:
                        idplayer = parsed_data["5"]["data"]["1"]["data"]["1"]["data"]
                        idplayer1 = fix_num(idplayer)
                        if tempdata == "IN ROOM":
                            idrooom = get_idroom_by_idplayer(packett)
                            idrooom1 = fix_num(idrooom)
                            
                            tempdata = f"-ID : {idplayer1}\nstatus : {tempdata}\n-ID ROOM : {idrooom1}"
                            data22 = packett
                            print(data22)
                            
                        if "INSQUAD" in tempdata:
                            idleader = get_leader(packett)
                            idleader1 = fix_num(idleader)
                            tempdata = f"-ID : {idplayer1}\n-STATUS : {tempdata}\n-LEADEER ID : {idleader1}"
                        else:
                            tempdata = f"-ID : {idplayer1}\n-STATUS : {tempdata}"
                    statusinfo = True 

                    print(data2.hex())
                    print(tempdata)
                
                    

                else:
                    pass
            if "0e00" in data2.hex()[0:4]:
                packett = f'08{data2.hex().split("08", 1)[1]}'
                print(packett)
                kk = get_available_room(packett)
                parsed_data = json.loads(kk)
                idplayer1 = fix_num(idplayer)
                asdj = parsed_data["2"]["data"]
                tempdata1 = get_player_status(packett)
                if asdj == 14:
                    nameroom = parsed_data["5"]["data"]["1"]["data"]["2"]["data"]
                    
                    maxplayer = parsed_data["5"]["data"]["1"]["data"]["7"]["data"]
                    maxplayer1 = fix_num(maxplayer)
                    nowplayer = parsed_data["5"]["data"]["1"]["data"]["6"]["data"]
                    nowplayer1 = fix_num(nowplayer)
                    tempdata1 = f"{tempdata}\nRoom name : {nameroom}\nMax player : {maxplayer1}\nLive player : {nowplayer1}"
                    print(tempdata1)
                    

                    
                
                    
            if data2 == b"":
                
                print("Connection closed by remote host")
                restart_program()
                break
#━━━━━━━━━━━━━━━━━━━
    def connect(self, tok, host, port, packet, key, iv):
        global clients
        global socket_client
        global sent_inv
        global tempid
        global leaveee
        global start_par
        global nameinv
        global idinv
        global senthi
        global statusinfo
        global tempdata
        global pleaseaccept
        global tempdata1
        global data22
        clients = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = int(port)
        clients.connect((host, port))
        clients.send(bytes.fromhex(tok))
        thread = threading.Thread(
            target=self.sockf1, args=(tok, chat_ip, chat_port, "anything", key, iv)
        )
        threads.append(thread)
        thread.start()        
        clients.send(self.joinclanchat())
        while True:
            data = clients.recv(9999)
            if data == b"":
                print("Connection closed by remote host")
                restart_program()
                break
                print(f"Received data: {data}")
            
            if senthi == True:
                
                clients.send(
                        self.GenResponsMsg(
                            f"""[C][B]Hello, thanks for accepting the friend request. Send an emoji to know what to do."""
                        )
                )
                senthi = False            
            if "1200" in data.hex()[0:4]:               
                json_result = get_available_room(data.hex()[10:])
                print(data.hex())
                parsed_data = json.loads(json_result)
                uid = parsed_data["5"]["data"]["1"]["data"]
                if "8" in parsed_data["5"]["data"] and "data" in parsed_data["5"]["data"]["8"]:
                    uexmojiii = parsed_data["5"]["data"]["8"]["data"]
                    if uexmojiii == "DefaultMessageWithKey":
                        pass
                    else:
                        clients.send(
                            self.GenResponsMsg(
                                f"""[C][B]
Welcome to [00ff00]PRO BOT BY RIFAT'S BOT[ffffff]!

[C][B]
To see the commands, just send: [00ff00]🗿/help🗿[ffffff]

[C][B]
Enjoy the bot!
"""
                            )
                        )
                else:
                    pass
            
####################################
            # ========= NEW AND MODIFIED COMMANDS START HERE =========
####################################

            # ** NEW /info COMMAND **
            if "1200" in data.hex()[0:4] and b"/info" in data:
                try:
                    raw_message = data.decode('utf-8', errors='ignore')
                    # This regex is more flexible: it allows a space or no space, e.g., /info123 or /info 123
                    match = re.search(r'/info[/\s]*(\d{5,15})', raw_message)
                    
                    if not match:
                        clients.send(self.GenResponsMsg("[FF0000]Invalid format. Use: /info<UID> or /info/UID"))
                        continue

                    uid = match.group(1)
                    
                    json_result = get_available_room(data.hex()[10:])
                    parsed_data = json.loads(json_result)
                    
                    clients.send(self.GenResponsMsg(f"{generate_random_color()}Searching for UID {uid} in BD server... Please wait."))
                    
                    # Call the new function
                    info_response = newinfo(uid)
                    
                    if 'data' in info_response:
                        info_data = info_response['data']
                        basic_info = info_data.get('basicInfo', {})
                        social_info = info_data.get('socialInfo', {})
                        clan_info = info_data.get('clanBasicInfo', {})
                        captain_info = info_data.get('captainBasicInfo', {})

                        # Format creation date - it's already a formatted string in the API
                        creation_date = basic_info.get('createAt', 'N/A')
                        if creation_date != 'N/A':
                            try:
                                # Try to reformat the date if needed (from "2025-04-04 11:44:42" to "04 April 2025")
                                from datetime import datetime
                                dt = datetime.strptime(creation_date, '%Y-%m-%d %H:%M:%S')
                                creation_date = dt.strftime('%d %B %Y')
                            except (ValueError, TypeError):
                                # Keep original format if parsing fails
                                pass

                        # Prepare clan info message
                        clan_info_msg = "\n[C][FF0000]Player is not in a clan.\n"
                        if clan_info and clan_info.get('clanId'):
                            clan_info_msg = (
                                f"\n[C][11EAFD]╒═══[b] Clan Info [/b]═══╕\n"
                                f"[FFFFFF]Guild Name: [00FF00]{clan_info.get('clanName', 'N/A')}\n"
                                f"[FFFFFF]Guild Level: [00FF00]{clan_info.get('clanLevel', 'N/A')}\n"
                                f"[FFFFFF]Guild ID: [00FF00]{fix_num(clan_info.get('clanId', 'N/A'))}\n"
                            )
                            if captain_info and captain_info.get('accountId'):
                                clan_info_msg += (
                                f"[C][11EAFD]Leader Info:\n"
                                f"[FFFFFF]Name: [00FF00]{captain_info.get('nickname', 'N/A')}\n"
                                f"[FFFFFF]ID: [00FF00]{fix_num(captain_info.get('accountId', 'N/A'))}\n"
                                )
                            clan_info_msg += f"[C][11EAFD]╘══════════════╛\n"

                        # Get and clean bio
                        bio = social_info.get('signature', 'No Bio').replace("|", " ")

                        # Construct the final "VIP" message
                        message_info = (
                            f"[C][FFB300]╒═══[b] Player Account Info [/b]═══╕\n"
                            f"[FFFFFF]Name: [00FF00]{basic_info.get('nickname', 'N/A')}\n"
                            f"[FFFFFF]UID: [00FF00]{fix_num(basic_info.get('accountId', 'N/A'))}\n"
                            f"[FFFFFF]Level: [00FF00]{basic_info.get('level', 'N/A')}\n"
                            f"[FFFFFF]Likes: [00FF00]{fix_num(basic_info.get('liked', 'N/A'))}\n"
                            f"[FFFFFF]BR Rank Score: [00FF00]{fix_num(basic_info.get('rankingPoints', 'N/A'))}\n"
                            f"[FFFFFF]Server: [00FF00]{basic_info.get('region', 'N/A')}\n"
                            f"[FFFFFF]Account Created: [00FF00]{creation_date}\n"
                            f"[FFFFFF]Bio: [00FF00]{bio}\n"
                            f"{clan_info_msg}"
                            f"[C][FFB300]╘══════════════════╛"
                        )
                    else:
                        # Handle API error
                        error_detail = info_response.get('message', 'An unknown error occurred.')
                        message_info = (
                            f"[C][B][FF0000]-----------------------------------\n"
                            f"[FFFFFF]Failed to get player info for UID: {uid}.\n"
                            f"[FFFF00]Reason: {error_detail}\n"
                            f"[FF0000]-----------------------------------"
                        )
                    
                    clients.send(self.GenResponsMsg(message_info))

                except Exception as e:
                    print(f"CRITICAL ERROR in /info handler: {e}")
                    clients.send(self.GenResponsMsg("[FF0000][b]An unexpected error occurred processing the /info command."))

            # ** MODIFIED /spm COMMAND FOR FRIEND REQUEST SPAM **
            # Note: Using /spm/ as it was in the original code for friend request spam.
            if "1200" in data.hex()[0:4] and b"/spam/" in data:
                try:
                    raw_message = data.decode('utf-8', errors='ignore')
                    match = re.search(r'/spam[/\s]*(\d{5,15})', raw_message)

                    if not match:
                        clients.send(self.GenResponsMsg("[FF0000]Invalid format. Use: /spam<UID> or /spam/UID"))
                        continue

                    player_id = match.group(1)

                    clients.send(self.GenResponsMsg(f"[FFB300]Contacting Spam API for UID: {player_id}... Please wait up to 25 seconds."))

                    # --- Call your SPAM API ---
                    response_message = ""
                    try:
                        api_url = f"https://like2.vercel.app/send_requests?uid={player_id}&key={keys}&server=BD"
                        # Increased timeout as requested
                        response = requests.get(api_url, timeout=25) 

                        if response.status_code == 200:
                            api_data = response.json()
                            success_count = api_data.get("success_count", 0)
                            failed_count = api_data.get("failed_count", 0)
                            
                            response_message = f"""
[C][B][11EAFD]‎━━━━━━
[FFFFFF]Spam Request API Response:

[00FF00]Successful Requests: {success_count}
[FF0000]Failed Requests: {failed_count}

[FFFFFF]Target UID: {fix_num(player_id)}
[C][B][11EAFD]‎━━━━━━
[C][B][FFB300]BOT BY PRO BOT BY RIFAT
"""
                        else:
                            response_message = f"[FF0000]Error: Spam API returned status code {response.status_code}."

                    except requests.exceptions.RequestException as api_error:
                        # This catches network errors if the API is offline or times out
                        print(f"SPAM API connection error: {api_error}")
                        response_message = f"[FF0000]Error: Could not connect to the spam API. It might be offline or the request timed out. ({api_error})"

                    # Send the final result back to the chat
                    clients.send(self.GenResponsMsg(response_message))

                except Exception as e:
                    print(f"\nCRITICAL Processing Error in /spam/ handler: {e}\n")
                    try:
                        error_msg = f"[FF0000]A critical error occurred: {str(e)}. The bot will now restart."
                        clients.send(self.GenResponsMsg(error_msg))
                    except:
                        print("Failed to send the final error message.")
                    finally:
                        restart_program()

            # CHECK ID ->> COMMAND
            if "1200" in data.hex()[0:4] and b"/check/" in data:
                try:
                    raw_message = data.decode('utf-8', errors='ignore')
                    match = re.search(r'/check[/\s]*(\d{5,15})', raw_message)
                    if not match:
                        clients.send(self.GenResponsMsg("[FF0000]Invalid format. Use: /check<UID>"))
                        continue
                    
                    player_id = match.group(1)
                    clients.send(self.GenResponsMsg("Checking ban status... Please Wait.."))
                    banned_status = check_banned_status(player_id)
                    
                    if 'error' in banned_status:
                        response_message = f"[FF0000]Error: {banned_status['error']}"
                    else:
                        status = banned_status.get('status', 'Unknown')
                        player_name = banned_status.get('data.nickname', 'N/A')
                        response_message = f"""
[11EAFD][b][c]
°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
Player Name: {player_name}
Player ID : {fix_num(player_id)}
Status: {status}
°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
[FFB300][b][c]BOT MADE BY PRO BOT BY RIFAT
                """
                    clients.send(self.GenResponsMsg(response_message))
                except Exception as e:
                    clients.send(self.GenResponsMsg(f"[FF0000]Error processing command: {e}"))


            # ** MODIFIED: GET 100 LIKES COMMAND with Daily Limit **
            if "1200" in data.hex()[0:4] and b"/like/" in data:
                try:
                    # Get the UID of the person who sent the command
                    json_result_for_uid = get_available_room(data.hex()[10:])
                    parsed_data_for_uid = json.loads(json_result_for_uid)
                    requester_uid = str(parsed_data_for_uid["5"]["data"]["1"]["data"])

                    # Check if the user is allowed to make a request
                    if check_and_update_like_limit(requester_uid):
                        raw_message = data.decode('utf-8', errors='ignore')
                        match = re.search(r'/like[/\s]*(\d{5,15})', raw_message)
                        
                        if not match:
                            clients.send(self.GenResponsMsg("[FF0000]Invalid format. Please use: /like<UID>"))
                        else:
                            player_id = match.group(1)
                            clients.send(self.GenResponsMsg(f"Sending likes to UID: {player_id}... Please wait."))
                            likes_info = send_likes(player_id)
                            clients.send(self.GenResponsMsg(likes_info))
                    else:
                        # User has reached their daily limit
                        limit_msg = f"[FF0000][B]You have reached your daily limit of {DAILY_LIKE_LIMIT} like requests. Please try again tomorrow."
                        clients.send(self.GenResponsMsg(limit_msg))

                except Exception as e:
                    print(f"Likes Command CRITICAL Error: {e}")
                    clients.send(self.GenResponsMsg("[FF0000][B]A critical error occurred with the likes command."))
                    restart_program()
            
            # AI COMMAND
            if "1200" in data.hex()[0:4] and b"/ai" in data:
                try:
                    clients.send(self.GenResponsMsg("Connecting to AI..."))
                    raw_message = data.decode('utf-8', errors='ignore').replace('\x00', '')
                    question_part = raw_message.split('/ai', 1)[1]
                    question = question_part.strip()
                    if not question:
                        raise ValueError("No question provided")
                    
                    ai_msg = talk_with_ai(question)
                    clients.send(self.GenResponsMsg(ai_msg))
                except Exception as e:
                    print(f"AI Command Error: {e}")
                    clients.send(self.GenResponsMsg("[FF0000]Error with AI command. Please provide a question after /ai."))


            # ** HELP COMMAND **
            if "1200" in data.hex()[0:4] and b"/help" in data:
                print("Help command detected!")
                help_message = """[C][B][00FFFF]━━━━━━━━━━━━
[FFFFFF][B]Get Full Player Info:  
[32CD32]/info/UID

[FFFFFF][B]Spam Friend Requests:
[1E90FF]/spam/UID

[FFFFFF][B]Check if Player is Banned:  
[32CD32]/check/UID

[FFFFFF][B]Add 100 Likes (5/day):  
[FF69B4]/like/UID

[FFFFFF][B]Chat with AI:  
[9370DB]/ai [your question]

[FFFFFF][B]Squad Commands:
[FFD700]/3s - Create 3-player squad
[FFD700]/4s - Create 4-player squad  
[FFD700]/5s - Create 5-player squad
[FFD700]/6s - Create 6-player squad

[FFFFFF][B]Player Interaction:
[FF6347]/inv/UID - Invite player to squad
[FF6347]/snd/UID - Unlock Squad 5 for player

[C][B][FFB300]OWNER: PRO BOT BY RIFAT
[00FFFF]━━━━━━━━━━━━"""
                clients.send(self.GenResponsMsg(help_message))


            # ** SQUAD COMMANDS **
            # /3s - Creates a 3-player squad and invites the user
            if "1200" in data.hex()[0:4] and b"/3s" in data:
                try:
                    print("3s command detected!")
                    json_result = get_available_room(data.hex()[10:])
                    parsed_data = json.loads(json_result)
                    uid = parsed_data["5"]["data"]["1"]["data"]
                    print(f"Extracted UID: {uid}")
                    
                    # Create squad and invite user
                    try:
                        print(f"Socket client status: {socket_client}")
                        print(f"Clients status: {clients}")
                        
                        packetmaker = self.skwad_maker()
                        socket_client.send(packetmaker)  # Use socket_client for squad operations
                        print(f"Sent squad maker packet for 3s via socket_client")
                        sleep(2)  # Increased delay to prevent server disconnection
                        
                        packetfinal = self.changes(2)  # 3-player squad
                        socket_client.send(packetfinal)  # Use socket_client for squad operations
                        print(f"Sent squad changes packet for 3s via socket_client")
                        sleep(1)  # Add delay between packets
                        
                        # Check connection before sending invite
                        try:
                            invitess = self.invite_skwad(uid)
                            socket_client.send(invitess)  # Use socket_client for squad operations
                            print(f"Sent invite packet for UID: {uid} via socket_client")
                        except (ConnectionAbortedError, ConnectionResetError, OSError) as conn_error:
                            print(f"Connection lost during invite send: {conn_error}")
                            print("Skipping invite packet to prevent crash")
                            # Don't raise the error, just continue
                    except Exception as packet_error:
                        print(f"Packet sending error: {packet_error}")
                        # Don't raise the error to prevent crash
                    
                    clients.send(self.GenResponsMsg("""
[11EAFD][b][c]
━━━━━━━━━━━━
3-Player Squad Created!
Accept request quickly!!!
━━━━━━━━━━━━
[FFB300][b][c]BOT BY PRO BOT BY RIFAT
                    """))
                    
                    sleep(5)
                    leavee = self.leave_s()
                    socket_client.send(leavee)
                except Exception as e:
                    print(f"3s Command Error: {e}")
                    clients.send(self.GenResponsMsg("[FF0000]Error creating 3-player squad"))

            # /4s - Creates a 4-player squad and invites the user
            if "1200" in data.hex()[0:4] and b"/4s" in data:
                try:
                    print("4s command detected!")
                    json_result = get_available_room(data.hex()[10:])
                    parsed_data = json.loads(json_result)
                    uid = parsed_data["5"]["data"]["1"]["data"]
                    print(f"Extracted UID: {uid}")
                    
                    try:
                        packetmaker = self.skwad_maker()
                        socket_client.send(packetmaker)  # Use socket_client for squad operations
                        print(f"Sent squad maker packet for 4s via socket_client")
                        sleep(2)  # Increased delay to prevent server disconnection
                        
                        packetfinal = self.changes(3)  # 4-player squad
                        socket_client.send(packetfinal)  # Use socket_client for squad operations
                        print(f"Sent squad changes packet for 4s via socket_client")
                        sleep(1)  # Add delay between packets
                        
                        # Check connection before sending invite
                        try:
                            invitess = self.invite_skwad(uid)
                            socket_client.send(invitess)  # Use socket_client for squad operations
                            print(f"Sent invite packet for UID: {uid} via socket_client")
                        except (ConnectionAbortedError, ConnectionResetError, OSError) as conn_error:
                            print(f"Connection lost during invite send: {conn_error}")
                            print("Skipping invite packet to prevent crash")
                            # Don't raise the error, just continue
                    except Exception as packet_error:
                        print(f"Packet sending error in 4s: {packet_error}")
                        # Don't raise the error to prevent crash
                    
                    clients.send(self.GenResponsMsg("""
[11EAFD][b][c]
━━━━━━━━━━━━
4-Player Squad Created!
Accept request quickly!!!
━━━━━━━━━━━━
[FFB300][b][c]BOT BY PRO BOT BY RIFAT
                    """))
                    
                    sleep(5)
                    leavee = self.leave_s()
                    socket_client.send(leavee)
                except Exception as e:
                    print(f"4s Command Error: {e}")
                    clients.send(self.GenResponsMsg("[FF0000]Error creating 4-player squad"))

            # /5s - Creates a 5-player squad and invites the user
            if "1200" in data.hex()[0:4] and b"/5s" in data:
                try:
                    json_result = get_available_room(data.hex()[10:])
                    parsed_data = json.loads(json_result)
                    uid = parsed_data["5"]["data"]["1"]["data"]
                    
                    try:
                        print(f"Socket client status: {socket_client}")
                        print(f"Clients status: {clients}")
                        
                        packetmaker = self.skwad_maker()
                        socket_client.send(packetmaker)  # Use socket_client for squad operations
                        print(f"Sent squad maker packet for 5s via socket_client")
                        sleep(2)  # Increased delay to prevent server disconnection
                        
                        packetfinal = self.changes(4)  # 5-player squad
                        socket_client.send(packetfinal)  # Use socket_client for squad operations
                        print(f"Sent squad changes packet for 5s via socket_client")
                        sleep(1)  # Add delay between packets
                        
                        # Check connection before sending invite
                        try:
                            invitess = self.invite_skwad(uid)
                            socket_client.send(invitess)  # Use socket_client for squad operations
                            print(f"Sent invite packet for UID: {uid} via socket_client")
                        except (ConnectionAbortedError, ConnectionResetError, OSError) as conn_error:
                            print(f"Connection lost during invite send: {conn_error}")
                            print("Skipping invite packet to prevent crash")
                            # Don't raise the error, just continue
                    except Exception as packet_error:
                        print(f"Packet sending error in 5s: {packet_error}")
                        # Don't raise the error to prevent crash
                    
                    clients.send(self.GenResponsMsg("""
[11EAFD][b][c]
━━━━━━━━━━━━
5-Player Squad Created!
Accept request quickly!!!
━━━━━━━━━━━━
[FFB300][b][c]BOT BY PRO BOT BY RIFAT
                    """))
                    
                    sleep(5)
                    leavee = self.leave_s()
                    socket_client.send(leavee)
                except Exception as e:
                    print(f"5s Command Error: {e}")
                    clients.send(self.GenResponsMsg("[FF0000]Error creating 5-player squad"))

            # /6s - Creates a 6-player squad and invites the user
            if "1200" in data.hex()[0:4] and b"/6s" in data:
                try:
                    json_result = get_available_room(data.hex()[10:])
                    parsed_data = json.loads(json_result)
                    uid = parsed_data["5"]["data"]["1"]["data"]
                    
                    try:
                        print(f"Socket client status: {socket_client}")
                        print(f"Clients status: {clients}")
                        
                        packetmaker = self.skwad_maker()
                        socket_client.send(packetmaker)  # Use socket_client for squad operations
                        print(f"Sent squad maker packet for 6s via socket_client")
                        sleep(2)  # Increased delay to prevent server disconnection
                        
                        packetfinal = self.changes(5)  # 6-player squad
                        socket_client.send(packetfinal)  # Use socket_client for squad operations
                        print(f"Sent squad changes packet for 6s via socket_client")
                        sleep(1)  # Add delay between packets
                        
                        # Check connection before sending invite
                        try:
                            invitess = self.invite_skwad(uid)
                            socket_client.send(invitess)  # Use socket_client for squad operations
                            print(f"Sent invite packet for UID: {uid} via socket_client")
                        except (ConnectionAbortedError, ConnectionResetError, OSError) as conn_error:
                            print(f"Connection lost during invite send: {conn_error}")
                            print("Skipping invite packet to prevent crash")
                            # Don't raise the error, just continue
                    except Exception as packet_error:
                        print(f"Packet sending error in 6s: {packet_error}")
                        # Don't raise the error to prevent crash
                    
                    clients.send(self.GenResponsMsg("""
[11EAFD][b][c]
━━━━━━━━━━━━
6-Player Squad Created!
Accept request quickly!!!
━━━━━━━━━━━━
[FFB300][b][c]BOT BY PRO BOT BY RIFAT
                    """))
                    
                    sleep(5)
                    leavee = self.leave_s()
                    socket_client.send(leavee)
                except Exception as e:
                    print(f"6s Command Error: {e}")
                    try:
                        clients.send(self.GenResponsMsg("[FF0000]Error creating 6-player squad"))
                    except (ConnectionAbortedError, ConnectionResetError, OSError):
                        print("Cannot send error message - connection lost")

            # ** PLAYER INTERACTION COMMANDS **
            # /inv/[PLAYER_ID] - Invites a specific player to squad
            if "1200" in data.hex()[0:4] and b"/inv/" in data:
                try:
                    raw_message = data.decode('utf-8', errors='ignore')
                    match = re.search(r'/inv[/\s]*(\d{5,15})', raw_message)
                    
                    if not match:
                        clients.send(self.GenResponsMsg("[FF0000]Invalid format. Use: /inv/UID"))
                        continue
                    
                    target_uid = match.group(1)
                    json_result = get_available_room(data.hex()[10:])
                    parsed_data = json.loads(json_result)
                    requester_uid = parsed_data["5"]["data"]["1"]["data"]
                    
                    # Create squad and invite both users
                    try:
                        print(f"Socket client status: {socket_client}")
                        print(f"Clients status: {clients}")
                        
                        packetmaker = self.skwad_maker()
                        clients.send(packetmaker)  # Use clients instead of socket_client
                        print(f"Sent squad maker packet for /inv via clients")
                        sleep(1)
                        
                        packetfinal = self.changes(5)  # 6-player squad
                        clients.send(packetfinal)  # Use clients instead of socket_client
                        print(f"Sent squad changes packet for /inv via clients")
                        
                        # Invite target player
                        invitess_target = self.invite_skwad(target_uid)
                        clients.send(invitess_target)  # Use clients instead of socket_client
                        print(f"Sent invite packet for target UID: {target_uid} via clients")
                        
                        # Invite requester
                        invitess_requester = self.invite_skwad(requester_uid)
                        clients.send(invitess_requester)  # Use clients instead of socket_client
                        print(f"Sent invite packet for requester UID: {requester_uid} via clients")
                    except Exception as packet_error:
                        print(f"Packet sending error in /inv: {packet_error}")
                        raise packet_error
                    
                    clients.send(self.GenResponsMsg(f"""
[11EAFD][b][c]
━━━━━━━━━━━━
Squad invitations sent!
Target: {fix_num(target_uid)}
Accept request quickly!!!
━━━━━━━━━━━━
[FFB300][b][c]BOT BY PRO BOT BY RIFAT
                    """))
                    
                    sleep(9)
                    leavee = self.leave_s()
                    socket_client.send(leavee)
                    
                except Exception as e:
                    print(f"Invite Command Error: {e}")
                    clients.send(self.GenResponsMsg("[FF0000]Error processing invite command"))

            # /snd/[PLAYER_ID] - Unlocks Squad 5 for a player
            if "1200" in data.hex()[0:4] and b"/snd/" in data:
                try:
                    raw_message = data.decode('utf-8', errors='ignore')
                    match = re.search(r'/snd[/\s]*(\d{5,15})', raw_message)
                    
                    if not match:
                        target_uid = "12194912428"  # Default fallback
                    else:
                        target_uid = match.group(1)
                    
                    json_result = get_available_room(data.hex()[10:])
                    parsed_data = json.loads(json_result)
                    requester_uid = parsed_data["5"]["data"]["1"]["data"]
                    
                    # Unlock Squad 5
                    try:
                        print(f"Socket client status: {socket_client}")
                        print(f"Clients status: {clients}")
                        
                        packetmaker = self.skwad_maker()
                        clients.send(packetmaker)  # Use clients instead of socket_client
                        print(f"Sent squad maker packet for /snd via clients")
                        sleep(1)
                        
                        packetfinal = self.changes(4)
                        clients.send(packetfinal)  # Use clients instead of socket_client
                        print(f"Sent squad changes packet for /snd via clients")
                        
                        invitess = self.invite_skwad(target_uid)
                        clients.send(invitess)  # Use clients instead of socket_client
                        print(f"Sent invite packet for target UID: {target_uid} via clients")
                    except Exception as packet_error:
                        print(f"Packet sending error in /snd: {packet_error}")
                        raise packet_error
                    
                    clients.send(self.GenResponsMsg(f"""
[11EAFD][b][c]
━━━━━━━━━━━━
Squad 5 unlocked for player:
{fix_num(target_uid)}
━━━━━━━━━━━━
[FFB300][b][c]BOT BY PRO BOT BY RIFAT
                    """))
                    
                    sleep(5)
                    leavee = self.leave_s()
                    socket_client.send(leavee)
                    
                except Exception as e:
                    print(f"Send Command Error: {e}")
                    clients.send(self.GenResponsMsg("[FF0000]Error processing send command"))

####################################
            # ========= END OF NEW AND MODIFIED COMMANDS =========
####################################

    
    def  parse_my_message(self, serialized_data):
        MajorLogRes = MajorLoginRes_pb2.MajorLoginRes()
        MajorLogRes.ParseFromString(serialized_data)
        
        timestamp = MajorLogRes.kts
        key = MajorLogRes.ak
        iv = MajorLogRes.aiv
        BASE64_TOKEN = MajorLogRes.token
        timestamp_obj = Timestamp()
        timestamp_obj.FromNanoseconds(timestamp)
        timestamp_seconds = timestamp_obj.seconds
        timestamp_nanos = timestamp_obj.nanos
        combined_timestamp = timestamp_seconds * 1_000_000_000 + timestamp_nanos
        return combined_timestamp, key, iv, BASE64_TOKEN

    def GET_PAYLOAD_BY_DATA(self,JWT_TOKEN , NEW_ACCESS_TOKEN,date):
        token_payload_base64 = JWT_TOKEN.split('.')[1]
        token_payload_base64 += '=' * ((4 - len(token_payload_base64) % 4) % 4)
        decoded_payload = base64.urlsafe_b64decode(token_payload_base64).decode('utf-8')
        decoded_payload = json.loads(decoded_payload)
        NEW_EXTERNAL_ID = decoded_payload['external_id']
        SIGNATURE_MD5 = decoded_payload['signature_md5']
        now = datetime.now()
        now =str(now)[:len(str(now))-7]
        formatted_time = date
        payload = bytes.fromhex("3a07312e3131342e32aa01026172b201203535656437353966636639346638353831336535376232656338343932663563ba010134ea0140366662376664656638363538666430333137346564353531653832623731623231646238313837666130363132633865616631623633616136383766316561659a060134a2060134ca03203734323862323533646566633136343031386336303461316562626665626466")
        payload = payload.replace(b"2024-12-26 13:02:43", str(now).encode())
        payload = payload.replace(b"88332848f415ca9ca98312edcd5fe8bc6547bc6d0477010a7feaf97e3435aa7f", NEW_ACCESS_TOKEN.encode("UTF-8"))
        payload = payload.replace(b"e1ccc10e70d823f950f9f4c337d7d20a", NEW_EXTERNAL_ID.encode("UTF-8"))
        payload = payload.replace(b"7428b253defc164018c604a1ebbfeMEf", SIGNATURE_MD5.encode("UTF-8"))
        PAYLOAD = payload.hex()
        PAYLOAD = encrypt_api(PAYLOAD)
        PAYLOAD = bytes.fromhex(PAYLOAD)
        ip,port = self.GET_LOGIN_DATA(JWT_TOKEN , PAYLOAD)
        return ip,port
    
    def dec_to_hex(ask):
        ask_result = hex(ask)
        final_result = str(ask_result)[2:]
        if len(final_result) == 1:
            final_result = "0" + final_result
            return final_result
        else:
            return final_result
    def convert_to_hex(PAYLOAD):
        hex_payload = ''.join([f'{byte:02x}' for byte in PAYLOAD])
        return hex_payload
    def convert_to_bytes(PAYLOAD):
        payload = bytes.fromhex(PAYLOAD)
        return payload
    def GET_LOGIN_DATA(self, JWT_TOKEN, PAYLOAD):
        url = "https://clientbp.common.ggbluefox.com/GetLoginData"
        headers = {
            'Expect': '100-continue',
            'Authorization': f'Bearer {JWT_TOKEN}',
            'X-Unity-Version': '2018.4.11f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': freefire_version,
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)',
            'Host': 'clientbp.common.ggbluefox.com',
            'Connection': 'close',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        
        max_retries = 3
        attempt = 0

        while attempt < max_retries:
            try:
                response = requests.post(url, headers=headers, data=PAYLOAD,verify=False)
                response.raise_for_status()
                x = response.content.hex()
                json_result = get_available_room(x)
                parsed_data = json.loads(json_result)
                print(parsed_data)
                
                # Extract clan data from login response
                extract_clan_data_from_response(x)
                
                address = parsed_data['32']['data']
                ip = address[:len(address) - 6]
                port = address[len(address) - 5:]
                return ip, port
            
            except requests.RequestException as e:
                print(f"Request failed: {e}. Attempt {attempt + 1} of {max_retries}. Retrying...")
                attempt += 1
                time.sleep(2)

        print("Failed to get login data after multiple attempts.")
        return None, None

    def guest_token(self,uid , password):
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {"Host": "100067.connect.garena.com","User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 11;en;BD;)","Content-Type": "application/x-www-form-urlencoded","Accept-Encoding": "gzip, deflate, br","Connection": "close",}
        data = {"uid": f"{uid}","password": f"{password}","response_type": "token","client_type": "2","client_secret": client_secret,"client_id": "100067",}
        response = requests.post(url, headers=headers, data=data)
        data = response.json()
        NEW_ACCESS_TOKEN = data['access_token']
        NEW_OPEN_ID = data['open_id']
        OLD_ACCESS_TOKEN = "6fb7fdef8658fd03174ed551e82b71b21db8187fa0612c8eaf1b63aa687f1eae"
        OLD_OPEN_ID = "55ed759fcf94f85813e57b2ec8492f5c"
        time.sleep(0.2)
        data = self.TOKEN_MAKER(OLD_ACCESS_TOKEN , NEW_ACCESS_TOKEN , OLD_OPEN_ID , NEW_OPEN_ID,id)
        return(data)
        
    def TOKEN_MAKER(self,OLD_ACCESS_TOKEN , NEW_ACCESS_TOKEN , OLD_OPEN_ID , NEW_OPEN_ID,id):
        headers = {
            'X-Unity-Version': '2018.4.11f1',
            'ReleaseVersion': 'OB50',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'Content-Length': '928',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
            'Host': 'loginbp.common.ggbluefox.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        data = bytes.fromhex(paylod_token1)
        data = data.replace(OLD_OPEN_ID.encode(),NEW_OPEN_ID.encode())
        data = data.replace(OLD_ACCESS_TOKEN.encode() , NEW_ACCESS_TOKEN.encode())
        hex = data.hex()
        d = encrypt_api(data.hex())
        Final_Payload = bytes.fromhex(d)
        URL = "https://loginbp.ggblueshark.com/MajorLogin"

        RESPONSE = requests.post(URL, headers=headers, data=Final_Payload,verify=False)
        
        combined_timestamp, key, iv, BASE64_TOKEN = self.parse_my_message(RESPONSE.content)
        if RESPONSE.status_code == 200:
            if len(RESPONSE.text) < 10:
                return False
            ip,port =self.GET_PAYLOAD_BY_DATA(BASE64_TOKEN,NEW_ACCESS_TOKEN,1)
            self.key = key
            self.iv = iv
            print(key, iv)
            return(BASE64_TOKEN,key,iv,combined_timestamp,ip,port)
        else:
            return False
    
    def time_to_seconds(hours, minutes, seconds):
        return (hours * 3600) + (minutes * 60) + seconds

    def seconds_to_hex(seconds):
        return format(seconds, '04x')
    
    def extract_time_from_timestamp(timestamp):
        dt = datetime.fromtimestamp(timestamp)
        h = dt.hour
        m = dt.minute
        s = dt.second
        return h, m, s
    
    def get_tok(self):
        global g_token
        token, key, iv, Timestamp, ip, port = self.guest_token(self.id, self.password)
        g_token = token
        print(ip, port)
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            account_id = decoded.get('account_id')
            encoded_acc = hex(account_id)[2:]
            hex_value = dec_to_hex(Timestamp)
            time_hex = hex_value
            BASE64_TOKEN_ = token.encode().hex()
            print(f"Token decoded and processed. Account ID: {account_id}")
        except Exception as e:
            print(f"Error processing token: {e}")
            return

        try:
            head = hex(len(encrypt_packet(BASE64_TOKEN_, key, iv)) // 2)[2:]
            length = len(encoded_acc)
            zeros = '00000000'

            if length == 9:
                zeros = '0000000'
            elif length == 8:
                zeros = '00000000'
            elif length == 10:
                zeros = '000000'
            elif length == 7:
                zeros = '000000000'
            else:
                print('Unexpected length encountered')
            head = f'0115{zeros}{encoded_acc}{time_hex}00000{head}'
            final_token = head + encrypt_packet(BASE64_TOKEN_, key, iv)
            print("Final token constructed successfully.")
            
            # Extract clan data from login response
            extract_clan_data_from_response(final_token)
            
        except Exception as e:
            print(f"Error constructing final token: {e}")
        token = final_token
        self.connect(token, ip, port, 'anything', key, iv)
        
      
        return token, key, iv
        
with open('guild_bot.txt', 'r') as file:
    data = json.load(file)
ids_passwords = list(data.items())
def run_client(id, password):
    print(f"ID: {id}, Password: {password}")
    client = FF_CLIENT(id, password)
    client.start()
    
max_range = 300000
num_clients = len(ids_passwords)
num_threads = 1
start = 0
end = max_range
step = (end - start) // num_threads
threads = []
if __name__ == "__main__":
    # Only run if this file is executed directly, not when imported as template
    for i in range(num_threads):
        ids_for_thread = ids_passwords[i % num_clients]
        id, password = ids_for_thread
        thread = threading.Thread(target=run_client, args=(id, password))
        threads.append(thread)
        time.sleep(3)
        thread.start()

    for thread in threads:
        thread.join()
        
    try:
        # You should have your bot account details in accs.txt
        # This part is just for a direct run example.
        # Ensure accs.txt is configured correctly for the main loop to work.
        pass
    except Exception as e:
        logging.error(f"Error occurred during initialization: {e}")
        restart_program()