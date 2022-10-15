# -*- coding: cp1252 -*-
import os, datetime
import pandas, xlwings
import config
logger=config.logger

""" Define Varibles """
app=xlwings.App(visible=False)
indicadoresDF           =pandas.read_excel("Indicadores.xlsx",sheet_name="Tabla")

""" Define functions """
def transformExcelToTable(path):
    yearData                =getYearData(path)
    yearDF                  =interpretExcel(path)
    yearDF                  =renameColumnsByIndicator(yearDF,indicadoresDF,yearData)
    return (convertToTableList(yearDF,indicadoresDF,yearData))

def getYearData(path) -> dict:
    """ Extrae la informacion basica del a�o escolar """
    
    book=xlwings.Book(path,update_links=False)
    sheet=book.sheets["2 Rendimiento Escolar"]
    sheetData={
        "Colegio"           :sheet.range("C2").value,
        "Nivel Educativo"   :sheet.range("C3").value,
        "Lapso"             :sheet.range("C4").value,
        "A�o"               :sheet.range("C5").value,
        "Seccion"           :sheet.range("C6").value,
        "#Docente"          :sheet.range("C7").value
    }
    book.close()
    return sheetData
def interpretExcel(path) -> pandas.DataFrame:
    """ Extrae la tabla de datos del rendimiento escolar """
    df=pandas.read_excel(path,sheet_name="2 Rendimiento Escolar",skiprows=12)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')] 
    df = df.loc[~df["APELLIDOS"].isna()]
    return df
def renameColumnsByIndicator(df:pandas.DataFrame,indDF:pandas.DataFrame,basicData:dict) -> pandas.DataFrame:
    """ Renombra los indicadores a su codigo ID"""
    yearCols=indDF.loc[indDF["A�o"]==basicData["Nivel Educativo"]]
    df.columns=[
        "N",'APELLIDOS', 'NOMBRES', 'SEXO', 
        'c�dula escolar o identidad',
        'MATR�C. INICIAL VS EVALUADA']+yearCols["ID_Indicador"].to_list()
    return df
def convertToTableList(df:pandas.DataFrame,indDF:pandas.DataFrame,basicData:dict) -> list:
    """ Genera una lista con los datos del estudiante y a�o educativo con el ID y resultado de cada indicador del a�o educativo """
    yearCols=indDF.loc[indDF["A�o"]==basicData["Nivel Educativo"]]
    resultList=[]
    for index, row in df.iterrows():
        studentData=row[['c�dula escolar o identidad','APELLIDOS', 'NOMBRES', 'SEXO','MATR�C. INICIAL VS EVALUADA']].to_list()
        for indicador in yearCols["ID_Indicador"].to_list():
            resultList.append(studentData+list(basicData.values())+[indicador,row[indicador]])
    return pandas.DataFrame(resultList,columns=["Cedula","Apellidos","Nombres","Sexo","Matricula","CE","NE","Lapso","A�o","Seccion","Docentes","ID_Indicador","Puntaje"])

def mergeTables(filelist) -> pandas.DataFrame:
    tableHolder=[]
    total=len(filelist)
    for i,file in enumerate(filelist):
        logger.info(f"Procesando ({i}/{total}): {os.path.split(file)[1]}")
        try:
            tableHolder.append(transformExcelToTable(file))
        except Exception as e:
            logger.error(e)
            continue
    df=pandas.concat(tableHolder)
    return df

""" Execute """


