from . import time_manager
import threading
from concurrent.futures import ThreadPoolExecutor

class Scheduler:
    def __init__(self, tasks=[], interval_sec=1, max_workers=10):
        self.tasks = tasks
        self.interval_sec = interval_sec
        self.max_workers = max_workers
        self.should_stop = False
        self.thread = threading.Thread(target=self.schedule)
        
    def __del__(self):
        self.stop()
        
    def exec_all_tasks(self):
        for task in self.tasks:
            task()
        
    def schedule(self):
        """任意の処理を定期的に実行する"""
        while not self.should_stop:
            time_manager.wait_if_pace_too_fast(self.interval_sec)
            self.exec_all_tasks()
        
        """
        # 必要以上にスレッドが生成されないようにスレッドプールを使う
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while not self.should_stop:
                time_manager.wait_if_pace_too_fast(self.interval_sec)
                future = executor.submit(self.exec_all_tasks)
        """
    
    def register(self, task):
        self.tasks.append(task)
    
    def start(self):
        self.thread.start()
    
    def stop(self):
        self.should_stop = True