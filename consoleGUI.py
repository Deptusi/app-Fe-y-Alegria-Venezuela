# -*- coding: utf-8 -*-
import random,os
from kivy.app                   import App
from kivy.core.window           import Window
from kivy.uix.boxlayout         import BoxLayout
from kivy.uix.textinput         import TextInput
from kivy.uix.scrollview        import ScrollView
from kivy.uix.label             import Label
from kivy.logger                import LoggerHistory

from kivy.modules.console import Console, ConsoleAddon, ConsoleLabel, Clock
import queue,logging
from supportFiles.privateLogger import privateLogger
logger=logging.getLogger()

class mainTestApp(App):
    def build(self):
        Window.clearcolor=(204/255,179/255,224/255,1)
        return consoleGUI()

class consoleGUI(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        self.scroll=TextInput(text='',multiline=True,disabled=False,
            size_hint=(1,self.height)
        )
        self.add_widget(self.scroll)
        self.log_queue = queue.Queue()
        self.queueHandler=QueueHandeler(self.log_queue)
        formatter = logging.Formatter('%(message)s')
        self.queueHandler.setFormatter(formatter)
        logger.addHandler(self.queueHandler)
        self.activate()
    def activate(self):
        self.event = Clock.schedule_interval(self.logDisplay, 1 / 2.)
    def logDisplay(self,text):
        while True:
            try:
                value=self.log_queue.get(block=False).msg
                self.scroll.text+=f'\n{value}'
                self.scroll_y= 1-self.scroll.text.count('\n')/self.scroll.height*self.scroll.line_height
            except queue.Empty:
                return
            else:
                continue

class QueueHandeler(logging.Handler):
    def __init__(self,logQueue) -> None:
        super().__init__()
        self.log_queue=logQueue
    def emit(self, record):
        self.log_queue.put(record)


if __name__=='__main__':
    mainTestApp().run()

