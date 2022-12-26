# -- coding: utf-8 --
# https://zenn.dev/takahashi_m/articles/d0fb009398e92c562662
import threading
import tkinter as tk
from tkinter import ttk
from traininfo.traininfo import make_via_codes, make_disp_text


FONT = "Yu Gothic UI"
FONT_SIZE = 12

n_candidate = 3
via_name_list = [ # ★★入力してください
                     [('三軒茶屋', '渋谷'),   ('渋谷', '新宿')],
                     [('三軒茶屋', '池尻大橋')],
                     [('三軒茶屋', '表参道'), ('表参道', '赤坂見附'), ('赤坂見附', '東京')]
                 ]




class Application(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.master.geometry("650x200")
        self.master.title("Train Schedule")
        self.via_codes = make_via_codes(via_name_list) # 経路の表記方法を駅名から駅コードへ変換するためのデータ
        
        self.create_widgets()
    
    def create_widgets(self):
        # 経路
        self.frame_via = tk.Frame(self, pady=10)
        self.frame_via.pack()
        self.label_via = tk.Label(self.frame_via, font=(FONT,FONT_SIZE), text="経路")
        self.label_via.pack(side="left")
        self.com_via = ttk.Combobox(self.frame_via, justify="center", state='readonly', font=(FONT,FONT_SIZE), width=60)
        self.com_via["values"] = list(self.via_codes)
        self.com_via.current(0)
        self.com_via.pack()
        self.com_via.bind('<<ComboboxSelected>>', self.update)
        
        # 結果表示部
        self.frame_result = tk.Frame(self, pady=10)
        self.frame_result.pack()
        self.label_result=[]
        self.label_waiting=[]
        self.label_interval=[]
        self.update()
    
    # 経路が更新されたら行先の選択肢も変更する
    def update(self, event=None):
        # 表示をクリア
        for l in self.label_result:
            l.pack_forget()
        for l in self.label_interval:
            l.pack_forget()
        
        # 待機画面を表示
        for i in range(len(self.label_waiting)):
            self.label_waiting[i].pack_forget()
        self.label_waiting = [tk.Label(self.frame_result, font=(FONT,FONT_SIZE))]
        self.label_waiting[0].config(text = "searching...")
        self.label_waiting[0].pack()
        
        # 結果表示は別スレッドへ
        th = threading.Thread(target=self.makedisp, args=(event,))
        th.start()
    
    # 結果表示
    def makedisp(self, event=None):
        via_codes = self.via_codes[self.com_via.get()]
        n_result = via_codes.count('+')
        text_disp = make_disp_text(via_codes, n_candidate)
        
        self.label_waiting[0].pack_forget()
        self.label_waiting=[]
        self.label_result   = []
        self.label_interval = []
        self.label_result = [tk.Label(self.frame_result, font=(FONT,FONT_SIZE))]
        self.label_result[0].config(text = text_disp[0])
        self.label_result[0].pack(side=tk.LEFT)
        for i in range(1,n_result):
            self.label_interval += [tk.Label(self.frame_result, font=(FONT,FONT_SIZE))]
            self.label_interval[i-1].config(text = "   ")
            self.label_interval[i-1].pack(side=tk.LEFT)
            self.label_result += [tk.Label(self.frame_result, font=(FONT,FONT_SIZE))]
            self.label_result[i].config(text = text_disp[i])
            self.label_result[i].pack(side=tk.LEFT)

def main():
    root = tk.Tk()
    app = Application(root)
    app.mainloop()

if __name__ == "__main__":
    main()
