import tkinter as tk
from pathlib import Path
from threading import Lock

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

from .utils.scheduler import Scheduler


class Application(tk.Tk):
    def __init__(self, calculator_main, calculator_dt=50, visualizer_dt=50, title='GUI App'):
        """
        GUIを実行しつつ、要求された値に対応するウィジェットを適宜追加する
        
        Parameters
        ----------
        calculator_main: callable
            一定時間ごとに実行したい計算
        calculator_dt: float, optional
            calculator_main 関数の実行間隔[ms]
        visualizer_dt: float, optional
            グラフの更新間隔[ms]
        title: str, optional
            GUIのタイトル
        """
        super().__init__()
        self.scheduler = Scheduler(tasks=[calculator_main], interval_sec=calculator_dt * 1.0e-3)
        self.protocol("WM_DELETE_WINDOW", self._stop_and_destroy) # ウィンドウが閉じられるときにループを止める
        
        self.title(title)
        
        # 画面をグラフを配置する場所とボタン等を配置する場所に分ける
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(side=tk.RIGHT)
        self.canvas_frame = tk.Frame(self, bg='yellow')
        self.canvas_frame.pack(expand=1, fill=tk.BOTH)#(side=tk.LEFT + tk.RIGHT)
        
        #self.figures = {}
        self.figure = None
        self.sliders = {}
        self.toggle_buttons = {}
        self.buttons = {}
        self.texts = {}
        
        self.on_image = tk.PhotoImage(file = Path(__file__).parent / "button_image/toggle_on.png").subsample(5)
        self.off_image = tk.PhotoImage(file = Path(__file__).parent / "button_image/toggle_off.png").subsample(5)
        
        self.dt = visualizer_dt # グラフの更新間隔
        
        self._lock = Lock() 
        
    def _stop_and_destroy(self):
        self.scheduler.stop()
        self.destroy()
        
    def start(self):
        self.scheduler.start()
        self.mainloop()

    def add_figure(self, figure):
        with self._lock:
            if self.figure is None:
                assert isinstance(figure, Figure)
                self.figure = figure
                self.figure.register_app(self)
                
    def add_figure_from_func(self, init_anim, update_anim, blit=False):
        with self._lock:
            if self.figure is None:
                self.figure = Figure(init_anim, update_anim, blit)
                self.figure.register_app(self)
        
    def _add_slider(self, name, from_=0, to=1, resolution=None, default=None):
        with self._lock:
            if name not in self.sliders:
                self.sliders[name] = Slider(self, name, from_, to, resolution, default)
        
    def _add_toggle_button(self, name):
        with self._lock:
            if name not in self.toggle_buttons:
                self.toggle_buttons[name] = ToggleButton(self, name, self.on_image, self.off_image)
        
    def _add_button(self, name, on_click):
        with self._lock:
            if name not in self.buttons:
                self.buttons[name] = Button(self, name, on_click)
        
    def text(self, name, text=""):
        with self._lock:
            if name in self.texts:
                self.texts[name].set_text(text)
            else:
                self.texts[name] = Text(self, name, text)
        
    def get_float(self, key, from_=0, to=1, resolution=None, default=None):
        """
        GUIのスライダーからfloatを取得する
        
        Parameters
        ----------
        key: str
            項目名
        from_: float, default=0
            スライダーの最小値
        to: float, default=1
            スライダーの最大値
        resolution: float, optional
            スライダーの解像度
        default: float, optional
            まだGUIにスライダーを追加していないときに返す値
            指定がなければスライダー追加前はfrom_が返る
        """
        if key in self.sliders:
            # GUIにすでにウィジェットがあったら
            return self.sliders[key].var.get()
        else:
            # GUIにまだウィジェットがなかったら
            # ウィジェットを追加しつつ、今回はデフォルト値を返す
            self._add_slider(
                name=key,
                from_=from_,
                to=to,
                resolution=resolution,
                default=default,
            )
            # 以下をdefault or from_ にするとdefault=0, from_を-1とかにしたときに-1が返ってきてしまう
            return from_ if default is None else default 
        
    def get_bool(self, key, default=None):
        """
        GUIのトグルボタンからboolを取得する
        
        Parameters
        ----------
        key: str
            項目名
        default: bool, optional
            まだGUIにトグルボタンを追加していないときに返す値
            デフォルトはFalse
        """
        if key in self.toggle_buttons:
            return self.toggle_buttons[key].is_on
        else:
            self._add_toggle_button(key)
            return default or False    
    
    @staticmethod
    def function_name(func):
        """関数に一意な名前を付ける"""
        if hasattr(func, "__self__"):
            # クラスメソッドのとき
            # クラス名.関数名　を返す
            class_name = func.__self__.__class__.__name__
            return f"{class_name}.{func.__name__}"
        else:
            # クラスメソッドでないとき
            return func.__name__
    
    def button(self, func):
        """
        GUIにボタンを追加し、
        ボタンが押されたら関数を実行するよう登録する
        """
        # GUIにボタンを追加
        key = self.function_name(func)
        self._add_button(key, func)

class Figure:
    def __init__(self, init_anim=None, update_anim=None, blit=False):
        self.fig = plt.figure(figsize=(5, 5))
        self.ax = self.fig.add_subplot(111)
        self.ani = None
        self.blit = blit
        
        if init_anim is not None:
            assert callable(init_anim)
            self.init_anim = lambda : init_anim(self.ax)
            
        if update_anim is not None:
            assert callable(update_anim)
            self.update_anim = lambda dt: update_anim(dt, self.ax)
        
    #def init_anim(self):
    #    pass
    
    #def update_anim(self, dt):
    #    pass
        
    def register_app(self, app):
        self.app = app
        self.canvas = FigureCanvasTkAgg(self.fig, self.app.canvas_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.draw_plot()
        
    def draw_plot(self, event=None):
           # すでにアニメーションが実行されている場合はevent_source.stopで停止
        if self.ani is not None:
            self.ani.event_source.stop()
            self.ax.clear()

        self.ani = FuncAnimation(
              self.fig,  # Figureオブジェクト
              self.update_anim,  # グラフ更新関数
              init_func=self.init_anim,  # 初期化関数
              interval = self.app.dt,  # 更新間隔(ms)
              blit = self.blit,
        )
        self.canvas.draw()
        
class Widget:
    def __init__(self, app, name):
        self.app = app
        self.name = name
        
        # 枠の作成
        self.frame = tk.Frame(app.control_frame, bd=1, relief=tk.SUNKEN)
        self.frame.pack(fill=tk.X)
    
        # 説明テキストの作成
        self.control_label = tk.Label(self.frame, text=self.name)
        self.control_label.pack(side='left')
        
class Slider(Widget):
    def __init__(self, app, name, from_=0, to=1, resolution=None, default=None):
        super().__init__(app, name)
        
        self.var = tk.DoubleVar()
        self.x_scale = tk.Scale(
            self.frame,
            variable=self.var,
            from_=from_,
            to=to,
            resolution=(to - from_) * 0.01 if resolution is None else resolution,
            orient=tk.HORIZONTAL,
        )
        self.x_scale.pack(anchor=tk.E)
        
class ToggleButton(Widget):
    def __init__(self, app, name, on_image, off_image):
        super().__init__(app, name)
        self.on_image = on_image
        self.off_image = off_image
        self.is_on = False
        
        self.button = tk.Button(
            self.frame, 
            image = off_image, 
            relief='sunken', 
            bd = 0, 
            command = self.switch
        )
        self.button.pack(anchor=tk.E)
    
    def switch(self):
        if self.is_on:
            self.button.config(image = self.off_image)
            self.is_on = False
        else:
            self.button.config(image = self.on_image)
            self.is_on = True
            
class Button(Widget):
    def __init__(self, app, name, on_click):
        super().__init__(app, name)
        
        self.button = tk.Button(
            self.frame, 
            text=self.name,
            command = on_click
        )
        self.button.pack(anchor=tk.E)
        
class Text(Widget):
    def __init__(self, app, name, s=""):
        super().__init__(app, name)
        self.text = tk.StringVar(value=s)
        self.label = tk.Label(
            self.frame,
            textvariable = self.text,
        )
        self.label.pack(anchor=tk.E)
        
    def set_text(self, s):
        self.text.set(s)