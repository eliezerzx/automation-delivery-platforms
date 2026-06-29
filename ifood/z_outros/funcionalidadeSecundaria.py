import shutil
import os
import pyautogui
import pyperclip
import time
import tkinter as tk
from tkinter import filedialog, messagebox
pyautogui.PAUSE=0.5
def baixar_gabaritos():
    arquivos = ["gabarito_categoria.txt", "gabarito_complemento.txt"]
    pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")

    for arquivo in arquivos:
        origem = os.path.join(os.getcwd(), arquivo)  # Arquivos ficam na pasta do projeto
        destino = os.path.join(pasta_downloads, arquivo)

        if os.path.exists(origem):
            shutil.copy2(origem, destino)  # copia mantendo data de modificação
        else:
            messagebox.showerror("Erro", f"Arquivo {arquivo} não encontrado!")

    messagebox.showinfo("Download", f"Gabaritos salvos em {pasta_downloads}")
def verificaPosicao(preco1,preco2,i,tentativas=1):
    #Declaração de Xs e Y utilizado
    xN= 00
    yN=636
    #Clica na caixa de preco
    if(i>4):
        pyautogui.click(xN,yN)
    pyautogui.hotkey('ctrl','a')
    pyautogui.hotkey('ctrl','c')
    valor = pyperclip.paste()
    if(valor>6):
        time.sleep(5)
        verificaPosicao(preco1,preco2,i,tentativas+1)
    elif(valor == preco1):
        return True
    elif(valor == preco2):
        time.sleep(1)
        #Chama Função para testar os próximos para testar os próximos
    elif(tentativas>5):
        time.sleep(1)
        #Chama Função para testar desde o inicio