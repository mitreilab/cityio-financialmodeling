import lib_bos_compstak_analysis as bos_compstak
import lib_bos_ncreif_analysis as bos_ncreif
import lib_bos_rca_analysis as bos_rca
import lib_dcf_setup as dcf
import script_dcf_wrapper as dcf_wrapper
import json
import urllib
import numpy as np


class simulation(object):

    def __init__(self):
        # east cambridge retail, class A, 5 year lease, 4 floors, 10,000 sqft, , built 2019, 20 TI, 1 month Free Rent
        # east cambridge office, class A, 5 year lease, 18 floors, 650,000 sqft, , built 2019, 20 TI, 1 month Free Rent
        self.feature_map = {
                            'Office': np.array([[1] +  [1] + [0]*10 + [0,0] + [4] + [17] + [600000] + [69] + [20] + [1]])
                            }
        self.compstak_obj = None
        self.ncreif_obj =  None
        self.rca_obj = None

        url_file = urllib.request.urlopen('http://cityio.media.mit.edu/api/table/citymatrix_volpe')
        url_file_text = url_file.read()
        json_data = json.loads(url_file_text)

        self.context_instance = dcf.context(None)
        self.economy_instance = dcf.economy(0.02)
        self.scenario_instance = dcf.scenario('independent basic types', self.economy_instance, None, None, self.context_instance, 8, json_data)
        self.city_instance = self.scenario_instance.get_city()

        self.setup_dcf_data(None)
        self.setup_market()
        self.add_buildings()
    def setup_dcf_data(self, city_scope_info):
        # each object contins use dict to regression or average
        self.compstak_obj = bos_compstak.bos_compstak()
        self.ncreif_obj = bos_ncreif.bos_ncreif()
        self.rca_obj = bos_rca.bos_rca()

    def setup_market(self):
        for use in ['Office']:
            name = use
            base_rent, rent_cagr = self.compstak_obj.calculate_index(self.feature_map[use], use)
            other_income = 0
            base_opex = self.ncreif_obj.use_opex_dict[use] * base_rent
            area = self.feature_map[use][0][16] + 50000
            base_vacancy = 0
            exit_cap = self.rca_obj.use_caprate_dict[use]
            going_in_cap = 0.07
            rent_trend = rent_cagr
            other_trend = 0
            opex_trend = self.economy_instance.get_inflation()
            vacancy_trend = 0
            capex_margin = 0
            TI_margin = 0
            leasing_margin = 0
            CAM_margin = 0
            self.context_instance.add_discount_rate(exit_cap+rent_trend)
            self.context_instance.add_building_type(name, base_rent, other_income, base_opex, area, base_vacancy, going_in_cap, exit_cap, rent_trend, other_trend, opex_trend, vacancy_trend, capex_margin, TI_margin,leasing_margin,CAM_margin)

    def run_DCF(self, building):
        DCF = dcf_wrapper.DCF_wrapper(self.scenario_instance.get_periods())
        DCF.main(self.context_instance, building)


    def add_buildings(self):
        #retail_building = dcf.building(0, 0, self.context_instance.get_type_object('Retail', 0, self.city_instance))
        office_building = dcf.building(0, 0, 'Office', 0, self.city_instance)
        self.city_instance.buildings.extend([office_building])

    def run_city_financials(self):
        for building in self.city_instance.get_buildings():
            self.run_DCF(building)

sim = simulation()
sim.run_city_financials()
