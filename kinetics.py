#  Kinetics Program - David Trupiano - Davetrupiano@gmail.com

#--------Required Modules---------

from __future__ import division

from math import *

import wx

from wx.lib.agw.floatspin import *

from wx.lib.plot import *

#---------The Formulas Needed--------
    
class Formulas:
    def __init__(self):
        pass

    def CrofGaul(self, sex, age, IBW, SCr):
        '''The Crockoft-Gault Equation'''
        if sex == 'Female':
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
class navpane(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self,parent=parent)

        self.topsizer = wx.StaticBoxSizer(wx.StaticBox(parent=self, label='Dosing Model'))
        self.SetSizer(self.topsizer)

        #Create some widgets for the top panel
        self.selectdruglabel = wx.StaticText(parent=self,label = 'Please Select the Drug: ')
        self.drugchoice = wx.ComboBox(parent=self,choices=(['Vancomycin','Gentamicin']),style=wx.CB_READONLY)
        self.drugchoice.SetValue('Vancomycin')

        self.empiricspecific = wx.StaticText(parent=self,label = 'Empiric or Patient Specific Dosing: ')
        self.empiricchoice = wx.ComboBox(parent=self,choices=(['Empiric','Patient Specific']),style=wx.CB_READONLY)
        self.empiricchoice.SetValue('Empiric')

        #Put widgets into the sizer
        self.topsizer.AddMany([self.empiricspecific,self.empiricchoice,self.selectdruglabel,self.drugchoice])       

    def getmodel(self):
        return self.empiricchoice.GetValue()
    def getdrug(self):
        return self.drugchoice.GetValue()   

class demographicspane(wx.Panel):
    def __init__(self, parent,drug,model):
        wx.Panel.__init__(self,parent=parent,style=wx.NO_BORDER|wx.TAB_TRAVERSAL)

        self.form = Formulas()
        self.drugmodel = drug

        self.boxlabel = wx.StaticBoxSizer(wx.StaticBox(parent=self, label='Kinetic Parameters'),wx.VERTICAL)
        self.midsizer = wx.FlexGridSizer(4,3,vgap=10)
        self.boxlabel.Add(self.midsizer)
        
        self.SetSizer(self.boxlabel)

        #create some widgets for the midpanel
        self.sexlabel = wx.StaticText(parent=self,label='Sex: ')
        self.sexinputmale = wx.RadioButton(parent=self,label='Male',style=wx.RB_GROUP)
        self.sexinputfemale = wx.RadioButton(parent=self,label='Female')
        
        self.agelabel = wx.StaticText(self,label='Age: ')
        self.ageinput = wx.SpinCtrl(parent=self,size=(50,-1),style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        self.ageinput.SetRange(0,400)
        self.ageinput.SetValue(65)        

        self.weightlabel = wx.StaticText(parent=self,label='Weight: ')
        self.weightinput = wx.SpinCtrl(parent=self,size=(50,-1),style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        self.weightinput.SetRange(10,800)
        self.weightinput.SetValue(155)
        self.weightunits = wx.ComboBox(parent=self,choices=(['Pounds','Kilograms']),style=wx.CB_READONLY)
        self.weightunits.SetValue('Kilograms')        

        self.heightlabel = wx.StaticText(parent=self,label='Height: ')
        self.heightinput = wx.SpinCtrl(parent=self,size=(50,-1),style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        self.heightinput.SetRange(0,500)
        self.heightinput.SetValue(65)
        self.heightunits = wx.ComboBox(parent=self,choices=(['Inches','Centimeters']),style=wx.CB_READONLY)
        self.heightunits.SetValue('Inches')
        
        self.scrlabel = wx.StaticText(parent=self,label='Serum Creatinine: ')
        self.scrinput = FloatSpin(parent=self,value=1.1,min_val=0, max_val=10, increment=0.1,digits=1,size=(50,-1))
        self.scrunitslabel = wx.StaticText(parent=self,label=' mg/dL')
            
        #IBW widgets    
        self.IdealBodyWeightlabel = wx.StaticText(parent=self,label='Ideal Weight: ')
        self.IdealBodyWeightoutput = wx.StaticText(parent=self,label=str(self.form.IdealBodyWeight(self.getsex(),self.getheight())))
        self.IdealBodyWeightunits = wx.StaticText(parent=self,label='Kilograms')

        #CrCl Label updated
        self.crcllabel = wx.StaticText(parent=self,label='CrCl: ')
        self.crcloutput = wx.StaticText(parent=self,label=str(self.form.CrofGaul(self.getsex(),self.getage(),self.getCrClWeight(),self.getscr())))
        self.crclunits = wx.StaticText(parent=self,label=' ml/min')

        #Create VD label and value
        self.VDlabel = wx.StaticText(self,label='Estimated Volume of Distribution: ')
        self.VDoutput = wx.StaticText(self,label=str(round(self.getvd(),1)))
        self.VDunits = wx.StaticText(self,label='Liters')

        #create K label and value
        self.klabel = wx.StaticText(self,label='Estimated Rate Constant (k): ')
        self.koutput = wx.StaticText(self,label=str(round(self.getk(),5)))
        self.kunits = wx.StaticText(self,label=' /hour')

        #create half life label and value
        self.thalflabel = wx.StaticText(self,label='Estimated Half-Life: ')
        self.thalfoutput = wx.StaticText(self,label=str(round(self.getthalf(),1)))
        self.thalfunits = wx.StaticText(self,label=' hours')

        #place widgets into the sizer
        self.dummypanel = wx.Panel(parent=self)
        self.dummypanel1 = wx.Panel(parent=self)
        self.dummypanel2 = wx.Panel(parent=self)
        self.dummypanel3 = wx.Panel(parent=self)        
        self.midsizer.AddMany([(self.sexlabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), self.sexinputmale,self.sexinputfemale,
                               (self.agelabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), self.ageinput,self.dummypanel1,
                               (self.weightlabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), self.weightinput,self.weightunits,
                               (self.IdealBodyWeightlabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.IdealBodyWeightoutput,-1,wx.ALIGN_CENTER),(self.IdealBodyWeightunits,-1,wx.ALIGN_CENTER_VERTICAL),
                               (self.heightlabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), self.heightinput,self.heightunits,
                               (self.scrlabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),self.scrinput,(self.scrunitslabel,-1,wx.ALIGN_CENTER_VERTICAL),
                               (self.crcllabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.crcloutput,-1,wx.ALIGN_CENTER),(self.crclunits,-1,wx.ALIGN_CENTER_VERTICAL),
                               (self.VDlabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.VDoutput,-1,wx.ALIGN_CENTER),(self.VDunits,-1,wx.ALIGN_CENTER_VERTICAL),
                               (self.klabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.koutput,-1,wx.ALIGN_CENTER),(self.kunits,-1,wx.ALIGN_CENTER_VERTICAL),
                               (self.thalflabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.thalfoutput,-1,wx.ALIGN_CENTER),(self.thalfunits,-1,wx.ALIGN_CENTER_VERTICAL)])
        #self.boxlabel.Add(self.reloadbutton, flag=wx.ALIGN_CENTER)

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

class dosepane(wx.Panel):
    def __init__(self, parent, VD, ke):
        wx.Panel.__init__(self,parent=parent,style=wx.NO_BORDER)

        self.form = Formulas()
        self.vd = VD
        self.k = ke

        self.boxlabel = wx.StaticBoxSizer(wx.StaticBox(parent=self, label='Empiric Dosing'))
        self.midsizer = wx.FlexGridSizer(4,3,vgap=10)
        self.boxlabel.Add(self.midsizer)
        
        self.SetSizer(self.boxlabel)

        #Create the widgets
        self.peaklabel = wx.StaticText(self,label='Desired Loading Peak: ')
        self.peakinput = wx.SpinCtrl(parent=self,size=(50,-1),style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        self.peakunits = wx.StaticText(self,label=' mg/L')
        self.peakinput.SetRange(0,50)
        self.peakinput.SetValue(30)

        
        self.loaddose = self.getloadingdose()
        self.loadinglabel = wx.StaticText(self,label='Loading Dose: ')
        self.loadingoutput = wx.StaticText(self,label=str(self.loaddose))
        self.loadingunits = wx.StaticText(self,label=' mg')

        self.infutimelabel = wx.StaticText(self,label='Infusion Time: ')
        self.infutimeinput = wx.SpinCtrl(parent=self,size=(50,-1),style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        self.infutimeunits = wx.StaticText(self,label=' hours')
        self.infutimeinput.SetRange(1,5)
        self.infutimeinput.SetValue(2)

        self.cmaxlabel = wx.StaticText(self,label='Desired Cmax: ')
        self.cmaxinput = wx.SpinCtrl(parent=self,size=(50,-1),style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        self.cmaxunits = wx.StaticText(self,label=' mg/L')
        self.cmaxinput.SetRange(0,50)
        self.cmaxinput.SetValue(30)

        self.cminlabel = wx.StaticText(self,label='Desired Trough: ')
        self.cmininput = wx.SpinCtrl(parent=self,size=(50,-1),style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        self.cminunits = wx.StaticText(self,label=' mg/L')
        self.cmininput.SetRange(0,50)
        self.cmininput.SetValue(10)

        self.taulabel = wx.StaticText(self,label='Calculated Interval: ')
        self.tauoutput = wx.StaticText(self,label=str(round(self.gettau(),0)))
        self.tauunits = wx.StaticText(self,label=' hours')

        self.dtaulabel = wx.StaticText(self,label='Desired Interval: ')
        self.dtauinput = wx.SpinCtrl(parent=self,size=(50,-1),style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        self.dtauunits = wx.StaticText(self,label=' hours')
        self.dtauinput.SetRange(0,50)
        self.dtauinput.SetValue(10)

        self.MDlabel = wx.StaticText(self,label='Calculated Maintenance Dose: ')
        self.MDoutput = wx.StaticText(self,label=str(round(self.getMD(),0)))
        self.MDunits = wx.StaticText(self,label=' mg')

        self.dMDlabel = wx.StaticText(self,label='Desired Maintenance Dose: ')
        self.dMDinput = wx.SpinCtrl(parent=self,size=(75,-1),style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        self.dMDunits = wx.StaticText(self,label=' mg')
        self.dMDinput.SetRange(0,5000)
        self.dMDinput.SetValue(2000)

        self.fincmaxlabel = wx.StaticText(self,label='Calculated Cmax: ')
        self.fincmaxoutput = wx.StaticText(self,label=str(round(self.form.Estimated_Cmax_Steady_State(self.dMDinput.GetValue(),self.infutimeinput.GetValue(),self.k,self.vd,self.dtauinput.GetValue()),0)))
        self.fincmaxunits = wx.StaticText(self,label=' mg')

        self.cmax = self.form.Estimated_Cmax_Steady_State(self.dMDinput.GetValue(),self.infutimeinput.GetValue(),self.k,self.vd,self.dtauinput.GetValue())
        self.fincminlabel = wx.StaticText(self,label='Calculated Trough: ')
        self.fincminoutput = wx.StaticText(self,label=str(round(self.form.Estimated_Cmin(self.form.Estimated_Cmax_Steady_State(self.dMDinput.GetValue(),self.infutimeinput.GetValue(),self.k,self.vd,self.dtauinput.GetValue()), self.k, self.dtauinput.GetValue(), self.infutimeinput.GetValue()),0)))
        self.fincminunits = wx.StaticText(self,label=' mg')        

        #add widgets to the sizer
        self.line1 = wx.StaticLine(self)
        self.line2 = wx.StaticLine(self)
        self.line3 = wx.StaticLine(self)
        self.midsizer.AddMany([(self.peaklabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.peakinput,-1,wx.ALIGN_CENTER),(self.peakunits,-1,wx.ALIGN_CENTER_VERTICAL),
                               (self.loadinglabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.loadingoutput,-1,wx.ALIGN_CENTER),(self.loadingunits,-1,wx.ALIGN_CENTER_VERTICAL),
                               self.line1,self.line2,self.line3,
                               (self.infutimelabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.infutimeinput,-1,wx.ALIGN_CENTER),(self.infutimeunits,-1,wx.ALIGN_CENTER_VERTICAL),
                               (self.cmaxlabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.cmaxinput,-1,wx.ALIGN_CENTER),(self.cmaxunits,-1,wx.ALIGN_CENTER_VERTICAL),
                               (self.cminlabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.cmininput,-1,wx.ALIGN_CENTER),(self.cminunits,-1,wx.ALIGN_CENTER_VERTICAL),
                               (self.taulabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.tauoutput,-1,wx.ALIGN_CENTER),(self.tauunits,-1,wx.ALIGN_CENTER_VERTICAL),
                               (self.dtaulabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.dtauinput,-1,wx.ALIGN_CENTER),(self.dtauunits,-1,wx.ALIGN_CENTER_VERTICAL),
                               (self.MDlabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.MDoutput,-1,wx.ALIGN_CENTER),(self.MDunits,-1,wx.ALIGN_CENTER_VERTICAL),
                               (self.dMDlabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.dMDinput,-1,wx.ALIGN_CENTER),(self.dMDunits,-1,wx.ALIGN_CENTER_VERTICAL),
                               (self.fincmaxlabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.fincmaxoutput,-1,wx.ALIGN_CENTER),(self.fincmaxunits,-1,wx.ALIGN_CENTER_VERTICAL),
                               (self.fincminlabel,-1,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.fincminoutput,-1,wx.ALIGN_CENTER),(self.fincminunits,-1,wx.ALIGN_CENTER_VERTICAL)])
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

class patientspecificdosepane(wx.Panel):
    def __init__(self, parent,VD,ke):
        wx.Panel.__init__(self,parent=parent,style=wx.NO_BORDER)

        self.form = Formulas()
        self.vd = VD
        self.k = ke

        self.boxlabel = wx.StaticBoxSizer(wx.StaticBox(parent=self, label='Patient Specific Dosing'))
        self.midsizer = wx.GridBagSizer(10,10)
        self.boxlabel.Add(self.midsizer)
        
        self.SetSizer(self.boxlabel)

        #create widgets
        self.firstlevellabel = wx.StaticText(self,label='Measured Peak Level: ')
        self.firstlevelinput = FloatSpin(parent=self,value=28.9,min_val=0, max_val=60, increment=0.1,digits=1,size=(75,-1))
        self.firstlevelunits = wx.StaticText(self,label=' mcg/ml')

        self.firsttimefromdoselabel = wx.StaticText(self,label='Time from end of infusion: ')
        self.firsttimefromdoseinput = FloatSpin(parent=self,value=2.4,min_val=0, max_val=60, increment=0.1,digits=1,size=(75,-1))
        self.firsttimefromdoseunits = wx.StaticText(self,label=' hours')

        self.secondlevellabel = wx.StaticText(self,label='Measured Trough Level: ')
        self.secondlevelinput = FloatSpin(parent=self,value=7.0,min_val=0, max_val=60, increment=0.1,digits=1,size=(75,-1))
        self.secondlevelunits = wx.StaticText(self,label=' mcg/ml')

        self.secondtimefromdoselabel = wx.StaticText(self,label='Time until next infusion: ')
        self.secondtimefromdoseinput = FloatSpin(parent=self,value=2.4,min_val=0, max_val=60, increment=0.1,digits=1,size=(75,-1))
        self.secondtimefromdoseunits = wx.StaticText(self,label=' hours')

        self.timebetweenlabel = wx.StaticText(self,label='Time Elapsed Between Levels: ')
        self.timebetweeninput = FloatSpin(parent=self,value=17.1,min_val=0, max_val=100, increment=0.1,digits=1,size=(75,-1))
        self.timebetweenunits = wx.StaticText(self,label=' hours')

        self.infutimelabel = wx.StaticText(self,label='Infusion Time: ')
        self.infutimeinput = wx.SpinCtrl(parent=self,size=(50,-1),style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        self.infutimeunits = wx.StaticText(self,label=' hours')
        self.infutimeinput.SetRange(1,5)
        self.infutimeinput.SetValue(2)

        self.dtaulabel = wx.StaticText(self,label='Interval of Doses: ')
        self.dtauinput = wx.SpinCtrl(parent=self,size=(50,-1),style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        self.dtauunits = wx.StaticText(self,label=' hours')
        self.dtauinput.SetRange(0,50)
        self.dtauinput.SetValue(24)

        self.cmaxlabel = wx.StaticText(self,label='Desired Cmax: ')
        self.cmaxinput = wx.SpinCtrl(parent=self,size=(50,-1),style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        self.cmaxunits = wx.StaticText(self,label=' mg/L')
        self.cmaxinput.SetRange(0,50)
        self.cmaxinput.SetValue(30)

        self.cminlabel = wx.StaticText(self,label='Desired Trough: ')
        self.cmininput = wx.SpinCtrl(parent=self,size=(50,-1),style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        self.cminunits = wx.StaticText(self,label=' mg/L')
        self.cmininput.SetRange(0,50)
        self.cmininput.SetValue(10)

        self.klabel = wx.StaticText(self,label='Calculated Rate Constant (k): ')
        self.koutput = wx.StaticText(self,label=str(round(self.getk(),5)))
        self.kunits = wx.StaticText(self,label=' /hour')

        #setup graphing area
        self.plotpanel = wx.Panel(self)
        self.plotsizer = wx.BoxSizer(wx.VERTICAL)
        self.plotpanel.SetSizer(self.plotsizer)

        self.plotter = PlotCanvas(self.plotpanel)
        self.plotter.SetInitialSize(size=(700, 550))
        self.plotter.SetEnableGrid(True)
        #self.plotter.SetEnableLegend(True)
        #self.plotter.SetEnablePointLabel(True)
        #self.plotter.setLogScale((False,True))



        self.logline = [(0,self.getextratrough()),(self.infutimeinput.GetValue(),self.getextrapeak())]
        self.timechange=0        
        self.data = [(0,0), (2,3), (3,5), (4,6), (5,8)]
        
        self.line = PolyLine(self.logline, colour='blue', width=3)
        #self.line.setLogScale((False,True))
        self.marker = PolyMarker(self.data, marker='triangle')
        self.gc = PlotGraphics([self.line, self.marker], 'Drug Levels', 'Hours', 'mcg/ml')

        self.plotsizer.Add(self.plotter)

        #add widgets to the sizer
        self.dummypanel = wx.Panel(parent=self)
        self.dummypanel1 = wx.Panel(parent=self)
        self.dummypanel2 = wx.Panel(parent=self)
        self.dummypanel3 = wx.Panel(parent=self) 
        self.midsizer.AddMany([(self.firstlevellabel,(0,0),(1,1),wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.firstlevelinput,(0,1),(1,1),wx.ALIGN_CENTER),(self.firstlevelunits,(0,2),(1,1),wx.ALIGN_CENTER_VERTICAL),
                               (self.firsttimefromdoselabel,(1,0),(1,1),wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.firsttimefromdoseinput,(1,1),(1,1),wx.ALIGN_CENTER),(self.firsttimefromdoseunits,(1,2),(1,1),wx.ALIGN_CENTER_VERTICAL),
                               (self.secondlevellabel,(2,0),(1,1),wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.secondlevelinput,(2,1),(1,1),wx.ALIGN_CENTER),(self.secondlevelunits,(2,2),(1,1),wx.ALIGN_CENTER_VERTICAL),
                               (self.secondtimefromdoselabel,(3,0),(1,1),wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.secondtimefromdoseinput,(3,1),(1,1),wx.ALIGN_CENTER),(self.secondtimefromdoseunits,(3,2),(1,1),wx.ALIGN_CENTER_VERTICAL),
                               (self.timebetweenlabel,(4,0),(1,1),wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.timebetweeninput,(4,1),(1,1),wx.ALIGN_CENTER),(self.timebetweenunits,(4,2),(1,1),wx.ALIGN_CENTER_VERTICAL),
                               (self.infutimelabel,(5,0),(1,1),wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.infutimeinput,(5,1),(1,1),wx.ALIGN_CENTER),(self.infutimeunits,(5,2),(1,1),wx.ALIGN_CENTER_VERTICAL),
                               (self.dtaulabel,(6,0),(1,1),wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.dtauinput,(6,1),(1,1),wx.ALIGN_CENTER),(self.dtauunits,(6,2),(1,1),wx.ALIGN_CENTER_VERTICAL),
                               (self.cmaxlabel,(7,0),(1,1),wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.cmaxinput,(7,1),(1,1),wx.ALIGN_CENTER),(self.cmaxunits,(7,2),(1,1),wx.ALIGN_CENTER_VERTICAL),
                               (self.cminlabel,(8,0),(1,1),wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.cmininput,(8,1),(1,1),wx.ALIGN_CENTER),(self.cminunits,(8,2),(1,1),wx.ALIGN_CENTER_VERTICAL),
                               (self.klabel,(9,0),(1,1),wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT),(self.koutput,(9,1),(1,1),wx.ALIGN_CENTER),(self.kunits,(9,2),(1,1),wx.ALIGN_CENTER_VERTICAL),
                               (self.plotpanel,(0,4),(11,11),wx.ALIGN_CENTER)])

        self.reloading(wx.EVT_SPINCTRL)
        
    def updatelogline(self):
        self.logline = [(0,self.getextratrough()),(self.infutimeinput.GetValue(),self.getextrapeak())]
        self.timechange=0
        #create line points for the logline
        while self.timechange<(self.dtauinput.GetValue()-self.infutimeinput.GetValue()):
            self.infutime = self.infutimeinput.GetValue()
            self.top = self.getextrapeak()
            self.nextpoint = self.top*pow(e,(-self.getk()*self.timechange))
            self.logline.append((self.infutime+self.timechange,self.nextpoint))
            self.timechange = self.timechange + 0.4
           
    def getk(self):
        '''Calculates the ke when given two levels'''
        self.ke = log(self.firstlevelinput.GetValue()/self.secondlevelinput.GetValue())/(self.timebetweeninput.GetValue())
        return self.ke
    def getextrapeak(self):
        return self.firstlevelinput.GetValue()/pow(e,(-self.getk()*self.firsttimefromdoseinput.GetValue()))
    def getextratrough(self):
        return self.secondlevelinput.GetValue()*pow(e,(-self.getk()*self.secondtimefromdoseinput.GetValue()))
    def updategraphpoints(self):
        self.data[0]= (0,self.getextratrough())     #previous trough (extrapolated)
        self.data[1] = (self.infutimeinput.GetValue(),self.getextrapeak())  #extrapolated peak
        self.data[2] = ((self.infutimeinput.GetValue()+self.firsttimefromdoseinput.GetValue()),self.firstlevelinput.GetValue())  # time, measure peak level
        self.data[3] = ((self.infutimeinput.GetValue()+self.firsttimefromdoseinput.GetValue()+self.timebetweeninput.GetValue()),self.secondlevelinput.GetValue()) #measured trough level
        self.data[4] = ((self.infutimeinput.GetValue()+self.firsttimefromdoseinput.GetValue()+self.timebetweeninput.GetValue()+self.secondtimefromdoseinput.GetValue()),self.getextratrough())
        self.updatelogline()
        self.line = PolyLine(self.logline, colour='blue', width=3)
        self.marker = PolyMarker(self.data, marker='square',size=2,)
        self.gc = PlotGraphics([self.line, self.marker], 'Drug Levels', 'Hours', 'mcg/ml')
        self.plotter.Draw(self.gc)
    def reloading(self,event):
        self.koutput.SetLabel(str(round(self.getk(),5)))
        self.updategraphpoints()






class MainWindow(wx.Frame):
    '''the main window frame'''
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(400,800))

        self.Centre()
        self.SetBackgroundColour('Silver')
        #self.SetBackgroundStyle(BG_STYLE_COLOUR)

        # Create the menu items
        filemenu= wx.Menu() 
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        
        helpmenu = wx.Menu()
        menuAbout= helpmenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        
        #Create the menubar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the wx.MenuBar
        menuBar.Append(helpmenu,"Help") # Adding the "helpmenu" to the wx.MenuBar
        self.SetMenuBar(menuBar)  # Adding the wx.MenuBar to the wx.Frame content.

        #Create the top pane
        self.navpane = navpane(parent=self)

        #Create the demographics pane
        self.demographpane = demographicspane(self,self.navpane.getdrug(),self.navpane.getmodel())

        #create the dosing pane
        self.dosepane = dosepane(self,self.demographpane.getvd(),self.demographpane.getk())

        #create the patient specific dosing pane
        self.specificpane = patientspecificdosepane(self,self.demographpane.getvd(),self.demographpane.getk())

        #create debug button
        #self.debugbutton = wx.Button(self, label='Click Me')
        #self.debugbutton.Bind(wx.EVT_BUTTON,self.debugevent)
        
        #Create a status bar at the bottom of the window
        self.CreateStatusBar()

        #bindings
        self.navpane.empiricchoice.Bind(wx.EVT_COMBOBOX, self.changemodel)
        self.navpane.drugchoice.Bind(wx.EVT_COMBOBOX, self.update)

        self.demographpane.sexinputmale.Bind(wx.EVT_RADIOBUTTON, self.update)
        self.demographpane.sexinputfemale.Bind(wx.EVT_RADIOBUTTON, self.update)
        self.demographpane.ageinput.Bind(wx.EVT_SPINCTRL, self.update)
        self.demographpane.Bind(wx.EVT_SPINCTRL, self.update)  #weightinput.
        self.demographpane.weightunits.Bind(wx.EVT_COMBOBOX, self.update)
        self.demographpane.heightinput.Bind(wx.EVT_SPINCTRL, self.update)
        self.demographpane.heightunits.Bind(wx.EVT_COMBOBOX, self.update)
        self.demographpane.scrinput.Bind(EVT_FLOATSPIN,self.update)

        #self.demographpane.ageinput.Bind(wx.EVT_SET_FOCUS, self.demographpane.ageinput.SetSelection(0,-1))
        #self.demographpane.weightinput.Bind(wx.EVT_SET_FOCUS, self.demographpane.weightinput.SetSelection(0,-1))
        #self.demographpane.heightinput.Bind(wx.EVT_SET_FOCUS, self.demographpane.heightinput.SetSelection(0,-1))
        #self.heightunits.Bind(wx.EVT_KILL_FOCUS, self.scrinput.SelectAll())

        self.dosepane.peakinput.Bind(wx.EVT_SPINCTRL,self.update)
        self.dosepane.infutimeinput.Bind(wx.EVT_SPINCTRL,self.update)
        self.dosepane.cmaxinput.Bind(wx.EVT_SPINCTRL,self.update)
        self.dosepane.cmininput.Bind(wx.EVT_SPINCTRL,self.update)
        self.dosepane.dtauinput.Bind(wx.EVT_SPINCTRL,self.update)
        self.dosepane.dMDinput.Bind(wx.EVT_SPINCTRL,self.update)

        self.specificpane.firstlevelinput.Bind(EVT_FLOATSPIN,self.update)
        self.specificpane.firsttimefromdoseinput.Bind(EVT_FLOATSPIN,self.update)
        self.specificpane.secondlevelinput.Bind(EVT_FLOATSPIN,self.update)
        self.specificpane.secondtimefromdoseinput.Bind(EVT_FLOATSPIN,self.update)
        self.specificpane.timebetweeninput.Bind(EVT_FLOATSPIN,self.update)
        self.specificpane.infutimeinput.Bind(wx.EVT_SPINCTRL,self.update)
        self.specificpane.dtauinput.Bind(wx.EVT_SPINCTRL,self.update)
        self.specificpane.cmaxinput.Bind(EVT_FLOATSPIN,self.update)
        self.specificpane.cmininput.Bind(EVT_FLOATSPIN,self.update)



        #Setup sizer for main window
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainsizer.Add(self.navpane,flag=wx.ALIGN_CENTER)
        self.mainsizer.Add(self.demographpane,flag=wx.ALIGN_CENTER)
        self.mainsizer.Add(self.dosepane,flag=wx.ALIGN_CENTER)
        self.mainsizer.Add(self.specificpane,flag=wx.ALIGN_CENTER)
        
        ##self.mainsizer.Add(self.debugbutton,flag=wx.ALIGN_CENTER)
        
        self.SetSizer(self.mainsizer)
        self.SetAutoLayout(True)
        

        #Show Everything
        self.Show()
        self.specificpane.Hide()
        self.specificpane.plotter.Hide()
        self.mainsizer.Fit(self)
    def update(self,event):
        self.demographpane.drugmodel = self.navpane.getdrug()
        self.demographpane.reloading(event)
        self.dosepane.vd = self.demographpane.getvd()
        self.dosepane.k = self.demographpane.getk()
        self.dosepane.reloading(event)
        self.specificpane.reloading(event)
        #print self.navpane.getdrug()
    def debugevent(self,event):
        print self.specificpane.data
    def changemodel(self,event):
        if self.navpane.empiricchoice.GetValue()=='Patient Specific':
            self.dosepane.Hide()
            self.demographpane.Hide()
            self.specificpane.Show()
            self.specificpane.plotter.Show()
            self.mainsizer.Fit(self)
        else:
            self.dosepane.Show()
            self.demographpane.Show()
            self.specificpane.Hide()
            self.specificpane.plotter.Hide()
            self.mainsizer.Fit(self)
        
        
    

##formulas = Formulas()
app = wx.App(False)
mainwindow = MainWindow(None, "Dave's Kinetics Program")
app.MainLoop()


