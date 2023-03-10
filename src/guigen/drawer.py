import numpy as np

#from matplotlib import pyplot as plt

from .app import Figure
from .utils import time_manager

class TimeDeque:
    def __init__(self, save_time_second = 10):
        """
        過去x秒間に与えられた値を保存する
        
        Parameters
        ----------
        save_time_second : int, optional
            与えられた値を何秒間保存するか
        """
        self.save_time = np.timedelta64(save_time_second, 's')
        self.times = []
        self.values = []
        
    def append(self, value):
        """
        要素を追加する
        """
        self.times.append(time_manager.now())
        self.values.append(value)
        self.refresh()
        
    def refresh(self):
        """
        現在時刻を更新して古い値を削除する
        """
        oldest_time = time_manager.now() - self.save_time
        oldest_idx = np.searchsorted(self.times, oldest_time)
        self.times = self.times[oldest_idx:]
        self.values = self.values[oldest_idx:]
    
    def __getitem__(self, i):
        return self.values[i]
    
    def __len__(self):
        return len(self.values)
    
    def __iter__(self):
        yield from self.values

class PlotData:
    def __init__(self, ax, save_time_second, **kwargs):
        self.ax = ax
        self.x = TimeDeque(save_time_second=save_time_second)
        self.kwargs = kwargs
        self.line = None
        
    def append(self, x, y):
        self.x.append((x, y))
                
    def plot(self):
        if self.line is None:
            if len(self.x) > 0:
                self.line, = self.ax.plot(*np.transpose(self.x), **self.kwargs)
        else:
            self.line.set_data(*np.transpose(self.x))
            
class ScatterData:
    def __init__(self, ax, save_time_second, **kwargs):
        self.ax = ax
        self.values = TimeDeque(save_time_second=save_time_second)
        self.kwargs = kwargs
        self.line = None
        
    def append(self, x, y, size):
        self.values.append((x, y, size))
    
    def plot(self):
        self.values.refresh()
        if self.line is None:
            if len(self.values) > 0:
                x, y, size = zip(*self.values)
                self.line = self.ax.scatter(x, y, size, **self.kwargs)
        else:
            x, y, size = zip(*self.values)
            self.line.set_offsets(np.transpose([x, y]))
            self.line.set_sizes(size)
            self.ax.update_datalim(self.line.get_datalim(self.ax.transData))
            
class RealTimeDrawer(Figure):
    def __init__(self, blit=False):
        super().__init__(blit=blit)
        self.plot_data = {}
        self.scatter_data = {}
        
    def add_plot(self, label, save_time_second=60, **kwargs):
        kwargs['label'] = label
        self.plot_data[label] = PlotData(self.ax, save_time_second=save_time_second, **kwargs)
        
    def add_scatter(self, label, save_time_second=60, **kwargs):
        kwargs['label'] = label
        self.scatter_data[label] = ScatterData(self.ax, save_time_second=save_time_second, **kwargs)
        
    def append_plot_data(self, x, y, label):
        self.plot_data[label].append(x, y)
        
    def append_scatter_data(self, x, y, size, label):
        self.scatter_data[label].append(x, y, size)
    
    def update_anim(self, dt):
        self.ax.ignore_existing_data_limits = True
        for p in self.plot_data.values():
            p.plot()
        self.ax.relim()
        for p in self.scatter_data.values():
            p.plot()
        
        if len(self.ax.artists) > 0:
            self.ax.legend()

        # 軸の範囲を調整
        self.ax.autoscale_view(True,True,True)