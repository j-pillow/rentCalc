# ===== Import Modules =====

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tkinter import Tk, Label, StringVar, Entry, IntVar, DoubleVar, END, BOTH, TOP, Checkbutton
from tkinter.ttk import Button
from tkinter import N,S,E,W

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

# ===== /Import Modules/ =====

# ===== Define Classes =====

class Person:

    pa_limit = 100000
    personal_allowance = 12500

    lower_band = 50000
    higher_band = 150000

    ni_free_limit = 9500
    ni_lower_band = 50000

    student_loan_limit = 26575

    def __init__(self, name, pay, student=0, pension=0):
        self.name          = name
        self.pay           = pay
        self.student       = student
        self.pension_pcent = pension

        self.init_dicts()
        self.calc_all()

    def __repr__(self):
        stringToReturn = \
"""
Name:                             {name}
Student Loan:                     {student}
Income:                           £{pay:,.0f}
Pension Contribution:             £{pension:,.0f}
Personal Allowance:               £{PA:,.0f}
Taxable Income:                   £{taxable:,.0f}

Income Lower Band:                £{LB:,.0f}
Income Tax Lower Band (20%):      £{TaxLB:,.0f}

Income Higher Band:               £{HB:,.0f}
Income Tax Higher Band (40%):     £{TaxHB:,.0f}

Income Additional Band:           £{AB:,.0f}
Income Tax Additional Band (45%): £{TaxAB:,.0f}

National Insurance Lower Band:    £{niLB:,.0f}
NI Tax Lower Band:                £{TaxniLB:,.0f}

National Insurance Higher Band:   £{niHB:,.0f}
NI Tax:                           £{TaxniHB:,.0f}

Student Loan Band:                £{SL:,.0f}
Student Loan Repayment:           £{TaxSL:,.0f}

Total Tax:     £{tax:,.0f}
Take Home Pay:
Yearly:        £{yearPay:,.0f}
Monthly:       £{monthPay:,.0f}
Weekly:        £{weekPay:,.0f}
"""\
                .format(    name=self.name,
                            student="Yes" if self.student else "No",
                            pay=self.income,
                            pension=self.pension,
                            PA=self.taxDict["PA"],
                            taxable=self.pay - self.taxDict["PA"],
                            LB=self.taxDict["LB"],
                            TaxLB=self.taxAmounts["LB"],
                            HB=self.taxDict["HB"],
                            TaxHB=self.taxAmounts["HB"],
                            AB=self.taxDict["AB"],
                            TaxAB=self.taxAmounts["AB"],
                            niLB=self.taxDict["niLB"],
                            TaxniLB=self.taxAmounts["niLB"],
                            niHB=self.taxDict["niHB"],
                            TaxniHB=self.taxAmounts["niHB"],
                            SL=self.taxDict["SL"],
                            TaxSL=self.taxAmounts["SL"],
                            tax=self.totalTax,
                            yearPay=self.year,
                            monthPay=self.month,
                            weekPay=self.week
                        )
        return stringToReturn

    def init_dicts(self):
        self.taxDict    = { "PA": 0, "LB": 0, "HB": 0, "AB": 0, "niLB": 0, "niHB": 0, "SL": 0 }
        self.taxRates   = { "PA": 0, "LB": .2, "HB": .4, "AB": .45, "niLB": .12, "niHB": .02, "SL": .09 }
        self.taxAmounts = { "PA": 0, "LB": 0, "HB": 0, "AB": 0, "niLB": 0, "niHB": 0, "SL": 0 }
        self.totalTax = 0

    def calc_all(self):

        self.income  = self.pay
        self.pension = 0
        self.init_dicts()

        self.pa_calc()
        self.pension_calc()
        self.income_tax_calc()
        self.ni_calc()
        if self.student:
            self.student_loan()
        self.total_tax()

        self.year  = round(self.pay - self.totalTax,0)
        self.month = round(self.year / 12, 0)
        self.week  = round(self.year / 52, 0)


    def pa_calc( self ):
        if self.pay <= self.personal_allowance:
            self.taxDict["PA"] = self.pay
        elif self.pay <= self.pa_limit:
            self.taxDict["PA"] = self.personal_allowance
        elif self.pay <= self.pa_limit + (2 * self.personal_allowance):
            self.taxDict["PA"] = self.personal_allowance - np.floor( (self.pay - self.pa_limit) / 2)
        else:
            self.taxDict["PA"] = 0

    def pension_calc(self):
        self.pension = self.pension_pcent * self.pay
        self.pay -= self.pension


    def income_tax_calc(self):
        if self.pay <= self.personal_allowance:
            pass
        elif self.pay <= self.lower_band:
            self.taxDict["LB"] = self.pay - self.taxDict["PA"]
        elif self.pay <= self.higher_band:
            self.taxDict["LB"] = self.lower_band - self.taxDict["PA"]
            self.taxDict["HB"] = self.pay - self.taxDict["LB"] - self.taxDict["PA"]
        else:
            self.taxDict["LB"] = self.lower_band - self.taxDict["PA"]
            self.taxDict["HB"] = self.higher_band - self.taxDict["LB"] - self.taxDict["PA"]
            self.taxDict["AB"] = self.pay - self.higher_band

    def ni_calc(self):
        if self.income <= self.ni_free_limit:
            return
        elif self.income <= self.ni_lower_band:
            self.taxDict["niLB"] = self.income - self.ni_free_limit
        else:
            self.taxDict["niLB"] = self.ni_lower_band - self.ni_free_limit
            self.taxDict["niHB"] = self.income - self.ni_lower_band

    def student_loan(self):
        sl_repay = self.income - self.student_loan_limit
        self.taxDict["SL"] = sl_repay if sl_repay > 0 else 0

    def total_tax(self):
        for key in self.taxDict.keys():
            thisTax = self.taxDict[key] * self.taxRates[key]
            self.taxAmounts[key] = thisTax
            self.totalTax += thisTax

class UtilCalc:

    def __init__(self, master):
        self.master = master
        master.title("Utilities Calculator")

            # Init salaries
        self.james_sal = 0
        self.mark_sal  = 0
        
        self.james_penCont = 0
        self.mark_penCont  = 0

        self.james_student = IntVar()
        self.mark_student  = IntVar()
        
        self.j_student_button = Checkbutton(master, variable=self.james_student) 
        self.m_student_button = Checkbutton(master, variable=self.mark_student) 

            # Init tax values
        self.init_m()
        self.init_j()

            # Monthly and its labels
        self.monthly_total = 0
        self.monthly_total_text = IntVar()
        self.monthly_total_text.set(self.monthly_total)
        self.monthly_label = Label(master, textvariable=self.monthly_total_text)

        self.monthly_50_total = 0
        self.monthly_50_total_text = IntVar()
        self.monthly_50_total_text.set(self.monthly_50_total)
        self.monthly_50_label = Label(master, textvariable=self.monthly_50_total_text)

        self.monthly_45_total = 0
        self.monthly_45_total_text = IntVar()
        self.monthly_45_total_text.set(self.monthly_45_total)
        self.monthly_45_label = Label(master, textvariable=self.monthly_45_total_text)

        self.monthly_40_total = 0
        self.monthly_40_total_text = IntVar()
        self.monthly_40_total_text.set(self.monthly_40_total)
        self.monthly_40_label = Label(master, textvariable=self.monthly_40_total_text)

        self.monthly_35_total = 0
        self.monthly_35_total_text = IntVar()
        self.monthly_35_total_text.set(self.monthly_35_total)
        self.monthly_35_label = Label(master, textvariable=self.monthly_35_total_text)

        self.monthly_30_total = 0
        self.monthly_30_total_text = IntVar()
        self.monthly_30_total_text.set(self.monthly_30_total)
        self.monthly_30_label = Label(master, textvariable=self.monthly_30_total_text)

        self.monthly_25_total = 0
        self.monthly_25_total_text = IntVar()
        self.monthly_25_total_text.set(self.monthly_25_total)
        self.monthly_25_label = Label(master, textvariable=self.monthly_25_total_text)

            # Salary entry field and validator
        vcmd = master.register(self.validate) # we have to wrap the command
        self.james_salary_entry = Entry(master, validate="key", validatecommand=(vcmd, '%P', "j", "salary"))
        self.mark_salary_entry  = Entry(master, validate="key", validatecommand=(vcmd, '%P', "k", "salary"))
        
        self.james_penCont_entry = Entry(master, validate="key", validatecommand=(vcmd, '%P', "j", "pension"))
        self.mark_penCont_entry  = Entry(master, validate="key", validatecommand=(vcmd, '%P', "k", "pension"))

            # Calculation button
        self.quit_button = Button(master, text="Quit", command=self._quit)
        self.calc_button = Button(master, text="Calculate intervals", command=self.calcIt)

            # Labels for taxes
        self.label_list  =[ ("Pension Contribution:",    self.j_pension_label,    self.m_pension_label),
                            ("Personal Allowance:",      self.j_personal_label,   self.m_personal_label),
                            ("Taxable Income:",          self.j_taxable_label,    self.m_taxable_label),
                            ("Lower Band Taxable:",      self.j_lbTaxable_label,  self.m_lbTaxable_label),
                            ("Lower Band Tax:",          self.j_lbTax_label,      self.m_lbTax_label),
                            ("Higher Band Taxable:",     self.j_hbTaxable_label,  self.m_hbTaxable_label),
                            ("Higher Band Tax:",         self.j_hbTax_label,      self.m_hbTax_label),
                            ("Additional Band Taxable:", self.j_abTaxable_label,  self.m_abTaxable_label),
                            ("Additional Band Tax:",     self.j_abTax_label,      self.m_abTax_label),
                            ("NI Lower Band Taxable:",   self.j_nlbTaxable_label, self.m_nlbTaxable_label),
                            ("NI Lower Band Tax:",       self.j_nlbTax_label,     self.m_nlbTax_label),
                            ("NI Higher Band Taxable:",  self.j_nhbTaxable_label, self.m_nhbTaxable_label),
                            ("NI Higher Band Tax:",      self.j_nhbTax_label,     self.m_nhbTax_label),
                            ("Student Loan Taxable:",    self.j_slTaxable_label,  self.m_slTaxable_label),
                            ("Student Loan Tax:",        self.j_slTax_label,      self.m_slTax_label),
                            ("Total Tax:",               self.j_totalTax_label,   self.m_totalTax_label),
                            ("Yearly Income:",           self.j_year_label,       self.m_year_label),
                            ("Monthly Income:",          self.j_month_label,      self.m_month_label)
                          ]

        # LAYOUT
            # Row
        rowNumber = 0
        self.quit_button.grid( row=rowNumber, column=0, sticky=W )
        self.calc_button.grid( row=rowNumber, column=4, sticky=E )
        rowNumber += 1

            # Row
        self.textLabel( "Names:", rowNumber, 0, sticky=E )
        self.textLabel( "James",  rowNumber, 2 )
        self.textLabel( "Mark",   rowNumber, 4 )
        rowNumber += 1
        
            # Row
        self.textLabel( "Student Loan?", rowNumber, 0, sticky=E )
        self.j_student_button.grid( row=rowNumber, column=2 )
        self.m_student_button.grid( row=rowNumber, column=4 )
        rowNumber += 1

            # Row
        self.textLabel("Salary:", rowNumber, 0, sticky=E)
        self.textLabel("£", rowNumber, 1)
        self.james_salary_entry.grid( row=rowNumber, column=2 )
        self.textLabel("£",rowNumber,3)
        self.mark_salary_entry.grid( row=rowNumber, column=4 )
        rowNumber += 1
        
            # Row
        self.textLabel("Pension:", rowNumber, 0, sticky=E)
        self.textLabel("%", rowNumber, 1)
        self.james_penCont_entry.grid( row=rowNumber, column=2 )
        self.textLabel("%",rowNumber,3)
        self.mark_penCont_entry.grid( row=rowNumber, column=4 )
        rowNumber += 1

            # Row N
        for rowName, j_lab, m_lab in self.label_list:
            self.textLabel( rowName, rowNumber, 0, sticky=E )
            self.textLabel( "£",           rowNumber, 1, sticky=E )
            j_lab.grid(     row=rowNumber, column=2, sticky=W   )
            self.textLabel( "£",           rowNumber, 3, sticky=E )
            m_lab.grid(     row=rowNumber, column=4, sticky=W   )
            rowNumber +=1


            # Row N+1
        self.textLabel("Total Monthly Income:", rowNumber, 0, sticky=E)
        self.textLabel( "£", rowNumber, 1, sticky=E )
        self.monthly_label.grid( row=rowNumber, column=2, sticky=W )
        rowNumber += 1
        
        self.textLabel("50% Monthly Income:", rowNumber, 0, sticky=E)
        self.textLabel( "£", rowNumber, 1, sticky=E )
        self.monthly_50_label.grid( row=rowNumber, column=2, sticky=W )
        rowNumber += 1
        self.textLabel("45% Monthly Income:", rowNumber, 0, sticky=E)
        self.textLabel( "£", rowNumber, 1, sticky=E )
        self.monthly_45_label.grid( row=rowNumber, column=2, sticky=W )
        rowNumber += 1
        self.textLabel("40% Monthly Income:", rowNumber, 0, sticky=E)
        self.textLabel( "£", rowNumber, 1, sticky=E )
        self.monthly_40_label.grid( row=rowNumber, column=2, sticky=W )
        rowNumber += 1
        self.textLabel("35% Monthly Income:", rowNumber, 0, sticky=E)
        self.textLabel( "£", rowNumber, 1, sticky=E )
        self.monthly_35_label.grid( row=rowNumber, column=2, sticky=W )
        rowNumber += 1
        self.textLabel("30% Monthly Income:", rowNumber, 0, sticky=E)
        self.textLabel( "£", rowNumber, 1, sticky=E )
        self.monthly_30_label.grid( row=rowNumber, column=2, sticky=W )
        rowNumber += 1
        self.textLabel("25% Monthly Income:", rowNumber, 0, sticky=E)
        self.textLabel( "£", rowNumber, 1, sticky=E )
        self.monthly_25_label.grid( row=rowNumber, column=2, sticky=W )
        rowNumber += 1



    def validate(self, new_text, person, variable):
        if not new_text: # the field is being cleared
            if person == "j":
                if variable == "salary":
                    self.james_sal = 0
                elif variable == "pension":
                    self.james_penCont = 0
            else:
                if variable == "salary":
                    self.mark_sal = 0
                elif variable == "pension":
                    self.mark_penCont = 0
            return True

        try:
            if person == "j":
                if variable == "salary":
                    self.james_sal = int(new_text)
                elif variable == "pension":
                    self.james_penCont = float(new_text) / 100
            else:
                if variable == "salary":
                    self.mark_sal = int(new_text)
                elif variable == "pension":
                    self.mark_penCont = float(new_text) / 100
            return True
        except ValueError:
            return False

    def calcIt(self):
        james = Person("James", self.james_sal, self.james_student, self.james_penCont)
        mark  = Person("Mark",  self.mark_sal,  self.mark_student, self.mark_penCont)
        self.setValues(james, mark)

#        x_vals = list(range(25,50))
#        y_vals = [ (x/100) * self.monthly_total for x in x_vals ]
#
#        fig = Figure(figsize=(5, 4), dpi=100)
#        t = np.arange(0, 3, .01)
#        fig.add_subplot(111).plot( x_vals, y_vals )
#
#        canvas = FigureCanvasTkAgg(fig, master=self.master)  # A tk.DrawingArea.
#        canvas.draw()
#        canvas.get_tk_widget().grid( row=self.rowNumber, columnspan=5 )


    def textLabel(self, text, row, column, sticky=None):
        thisLabel = Label(self.master, text=text)
        thisLabel.grid( row=row, column=column, sticky=sticky )
        return thisLabel

    def varLabel(self, variableName):
        return Label(self.master, textvariable=variableName)

    def _quit(self):
        self.master.quit()     # stops mainloop
        self.master.destroy()  # this is necessary on Windows to prevent
                               # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def setValues(self, james, mark):
        self.j_pension    = james.pension
        self.j_personal   = james.taxDict["PA"]
        self.j_taxable    = james.pay - james.taxDict["PA"]
        self.j_lbTaxable  = james.taxDict["LB"]
        self.j_lbTax      = james.taxAmounts["LB"]
        self.j_hbTaxable  = james.taxDict["HB"]
        self.j_hbTax      = james.taxAmounts["HB"]
        self.j_abTaxable  = james.taxDict["AB"]
        self.j_abTax      = james.taxAmounts["AB"]
        self.j_nlbTaxable = james.taxDict["niLB"]
        self.j_nlbTax     = james.taxAmounts["niLB"]
        self.j_nhbTaxable = james.taxDict["niHB"]
        self.j_nhbTax     = james.taxAmounts["niHB"]
        self.j_slTaxable  = james.taxDict["SL"]
        self.j_slTax      = james.taxAmounts["SL"]
        self.j_totalTax   = james.totalTax
        self.j_year       = james.year
        self.j_month      = james.month
        
        self.m_pension    = mark.pension
        self.m_personal   = mark.taxDict["PA"]
        self.m_taxable    = mark.pay - james.taxDict["PA"]
        self.m_lbTaxable  = mark.taxDict["LB"]
        self.m_lbTax      = mark.taxAmounts["LB"]
        self.m_hbTaxable  = mark.taxDict["HB"]
        self.m_hbTax      = mark.taxAmounts["HB"]
        self.m_abTaxable  = mark.taxDict["AB"]
        self.m_abTax      = mark.taxAmounts["AB"]
        self.m_nlbTaxable = mark.taxDict["niLB"]
        self.m_nlbTax     = mark.taxAmounts["niLB"]
        self.m_nhbTaxable = mark.taxDict["niHB"]
        self.m_nhbTax     = mark.taxAmounts["niHB"]
        self.m_slTaxable  = mark.taxDict["SL"]
        self.m_slTax      = mark.taxAmounts["SL"]
        self.m_totalTax   = mark.totalTax
        self.m_year       = mark.year
        self.m_month      = mark.month

        self.monthly_total = james.month + mark.month
        self.monthly_50_total = round(self.monthly_total * .5,  0)
        self.monthly_45_total = round(self.monthly_total * .45, 0)
        self.monthly_40_total = round(self.monthly_total * .4,  0)
        self.monthly_35_total = round(self.monthly_total * .35, 0)
        self.monthly_30_total = round(self.monthly_total * .3,  0)
        self.monthly_25_total = round(self.monthly_total * .25, 0)

        self.setText()


    def setText(self):
        self.j_pension_text.set(self.j_pension)
        self.j_personal_text.set(self.j_personal)
        self.j_taxable_text.set(self.j_taxable)
        self.j_lbTaxable_text.set(self.j_lbTaxable)
        self.j_lbTax_text.set(self.j_lbTax)
        self.j_hbTaxable_text.set(self.j_hbTaxable)
        self.j_hbTax_text.set(self.j_hbTax)
        self.j_abTaxable_text.set(self.j_abTaxable)
        self.j_abTax_text.set(self.j_abTax)
        self.j_nlbTaxable_text.set(self.j_nlbTaxable)
        self.j_nlbTax_text.set(self.j_nlbTax)
        self.j_nhbTaxable_text.set(self.j_nhbTaxable)
        self.j_nhbTax_text.set(self.j_nhbTax)
        self.j_slTaxable_text.set(self.j_slTaxable)
        self.j_slTax_text.set(self.j_slTax)
        self.j_totalTax_text.set(self.j_totalTax)
        self.j_year_text.set(self.j_year)
        self.j_month_text.set(self.j_month)

        self.m_pension_text.set(self.m_pension)
        self.m_personal_text.set(self.m_personal)
        self.m_taxable_text.set(self.m_taxable)
        self.m_lbTaxable_text.set(self.m_lbTaxable)
        self.m_lbTax_text.set(self.m_lbTax)
        self.m_hbTaxable_text.set(self.m_hbTaxable)
        self.m_hbTax_text.set(self.m_hbTax)
        self.m_abTaxable_text.set(self.m_abTaxable)
        self.m_abTax_text.set(self.m_abTax)
        self.m_nlbTaxable_text.set(self.m_nlbTaxable)
        self.m_nlbTax_text.set(self.m_nlbTax)
        self.m_nhbTaxable_text.set(self.m_nhbTaxable)
        self.m_nhbTax_text.set(self.m_nhbTax)
        self.m_slTaxable_text.set(self.m_slTaxable)
        self.m_slTax_text.set(self.m_slTax)
        self.m_totalTax_text.set(self.m_totalTax)
        self.m_year_text.set(self.m_year)
        self.m_month_text.set(self.m_month)

        self.monthly_total_text.set(self.monthly_total)
        self.monthly_50_total_text.set(self.monthly_50_total)
        self.monthly_45_total_text.set(self.monthly_45_total)
        self.monthly_40_total_text.set(self.monthly_40_total)
        self.monthly_35_total_text.set(self.monthly_35_total)
        self.monthly_30_total_text.set(self.monthly_30_total)
        self.monthly_25_total_text.set(self.monthly_25_total)

    def init_m(self):
        self.m_pension,    self.m_pension_text = (0, IntVar())
        self.m_pension_text.set(self.m_pension)
        self.m_pension_label = self.varLabel( self.m_pension_text )

        self.m_personal,   self.m_personal_text   = (0, IntVar())
        self.m_personal_text.set(self.m_personal)
        self.m_personal_label = self.varLabel( self.m_personal_text )

        self.m_taxable,    self.m_taxable_text    = (0, IntVar())
        self.m_taxable_text.set(self.m_taxable)
        self.m_taxable_label = self.varLabel( self.m_taxable_text )

        self.m_lbTaxable,  self.m_lbTaxable_text  = (0, IntVar())
        self.m_lbTaxable_text.set(self.m_lbTaxable)
        self.m_lbTaxable_label = self.varLabel( self.m_lbTaxable_text )

        self.m_lbTax,      self.m_lbTax_text      = (0, IntVar())
        self.m_lbTax_text.set(self.m_lbTax)
        self.m_lbTax_label = self.varLabel( self.m_lbTax_text )

        self.m_hbTaxable,  self.m_hbTaxable_text  = (0, IntVar())
        self.m_hbTaxable_text.set(self.m_hbTaxable)
        self.m_hbTaxable_label = self.varLabel( self.m_hbTaxable_text )

        self.m_hbTax,      self.m_hbTax_text      = (0, IntVar())
        self.m_hbTax_text.set(self.m_hbTax)
        self.m_hbTax_label = self.varLabel( self.m_hbTax_text )

        self.m_abTaxable,  self.m_abTaxable_text  = (0, IntVar())
        self.m_abTaxable_text.set(self.m_abTaxable)
        self.m_abTaxable_label = self.varLabel( self.m_abTaxable_text )

        self.m_abTax,      self.m_abTax_text      = (0, IntVar())
        self.m_abTax_text.set(self.m_abTax)
        self.m_abTax_label = self.varLabel( self.m_abTax_text )

        self.m_nlbTaxable, self.m_nlbTaxable_text = (0, IntVar())
        self.m_nlbTaxable_text.set(self.m_nlbTaxable)
        self.m_nlbTaxable_label = self.varLabel( self.m_nlbTaxable_text )

        self.m_nlbTax,     self.m_nlbTax_text     = (0, IntVar())
        self.m_nlbTax_text.set(self.m_nlbTax)
        self.m_nlbTax_label = self.varLabel( self.m_nlbTax_text )

        self.m_nhbTaxable, self.m_nhbTaxable_text = (0, IntVar())
        self.m_nhbTaxable_text.set(self.m_nhbTaxable)
        self.m_nhbTaxable_label = self.varLabel( self.m_nhbTaxable_text )

        self.m_nhbTax,     self.m_nhbTax_text     = (0, IntVar())
        self.m_nhbTax_text.set(self.m_nhbTax)
        self.m_nhbTax_label = self.varLabel( self.m_nhbTax_text )

        self.m_slTaxable,  self.m_slTaxable_text  = (0, IntVar())
        self.m_slTaxable_text.set(self.m_slTaxable)
        self.m_slTaxable_label = self.varLabel( self.m_slTaxable_text )

        self.m_slTax,      self.m_slTax_text      = (0, IntVar())
        self.m_slTax_text.set(self.m_slTax)
        self.m_slTax_label = self.varLabel( self.m_slTax_text )

        self.m_totalTax,   self.m_totalTax_text   = (0, IntVar())
        self.m_totalTax_text.set(self.m_totalTax)
        self.m_totalTax_label = self.varLabel( self.m_totalTax_text )
        
        self.m_year,   self.m_year_text   = (0, IntVar())
        self.m_year_text.set(self.m_year)
        self.m_year_label = self.varLabel( self.m_year_text )
        
        self.m_month,   self.m_month_text   = (0, IntVar())
        self.m_month_text.set(self.m_month)
        self.m_month_label = self.varLabel( self.m_month_text )

    def init_j(self):
        self.j_pension,    self.j_pension_text = (0, IntVar())
        self.j_pension_text.set(self.j_pension)
        self.j_pension_label = self.varLabel( self.j_pension_text )

        self.j_personal,   self.j_personal_text   = (0, IntVar())
        self.j_personal_text.set(self.j_personal)
        self.j_personal_label = self.varLabel( self.j_personal_text )

        self.j_taxable,    self.j_taxable_text    = (0, IntVar())
        self.j_taxable_text.set(self.j_taxable)
        self.j_taxable_label = self.varLabel( self.j_taxable_text )

        self.j_lbTaxable,  self.j_lbTaxable_text  = (0, IntVar())
        self.j_lbTaxable_text.set(self.j_lbTaxable)
        self.j_lbTaxable_label = self.varLabel( self.j_lbTaxable_text )

        self.j_lbTax,      self.j_lbTax_text      = (0, IntVar())
        self.j_lbTax_text.set(self.j_lbTax)
        self.j_lbTax_label = self.varLabel( self.j_lbTax_text )

        self.j_hbTaxable,  self.j_hbTaxable_text  = (0, IntVar())
        self.j_hbTaxable_text.set(self.j_hbTaxable)
        self.j_hbTaxable_label = self.varLabel( self.j_hbTaxable_text )

        self.j_hbTax,      self.j_hbTax_text      = (0, IntVar())
        self.j_hbTax_text.set(self.j_hbTax)
        self.j_hbTax_label = self.varLabel( self.j_hbTax_text )

        self.j_abTaxable,  self.j_abTaxable_text  = (0, IntVar())
        self.j_abTaxable_text.set(self.j_abTaxable)
        self.j_abTaxable_label = self.varLabel( self.j_abTaxable_text )

        self.j_abTax,      self.j_abTax_text      = (0, IntVar())
        self.j_abTax_text.set(self.j_abTax)
        self.j_abTax_label = self.varLabel( self.j_abTax_text )

        self.j_nlbTaxable, self.j_nlbTaxable_text = (0, IntVar())
        self.j_nlbTaxable_text.set(self.j_nlbTaxable)
        self.j_nlbTaxable_label = self.varLabel( self.j_nlbTaxable_text )

        self.j_nlbTax,     self.j_nlbTax_text     = (0, IntVar())
        self.j_nlbTax_text.set(self.j_nlbTax)
        self.j_nlbTax_label = self.varLabel( self.j_nlbTax_text )

        self.j_nhbTaxable, self.j_nhbTaxable_text = (0, IntVar())
        self.j_nhbTaxable_text.set(self.j_nhbTaxable)
        self.j_nhbTaxable_label = self.varLabel( self.j_nhbTaxable_text )

        self.j_nhbTax,     self.j_nhbTax_text     = (0, IntVar())
        self.j_nhbTax_text.set(self.j_nhbTax)
        self.j_nhbTax_label = self.varLabel( self.j_nhbTax_text )

        self.j_slTaxable,  self.j_slTaxable_text  = (0, IntVar())
        self.j_slTaxable_text.set(self.j_slTaxable)
        self.j_slTaxable_label = self.varLabel( self.j_slTaxable_text )

        self.j_slTax,      self.j_slTax_text      = (0, IntVar())
        self.j_slTax_text.set(self.j_slTax)
        self.j_slTax_label = self.varLabel( self.j_slTax_text )

        self.j_totalTax,   self.j_totalTax_text   = (0, IntVar())
        self.j_totalTax_text.set(self.j_totalTax)
        self.j_totalTax_label = self.varLabel( self.j_totalTax_text )
        
        self.j_year,   self.j_year_text   = (0, IntVar())
        self.j_year_text.set(self.j_year)
        self.j_year_label = self.varLabel( self.j_year_text )
        
        self.j_month,   self.j_month_text   = (0, IntVar())
        self.j_month_text.set(self.j_month)
        self.j_month_label = self.varLabel( self.j_month_text )

class Poop:

    def __init__(self):

        self.setStuff()

    def setStuff(self):
        self.x = 10

# ===== /Define Classes/ =====

# ===== Define Functions =====

def main():

    root = Tk()
    my_gui = UtilCalc(root)
    root.mainloop()


#    James = Person( "James", 35000, 1, .04 )
#    Mark  = Person( "Mark",  35000, 1, .04 )
#    print(James)
#
#    lower_bound = .35
#    upper_bound = .45
#
#    utility_cTax_est = 350
#
#    pay_range = range(30000, 60150, 50)
#    monthly_take = np.array([ Mark.month + Person("James", pay, 1, .04).month for pay in pay_range ])
#
#    fig = plt.figure(constrained_layout=True, figsize=(15,10))
#
#    #plt.plot( pay_range, [Mark.month for i in pay_range],                           c='xkcd:tomato', lw=2, ls='--', label="Mark at £{:,.0f}".format(Mark.income)  )
#    #plt.plot( pay_range, [Person("James", pay, 1, .04).month for pay in pay_range], c='xkcd:purple', lw=2, ls='--', label="James at £x-value"  )
#
#    plt.plot( pay_range, [Mark.month for i in pay_range],                           c='xkcd:tomato', lw=3, ls='--' )
#    plt.text( 30100, Mark.month + 150, "Mark monthly:", fontsize=20, c='xkcd:tomato', fontweight='bold')
#    plt.text( 30100, Mark.month + 40,  "£{:,.0f}".format(Mark.month), fontsize=20, c='xkcd:tomato', fontweight='bold')
#
#    plt.plot( pay_range, [Person("James", pay, 1, .04).month for pay in pay_range], c='xkcd:purple', lw=3, ls='--' )
#    plt.text( 40000, 2430, "James monthly", rotation=18, fontsize=20, c='xkcd:purple', fontweight='bold')
#
#
#    #plt.plot( pay_range, monthly_take, label="Mark + James", lw=2, c='xkcd:magenta'  )
#
#    plt.fill_between( pay_range, monthly_take * upper_bound, monthly_take * lower_bound, alpha=0.3, fc='xkcd:azure', label="{:.0f}% to {:.0f}% band".format(lower_bound*100,upper_bound*100) )
#    plt.plot( pay_range, monthly_take * upper_bound, lw=2, alpha=0.6, c='xkcd:azure'  )
#    plt.plot( pay_range, monthly_take * lower_bound, lw=2, alpha=0.6, c='xkcd:azure'  )
#    #plt.plot( pay_range, monthly_take * ((lower_bound+upper_bound)/2), lw=2, alpha=0.6, c='xkcd:black', ls='--'  )
#
#    plt.fill_between( pay_range, monthly_take * upper_bound - utility_cTax_est, monthly_take * lower_bound - utility_cTax_est, alpha=0.3, fc='xkcd:orange', label="{:.0f}% to {:.0f}% band less estimated utilities and council tax".format(lower_bound*100,upper_bound*100) )
#    plt.plot( pay_range, monthly_take * upper_bound - utility_cTax_est, lw=2, alpha=0.6, c='xkcd:orange'  )
#    plt.plot( pay_range, monthly_take * lower_bound - utility_cTax_est, lw=2, alpha=0.6, c='xkcd:orange'  )
#    #plt.plot( pay_range, monthly_take * ((lower_bound+upper_bound)/2) - utility_cTax_est, lw=2, alpha=0.6, c='xkcd:black', ls='--'  )
#
#    plt.scatter(   range(35000,60000,5000),
#                   [ (Mark.month + Person("James", pay, 1, .04).month) * lower_bound for pay in range(35000,60000,5000)],
#                   c='xkcd:azure'
#            )
#    plt.scatter(   range(35000,60000,5000),
#                   [ (Mark.month + Person("James", pay, 1, .04).month) * upper_bound for pay in range(35000,60000,5000)],
#                   c='xkcd:azure'
#            )
#
#    plt.scatter(   range(35000,60000,5000),
#                   [ (Mark.month + Person("James", pay, 1, .04).month) * lower_bound - utility_cTax_est for pay in range(35000,60000,5000)],
#                   c='xkcd:orange'
#            )
#    plt.scatter(   range(35000,60000,5000),
#                   [ (Mark.month + Person("James", pay, 1, .04).month) * upper_bound - utility_cTax_est for pay in range(35000,60000,5000)],
#                   c='xkcd:orange'
#            )
#
#    for pay in range(35000,60000,5000):
#        upper_cost = (Mark.month + Person("James", pay, 1, .04).month) * upper_bound
#        lower_cost = (Mark.month + Person("James", pay, 1, .04).month) * lower_bound
#
#        upper_cost_less = (Mark.month + Person("James", pay, 1, .04).month) * upper_bound - utility_cTax_est
#        lower_cost_less = (Mark.month + Person("James", pay, 1, .04).month) * lower_bound - utility_cTax_est
#
#        plt.text( pay, -70 + upper_cost, "£{:,.0f}".format(upper_cost), fontsize=15)
#        plt.text( pay, -70 + lower_cost, "£{:,.0f}".format(lower_cost), fontsize=15)
#
#        plt.text( pay, 20 + upper_cost_less, "£{:,.0f}".format(upper_cost_less), ha='right', fontsize=15)
#        plt.text( pay, 20 + lower_cost_less, "£{:,.0f}".format(lower_cost_less), ha='right', fontsize=15)
#
#        plt.text( pay, -150 + lower_cost_less, "£{:,.0f}".format(pay), ha='center', fontsize=15, fontweight='bold')
#        plt.plot( [pay,pay], [lower_cost, upper_cost], c='xkcd:azure', zorder=0 )
#        plt.plot( [pay,pay], [lower_cost_less, upper_cost_less], c='xkcd:orange', zorder=0 )
#
#
#    plt.ylim(500)
#    plt.xlim(min(pay_range))
#    ax = plt.gca()
#    ax.tick_params(axis='both', which='major', labelsize=15)
#    plt.xlabel("James' Salary (£)",fontsize=20,fontweight='bold')
#    plt.ylabel("Cost (£)",fontsize=20,fontweight='bold')
#    plt.legend(fontsize=20)
#    plt.savefig("income.pdf")


# ===== /Define Functions/ =====

# ===== Main Program =====

if __name__ == '__main__':
    main()

# ===== /Main Program/ =====

