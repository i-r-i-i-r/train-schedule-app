import requests
from bs4 import BeautifulSoup as bs
from urllib import request as ur
import datetime as dt

_API_KEY = "xxxxxx" # API keyをここに記載してください

# 24時以降でバグらないか確認する
def make_disp_text(via_code, n_candidate):
    # 現在の日付と時刻を取得
    now        = dt.datetime.today()
    date_now   = now.strftime("%Y%m%d")
    hour_now   = now.strftime("%H")
    minute_now = now.strftime("%M")
    
    # 表示内容の取得
    text_disp = _search_course(via_code, date_now, [hour_now, minute_now], n_candidate)
    text_disp =  ["\n".join(t) for t in text_disp]
    return text_disp


# 経路の名称とコードのデータを作成
def make_via_codes(via_name_list):
    via_code_list = []
    via_disp_list = []
    for via_name in via_name_list:
        # 処理対象の駅の名称
        station_names = []
        for v in via_name:
            station_names += [v[0], v[1]]
        
        # 処理対象の駅のコード
        station_codes = {}
        for n in station_names:
            station_codes.update(_get_station_property(n))
        
        # 駅名から経路コードに変換
        count=0
        via_code = ""
        via_disp = "[ "
        for v in via_name:
            if count>0:
                via_code += "-"
                via_disp += " ]  [ "
            c = [station_codes[vi] for vi in v]
            via_disp += " -> ".join(v)
            via_code += "+".join(c)
            count += 1
        
        via_disp += " ]"
        via_code_list += [via_code]
        via_disp_list += [via_disp]
    
    return dict(zip(via_disp_list,via_code_list))


# 駅名(ある程度不正確でもよい)からの、正確な駅名と駅コードを取得
def _get_station_property(name):
    url = "http://api.ekispert.jp/v1/json/station"
    querystring = {"name":name,
                   "key": _API_KEY}
    
    response = requests.request("GET", url, params=querystring)
    points = response.json()["ResultSet"]["Point"]
    if type(points) is list:
        code = [p["Station"]["code"] for p in points]
        name = [p["Station"]["Name"] for p in points]
    else:
        code = [points["Station"]["code"]]
        name = [points["Station"]["Name"]]
    return dict(zip(name,code))


def _search_course(via, dep_date, dep_time, n_candidate):
    # dep_date: str (yyyymmdd), dep_time: list(str, str) (hh, mm)
    # -: 探索しない経路(徒歩区間など)
    # +: 探索する経路
    interval = 1 # 経路切替の際のインターバル(乗り換えに最低限かかる時間など。可変にしてもそれ程うれしくないので1に固定) [min]
    result_list = []
    for v in via.split("-"):
        for i in range(len(v.split("+"))-1):
            result = []
            while len(result)<n_candidate:
                result += _search_course_single(v.split("+")[i], v.split("+")[i+1], dep_date, dep_time)
                # 最も遅い出発時刻+1を次の探索の出発時刻にする
                minutes = [int(i[:2])*60+int(i[3:5]) for i in result]
                index_dep_last = minutes.index(max(minutes))
                next_dep_time = result[index_dep_last][:5].split(":")
                dep_time = [ next_dep_time[0], str( int(next_dep_time[1])+1 )]
            
            result_list += [result[:n_candidate]]
            # 最も早い到着時刻を次経路の出発時刻にする
            minutes = [int(i[8:10])*60+int(i[11:13]) for i in result]
            index_arr_fastest = minutes.index(min(minutes))
            next_dep_time = result[index_arr_fastest][8:13].split(":")
            dep_time = [next_dep_time[0], str(int(next_dep_time[1])+interval)]
    
    return result_list


def _search_course_single(code_from, code_to, dep_date, dep_time):
    url = "https://roote.ekispert.net/result?arr_code="+code_to+\
          "&connect=true&dep_code="+code_from+\
          "&hour="+dep_time[0]+"&minute="+dep_time[1]+\
          "&sleep=false&sort=time&surcharge=3&type=dep&yyyymmdd="+dep_date
    #print(url)
    response = ur.urlopen(url)
    soup = bs(response, 'html.parser')
    response.close()
    s1 = soup.find('table', class_='candidate_list_table tabs_content')
    s2 = s1.find_all('p', class_='candidate_list_txt')
    
    return [s2[i].text for i in range(0,len(s2),3)] # 乗り換え回数: s2[i*3+1].text



