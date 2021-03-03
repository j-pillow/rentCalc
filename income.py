# ===== Import Modules =====

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
            

            

# ===== /Define Classes/ =====

# ===== Define Functions =====

def main():

    James = Person( "James", 35000, 1, .04 )
    Mark  = Person( "Mark",  35000, 1, .04 )
    print(James)
    
    lower_bound = .35
    upper_bound = .45

    utility_cTax_est = 350

    pay_range = range(30000, 60150, 50)
    monthly_take = np.array([ Mark.month + Person("James", pay, 1, .04).month for pay in pay_range ])

    fig = plt.figure(constrained_layout=True, figsize=(15,10))

    #plt.plot( pay_range, [Mark.month for i in pay_range],                           c='xkcd:tomato', lw=2, ls='--', label="Mark at £{:,.0f}".format(Mark.income)  )
    #plt.plot( pay_range, [Person("James", pay, 1, .04).month for pay in pay_range], c='xkcd:purple', lw=2, ls='--', label="James at £x-value"  )
   
    plt.plot( pay_range, [Mark.month for i in pay_range],                           c='xkcd:tomato', lw=3, ls='--' )
    plt.text( 30100, Mark.month + 150, "Mark monthly:", fontsize=20, c='xkcd:tomato', fontweight='bold')
    plt.text( 30100, Mark.month + 40,  "£{:,.0f}".format(Mark.month), fontsize=20, c='xkcd:tomato', fontweight='bold')
    
    plt.plot( pay_range, [Person("James", pay, 1, .04).month for pay in pay_range], c='xkcd:purple', lw=3, ls='--' )
    plt.text( 40000, 2430, "James monthly", rotation=18, fontsize=20, c='xkcd:purple', fontweight='bold')
    

    #plt.plot( pay_range, monthly_take, label="Mark + James", lw=2, c='xkcd:magenta'  )

    plt.fill_between( pay_range, monthly_take * upper_bound, monthly_take * lower_bound, alpha=0.3, fc='xkcd:azure', label="{:.0f}% to {:.0f}% band".format(lower_bound*100,upper_bound*100) )
    plt.plot( pay_range, monthly_take * upper_bound, lw=2, alpha=0.6, c='xkcd:azure'  )
    plt.plot( pay_range, monthly_take * lower_bound, lw=2, alpha=0.6, c='xkcd:azure'  )
    #plt.plot( pay_range, monthly_take * ((lower_bound+upper_bound)/2), lw=2, alpha=0.6, c='xkcd:black', ls='--'  )
    
    plt.fill_between( pay_range, monthly_take * upper_bound - utility_cTax_est, monthly_take * lower_bound - utility_cTax_est, alpha=0.3, fc='xkcd:orange', label="{:.0f}% to {:.0f}% band less estimated utilities and council tax".format(lower_bound*100,upper_bound*100) )
    plt.plot( pay_range, monthly_take * upper_bound - utility_cTax_est, lw=2, alpha=0.6, c='xkcd:orange'  )
    plt.plot( pay_range, monthly_take * lower_bound - utility_cTax_est, lw=2, alpha=0.6, c='xkcd:orange'  )
    #plt.plot( pay_range, monthly_take * ((lower_bound+upper_bound)/2) - utility_cTax_est, lw=2, alpha=0.6, c='xkcd:black', ls='--'  )

    plt.scatter(   range(35000,60000,5000),
                   [ (Mark.month + Person("James", pay, 1, .04).month) * lower_bound for pay in range(35000,60000,5000)], 
                   c='xkcd:azure'
            )
    plt.scatter(   range(35000,60000,5000),
                   [ (Mark.month + Person("James", pay, 1, .04).month) * upper_bound for pay in range(35000,60000,5000)],
                   c='xkcd:azure'
            )
    
    plt.scatter(   range(35000,60000,5000),
                   [ (Mark.month + Person("James", pay, 1, .04).month) * lower_bound - utility_cTax_est for pay in range(35000,60000,5000)], 
                   c='xkcd:orange'
            )
    plt.scatter(   range(35000,60000,5000),
                   [ (Mark.month + Person("James", pay, 1, .04).month) * upper_bound - utility_cTax_est for pay in range(35000,60000,5000)],
                   c='xkcd:orange'
            )
    
    for pay in range(35000,60000,5000):
        upper_cost = (Mark.month + Person("James", pay, 1, .04).month) * upper_bound
        lower_cost = (Mark.month + Person("James", pay, 1, .04).month) * lower_bound

        upper_cost_less = (Mark.month + Person("James", pay, 1, .04).month) * upper_bound - utility_cTax_est
        lower_cost_less = (Mark.month + Person("James", pay, 1, .04).month) * lower_bound - utility_cTax_est

        plt.text( pay, -70 + upper_cost, "£{:,.0f}".format(upper_cost), fontsize=15)
        plt.text( pay, -70 + lower_cost, "£{:,.0f}".format(lower_cost), fontsize=15)
        
        plt.text( pay, 20 + upper_cost_less, "£{:,.0f}".format(upper_cost_less), ha='right', fontsize=15)
        plt.text( pay, 20 + lower_cost_less, "£{:,.0f}".format(lower_cost_less), ha='right', fontsize=15)
        
        plt.text( pay, -150 + lower_cost_less, "£{:,.0f}".format(pay), ha='center', fontsize=15, fontweight='bold')
        plt.plot( [pay,pay], [lower_cost, upper_cost], c='xkcd:azure', zorder=0 )
        plt.plot( [pay,pay], [lower_cost_less, upper_cost_less], c='xkcd:orange', zorder=0 )


    plt.ylim(500)
    plt.xlim(min(pay_range))
    ax = plt.gca()
    ax.tick_params(axis='both', which='major', labelsize=15)
    plt.xlabel("James' Salary (£)",fontsize=20,fontweight='bold')
    plt.ylabel("Cost (£)",fontsize=20,fontweight='bold')
    plt.legend(fontsize=20)
    plt.savefig("income.pdf")


# ===== /Define Functions/ =====

# ===== Main Program =====

if __name__ == '__main__':
    main()

# ===== /Main Program/ =====

