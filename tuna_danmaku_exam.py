import requests
from getpass import getpass
from time import sleep, strftime

print("TUNA Danmaku Examine Terminal by cai_lw")
cname = input("Channel name:")
fetch_dmk_api = 'http://dm.tuna.moe/api/v1/channels/%s/danmaku/exam' % cname
post_dmk_api = 'http://dm.tuna.moe/api/v1/channels/%s/danmaku' % cname
pub_pwd = getpass("Post password:")
exam_pwd = getpass("Examine password:")

def make_dmk(content, color="blue", position="fly"):
    return {"content":content,"color":color,"position":position}

def post_dmk(dmk):
    return requests.post(post_dmk_api, headers={"X-GDANMAKU-AUTH-KEY":pub_pwd,"X-GDANMAKU-TOKEN":"APP:","X-GDANMAKU-EXAM-KEY":exam_pwd},json=dmk)

def fetch_dmk():
    return requests.get(fetch_dmk_api, headers={"X-GDANMAKU-AUTH-KEY":exam_pwd})

try:
    test_resp = post_dmk(make_dmk("Test from examiner~"))
    if test_resp.status_code != 200:
        print("========== Test failed, closing ==========")
        print("Status code:", test_resp.status_code)
        print("Content:")
        print(test_resp.text)
        exit()
    channels_resp = requests.get('http://dm.tuna.moe/api/v1/channels')
    for channel in channels_resp.json()["channels"]:
        if channel["name"] == cname and not channel["need_exam"]:
            print("=========== Examine-free channel, closing ==========")
            exit()
except requests.RequestException:
    print("=========== Network error, closing ==========")
    exit()
print("========== Test passed, start listening ==========")

sleep_time = 0
log = open("danmaku_log.txt", "w", encoding="utf8")
while True:
    request_exception = None
    try:
        resp = fetch_dmk()
    except requests.RequestException as e:
        request_exception = e
    if request_exception or resp.status_code != 200:
        print("Fetch failed, retrying.")
        sleep(sleep_time)
        if sleep_time < 5:
            sleep_time += 1
        continue
    dmks = resp.json()
    if len(dmks) == 0:
        sleep(sleep_time)
        if sleep_time < 5:
            sleep_time += 1
        continue
    for dmk in dmks:
        print('========== Danmaku begin =========')
        try:
            print(dmk["text"])
        except UnicodeEncodeError:
            print("*** Not printable in the console, see in danmaku_log.txt")
        log.write('[' + strftime("%y-%m-%d %H:%M:%S") + '] ' + dmk["text"])
        log.flush()
        print('========== Danmaku end ===========')
        while True:
            cmd = input("Press Enter to ACCEPT. Input 'x' to REJECT. Input 'c' to show style:")
            if cmd == "":
                post_dmk(make_dmk(dmk["text"], dmk["style"], dmk["position"]))
                print(' <ACCEPT>', file=log, flush=True)
                break
            elif cmd.lower() == 'x':
                print(' <REJECT>' ,file=log, flush=True)
                break
            elif cmd.lower() == 'c':
                print('Color:',dmk["style"],'Position:',dmk["position"])
