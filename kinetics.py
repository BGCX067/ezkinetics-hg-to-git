#  Kinetics Program

#--------Required Modules---------

#from __future__ import division

from math import *

##from Tkinter import *

from wx import *


#----------the GUI-----------------

class WXGUI(Frame):
    def __init__(self, parent, title):
        Frame.__init__(self, parent, title=title, size=(400,400))

        # Create the menu items
        filemenu= Menu() 
        menuOpen = filemenu.Append(ID_OPEN, "&Open"," Open a file to edit")
        menuExit = filemenu.Append(ID_EXIT,"E&xit"," Terminate the program")
        
        helpmenu = Menu()
        menuAbout= helpmenu.Append(ID_ABOUT, "&About"," Information about this program")
        
        #Create the menubar
        menuBar = MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(helpmenu,"Help") # Adding the "helpmenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        #Create Top panel and its sizer
        self.topsizer = BoxSizer(HORIZONTAL)
        self.toppanel = Panel(self, size=(600,600))
        self.toppanel.SetSizer(self.topsizer)        

        #Create some widgets for the top panel
        self.selectdruglabel = StaticText(parent=self.toppanel,label = 'Please Select the Drug: ')
        self.drugchoice = Choice(parent=self.toppanel,choices=(['Vancomycin','Gentamicin']),name='Vancomycin')

        #Put the widgets into the top panel sizer
        self.topsizer.AddMany([self.selectdruglabel,self.drugchoice])
        
        #Create a status bar at the bottom of the window
        self.CreateStatusBar()

        #Setup sizer for main window
        self.mainsizer = BoxSizer(VERTICAL)
        self.mainsizer.Add(self.toppanel)
        self.SetSizer(self.mainsizer)
        self.SetAutoLayout(True)
        self.mainsizer.Fit(self)

        #Show Everything
        self.Show()

        

        



##class TkinterGUI:
##    def __init__(self, parent):
##        self.TabFrame = Frame(parent)
##        self.TabFrame.grid(row=0,column=0)
##
##        self.EmpiricFrame = Frame(parent)
##        self.EmpiricFrame.grid(row=1,column=0)
##
##        self.SelectDrugLabel = Label(self.TabFrame, text="Select Drug:")
##        self.SelectDrugLabel.grid(row=0, column=3,sticky=W)
##
##        self.CurrentDrug = StringVar(parent)
##        self.CurrentDrug.set('Vancomycin')
##        self.SelectDrugBox = OptionMenu(self.TabFrame, self.CurrentDrug, 'Vancomycin', 'Gentamicin')
##        self.SelectDrugBox.grid(row=0,column=4,sticky=W)
##
##        self.AgeLabel = Label(self.EmpiricFrame, text='Age')
##        self.AgeLabel.grid(column=0,row=0,sticky=W)
##
##        self.Ageinput = Scale(self.EmpiricFrame, from_=0, to=120, orient=HORIZONTAL, resolution=1)
##        self.Ageinput.grid(row=0,column=1)
##
##        self.SexLabel = Label(self.EmpiricFrame, text='Sex')
##        self.SexLabel.grid(row=1,column=0,sticky=W)
##
##        self.CurrentSex = StringVar(parent)
##        self.CurrentSex.set('Male')
##        self.SexSelect = Radiobutton(self.EmpiricFrame, text='Male', variable = self.CurrentSex, value='Male')
##        self.SexSelect.grid(row=1,column=1)
##        self.SexSelect = Radiobutton(self.EmpiricFrame, text='Female', variable = self.CurrentSex, value='Female')
##        self.SexSelect.grid(row=1,column=2)
##
##        self.WeightLabel = Label(self.EmpiricFrame, text='Weight')
##        self.WeightLabel.grid(row=2,column=0,sticky=W)
##
##        self.HeightLabel = Label(self.EmpiricFrame, text='Height')
##        self.HeightLabel.grid(row=3,column=0,sticky=W)
##
##        self.SCrLabel = Label(self.EmpiricFrame, text='Serum Creatinine')
##        self.SCrLabel.grid(row=4,column=0,sticky=W)
##
##        self.DoseLabel = Label(self.EmpiricFrame, text='Maintenance Dose')
##        self.DoseLabel.grid(row=5,column=0,sticky=W)
##
##        

               
        


#---------The Formulas Needed--------
    
##class Formulas:
##    def __init__(self):
##        pass
##
##    def CrofGaul(self, sex, age, IBW, SCr):
##        '''The Crockoft-Gault Equation'''
##        if sex == 'female':
##            self.CrCl=(((140-age)*IBW)/(SCr*72))*0.85
##        else:
##            self.CrCl=(((140-age)*IBW)/(SCr*72))
##        if self.CrCl>100:
##            return 100
##        else:
##            return self.CrCl
##
##    def IdealBodyWeight(self, sex, height_inches):
##        '''Returns the Ideal Body weight'''
##        if sex == 'female':
##            self.IdealWeight = 45.5 + (2.3*(height_inches-60))
##        else:
##            self.IdealWeight = 50.0 + (2.3*(height_inches-60))
##        return self.IdealWeight
##
##    def NeedDosingWeight(self, Total_Weight, IBW):
##        '''Do we need to use the adjusted dosing weight??'''
##        if Total_Weight > 1.2*IBW:
##            return True
##        else:
##            return False
##
##    def DosingWeight(self, Total_Weight, IBW):
##        '''Find the dosing weight.  Also called adjusted body weight'''
##        self.DoseWeight = ((Total_Weight - IBW)*0.4)+IBW
##        return self.DoseWeight
##    
##    def cmToin(self, cm):
##        '''Convert centimeters to inches'''
##        self.inches = cm/2.54
##        return self.inches
##
##    def lbTokg(self, lb):
##        '''Convert pound to kilograms'''
##        self.kilos = lb*0.45359237
##        return self.kilos
##
##    def Estimated_Cmax_One_Dose(self, Dose_mg, Vd):
##        '''Estimates the Cmax after a one time dose'''
##        self.Cmax = Dose_mg/Vd
##        return Cmax
##
##    def Estimated_Cmax_Steady_State(self, Dose, Infusion_time_hrs, ke, Vd, tau):
##        '''Estimates the Cmax at steady state given the dosing information'''
##        self.Cmax = ((Dose/Infusion_time_hrs)*(1-pow(e,-(ke*Infusion_time_hrs))))/(Vd*ke*(1-pow(e,-(ke*tau))))
##        return self.Cmax
##
##    def Estimated_Cmin(self, Cmax, ke, tau, Infusion_time_hrs):
##        '''Estimates the Cmin given a Cmax'''
##        self.Cmin = Cmax*pow(e,-(ke*(tau-Infusion_time_hrs)))
##        return self.Cmin
##
##    def Find_Ke(self, Concentration_1, Concentration_2, Time_1, Time_2):
##        '''Calculates the ke when given two levels'''
##        self.ke = log(Concentration_1/Concentration_2)/(Time_1-Time_2)
##        return self.ke
##
##    def Find_Half_Life(self, ke):
##        '''Calculates the T1/2 from the elimination rate'''
##        T_half = log(2)/ke
##        return T_half

##formulas = Formulas()
app = App(False)
mainwindow = WXGUI(None, "Ez Kinetics")
app.MainLoop()


