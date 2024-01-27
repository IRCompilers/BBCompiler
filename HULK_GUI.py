import PySimpleGUI as sg

#This file contain the code for the visual interface of the HULK files compiler


#GLOBAL VARIABLES
#----------------------------------------------------------

file_location=None #hold the file for quickSave
compiled=False #avoid to run an uncompiled code

#----------------------------------------------------------


#BUTTONS METHODS
#----------------------------------------------------------

def Run():
#run the compiled project
    global compiled
    
    if not compiled:
        sg.popup_cancel("You need to compile first!")
        return
    
    #To complete


def Compile(input):
#Send the input to the compiler
    try:
        #Call the function to compile. Once created, delette the followin line
        raise Exception("Todavia no se ha implementado el compilador")
        
        sg.popup_ok("Compilation succeded")
        global compiled
        compiled=True
    
    except Exception as e:
        if sg.popup_ok_cancel("You have some compilation errors.\nYou want to see the ouput console?")=='OK':
            #Show the user the different errors detected by the compiler
            sg.popup_scrolled(e)


def Save(input, override=True):
#Save the current code in a file on the computer
    
    global file_location
    
    if file_location is None or not override:
        #Select the folder to save it and give it a name to the file 
        folder=sg.popup_get_folder("Search the folder")
        name=sg.popup_get_text("Introduce name")
        file_location=f"{folder}/{name}.hlk"
    #If you are working on a file, override=True allows a quicksave
    
    try:
        with open(file_location, 'w') as archivo:
            archivo.write(input)
    except Exception as e:
        sg.popup("Ha ocurrido un error al salvar")


def Load():
#Allows to load a code previously saved
    file=sg.popup_get_file("Search the file")
    global file_location
    file_location=file
    try:
        with open(file_location, 'r') as archivo:
            code=archivo.read()
        return code
    except Exception as e:
        sg.popup("Ha ocurrido un error al cargar")

#----------------------------------------------------------


#MAIN PROGRAM
#----------------------------------------------------------

def main():

    #General Configurations
    sg.theme('DarkGreen5')
    sg.set_options(font=('Arial Bold',12))
    width , height = sg.Window.get_screen_size()
    layout = [
        [sg.Multiline(size=(width//10,height//22),key='input')],
        [
            sg.Button('Compile'),
            sg.Button('Run'),
            sg.Button('Save'),
            sg.Button('Save As'),
            sg.Button('Load'),
        ]
    ]
    window2 = sg.Window('The Incredible HULK', layout,icon='logo.ico', element_justification='c',resizable=True)
    #Event Catcher
    while True:
        event, values = window2.read()
        if event == sg.WIN_CLOSED:
            window2.close()
            break
        if event =='Run':
            Run()
        if event =='Compile':
            Compile(values['input'])
        if event =='Save':
            Save(values['input'])
        if event =='Save As':
            Save(values['input'],False)
        if event =='Load':
            window2['input'].Update(Load())


if __name__ == "__main__":
    main()