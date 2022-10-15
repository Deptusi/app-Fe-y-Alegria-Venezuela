# -*- coding: cp1252 -*-
""" Global imports """
import os,sys,tkinter,pandas,logging,datetime,threading,time,warnings,traceback
from tkinter.filedialog                         import askopenfilename,askdirectory,asksaveasfilename,askopenfilenames
pandas.options.display.float_format = '{:.,2f}'.format
sys.path.append(os.getcwd())
warnings.filterwarnings(action='once')
""" Kivy imports """
from kivy.app                                   import App
from kivy.uix.gridlayout                        import GridLayout
from kivy.uix.boxlayout                         import BoxLayout
from kivy.uix.textinput                         import TextInput
from kivy.uix.button                            import Button
from kivy.uix.label                             import Label
from kivy.uix.floatlayout                       import FloatLayout
from kivy.uix.pagelayout                        import PageLayout
from kivy.uix.anchorlayout                      import AnchorLayout      
from kivy.uix.widget                            import Widget
from kivy.uix.spinner                           import Spinner
from kivy.uix.dropdown                          import DropDown
from kivy.uix.togglebutton                      import ToggleButton
from kivy.core.window                           import Window
from kivy.uix.image                             import Image
from kivy.uix.switch                            import Switch
from kivy.uix.checkbox                          import CheckBox
from kivy.utils                                 import get_color_from_hex
from kivy.factory                               import Factory
from kivy.lang                                  import Builder
from kivy.uix.popup                             import Popup

""" Local imports """
import mainTransform                            as codeTransform
import config
import consoleGUI
logger=config.logger

""" Define Classes """
class mainFyAApp(App):
    def build(self):
        Window.clearcolor=(config.__colors__[0])
        self.root=Builder.load_file('supportFiles\AppFyA.kv')
        return FyAApp()

class FyAApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spacing= '10dp'
        self.padding= '5dp'
        self.orientation='vertical'
        self.add_widget(logoLayout())
        fileList=[
            'Carpeta de archivos',
            'Lista de archivos',
        ]
        self.fileBox=fileSelectBox(fileList,size_hint_y=0.3)
        self.executeBox=executeBox(size_hint_y=0.5/4)
        self.add_widget(self.fileBox)
        self.add_widget(self.executeBox)
        console=consoleGUI.consoleGUI(size_hint_y=0.2)
        self.add_widget(console)
        threading.Thread(target=sendMadeBy).start()
    
class fileSelectBox(BoxLayout):
    def __init__(self,fileList, **kwargs):
        super().__init__(**kwargs)
        self.orientation='vertical'
        self.rowList=[fileSelectRow(n) for n in fileList]
        self.add_widget(Label(size_hint_y=0.2))
        for index,file in enumerate(fileList):
            self.add_widget(Label(text=f'Seleccione {file}',halign='left',size_hint_y=0.3))
            self.add_widget(self.rowList[index])
        pass

class fileSelectRow(BoxLayout):
    def __init__(self,name, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y=0.5
        self.name=name
        self.path=None
        self.orientation='horizontal'
        self.label=TextInput(text=f'{name}',disabled=True)
        self.checkbox=CheckBox(disabled=True,)
        self.button=Button(text='...',)
        
        self.button.bind(on_press=self.selectFileButton)
        self.buttons=BoxLayout(orientation='horizontal',size_hint=(0.1,1))
        self.buttons.add_widget(self.checkbox)
        self.buttons.add_widget(self.button)
        
        self.add_widget(self.label)
        self.add_widget(self.buttons)
        if self.name=='Ubicacionn de guardado':
            try:
                self.readFile(config.__defaultSaveLocation__)
            except:
                self.selectFileButton(None)
    def selectFileButton(self,instance):
        logger.info(f'Leyendo {self.name}')
        if self.name!='Carpeta de archivos':
            funct=selectFiles
        else:
            funct=selectFolder
        try:
            path=funct(config.__defaultFolderPicker__)
        except:
            path=funct()

        try:
            self.readFile(path)
        except Exception as e:
            logger.error(f'No se pudo leer el archivo: {e}')
    def readFile(self,path):
        functionIDs={
            'Carpeta de archivos'       :readReportsFolder,
            'Lista de archivos'         :readReportsList,
        }
        try:
            functionIDs[self.name](path)
            self.path=path
            if self.name!="Lista de archivos":
                self.label.text=os.path.split(path)[1]
                self.checkbox.state='down'
            else:
                self.label.text=f"{len(path)} archivos seleccionados"
                self.checkbox.state='down'
        except Exception as e:
            logger.error(e)

class executeBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation='horizontal'
        self.dropDown=Spinner(text='Proceso a ejecutar',pos_hint={'x': 0.5, 'y': 0.25},size_hint_y=0.5)
        
        self.buttons        =BoxLayout(orientation='vertical')
        self.executeSaveBTN =Button(text='Ejecutar y Guardar')
        self.executeSaveBTN .bind(on_release=self.toggleEjecuccion)

        self.buttons.add_widget(self.executeSaveBTN)
        self.buttons.size_hint=(0.5,1)

        self.box=BoxLayout(orientation='vertical')
        self.setOperacion()
        self.add_widget(self.box)
        self.add_widget(self.buttons)
    def setOperacion(self):
        self.optionLabel=Label(text='Opciones')
        self.optionSelect=Spinner(text='Procesar Archivos',values=[
            'Procesar Carpeta','Procesar Archivos'
        ])
        self.optionBox=BoxLayout(orientation='horizontal')
        self.optionBox.add_widget(self.optionLabel)
        self.optionBox.add_widget(self.optionSelect)
        self.box.add_widget(self.optionBox)
    def guardarBD(self,instance,filelist):
        try:
            global reportsFolder
            pathSave=saveFilePrompt(f'BD Reporte de Rendimiento')
            extension=os.path.splitext(pathSave)[1]
            logger.info(f'Ejecutando BD Reporte de Rendimiento')
            startTimer=datetime.datetime.now()
            df=codeTransform.mergeTables(filelist)
            if extension=='.csv':
                df.to_csv(pathSave,sep=';',index=None,decimal=',')
            elif extension=='.xlsx':
                df.to_excel(pathSave,index=None)
            logger.info(f'Ejecuccion finalizada en {datetime.datetime.now()-startTimer}')
        except Exception as e:
            logger.error(f'No se pudo guardar la base de datos: {e}')
        return pathSave
    def toggleEjecuccion(self,instance):
        if self.optionSelect.text=='Procesar Carpeta':
            self.guardarBD(None,reportsFolder)
        elif self.optionSelect.text=='Procesar Archivos':
            self.guardarBD(None,reportsList)

class logoLayout(AnchorLayout):
    def popInstruccions(self):
        showInstruccions().open()
    pass

class MyLabel(Label):
   def on_size(self, *args):
      self.text_size = self.size

class showInstruccions(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title='Instrucciones'
        self.separator_color=config.__colors__[1]
        self.size_hint=(1,0.8)
        self.auto_dismiss=True
        self.box=BoxLayout(orientation='vertical')
        self.add_widget(self.box)
        self.pdfInstruccions=Button(text='Abrir Instrucciones en PDF')
        self.pdfInstruccions.bind(on_press=self.pdf)
        self.box.add_widget(self.pdfInstruccions)
        self.videoInstruccions=Button(text='Mostrar video explicativo')
        self.videoInstruccions.bind(on_press=self.video)
        self.box.add_widget(self.videoInstruccions)
    def pdf(self,event):
        os.startfile('supportFiles\Instructivo FyA Colombia.pdf')
        self.dismiss()
    def video(self,event):
        os.startfile('supportFiles\Instructivo FyA Colombia.mp4')
        self.dismiss()


""" Define Functions """
def mainFyA():
    try:
        app=mainFyAApp()
        app.run()
    except Exception as e:
        app.stop()
        app=mainFyAApp()
        app.run()
        

def readReportsList(filelist):
    global reportsList
    reportsList=filelist
    logger.info(f'Archivos leidos exitosamente')
def readReportsFolder(path:str):
    global reportsFolder
    try:
        logger.info('Leyendo carpeta')
        startTimer=datetime.datetime.now()
        for root, folders, files in os.walk(path):
            for file in files:
                extension=os.path.splitext(file.lower())[1]
                if extension=='.xlsx':
                    reportsFolder.append(os.path.join(root,file))
        logger.info(f'Carpeta leida exitosamente en {datetime.datetime.now()-startTimer}')
    except Exception as e:
        logger.error(f'No se pudo leer la carpeta {path}: {e}')
def setSaveFolder(path):
    config.__defaultSaveLocation__=path

def selectFiles(path=os.getcwd()):
    tkinter.Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filenames = askopenfilenames(
        initialdir=path,
        filetypes=(
                    ("Excel", "*xlsx"),
                    ("All files", "*.*"))
        ) # show an "Open" dialog box and return the path to the selected file
    return filenames
def saveFilePrompt(title,path=os.getcwd()):
    tkinter.Tk().withdraw()
    filename = asksaveasfilename(
        initialdir=path,
        initialfile=title,
        defaultextension=".csv",
        filetypes=(
                    ("CSV (Rapido)", "*.csv"),
                    ("Excel (Lento)", "*.xlsx"),
                    ("All files", "*.*"))
                    )
    return filename
def selectFolder(path=os.getcwd()):
    tkinter.Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askdirectory(initialdir=path) # show an "Open" dialog box and return the path to the selected file
    return filename
def sendMadeBy():
    time.sleep(0.5)
    logger.info('Hecho por Germán Bermúdez como parte del proyecto de Servicio Comunitario necesario para optar al título de Ingeniero Industrial ')
        
""" Define Variables """

reportsList=[]
reportsFolder=[]

""" Define Test """
def test():
    app=FyAApp()
    for child in [child for child in app.children]:  
        print(child) 
        if type(child)==logoLayout:
            app.remove_widget(child)
        if type(child)==executeBox:
            boxer=child
        if type(child)==fileSelectBox:
            for child2 in [child2 for child2 in child.children]:
                if type(child2)==fileSelectRow:
                    if child2.name=='Access ComitÃ© Comercial':
                        child2.readFile(r"C:\Users\u1263856\OneDrive - MMC\ComitÃ© comercial\Access ComitÃ© Comercial JUNIO 2022.csv")
                    if child2.name=='Libro Finanzas':
                        child2.readFile(r"C:\Users\u1263856\OneDrive - MMC\ComitÃ© comercial\Finanzas_20220727072022125158.csv")
    class testApp(App):
        def build(self):
            Window.clearcolor=(config.__colors__[0])
            self.root=Builder.load_file('supportFiles\AppFyA.kv')
            return app
    testApp().run()

""" Execution """
if __name__=='__main__':
    mainFyA()