#  Kinetics Program - David Trupiano - Davetrupiano@gmail.com

#--------Required Modules---------

from __future__ import division

from math import *

from wx import *

from wx.lib.agw.floatspin import *

#---------The Formulas Needed--------
    
class Formulas:
    def __init__(self):
        pass

    def CrofGaul(self, sex, age, IBW, SCr):
        '''The Crockoft-Gault Equation'''
        if sex == 'female':
            self.CrCl=(((140-age)*IBW)/(SCr*72))*0.85
        else:
            self.CrCl=(((140-age)*IBW)/(SCr*72))
        if self.CrCl>100:
            return 125
        else:
            return round(self.CrCl,1)

    def IdealBodyWeight(self, sex, height_inches):
        '''Returns the Ideal Body weight'''
        if sex == 'Female':
            self.IdealWeight = 45.5 + (2.3*(height_inches-60))
        else:
            self.IdealWeight = 50.0 + (2.3*(height_inches-60))
        return self.IdealWeight

    def NeedDosingWeight(self, Total_Weight, IBW):
        '''Do we need to use the adjusted dosing weight??'''
        if Total_Weight > 1.2*IBW:
            return True
        else:
            return False

    def DosingWeight(self, Total_Weight, IBW):
        '''Find the dosing weight.  Also called adjusted body weight'''
        self.DoseWeight = ((Total_Weight - IBW)*0.4)+IBW
        return self.DoseWeight
    
    def cmToin(self, cm):
        '''Convert centimeters to inches'''
        self.inches = cm/2.54
        return self.inches

    def lbTokg(self, lb):
        '''Convert pound to kilograms'''
        self.kilos = lb*0.45359237
        return self.kilos

    def Estimated_Cmax_One_Dose(self, Dose_mg, Vd):
        '''Estimates the Cmax after a one time dose'''
        self.Cmax = Dose_mg/Vd
        return Cmax

    def Estimated_Cmax_Steady_State(self, Dose, Infusion_time_hrs, ke, Vd, tau):
        '''Estimates the Cmax at steady state given the dosing information'''
        self.Cmax = ((Dose/Infusion_time_hrs)*(1-pow(e,-(ke*Infusion_time_hrs))))/(Vd*ke*(1-pow(e,-(ke*tau))))
        return self.Cmax

    def Estimated_Cmin(self, Cmax, ke, tau, Infusion_time_hrs):
        '''Estimates the Cmin given a Cmax'''
        self.Cmin = Cmax*pow(e,-(ke*(tau-Infusion_time_hrs)))
        return self.Cmin

    def Find_Ke(self, Concentration_1, Concentration_2, Time_1, Time_2):
        '''Calculates the ke when given two levels'''
        self.ke = log(Concentration_1/Concentration_2)/(Time_1-Time_2)
        return self.ke

    def Find_Half_Life(self, ke):
        '''Calculates the T1/2 from the elimination rate'''
        T_half = log(2)/ke
        return T_half

    
#----------the GUI-----------------
class navpane(Panel):
    def __init__(self, parent):
        Panel.__init__(self,parent=parent)

        self.topsizer = StaticBoxSizer(StaticBox(parent=self, label='Dosing Model'),VERTICAL)
        self.SetSizer(self.topsizer)

        #Create some widgets for the top panel
        self.selectdruglabel = StaticText(parent=self,label = 'Please Select the Drug: ')
        self.drugchoice = ComboBox(parent=self,choices=(['Vancomycin','Gentamicin']),style=CB_READONLY)
        self.drugchoice.SetValue('Vancomycin')

        self.empiricspecific = StaticText(parent=self,label = 'Empiric or Patient Specific Dosing: ')
        self.empiricchoice = ComboBox(parent=self,choices=(['Empiric','Patient Specific']),style=CB_READONLY)
        self.empiricchoice.SetValue('Empiric')

        #Put widgets into the sizer
        self.topsizer.AddMany([self.empiricspecific,self.empiricchoice,self.selectdruglabel,self.drugchoice])

class demographicspane(Panel):
    def __init__(self, parent):
        Panel.__init__(self,parent=parent,style=NO_BORDER|TAB_TRAVERSAL)

        self.boxlabel = StaticBoxSizer(StaticBox(parent=self, label='Demographics'),VERTICAL)
        self.midsizer = FlexGridSizer(4,3,vgap=10)
        self.boxlabel.Add(self.midsizer)
        
        self.SetSizer(self.boxlabel)

        #create some widgets for the midpanel
        self.sexlabel = StaticText(parent=self,label='Sex: ')
        self.sexinputmale = RadioButton(parent=self,label='Male',style=RB_GROUP)
        self.sexinputfemale = RadioButton(parent=self,label='Female')
        
        self.agelabel = StaticText(self,label='Age: ')
        self.ageinput = SpinCtrl(parent=self,size=(50,-1),style=SP_WRAP|SP_ARROW_KEYS)
        self.ageinput.SetRange(0,400)
        self.ageinput.SetValue(65)        

        self.weightlabel = StaticText(parent=self,label='Weight: ')
        self.weightinput = SpinCtrl(parent=self,size=(50,-1),style=SP_WRAP|SP_ARROW_KEYS)
        self.weightinput.SetRange(10,120)
        self.weightinput.SetValue(155)
        self.weightunits = ComboBox(parent=self,choices=(['Pounds','Kilograms']),style=CB_READONLY)
        self.weightunits.SetValue('Kilograms')        

        self.heightlabel = StaticText(parent=self,label='Height: ')
        self.heightinput = SpinCtrl(parent=self,size=(50,-1),style=SP_WRAP|SP_ARROW_KEYS)
        self.heightinput.SetRange(0,500)
        self.heightinput.SetValue(65)
        self.heightunits = ComboBox(parent=self,choices=(['Inches','Centimeters']),style=CB_READONLY)
        self.heightunits.SetValue('Inches')
        
        self.scrlabel = StaticText(parent=self,label='Serum Creatinine: ')
        self.scrinput = FloatSpin(parent=self,value=1.1,min_val=0, max_val=10, increment=0.1,digits=1,size=(50,-1))
        self.scrunitslabel = StaticText(parent=self,label=' mg/dL')

        #formulas to update IBW label dynamically
        self.form = Formulas()
        def getsex():
            if self.sexinputmale.GetValue():
                return 'Male'
            else:
                return 'Female'
        def getheight():
            if self.heightunits.GetValue() == 'Inches':
                return int(self.heightinput.GetValue())
            else:
                return int(self.form.cmToin(self.heightinput.GetValue()))
        def getage():
            return self.ageinput.GetValue()
        def getscr():
            return self.scrinput.GetValue()
        def getIBW():
            return self.form.IdealBodyWeight(getsex(),getheight())
        def reloading(event):
            self.IdealBodyWeightoutput.SetLabel(str(self.form.IdealBodyWeight(getsex(),getheight())))
            self.crcloutput.SetLabel(str(self.form.CrofGaul(getsex(),getage(),getIBW(),getscr())))
            
        #IBW widgets    
        self.IdealBodyWeightlabel = StaticText(parent=self,label='Ideal Weight: ')
        self.IdealBodyWeightoutput = StaticText(parent=self,label=str(self.form.IdealBodyWeight(getsex(),getheight())))
        self.IdealBodyWeightunits = StaticText(parent=self,label='Kilograms')

        #IBW event binding to dynamically update the value  
        self.ageinput.Bind(EVT_SPINCTRL, reloading)
        self.heightinput.Bind(EVT_SPINCTRL, reloading)
        self.heightunits.Bind(EVT_COMBOBOX, reloading)
        self.sexinputmale.Bind(EVT_RADIOBUTTON, reloading)
        self.sexinputfemale.Bind(EVT_RADIOBUTTON, reloading)
        self.scrinput.Bind(EVT_FLOATSPIN,reloading)

        #CrCl Label updated
        self.crcllabel = StaticText(parent=self,label='CrCl: ')
        self.crcloutput = StaticText(parent=self,label=str(self.form.CrofGaul(getsex(),getage(),getIBW(),getscr())))
        self.crclunits = StaticText(parent=self,label=' ml/min')

        #place widgets into the sizer
        self.dummypanel = Panel(parent=self)
        self.dummypanel1 = Panel(parent=self)
        self.dummypanel2 = Panel(parent=self)
        self.dummypanel3 = Panel(parent=self)        
        self.midsizer.AddMany([(self.sexlabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT), self.sexinputmale,self.sexinputfemale,
                               (self.agelabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT), self.ageinput,self.dummypanel1,
                               (self.weightlabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT), self.weightinput,self.weightunits,
                               (self.IdealBodyWeightlabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.IdealBodyWeightoutput,-1,ALIGN_CENTER),(self.IdealBodyWeightunits,-1,ALIGN_CENTER_VERTICAL),
                               (self.heightlabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT), self.heightinput,self.heightunits,
                               (self.scrlabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),self.scrinput,(self.scrunitslabel,-1,ALIGN_CENTER_VERTICAL),
                               (self.crcllabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.crcloutput,-1,ALIGN_CENTER),(self.crclunits,-1,ALIGN_CENTER_VERTICAL)])
        #self.boxlabel.Add(self.reloadbutton, flag=ALIGN_CENTER)

class calculatedpane(Panel):
    def __init__(self, parent):
        Panel.__init__(self,parent=parent,style=NO_BORDER)

        self.boxlabel = StaticBoxSizer(StaticBox(parent=self, label='Demographics'))
        self.midsizer = FlexGridSizer(4,3,vgap=10)
        self.boxlabel.Add(self.midsizer)
        
        self.SetSizer(self.boxlabel)

        #Create the widgets
        self.IBWlabel = StaticText(self,label='IBW: ')
        self.IBWoutput = StaticText(self,label='Age: ')

        

class MainWindow(Frame):
    '''the main window frame'''
    def __init__(self, parent, title):
        Frame.__init__(self, parent, title=title, size=(400,400))

        self.SetBackgroundColour('Silver')
        #self.SetBackgroundStyle(BG_STYLE_COLOUR)

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

        #Create the top pane
        self.navpane = navpane(parent=self)

        #Create the demographics pane
        self.demographpane = demographicspane(parent=self)
        
        #Create a status bar at the bottom of the window
        self.CreateStatusBar()

        #Setup sizer for main window
        self.mainsizer = BoxSizer(VERTICAL)
        self.mainsizer.Add(self.navpane,flag=ALIGN_CENTER)
        self.mainsizer.Add(self.demographpane,flag=ALIGN_CENTER)
        self.SetSizer(self.mainsizer)
        self.SetAutoLayout(True)
        self.mainsizer.Fit(self)

        #Show Everything
        self.Show()
    

##formulas = Formulas()
app = App(False)
mainwindow = MainWindow(None, "Ez Kinetics")
app.MainLoop()


