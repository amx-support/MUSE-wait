from mojo import context
from ele_lib import muse_wait

# デバイス定義 ------------------------------------------------------------------------------------------
# MUSE
muse = context.devices.get("idevice")
serial = muse.serial
relay = muse.relay
io = muse.io

# TP
tp = context.devices.get("AMX-10001")

# TIMELINE
tl = context.services.get("timeline")
tl.start([300],False,-1)


# 変数定義 --------------------------------------------------------------------------------------------
# WAIT処理用インスタンス生成
wt = muse_wait.Wait()


# 関数定義 --------------------------------------------------------------------------------------------
def serial_control(dev,data):
    dev.send(data)

def rel_control(devch,state):
    devch.state = state

def level_control(devlev,value):
    devlev.value = value

def io_state():
    return io[0].digitalInput.value

def send_data():
    wt.wait(20,serial_control,[serial[0],"Hello,world!"],"Wait Name Send 1")
    wt.wait(40,lambda:serial[0].send("hoge fuga piyo"),name="Wait Name Send 2")
    wt.wait(60,serial_control,[serial[0],"0123456789"],"Wait Name Send 3")

def show_wait_list():
    # *********************************************************************
    # 動作がわかりやすくなるように残り時間やWAITの名前を可視化しています。
    # 実運用時は必要ありませんです。
    # *********************************************************************
    list_len = len(wt.wait_list)
    for i in range(12):
        if i < list_len:
            tp.port[1].send_command("^TXT-%s,0,%s"%(i+11,wt.wait_list[i]["type"]))
            tp.port[1].send_command("^TXT-%s,0,%s"%(i+31,"{:.3f}".format(wt.wait_list[i]["time"])))
            tp.port[1].send_command("^TXT-%s,0,%s"%(i+51,wt.wait_list[i]["name"]))
        else:
            tp.port[1].send_command("^TXT-%s,0,"%(i+11))
            tp.port[1].send_command("^TXT-%s,0,"%(i+31))
            tp.port[1].send_command("^TXT-%s,0,"%(i+51))

def refresh_tp():
    show_wait_list() # WAITのリストを表示 (運用時には不要)

    # ボタンのフィードバック
    tp.port[1].channel[11] = relay[0].state.value
    tp.port[1].channel[12] = io[0].digitalInput.value


# イベント定義 ------------------------------------------------------------------------------------------
# TIMELINE
def timeline_event(e):
    refresh_tp()
tl.expired.listen(timeline_event)

# SERIAL
def data_event(e):
    data_text = e.arguments["data"].decode("UTF-8")

    tp.port[1].send_command("^TXT-1,0,%s"%data_text)
serial[0].receive.listen(data_event)

# BUTTON
def button_event(e):
    ch = int(e.id)
    #print("Ch: %s - %s"%(ch,e.value))

    tp.port[1].channel[ch] = e.value

    if e.value:
        if ch == 1:
            tp.port[1].level[1].value = 0
            wt.wait(10,level_control,[tp.port[1].level[1],1],"Wait Name 1")
            wt.wait(20,level_control,[tp.port[1].level[1],2],"Wait Name 2")
            wt.wait(30,level_control,[tp.port[1].level[1],3],"Wait Name 3")
            wt.wait(40,level_control,[tp.port[1].level[1],4],"Wait Name 4")
            wt.wait(50,level_control,[tp.port[1].level[1],5],"Wait Name 5")
            wt.wait(60,level_control,[tp.port[1].level[1],6],"Wait Name 6")
            wt.wait(70,level_control,[tp.port[1].level[1],7],"Wait Name 7")
            wt.wait(80,level_control,[tp.port[1].level[1],8],"Wait Name 8")
            wt.wait(90,level_control,[tp.port[1].level[1],9],"Wait Name 9")
            wt.wait(100,level_control,[tp.port[1].level[1],10],"Wait Name 10")

        elif ch == 2:
            wt.cancel_wait("Wait Name 1")
            wt.cancel_wait("Wait Name 2")
            wt.cancel_wait("Wait Name 3")
            wt.cancel_wait("Wait Name 4")
            wt.cancel_wait("Wait Name 5")
            wt.cancel_wait("Wait Name 6")
            wt.cancel_wait("Wait Name 7")
            wt.cancel_wait("Wait Name 8")
            wt.cancel_wait("Wait Name 9")
            wt.cancel_wait("Wait Name 10")
            tp.port[1].level[1].value = 0

        elif ch == 3:
            tp.port[1].level[1].value = 0
            wt.wait(10,level_control,[tp.port[1].level[1],1])
            wt.wait(20,level_control,[tp.port[1].level[1],2])
            wt.wait(30,level_control,[tp.port[1].level[1],3])
            wt.wait(40,level_control,[tp.port[1].level[1],4])
            wt.wait(50,level_control,[tp.port[1].level[1],5])
            wt.wait(60,level_control,[tp.port[1].level[1],6])
            wt.wait(70,level_control,[tp.port[1].level[1],7])
            wt.wait(80,level_control,[tp.port[1].level[1],8])
            wt.wait(90,level_control,[tp.port[1].level[1],9])
            wt.wait(100,level_control,[tp.port[1].level[1],10])

        elif ch == 4:
            wt.cancel_all_wait()
            tp.port[1].level[1].value = 0
        
        elif ch == 5:
            wt.wait_until(io_state,rel_control,[relay[0],True],"Wait Name Until 1")

        elif ch == 6:
            wt.cancel_wait_until("Wait Name Until 1")
            rel_control(relay[0],False)
        
        elif ch == 7:
            wt.timed_wait_until(lambda:io[0].digitalInput.value,100,rel_control,[relay[0],True])

        elif ch == 8:
            wt.cancel_all_wait_until()
            rel_control(relay[0],False)
        
        elif ch == 9:
            wt.wait(50,send_data)
        
        elif ch == 10:
            wt.cancel_wait("Wait Name Send 1")
            wt.cancel_wait("Wait Name Send 2")
            wt.cancel_wait("Wait Name Send 3")
            tp.port[1].send_command("^TXT-1,0,")
for ch in range(1,11):
    tp.port[1].button[ch].watch(button_event)

# MUSE ONLINE EVENT
def muse_online(e):
    serial[0].setCommParams("9600",8,1,"NONE","232")
    serial[0].setFlowControl("NONE")

    rel_control(relay[0],False)
    rel_control(relay[1],False)
    rel_control(relay[2],False)
    rel_control(relay[3],False)
    rel_control(relay[4],False)
    rel_control(relay[5],False)
    rel_control(relay[6],False)
    rel_control(relay[7],False)

    io[0].mode = "INPUT"
    io[0].inputMode = "DIGITAL"
    io[0].digitalInput2KPullup = True
muse.online(muse_online)

context.run(globals())
