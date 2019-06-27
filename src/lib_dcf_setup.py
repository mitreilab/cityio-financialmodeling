import json
import urllib
import numpy as np
import matplotlib.pyplot as plt


# read json file
url_file = urllib.request.urlopen('http://cityio.media.mit.edu/api/table/citymatrix_volpe')
url_file_text = url_file.read()
json_data = json.loads(url_file_text)


class scenario(object):
    # scenario object holds all drivers, time horizon, and json file input
    def __init__(self, name, economy, technology, policy, context, periods, json_file):
        self.name = name
        self.economy = economy
        self.technology = technology
        self.policy = policy
        self.context = context
        self.periods = periods
        self.json_file = json_file
        self.city = city(self, json_file['grid'])
    def print_name(self):
        print(self.name)
    def get_context(self):
        return self.context
    def get_periods(self):
        return self.periods
    def get_city(self):
        return self.city


class economy(object):
    # economy object holds macro trends
    def __init__(self, inflation):
        self.inflation = inflation

    def get_inflation(self):
        return self.inflation


class technology(object):
    # technology object holds drivers related to tech factors
    pass
class policy(object):
    # policy object holds drivers related to policy factors
    pass
class context(object):
    # context object holds data related to current building data and investor preferences
    def __init__(self, discount_rate):
        # store building data in dictionary; index by type name
        self.building_type_data = {}
        self.discount_rate = discount_rate
    def add_building_type(self, name, base_rent, other_income, base_opex, area, base_vacancy, going_in_cap, exit_cap, rent_trend, other_trend, opex_tred, vacancy_trend, capex_margin, TI_margin,leasing_margin,CAM_margin):
        new = building_type(name, base_rent, other_income, base_opex, area, base_vacancy, going_in_cap, exit_cap, rent_trend, other_trend, opex_tred, vacancy_trend, capex_margin, TI_margin,leasing_margin,CAM_margin)
        self.building_type_data[name] = new
    def get_type_object(self,name):
        return self.building_type_data[name]
    def add_discount_rate(self, discount_rate):
        self.discount_rate = discount_rate
    def get_discount_rate(self):
        return self.discount_rate


class building_type(object):
    # building type object stores data particular to an individual building type
    def __init__(self, name, base_rent, other_income, base_opex, area, base_vacancy, going_in_cap, exit_cap, rent_trend, other_trend, opex_tred, vacancy_trend, capex_margin, TI_margin,leasing_margin,CAM_margin):
        self.name = name
        self.rent = base_rent
        self.other = other_income
        self.opex = base_opex
        self.area = area
        self.vacancy = base_vacancy
        self.going_in_cap = going_in_cap
        self.exit_cap = exit_cap

        self.rent_trend = rent_trend
        self.other_trend = other_trend
        self.opex_trend = opex_tred
        self.vacancy_trend = vacancy_trend
        self.capex_margin = capex_margin
        self.TI_margin = TI_margin
        self.leasing_margin = leasing_margin
        self.CAM_margin = CAM_margin
    def get_area(self):
        return self.area
    def get_name(self):
        return self.name
    def get_rent(self):
        return self.rent
    def get_vacancy(self):
        return self.vacancy
    def get_opex(self):
        return self.opex
    def get_other_income(self):
        return self.other
    def get_going_in_cap(self):
        return self.going_in_cap
    def get_exit_cap(self):
        return self.exit_cap
    def get_rent_trend(self):
        return self.rent_trend
    def get_other_trend(self):
        return self.other_trend
    def get_opex_trend(self):
        return self.opex_trend
    def get_capex_margin(self):
        return self.capex_margin
    def get_TI_margin(self):
        return self.TI_margin
    def get_leasing_margin(self):
        return self.leasing_margin
    def get_CAM_margin(self):
        return self.CAM_margin

class city(object):
    # city object stores all of the buildings in the city
    def __init__(self, scenario, json_grid_dict_list):
        # store scenario and buildings
        self.scenario = scenario
        self.buildings = []
        #for position_dict in json_grid_dict_list:
            #x, y, building_type, rot = position_dict['x'], position_dict['y'], position_dict['type'], position_dict['rot']
            #self.buildings.append(building(x,y,building_type,rot, self))
    def get_scenario(self):
        return self.scenario
    def get_buildings(self):
        return self.buildings

class building(object):
    # building object stores data of a building instance
    def __init__(self, x, y, building_type, rotation, city):
        self.x = x
        self.y = y
        self.type = building_type
        self.rotation = rotation
        self.city = city
        self.area = cell(city.get_scenario().get_context().get_type_object(building_type).get_area(), 'area') # need to get from type
        self.pro_forma = None
    def get_position(self):
        return (x,y)
    def generate_pro_forma(self):
        self.pro_forma = pro_forma_table(self)
    def get_city(self):
        return self.city
    def get_type(self):
        return self.type
    def get_area(self):
        return self.area
    def get_pro_forma(self):
        return self.pro_forma



class pro_forma_table(object):
    # pro forma table stores data and methods related to calculating pro
    def __init__(self, building):
        # represent line item rows and time period columns
        self.line_items = {}
        self.time_periods = {}
        self.total_time = building.get_city().get_scenario().get_periods()
        self.building = building
        self.IRR = None
        self.NPV_rate = (None, None)
    item_names = ["PGI", "Vacancy", "EGI", 'Other Income', 'Revenue', "Opex", "NOI", 'Capex', 'TI', 'Leasing Costs', 'CAM', 'Purchase','Reversion', 'PBTCF']
    def fill_row(self,name,trend_list,base_value, percent_change = True, filled_entry = False):
        # function to complete a row in the pro forma
        # based on either a base and growth rate, or a margin calculation
        if filled_entry:
            line_item = trend_list
        else:
            line_item = []
            for time in range(self.total_time):
                if time == 0:
                    line_item.append(cell(base_value, name))
                # consider if changing by percentage of or by percentage points
                elif percent_change:
                    last = line_item[-1]
                    new = last*(cell(1,'one')+trend_list[time-1])
                    line_item.append(new)
                else:
                    last = line_item[-1]
                    new = last + trend_list[time-1]
                    line_item.append(new)
        self.line_items[name] = line_item
    def fill_time_periods(self):
        # make dictionary to organize line items for a particular year
        for time in range(self.total_time):
            self.time_periods[time] = [self.line_items[name][time] for name in pro_forma_table.item_names]
    def visualize_table(self, building_number):
        # use matplotlib to print visualization of table
        table_array = []
        for line_item in pro_forma_table.item_names:
            table_array.append([c.get_value()/1000000*10//1/10 for c in self.line_items[line_item]])

        fig, axs = plt.subplots(1, 1, dpi = 200, figsize = (11,10))
        table_np_data = np.array(table_array)
        collabel = ["Year " + str(y) for y in range(0, self.total_time+1)]
        rowlabel = self.item_names
        axs.axis('tight')
        axs.axis('off')
        the_table = axs.table(cellText=table_np_data, colLabels=collabel, loc='center', rowLabels=rowlabel, rowLoc='right', )
        the_table.auto_set_column_width(range(-1,self.total_time))
        the_table.set_fontsize(9)
        fig.suptitle('Building Number: ' + str(building_number) + '\n IRR: ' + str(self.IRR*10000//1/100) + '%' +'\n' 'NPV discounted at ' + str(self.NPV_rate[1]*10000//1/100) + '%: $' + str(self.NPV_rate[0]//1000000) +  'M\n Prices shown in $ millons')
        plt.show()





    # methods for calculating line time rows
    def calculate_PGI(self):
        PGI = [cell(0,'zero')]
        PGI.extend([c*self.building.get_area() for c in self.line_items['rent psf']])
        self.line_items['PGI'] = PGI
        return PGI
    def calculate_vacancy(self):
        PGI = self.calculate_PGI()
        vacancy_rate = self.line_items['vacancy rate']
        vacancy = [cell(0,'zero')]
        for i in range(len(PGI)-1):
            vacancy.append(cell(-1,'negative')*PGI[1+i]*vacancy_rate[i])
        self.line_items['Vacancy'] = vacancy
        return vacancy
    def calculate_EGI(self):
        vacancy = self.calculate_vacancy()
        PGI = self.line_items['PGI']
        EGI = []
        for i in range(len(PGI)):
            EGI.append(PGI[i] + vacancy[i])
        self.line_items['EGI'] = EGI
        return EGI
    def calculate_other_income(self):
        other = [cell(0,'zero')]
        other.extend([c * self.building.get_area() for c in self.line_items['other_income psf']])
        self.line_items['Other Income'] = other
        return other
    def calculate_revenue(self):
        EGI = self.calculate_EGI()
        other = self.calculate_other_income()
        revenue = []
        for i in range(len(EGI)):
            revenue.append(EGI[i] + other[i])
        self.line_items['Revenue'] = revenue
        return revenue
    def calculate_opex(self):
        opex = [cell(0,'zero')]
        opex.extend([cell(-1,'negative')* c * self.building.get_area() for c in self.line_items['opex psf']])
        self.line_items['Opex'] = opex
        return opex
    def calculate_NOI(self):
        revenue = self.calculate_revenue()
        opex = self.calculate_opex()
        NOI = []
        for i in range(len(revenue)):
            NOI.append(revenue[i] + opex[i])
        self.line_items['NOI'] = NOI
        return NOI
    def calculate_Capex(self):
        reveneue = self.calculate_revenue()
        margin = self.line_items['Capex margin']
        capex = []
        for i in range(len(reveneue)):
            capex.append(cell(-1,'negative')*reveneue[i]*margin[i])
        self.line_items['Capex'] = capex
        return capex
    def calculate_TI(self):
        reveneue = self.calculate_revenue()
        margin = self.line_items['TI margin']
        TI = []
        for i in range(len(reveneue)):
            TI.append(cell(-1,'negative')*reveneue[i]*margin[i])
        self.line_items['TI'] = TI
        return TI
    def calculate_Leasing(self):
        reveneue = self.calculate_revenue()
        margin = self.line_items['Leasing margin']
        leasing = []
        for i in range(len(reveneue)):
            leasing.append(cell(-1,'negative')*reveneue[i]*margin[i])
        self.line_items['Leasing Costs'] = leasing
        return leasing
    def calculate_CAM(self):
        reveneue = self.calculate_revenue()
        margin = self.line_items['CAM margin']
        CAM = []
        for i in range(len(reveneue)):
            CAM.append(cell(-1,'negative')*reveneue[i]*margin[i])
        self.line_items['CAM'] = CAM
        return CAM
    def calculate_reversion(self):
        forward_NOI = self.calculate_NOI()[-1].get_value()
        cap = self.building.get_city().get_scenario().get_context().get_type_object(self.building.get_type()).get_exit_cap()
        reversion_value = forward_NOI / cap
        reversion = [cell(0, 'zero') for i in range(0,self.total_time-1)]
        reversion.append(cell(reversion_value, 'Reversion'))
        reversion.append(cell(0,'zero'))
        self.line_items['Reversion'] = reversion
        return reversion
    def calculate_purchase(self):
        forward_NOI = self.calculate_NOI()[1].get_value()
        cap = self.building.get_city().get_scenario().get_context().get_type_object(self.building.get_type()).get_going_in_cap()
        purchase_value = forward_NOI / cap
        purchase = [cell(-1,'negative')*cell(purchase_value, 'Purchase')]
        purchase.extend([cell(0,'zero') for i in range(1, self.total_time + 1)])
        self.line_items['Purchase'] = purchase
        return purchase
    def calculate_PBTCF(self):
        NOI = self.calculate_NOI()
        reversion = self.calculate_reversion()
        capex = self.calculate_Capex()
        TI = self.calculate_TI()
        leasing = self.calculate_Leasing()
        CAM = self.calculate_CAM()
        purchase = self.calculate_purchase()
        PBTCF = []
        for i in range(len(NOI) - 1):
            PBTCF.append(NOI[i] + capex[i] + TI[i] + leasing[i] + CAM[i] + reversion[i] + purchase[i])
        PBTCF.append(cell(0,'zero'))
        self.line_items['PBTCF'] = PBTCF
        return PBTCF
    def calculate_cash_flows(self):
        PBTCF = self.calculate_PBTCF()
        cash_flows = []
        for i in range(len(PBTCF)-1):
            cash_flows.append(PBTCF[i].get_value())
        return cash_flows
    def calculate_IRR(self):
        cash_flows = self.calculate_cash_flows()
        IRR = np.irr(cash_flows)
        self.IRR = IRR
        return IRR
    def calculate_NPV_rate(self, discount_rate):
        cash_flows = self.calculate_cash_flows()
        NPV = 0
        for i in range(len(cash_flows)):
            NPV += cash_flows[i]/ ((1 + discount_rate)**(i))
        self.NPV_rate = (NPV, discount_rate)
        return (NPV,discount_rate)



class cell(object):
    def __init__(self, value, name):
        self.value = value
        self.name = name
    def get_value(self):
        return self.value
    def __add__(self, other):
        add_value = self.value + other.get_value()
        return cell(add_value, 'add output')
    def __sub__(self, other):
        sub_value = self.value - other.get_value()
        return cell(sub_value, 'subtract output')
    def __mul__(self, other):
        mul_value = self.value * other.get_value()
        return cell(mul_value, 'multiplication output')
    def __truediv__(self, other):
        div_value = self.value / other.get_value()
        return cell(div_value, 'division output')



def test_code(building_number):
    # test visualization based on Geltner Pro Forma
    # initialize trend numbers
    rent_trend = [cell(v, 'rent trend') for v in [.00328, 0, -.00644, 0, .01678, .01667, 0, .01672, 0, .01678]]
    other_trend =[cell(v, 'other income trend') for v in [.16926,.02318,-.08826, .11829, -.11201, .01914, .16831, -.14008, .17410, -.12676]]
    opex_trend = [cell(v, 'opex trend') for v in [.18886, .00683, -.07323, .09325, -.04571, .00824, .09342, -.07205, .09536, -.07338]]
    vacancy_trend = [cell(v, 'vacancy trend') for v in [-.32787, 0, .16944, -.16944, .16999, -.00111, -.16888, .16944, -.16944, .1699]]
    capex_margin = [cell(v, 'vacancy trend') for v in [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    TI_margin = [cell(v, 'vacancy trend') for v in [0, 0, .1466, 0, .1753, 0, .1903, .1869, 0, .1842, 0, .1811]]
    Leasing_margin = [cell(v, 'vacancy trend') for v in [0, 0, .044, 0, .0542, 0, .0545, .0541, 0, .0544, 0, 5.45]]
    CAM_margin = [cell(v, 'vacancy trend') for v in [0, 0, 0, 0, 0, .2936, 0, 0, 0, 0, 0, 0]]

    # initialize economy and context object that use trends as inputs
    economy_instance = economy()
    context_instance = context(None)
    context_instance.add_discount_rate(.20)
    # initialize building type data and add to context object
    for type_name in range(-2,6):
        context_instance.add_building_type(type_name, 10.16667, 1, 2.09389, 30000, .32787, .0861, .1, rent_trend, other_trend, opex_trend, vacancy_trend, capex_margin, TI_margin, Leasing_margin, CAM_margin)
    # initialize scenario
    scenario_instance = scenario('scenario test', economy_instance, None, None, context_instance, 11, json_data)

    building_list = scenario_instance.get_city().get_buildings()
    building_list[building_number].generate_pro_forma()
    building_list[building_number].get_pro_forma().fill_row('rent psf',context_instance.get_type_object(building_list[building_number].get_type()).get_rent_trend(), context_instance.get_type_object(building_list[building_number].get_type()).get_rent())
    building_list[building_number].get_pro_forma().fill_row('other_income psf', context_instance.get_type_object(building_list[building_number].get_type()).get_other_trend(),context_instance.get_type_object(building_list[building_number].get_type()).get_other_income())
    building_list[building_number].get_pro_forma().fill_row('vacancy rate',context_instance.get_type_object(building_list[building_number].get_type()).vacancy_trend, context_instance.get_type_object(building_list[building_number].get_type()).get_vacancy(), percent_change= False)
    building_list[building_number].get_pro_forma().fill_row('opex psf',context_instance.get_type_object(building_list[building_number].get_type()).get_opex_trend(), context_instance.get_type_object(building_list[building_number].get_type()).get_opex())
    building_list[building_number].get_pro_forma().fill_row('Capex margin', context_instance.get_type_object(building_list[building_number].get_type()).get_capex_margin(), None, filled_entry=True)
    building_list[building_number].get_pro_forma().fill_row('TI margin', context_instance.get_type_object(building_list[building_number].get_type()).get_TI_margin(), None, filled_entry=True)
    building_list[building_number].get_pro_forma().fill_row('Leasing margin', context_instance.get_type_object(building_list[building_number].get_type()).get_leasing_margin(), None,filled_entry=True)
    building_list[building_number].get_pro_forma().fill_row('CAM margin', context_instance.get_type_object(building_list[building_number].get_type()).get_CAM_margin(), None,filled_entry=True)
    building_list[building_number].get_pro_forma().calculate_IRR()
    building_list[building_number].get_pro_forma().calculate_NPV_rate(context_instance.get_discount_rate())

    building_list[building_number].get_pro_forma().visualize_table(building_number)



