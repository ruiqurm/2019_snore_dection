"""



"""


from flask import Flask, jsonify,request,abort, send_file,Response
import time,json
from enum import Enum
import redis,pymongo
import os
from pathlib import Path
from werkzeug.utils import secure_filename
#from celery import Celery
from scipy import signal
from librosa import display
import librosa
from matplotlib import pyplot as plt
import hashlib
import numpy as np
import pyroomacoustics
UPLOAD_FOLDER = './data/'
ALLOWED_EXTENSIONS = {'wav'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JSON_AS_ASCII'] = False

if not os.path.exists("data"):
    os.mkdir("data")
if not os.path.exists("img"):
    os.mkdir("img")
config = {
            "order":None,
            "confirm_device":set(),
            "device_pos":{},
        }
option={
    "device":{
        "len":0,
        "name_list":[],
        "detail":{}
    },
    "order":{
            "len":0,
            "name_list":[],
            "detail":{}
    }
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
def get_time_stamp():
    return time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
def get_file_time(path):
    return time.ctime(os.path.getatime(path))
def get_file_detail(name):
    #此处的name是*.*.*.wav格式的
    #示例：mic1.1.asd.wav
    split_name = name.split('.')
    return {"full_name":name,
            "name":split_name[2],
            "device":split_name[0],
            "order":split_name[1],
            "create_time":get_file_time('./data/'+name),
            "size": round(os.path.getsize('./data/'+name)/1024/1024,5)}

def check_new(info,reset=False):
    parameters = ["device","order"]
    for parameter in parameters:
        if(reset==True and parameter=="device"):
            print("reseting")
            option[parameter]["name_list"] = [i[parameter] for i in info]
        else:
            option[parameter]["name_list"].extend([i[parameter] for i in info])
            option[parameter]["name_list"] = list(set(option[parameter]["name_list"]))
        option[parameter]["len"] = len(option[parameter]["name_list"])
        for i in info:
            if i[parameter] not in option[parameter]:
                option[parameter]["detail"][i[parameter]] = [i["full_name"]]
            else:
                option[parameter]["detail"][i[parameter]].append(i["full_name"])

        #不判重
def _update(reset=False):
    file_info = [get_file_detail(i.name) for i in Path('./data').glob("*.wav")]
    check_new(file_info,reset)
def clear_cache():
    pass
_update()
"""
声源定位
"""


def gcc_phat(sig, refsig, fs=1, max_tau=None, interp=16):
    '''
    This function computes the offset between the signal sig and the reference signal refsig
    using the Generalized Cross Correlation - Phase Transform (GCC-PHAT)method.
    '''

    # make sure the length for the FFT is larger or equal than len(sig) + len(refsig)
    n = sig.shape[0] + refsig.shape[0]

    # Generalized Cross Correlation Phase Transform
    SIG = np.fft.rfft(sig, n=n)
    REFSIG = np.fft.rfft(refsig, n=n)
    R = SIG * np.conj(REFSIG)

    cc = np.fft.irfft(R / np.abs(R), n=(interp * n))

    max_shift = int(interp * n / 2)
    if max_tau:
        max_shift = np.minimum(int(interp * fs * max_tau), max_shift)

    cc = np.concatenate((cc[-max_shift:], cc[:max_shift + 1]))

    # find max cross correlation index
    shift = np.argmax(np.abs(cc)) - max_shift

    tau = shift / float(interp * fs)

    return tau, cc

def tdoa(x1, y1, x2, y2, x3, y3, r2, r3):
    """
    by @ruiqurm
    参数：
    x1,x2,y1,y2,x3,y3是坐标；
    r2,r3声源到第一个麦克风与第2/3个麦克风的距离之差

    返回值：
    两个可能的解。
    """
    P1 = -np.linalg.inv(np.array([[x2 - x1, y2 - y1], [x3 - x1, y3 - y1]]))
    P2 = np.array([[r2], [r3]])
    P3 = 1 / 2 * np.array([[-(x2 ** 2 + y2 ** 2) + (x1 ** 2 + y1 ** 2) + r2 ** 2],
                           [-(x3 ** 2 + y3 ** 2) + (x1 ** 2 + y1 ** 2) + r3 ** 2]])
    X1 = [[x1], [y1]]

    A = ((P1 @ P2).T @ P1 @ P2 - 1)[0][0]
    B = ((P1 @ P2).T @ (P1 @ P3 - X1) + (P1 @ P3 - X1).T @ P1 @ P2)[0][0]
    C = ((P1 @ P3 - X1).T @ (P1 @ P3 - X1))[0][0]
    delta = B ** 2 - 4 * A * C
    t1, t2 = (-B + delta) / (2 * A), (-B - delta) / (2 * A)
    return (P1 @ P2 * t1 + P1 @ P3, P1 @ P2 * t2 + P1 @ P3)

def getDoa(x, pos, fs, nfft=2048):
    '''
    by @ruiqurm
    parameter:
    x: list，每个元素都是一个1*n的np.array，里面是语音序列。
    pos: list，每个元素都是一个{"x":int,"y":int}形式的字典，保存的是传感器的位置
    fs: int,wav文件的采样率
    nfft: int,短时傅里叶变换的参数，默认为2048，具体见http://librosa.github.io/librosa/generated/librosa.core.stft.html?highlight=stft#librosa.core.stft

    return:
    无返回值
    但会显示一张图像。
    '''
    plt.clf()
    stft = np.array([librosa.stft(i) for i in x])  # 先做短时傅里叶变换
    doa = pyroomacoustics.doa.MUSIC(np.array([[i["x"] for i in pos], [i["y"] for i in pos]]), fs, nfft)
    doa.locate_sources(stft)
    doa.polar_plt_dirac()
    plt.title("雷达图")
    save_name = get_random_name()
    plt.savefig("./img/{}.jpg".format(save_name))
    return save_name

def sound_source(data,fs):
    return []

'''
判断是否是呼噜声和波形图
'''
#base_files=[]
base_files = [librosa.load("./compare/{}".format(i.name))[0] for i in Path('./compare').glob("*.wav")]

def get_random_name():    #通过MD5的方式创建
    m=hashlib.md5()
    m.update(bytes(str(time.time()),encoding='utf-8'))
    return m.hexdigest()

def show_fft(x,sampling_rate,fft_size=None):
    plt.clf()
    """
    参考自：https://blog.csdn.net/qq_40587575/article/details/83316980
    """
    if fft_size is None:
        fft_size = len(x)#FFT长度
    xf = np.fft.rfft(x) / fft_size  #返回fft_size/2+1 个频率
    freqs = np.linspace(0, sampling_rate/2, fft_size/2+1)   #表示频率
    xfp = np.abs(xf) * 2    #代表信号的幅值，即振幅
    plt.plot(freqs, xfp)
    plt.title('频域图')
    plt.xlabel(u"频率(Hz)")
    plt.ylabel(u'幅值')
    save_name = get_random_name()
    plt.savefig("./img/{}.jpg".format(save_name))
    return save_name
def show_oscillograph(x,sampling_rate):
    plt.clf()
    plt.title('波形图') #改变图标题字体
    librosa.display.waveplot(x,sampling_rate)
    save_name = get_random_name()
    plt.savefig("./img/{}.jpg".format(save_name))
    return save_name
def show_zero_rate(x,sampling_rate):
    plt.clf()
    tmp = librosa.feature.zero_crossing_rate(x,frame_length=2048)
    x = tmp.reshape(tmp.shape[1])
    plt.plot(x)
    plt.title('过零率')
    plt.xlabel(u"帧(Frame)")
    plt.ylabel(u'过零率')
    save_name = get_random_name()
    plt.savefig("./img/{}.jpg".format(save_name))
    return save_name
def show_mel(x,sampling_rate):
    plt.clf()
    plt.title('梅尔频率倒谱图')
    display.specshow(librosa.feature.mfcc(x,sampling_rate),sr = sampling_rate,x_axis='time')
    save_name = get_random_name()
    plt.savefig("./img/{}.jpg".format(save_name))
    return save_name

show_image_func = {"mel":show_mel,"zero_rate":show_zero_rate,"oscillograph":show_oscillograph,"fft":show_fft}

def show_image(x,sampling_rate,imgCategory=("mel","zero_rate","oscillograph","fft")):
    return {i:"/img/"+show_image_func[i](x,sampling_rate)+".jpg" for i in imgCategory}
#x = show_image(model,model_fs,"test")

def is_snore(x,detail=False):
    #如果互相关函数的最大值在8以上，大概率就是呼噜声。
    if detail == True:
        return [max(signal.correlate(i,x)) for i in base_files]
    else:
        return round(np.mean([max(signal.correlate(i,x)) for i in base_files]),4)



"""
路由部分
"""
@app.route('/api/audio/', methods=['UPDATE'],strict_slashes=False)
@app.route('/api/option/',methods=['UPDATE'],strict_slashes=False)
def update():
    _update()
    jsonify(option),200


@app.route('/api/audio/', methods=['POST'],strict_slashes=False)
def upload():
    file = request.files['files']
    if file and allowed_file(file.filename):
        if "device" not in file.headers or "order" not in file.headers:
            abort(400,"lack of parameter 'device'")
        filename = secure_filename(file.headers["device"])+"."+file.headers["order"]+"."+file.filename
        if (os.path.exists(r'./data/{}'.format(filename))):
            if ("ignore" not in file.headers):
                abort(403, "file existed")
            if (file.headers["ignore"]==0):
                abort(403,"file existed")
            else:
                os.remove(r'./data/{}'.format(filename))
                file.save(r'./data/{}'.format(filename))
                return jsonify({"status": "success", "filename": filename,"info":"file existed but replace"})
        else:
            file.save(r'./data/{}'.format(filename))
            return jsonify({"status":"success","filename":filename})
    update()
    return jsonify({"status":"failed"}),400

@app.route('/api/audio/<name>/', methods=['GET'],strict_slashes=False)
def getFile(name):
    filename="./data/"+name+'.wav'
    return send_file(filename)

@app.route('/api/audio/', methods=['GET'],strict_slashes=False)
@app.route('/api/audio/list/', methods=['GET'],strict_slashes=False)
def Filelist():
    root = Path('./data')
    tmp = [i.name for i in root.glob("*.wav")]
    return jsonify({"file":[get_file_detail(i) for i in tmp],"len":len(tmp)})
    #tmp[:-4]是为了去除尾部的".wav"

@app.route('/api/audio/<name>/', methods=['DELETE'],strict_slashes=False)
def deleteFile(name):
    name = secure_filename(name)
    name = "./data/" + name +".wav"
    print(name)
    if not os.path.exists(name):
        return jsonify({"status": "failed", "error_message": "File not exists"}), 404
    try:
        os.remove(name)
    except Exception as e:
        return jsonify({"status":"failed","error_message":e}),500
    update()
    return jsonify({"status":"succss"})

@app.route('/api/config/',methods=['POST'],strict_slashes=False)
def confirm():
    try:
        if "order" in request.json:
            config["order"] = str(request.json.get("order"))
        if "confirm_device" in request.json:
            device = request.json.get("confirm_device")
            if device["mode"] == "update":
                data = [i for i in device["data"] if i in option["device"]["name_list"]]
                config["confirm_device"].update(data)
            elif device["mode"] == "replace":
                data = [i for i in device["data"] if i in option["device"]["name_list"]]
                config["confirm_device"]=set(data)
            elif device["mode"] == "clear":
                config["confirm_device"].clear()
        if "pos" in request.json:
            pos = request.json.get("pos")
            # 不判断是否存在设备
            if pos["mode"] == "update":
                for device in pos["data"]:
                    config["device_pos"][device["name"]] = device["pos"]
            elif pos["mode"] == "replace":
                config["device_pos"] = [i["pos"] for i in pos["data"]]
            elif pos["mode"] == "clear":
                config["device_pos"].clear()
    except Exception as e:
        abort(400,e)
    return_config = config.copy()
    return_config["confirm_device"] = list(config["confirm_device"])
    return jsonify(return_config),200

@app.route('/api/config/',methods=['GET'],strict_slashes=False)
def getConfig():
    return_config = config.copy()
    return_config["confirm_device"] = list(config["confirm_device"])
    return jsonify(return_config), 200

@app.route('/api/option/',methods=['GET'],strict_slashes=False)
def getOption():
    return jsonify(option),200

@app.route('/api/option/<parameter>',methods=['GET','POST'],strict_slashes=False)
def getOption2(parameter):
    if(parameter=="order"or parameter=="device"):
        return jsonify(option[parameter]["name_list"]),200
    return 404

@app.route('/api/option/',methods=['POST'],strict_slashes=False)
def addOption():
    #只可以添加新设备或者恢复初始状态
    d = request.json.get("device")
    if d["mode"]=="update":
        option["device"]["name_list"].extend(d["data"])
        option["device"]["name_list"] = list(set(option["device"]["name_list"]))
        #去重
        option["device"]["len"] = len(option["device"]["name_list"])
    if d["mode"]=="reset":
        _update(reset=True)
    return jsonify(option),200

@app.route('/api/report/',methods=['GET','POST'],strict_slashes=False)
def report():
    #留给麦克风阵列的代码
    # report_id = get_random_name()
    # return_json = {"id":report_id}
    # try:
    #     files =  option["order"]["detail"][config["order"]]
    #     files = [i for i in files if i.split('.')[0] in config["confirm_device"]]
    # except Exception as e:
    #     abort(400,e)
    # for i in config["confirm_device"]:
    #     if i not in config["device_pos"]:
    #         abort(400,'lack of device "{}" position'.format(i))
    # data = [librosa.load("./data/{}".format(i)) for i in files]
    try:
        return_json = {}
        if "file_name" not in request.json or "mode" not in request.json:
            abort(400,"lack of parameter")
        name = request.json.get("file_name")
        mode = request.json.get("mode")
        data,fs = librosa.load(r'./data/{}'.format(name))

        #缺麦克风
        # if "sound_source" in request.json:
        #     #mode = request.json.get("sound_source")["mode"]
        #     return_json["sound_source"]=sound_source(np.array([i for i in files]),fs)

        if "is_snore" in mode:
            tmp = is_snore(data,detail=False)
            return_json["is_snore"] = 1 if (tmp>6) else 0

        if "show_image" in mode:
            return_json["show_image"] = show_image(data,fs)
        return jsonify(return_json), 200
    except Exception as e:
        abort(400,e)

@app.route('/api/img/<name>',methods=['GET','POST'],strict_slashes=False)
def getImg(name):
    name = secure_filename(name)
    if not os.path.exists('./img/{}'.format(name)):
        abort(404)
    return Response(open('./img/{}'.format(name),"rb"), mimetype="image/jpeg")

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=False,host="0.0.0.0")
    #在Centos下运行使用后者