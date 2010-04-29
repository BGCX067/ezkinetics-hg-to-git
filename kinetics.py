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
        if sex == 'F emale':
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
            if height_inches<=60:
                self.IdealWeight = 45.5
            else:
                self.IdealWeight = 45.5 + (2.3*(height_inches-60))
        else:
            if height_inches<=60:
                self.IdealWeight = 50.0
            else:
                self.IdealWeight = 50.0 + (2.3*(height_inches-60))
        return self.IdealWeight

    def NeedDosingWeight(self, Total_Weight, IBW):
        '''Do we need to use the adjusted dosing weight??'''
        if Total_Weight > 1.2*IBW:
            return True
        else:
            return False

    def AGDosingWeight(self, Total_Weight, IBW):
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

    def getmodel(self):
        return self.empiricchoice.GetValue()
    def getdrug(self):
        return self.drugchoice.GetValue()   

class demographicspane(Panel):
    def __init__(self, parent,drug,model):
        Panel.__init__(self,parent=parent,style=NO_BORDER|TAB_TRAVERSAL)

        self.form = Formulas()
        self.drugmodel = drug

        self.boxlabel = StaticBoxSizer(StaticBox(parent=self, label='Kinetic Parameters'),VERTICAL)
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
        self.weightinput.SetRange(10,800)
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
            
        #IBW widgets    
        self.IdealBodyWeightlabel = StaticText(parent=self,label='Ideal Weight: ')
        self.IdealBodyWeightoutput = StaticText(parent=self,label=str(self.form.IdealBodyWeight(self.getsex(),self.getheight())))
        self.IdealBodyWeightunits = StaticText(parent=self,label='Kilograms')

        #IBW event binding to dynamically update the value
##        self.sexinputmale.Bind(EVT_RADIOBUTTON, self.reloading)
##        self.sexinputfemale.Bind(EVT_RADIOBUTTON, self.reloading)
##        self.ageinput.Bind(EVT_SPINCTRL, self.reloading)
##        self.weightinput.Bind(EVT_SPINCTRL, self.reloading)
##        self.weightunits.Bind(EVT_COMBOBOX, self.reloading)
##        self.heightinput.Bind(EVT_SPINCTRL, self.reloading)
##        self.heightunits.Bind(EVT_COMBOBOX, self.reloading)
##        self.scrinput.Bind(EVT_FLOATSPIN,self.reloading)
##
##        self.ageinput.Bind(EVT_SET_FOCUS, self.ageinput.SetSelection(0,-1))
##        self.weightinput.Bind(EVT_SET_FOCUS, self.weightinput.SetSelection(0,-1))
##        self.heightinput.Bind(EVT_SET_FOCUS, self.heightinput.SetSelection(0,-1))
##        #self.heightunits.Bind(EVT_KILL_FOCUS, self.scrinput.SelectAll())

        #CrCl Label updated
        self.crcllabel = StaticText(parent=self,label='CrCl: ')
        self.crcloutput = StaticText(parent=self,label=str(self.form.CrofGaul(self.getsex(),self.getage(),self.getCrClWeight(),self.getscr())))
        self.crclunits = StaticText(parent=self,label=' ml/min')

        #Create VD label and value
        self.VDlabel = StaticText(self,label='Volume of Distribution: ')
        self.VDoutput = StaticText(self,label=str(round(self.getvd(),1)))
        self.VDunits = StaticText(self,label='Liters')

        #create K label and value
        self.klabel = StaticText(self,label='Rate Constant (k): ')
        self.koutput = StaticText(self,label=str(round(self.getk(),5)))
        self.kunits = StaticText(self,label=' /hour')

        #create half life label and value
        self.thalflabel = StaticText(self,label='Half-Life: ')
        self.thalfoutput = StaticText(self,label=str(round(self.getthalf(),1)))
        self.thalfunits = StaticText(self,label=' hours')

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
                               (self.crcllabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.crcloutput,-1,ALIGN_CENTER),(self.crclunits,-1,ALIGN_CENTER_VERTICAL),
                               (self.VDlabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.VDoutput,-1,ALIGN_CENTER),(self.VDunits,-1,ALIGN_CENTER_VERTICAL),
                               (self.klabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.koutput,-1,ALIGN_CENTER),(self.kunits,-1,ALIGN_CENTER_VERTICAL),
                               (self.thalflabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.thalfoutput,-1,ALIGN_CENTER),(self.thalfunits,-1,ALIGN_CENTER_VERTICAL)])
        #self.boxlabel.Add(self.reloadbutton, flag=ALIGN_CENTER)

        #formulas to update patient data dynamically
    def getsex(self):
        if self.sexinputmale.GetValue():
            return 'Male'
        else:
            return 'Female'
    def getage(self):
        return self.ageinput.GetValue()
    def getactualweight(self):
        if self.weightunits.GetValue()== 'Kilograms':
            self.actualweight = self.weightinput.GetValue()
        else:
            self.actualweight = self.form.lbTokg(self.weightinput.GetValue())
        return self.actualweight
    def getIBW(self):
        return self.form.IdealBodyWeight(self.getsex(),self.getheight())
    def getCrClWeight(self):
        '''Gets the weight to be used in the Crockauf Gault Equation   

        uses actual weight if actual<IBW, uses corrected if actual>IBW'''
        
        if self.getactualweight() < self.form.IdealBodyWeight(self.getsex(),self.getheight()):
            self.crcllabel.SetLabel('CrCl (Used Actual Weight): ')
            return self.getactualweight()
        else:
            self.crcllabel.SetLabel('CrCl (Used Corrected Weight): ')
            return ((self.getactualweight()-self.getIBW())*0.4)+self.getIBW()
    def getheight(self):
        if self.heightunits.GetValue() == 'Inches':
            return int(self.heightinput.GetValue())
        else:
            return int(self.form.cmToin(self.heightinput.GetValue()))
    def getscr(self):
        return self.scrinput.GetValue()
    def getcrcl(self):
        return self.form.CrofGaul(self.getsex(),self.getage(),self.getCrClWeight(),self.getscr())
    def getvd(self):
        if self.drugmodel=='Vancomycin':
            if self.getactualweight() < self.getIBW():
                vd = self.getactualweight()*0.7
                #self.VDlabel.SetLabel('VD (Actual Weight): ')
            else:
                vd = ((self.getactualweight()-self.getIBW())*0.4)+self.getIBW()*0.7
                #self.VDlabel.SetLabel('VD (Corrected Weight): ')
        elif self.drugmodel=='Gentamicin':
            vd = 0.3*self.getIBW()
        return vd
    def getk(self):
        if self.drugmodel=='Vancomycin':
            k = 0.00083*self.getcrcl()+0.0044
        elif self.drugmodel == 'Gentamicin':
            k = 0.00285*self.getcrcl() + 0.015
        return k
    def getthalf(self):
        return log(2)/self.getk()            
    def reloading(self,event):
        self.IdealBodyWeightoutput.SetLabel(str(self.getIBW()))
        self.crcloutput.SetLabel(str(self.getcrcl()))
        self.VDoutput.SetLabel(str(round(self.getvd(),1)))
        self.koutput.SetLabel(str(round(self.getk(),5)))
        self.thalfoutput.SetLabel(str(round(self.getthalf(),1)))

class dosepane(Panel):
    def __init__(self, parent, VD, ke):
        Panel.__init__(self,parent=parent,style=NO_BORDER)

        self.form = Formulas()
        self.vd = VD
        self.k = ke

        self.boxlabel = StaticBoxSizer(StaticBox(parent=self, label='Dosing'))
        self.midsizer = FlexGridSizer(4,3,vgap=10)
        self.boxlabel.Add(self.midsizer)
        
        self.SetSizer(self.boxlabel)

        #Create the widgets
        self.peaklabel = StaticText(self,label='Desired Loading Peak: ')
        self.peakinput = SpinCtrl(parent=self,size=(50,-1),style=SP_WRAP|SP_ARROW_KEYS)
        self.peakunits = StaticText(self,label=' mg/L')
        self.peakinput.SetRange(0,50)
        self.peakinput.SetValue(30)

        
        self.loaddose = self.getloadingdose()
        self.loadinglabel = StaticText(self,label='Loading Dose: ')
        self.loadingoutput = StaticText(self,label=str(self.loaddose))
        self.loadingunits = StaticText(self,label=' mg')

        self.infutimelabel = StaticText(self,label='Infusion Time: ')
        self.infutimeinput = SpinCtrl(parent=self,size=(50,-1),style=SP_WRAP|SP_ARROW_KEYS)
        self.infutimeunits = StaticText(self,label=' hours')
        self.infutimeinput.SetRange(1,5)
        self.infutimeinput.SetValue(2)

        self.cmaxlabel = StaticText(self,label='Desired Cmax: ')
        self.cmaxinput = SpinCtrl(parent=self,size=(50,-1),style=SP_WRAP|SP_ARROW_KEYS)
        self.cmaxunits = StaticText(self,label=' mg/L')
        self.cmaxinput.SetRange(0,50)
        self.cmaxinput.SetValue(30)

        self.cminlabel = StaticText(self,label='Desired Trough: ')
        self.cmininput = SpinCtrl(parent=self,size=(50,-1),style=SP_WRAP|SP_ARROW_KEYS)
        self.cminunits = StaticText(self,label=' mg/L')
        self.cmininput.SetRange(0,50)
        self.cmininput.SetValue(10)

        self.taulabel = StaticText(self,label='Calculated Interval: ')
        self.tauoutput = StaticText(self,label=str(round(self.gettau(),0)))
        self.tauunits = StaticText(self,label=' hours')

        self.dtaulabel = StaticText(self,label='Desired Interval: ')
        self.dtauinput = SpinCtrl(parent=self,size=(50,-1),style=SP_WRAP|SP_ARROW_KEYS)
        self.dtauunits = StaticText(self,label=' hours')
        self.dtauinput.SetRange(0,50)
        self.dtauinput.SetValue(10)

        self.MDlabel = StaticText(self,label='Calculated Maintenance Dose: ')
        self.MDoutput = StaticText(self,label=str(round(self.getMD(),0)))
        self.MDunits = StaticText(self,label=' mg')

        self.dMDlabel = StaticText(self,label='Desired Maintenance Dose: ')
        self.dMDinput = SpinCtrl(parent=self,size=(75,-1),style=SP_WRAP|SP_ARROW_KEYS)
        self.dMDunits = StaticText(self,label=' mg')
        self.dMDinput.SetRange(0,5000)
        self.dMDinput.SetValue(2000)

        self.fincmaxlabel = StaticText(self,label='Calculated Cmax: ')
        self.fincmaxoutput = StaticText(self,label=str(round(self.form.Estimated_Cmax_Steady_State(self.dMDinput.GetValue(),self.infutimeinput.GetValue(),self.k,self.vd,self.dtauinput.GetValue()),0)))
        self.fincmaxunits = StaticText(self,label=' mg')

        self.cmax = self.form.Estimated_Cmax_Steady_State(self.dMDinput.GetValue(),self.infutimeinput.GetValue(),self.k,self.vd,self.dtauinput.GetValue())
        self.fincminlabel = StaticText(self,label='Calculated Trough: ')
        self.fincminoutput = StaticText(self,label=str(round(self.form.Estimated_Cmin(self.form.Estimated_Cmax_Steady_State(self.dMDinput.GetValue(),self.infutimeinput.GetValue(),self.k,self.vd,self.dtauinput.GetValue()), self.k, self.dtauinput.GetValue(), self.infutimeinput.GetValue()),0)))
        self.fincminunits = StaticText(self,label=' mg')        

        #add widgets to the sizer
        self.line1 = StaticLine(self)
        self.line2 = StaticLine(self)
        self.line3 = StaticLine(self)
        self.midsizer.AddMany([(self.peaklabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.peakinput,-1,ALIGN_CENTER),(self.peakunits,-1,ALIGN_CENTER_VERTICAL),
                               (self.loadinglabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.loadingoutput,-1,ALIGN_CENTER),(self.loadingunits,-1,ALIGN_CENTER_VERTICAL),
                               self.line1,self.line2,self.line3,
                               (self.infutimelabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.infutimeinput,-1,ALIGN_CENTER),(self.infutimeunits,-1,ALIGN_CENTER_VERTICAL),
                               (self.cmaxlabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.cmaxinput,-1,ALIGN_CENTER),(self.cmaxunits,-1,ALIGN_CENTER_VERTICAL),
                               (self.cminlabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.cmininput,-1,ALIGN_CENTER),(self.cminunits,-1,ALIGN_CENTER_VERTICAL),
                               (self.taulabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.tauoutput,-1,ALIGN_CENTER),(self.tauunits,-1,ALIGN_CENTER_VERTICAL),
                               (self.dtaulabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.dtauinput,-1,ALIGN_CENTER),(self.dtauunits,-1,ALIGN_CENTER_VERTICAL),
                               (self.MDlabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.MDoutput,-1,ALIGN_CENTER),(self.MDunits,-1,ALIGN_CENTER_VERTICAL),
                               (self.dMDlabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.dMDinput,-1,ALIGN_CENTER),(self.dMDunits,-1,ALIGN_CENTER_VERTICAL),
                               (self.fincmaxlabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.fincmaxoutput,-1,ALIGN_CENTER),(self.fincmaxunits,-1,ALIGN_CENTER_VERTICAL),
                               (self.fincminlabel,-1,ALIGN_CENTER_VERTICAL|ALIGN_RIGHT),(self.fincminoutput,-1,ALIGN_CENTER),(self.fincminunits,-1,ALIGN_CENTER_VERTICAL)])
    def getloadingdose(self):
        return self.peakinput.GetValue()*self.vd
    def gettau(self):
        return -pow(self.k,-1)*(log(self.cmininput.GetValue(),e)-log(self.cmaxinput.GetValue(),e))+self.infutimeinput.GetValue()
    def getMD(self):
        return self.k*self.vd*self.cmaxinput.GetValue()*self.infutimeinput.GetValue()*((1-pow(e,-self.k*self.dtauinput.GetValue()))/(1-pow(e,-self.k*self.infutimeinput.GetValue())))                   
    def reloading(self,event):
        self.loadingoutput.SetLabel(str(round(self.getloadingdose(),0)))
        self.tauoutput.SetLabel(str(round(self.gettau(),1)))
        self.MDoutput.SetLabel(str(round(self.getMD(),0)))
        self.fincmaxoutput.SetLabel(str(round(self.form.Estimated_Cmax_Steady_State(self.dMDinput.GetValue(),self.infutimeinput.GetValue(),self.k,self.vd,self.dtauinput.GetValue()),0)))
        self.fincminoutput.SetLabel(str(round(self.form.Estimated_Cmin(self.cmax, self.k, self.dtauinput.GetValue(), self.infutimeinput.GetValue()),0)))

        

class MainWindow(Frame):
    '''the main window frame'''
    def __init__(self, parent, title):
        Frame.__init__(self, parent, title=title, size=(400,800))

        self.Centre()
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
        self.demographpane = demographicspane(self,self.navpane.getdrug(),self.navpane.getmodel())

        #create the dosing pane
        self.dosepane = dosepane(self,self.demographpane.getvd(),self.demographpane.getk())
        
        #Create a status bar at the bottom of the window
        self.CreateStatusBar()

        #bindings
        #self.navpane.empiricchoice.Bind(EVT_COMBOBOX, self.update)
        self.navpane.drugchoice.Bind(EVT_COMBOBOX, self.update)

        self.demographpane.sexinputmale.Bind(EVT_RADIOBUTTON, self.update)
        self.demographpane.sexinputfemale.Bind(EVT_RADIOBUTTON, self.update)
        self.demographpane.ageinput.Bind(EVT_SPINCTRL, self.update)
        self.demographpane.weightinput.Bind(EVT_SPINCTRL, self.update)
        self.demographpane.weightunits.Bind(EVT_COMBOBOX, self.update)
        self.demographpane.heightinput.Bind(EVT_SPINCTRL, self.update)
        self.demographpane.heightunits.Bind(EVT_COMBOBOX, self.update)
        self.demographpane.scrinput.Bind(EVT_FLOATSPIN,self.update)

        #self.demographpane.ageinput.Bind(EVT_SET_FOCUS, self.demographpane.ageinput.SetSelection(0,-1))
        #self.demographpane.weightinput.Bind(EVT_SET_FOCUS, self.demographpane.weightinput.SetSelection(0,-1))
        #self.demographpane.heightinput.Bind(EVT_SET_FOCUS, self.demographpane.heightinput.SetSelection(0,-1))
        #self.heightunits.Bind(EVT_KILL_FOCUS, self.scrinput.SelectAll())

        self.dosepane.peakinput.Bind(EVT_SPINCTRL,self.update)
        self.dosepane.infutimeinput.Bind(EVT_SPINCTRL,self.update)
        self.dosepane.cmaxinput.Bind(EVT_SPINCTRL,self.update)
        self.dosepane.cmininput.Bind(EVT_SPINCTRL,self.update)
        self.dosepane.dtauinput.Bind(EVT_SPINCTRL,self.update)
        self.dosepane.dMDinput.Bind(EVT_SPINCTRL,self.update)

        #Setup sizer for main window
        self.mainsizer = BoxSizer(VERTICAL)
        self.mainsizer.Add(self.navpane,flag=ALIGN_CENTER)
        self.mainsizer.Add(self.dosepane,flag=ALIGN_CENTER)
        self.mainsizer.Add(self.demographpane,flag=ALIGN_CENTER)
        
        self.SetSizer(self.mainsizer)
        self.SetAutoLayout(True)
        #self.mainsizer.Fit(self)

        #Show Everything
        self.Show()
    def update(self,event):
        self.demographpane.drugmodel = self.navpane.getdrug()
        self.demographpane.reloading(event)
        self.dosepane.vd = self.demographpane.getvd()
        self.dosepane.k = self.demographpane.getk()
        self.dosepane.reloading(event)
        #print self.navpane.getdrug()
        
        
    

##formulas = Formulas()
app = App(False)
mainwindow = MainWindow(None, "Ez Kinetics")
app.MainLoop()


