import lib_dcf_setup as dcf


class DCF_wrapper(object):

    def __init__(self, projection_length):
        self.rent = None
        self.other = None
        self.opex = None
        self.area = None
        self.vacancy = None
        self.going_in_cap = None
        self.exit_cap = None

        self.rent_trend = None
        self.other_trend = None
        self.opex_trend = None
        self.vacancy_trend = None
        self.capex_margin = None
        self.TI_margin = None
        self.leasing_margin = None
        self.CAM_margin = None


        self.projection_length = projection_length

    def set_building_features(self, use, submarket_list, class_list, floors, blg_sqft, year_built, TI, free_rent):
        self.use = use
        self.constant = 1
        self.submarket_list = submarket_list
        self.class_list = class_list
        self.floors = floors
        self.blg_sqft = blg_sqft
        self.year_built = year_built
        self.TI = TI
        self.free_rent = free_rent
        self.feature_list = [self.constant] + self.submarket_list + self.class_list + [self.floors, self.blg_sqft, self.year_built, self.TI, self.free_rent]


    def get_rent(self, bos_compstak):
        self.base_rent, self.rent_cagr = bos_compstak.calculate_index(self.feature_list, self.use)

    def get_opex(self, bos_ncreif):
        if self.base_rent == None:
            raise ValueError
        self.opex = self.base_rent * bos_ncreif.get_use_opex_dict[self.use]

    def get_capate(self, bos_rca):
        self.exit_caprate = bos_rca.use_caprate_dict[self.use]
        self.dev_yield =  self.exit_caprate
        # NEEDS TO BE MOVED TO CITY WRAPPER

    def evaluate_dcf(self, context_instance, building_instance):
        rent_trend = [dcf.cell(self.rent_trend, 'rent trend') for v in range(self.projection_length)]
        other_trend = [dcf.cell(self.other_trend, 'other income trend') for v in range(self.projection_length)]
        opex_trend = [dcf.cell(self.rent_trend, 'opex trend') for v in range(self.projection_length)]
        vacancy_trend = [dcf.cell(self.vacancy_trend, 'vacancy trend') for v in range(self.projection_length)]
        capex_margin = [dcf.cell(self.capex_margin, 'capex margin') for v in range(self.projection_length + 1)]
        TI_margin = [dcf.cell(self.TI_margin, 'TI margin') for v in range(self.projection_length + 1)]
        leasing_margin = [dcf.cell(self.leasing_margin, 'leasing margin') for v in range(self.projection_length + 1)]
        CAM_margin = [dcf.cell(self.CAM_margin, 'CAM margin') for v in range(self.projection_length + 1)]

        building_instance.generate_pro_forma()
        building_instance.get_pro_forma().fill_row('rent psf',rent_trend, self.rent)
        building_instance.get_pro_forma().fill_row('other_income psf', other_trend, self.other)
        building_instance.get_pro_forma().fill_row('vacancy rate', vacancy_trend, self.vacancy)
        building_instance.get_pro_forma().fill_row('opex psf', opex_trend, self.opex)
        building_instance.get_pro_forma().fill_row('Capex margin', capex_margin, None, filled_entry=True)
        building_instance.get_pro_forma().fill_row('TI margin', TI_margin, None, filled_entry=True)
        building_instance.get_pro_forma().fill_row('Leasing margin', leasing_margin, None, filled_entry=True)
        building_instance.get_pro_forma().fill_row('CAM margin', CAM_margin, None, filled_entry=True)
        building_instance.get_pro_forma().calculate_IRR()
        building_instance.get_pro_forma().calculate_NPV_rate(context_instance.get_discount_rate())
        building_instance.get_pro_forma().visualize_table(1)



    def main(self, context_instance, building_instance):
        building_type_obj = context_instance.get_type_object(building_instance.type)

        self.rent = building_type_obj.rent
        self.other = building_type_obj.other
        self.opex = building_type_obj.opex
        self.area = building_type_obj.area
        self.vacancy = building_type_obj.vacancy
        self.going_in_cap = building_type_obj.going_in_cap
        self.exit_cap = building_type_obj.exit_cap

        self.rent_trend = building_type_obj.rent_trend
        self.other_trend = building_type_obj.other_trend
        self.opex_trend = building_type_obj.opex_trend
        self.vacancy_trend = building_type_obj.vacancy_trend
        self.capex_margin = building_type_obj.capex_margin
        self.TI_margin = building_type_obj.TI_margin
        self.leasing_margin =building_type_obj.leasing_margin
        self.CAM_margin = building_type_obj.CAM_margin

        self.evaluate_dcf(context_instance, building_instance)
