import math 
import pandas as pd
import numpy as np
inf = math.inf
excel_file_path = 'MCAP31122023.xlsx'
pickel_file_path = 'Data_folder/AllStocks.pkl'
# all_stocks_df = pd.read_excel(excel_file_path)
allIndustriesList = []
companies_to_remove = ['ACL' , 'RAJMET' , 'GEPIL' , 'OSWALGREEN' , 'SOTL' , 'WABAG' , 'AVG'  ,'JINDWORLD' , 'ROHLTD' , 'FMNL' , 'ASTEC' , 'SHRENIK', 'AMNPLST' , 'SHIVALIK' , 'SERVOTECH' , 'BANARISUG' , '3PLAND' , 'AARTECH' , 'PLADAINFO' ,'STERTOOLS' , 'SATINDLTD' , 'AGRITECH' , 'INDOBORAX' , 'INOXGREEN'] 
def initStockInfo():
    all_stocks_df = pd.read_pickle(pickel_file_path)
    all_stocks_df['marketCap'] = all_stocks_df['marketCap']/10000000
    all_stocks_df['marketCap'] =all_stocks_df['marketCap'].round(2)
    all_stocks_df['new_col'] = np.where(all_stocks_df['industryKey'] != '' , all_stocks_df['industryKey'] , all_stocks_df['industry'])
    all_stocks_df = all_stocks_df.drop(columns=['industryKey' , 'industry'])
    all_stocks_df = all_stocks_df.rename(columns={'new_col' : 'industryKey'})
    all_stocks_df = all_stocks_df[all_stocks_df.eq(0).sum(axis=1) <= 4]
    all_stocks_df['industryKey'] = all_stocks_df['industryKey'].replace({'specialty-chemicals':'Specialty Chemicals' , 'auto-parts' : 'Auto Parts' , 'drug-manufacturers-specialty-generic':'Drug Manufacturers—Specialty & Generic' , 
                                        'specialty-industrial-machinery':'Specialty Industrial Machinery' ,'steel' : 'Steel' ,'information-technology-services' :'Information Technology Services' , 
                                        'credit-services' :'Credit Services' ,'packaged-foods' :'Packaged Foods' , 'real-estate-development' :'Real Estate—Development' , 'agricultural-inputs' :'Agricultural Inputs' ,
                                            'furnishings-fixtures-appliances' :'Furnishings, Fixtures & Appliances' ,'textile-manufacturing' :'Textile Manufacturing' , 'asset-management' : 'Asset Management',
                                            'chemicals' : 'Chemicals' , 'auto-manufacturers' : 'Auto Manufacturers' , 'auto-truck-dealerships' : 'Auto & Truck Dealerships' ,'farm-heavy-construction-machinery' : 'Farm & Heavy Construction Machinery',
                                            'internet-content-information' : 'Internet Content & Information' ,'engineering-construction' : 'Engineering & Construction' ,'food-distribution' : 'Food Distribution' ,
                                            'entertainment' : 'Entertainment' ,   'tools-accessories' : 'Tools & Accesories','capital-markets' : 'Capital Markets' , 'banks-regional' :'Banks—Regional' ,
                                            'real-estate-diversified' : 'Real Estate—Diversified', 'building-products-equipment' : 'Building Products & Equipment' , 'building-materials' : 'Building Materials' ,
                                            'packaging-containers' : 'Packaging & Containers' ,'electrical-equipment-parts' : 'Electrical Equipment & Parts' ,'apparel-manufacturing' : 'Apparel Manufacturing' , 'apparel-retail':'Apparel Retail' ,
                                            'paper-paper-products' : 'Paper & Paper Products' , 'drug-manufacturers-general' : 'Drug Manufacturers—General','farm-products':'Farm Products','software-application' : 'Software—Application' , 'software-infrastructure':'Software—Infrastructure',
                                            'other-industrial-metals-mining':'Other Industrial Metals & Mining','metal-fabrication':'Metal Fabrication' ,'confectioners':'Confectioners','integrated-freight-logistics':'Integrated Freight & Logistics',
                                            'lodging':'Lodging','luxury-goods':'Luxury Goods','education-training-services':'Education & Training Services','financial-conglomerates':'Financial Conglomerates','conglomerates':'Conglomerates',
                                            'business-equipment-supplies':'Business Equipment & Supplies',  'specialty-business-services':'Specialty Business Services','communication-equipment':'Communication Equipment','medical-instruments-supplies':'Medical Instruments & Supplies' , 'medical-care-facilities':'Medical Care Facilities',
                                            'publishing':'Publishing','household-personal-products':'Household & Personal Products','oil-gas-refining-marketing':'Oil & Gas Refining & Marketing','footwear-accessories':'Footwear & Accessories','aerospace-defense':'Aerospace & Defense','utilities-independent-power-producers':'Utilities—Independent Power Producers',
                                            'utilities-regulated-gas':'Utilities—Regulated Gas','utilities-renewable':'Utilities—Renewable','utilities-regulated-electric':'Utilities—Regulated Electric','mortgage-finance':'Mortgage Finance','telecom-services':'Telecom Services','biotechnology':'Biotechnology','Tools & Accesories':'Tools & Accessories',
                                            'beverages-wineries-distilleries':'Beverages—Wineries & Distilleries','beverages-brewers':'Beverages—Brewers'})
    all_stocks_df = all_stocks_df.drop(companies_to_remove)
    allIndustriesList = all_stocks_df['industryKey'].unique().tolist()
    return all_stocks_df
def perform_filtering(all_stocks_df,filter_lims,checked_filter_boxes,Industries_filter):
    condition = (
        (pd.to_numeric(all_stocks_df['volume'], errors='coerce') >= filter_lims['vol'][0]) &
        (pd.to_numeric(all_stocks_df['volume'], errors='coerce') <= filter_lims['vol'][1]) &
        (pd.to_numeric(all_stocks_df['marketCap'], errors='coerce') >= filter_lims['marketCap'][0]) &
        (pd.to_numeric(all_stocks_df['marketCap'], errors='coerce') <= filter_lims['marketCap'][1]) &
        (pd.to_numeric(all_stocks_df['currentPrice'], errors='coerce') >= filter_lims['price'][0]) &
        (pd.to_numeric(all_stocks_df['currentPrice'], errors='coerce') <= filter_lims['price'][1]) &
        (pd.to_numeric(all_stocks_df['trailingPE'], errors='coerce') >= filter_lims['pe_rat'][0]) &
        (pd.to_numeric(all_stocks_df['trailingPE'], errors='coerce') <= filter_lims['pe_rat'][1])
    )
    filtered_df = all_stocks_df[condition]
    
    filtered_df = filtered_df.reset_index().rename(columns={'index':'Symbol'})
    filtered_df = filtered_df.rename(columns={'marketCap':'Market Cap(in Cr)' , 'previousClose':'Prev. Close' , 'sector':'Sector' ,'open':'Open','dayLow':'Low','dayHigh' :'High' , 'currentPrice':'Price' , 'trailingPE' :'PE' ,'volume' :'Volume'})
    filtered_df['PE'] = pd.to_numeric(filtered_df['PE'], errors='coerce')
    filtered_df['PE'] = filtered_df['PE'].round(2)
    filtered_df = filtered_df.rename(columns={'industryKey' : 'Industry'})

    colums_order = ['Symbol' , 'Industry' , 'Sector' , 'Prev. Close' , 'Open' , 'Low' , 'High' , 'Price' ,'Volume' , 'PE' , 'Market Cap(in Cr)']
    filtered_df = filtered_df[colums_order]

    filtered_df_columns = filtered_df.columns

    checked_boxes_industry_list = []
    if checked_filter_boxes[11] == 'no' :
        for i in range(0,10) :
            if checked_filter_boxes[i] == 'yes' :
                checked_boxes_industry_list.append(Industries_filter[i])
        if checked_filter_boxes[10] == 'yes' :
            for x in allIndustriesList :
                if not(x in Industries_filter) :
                    checked_boxes_industry_list.append(x)
        filtered_df = filtered_df[filtered_df['Industry'].isin(checked_boxes_industry_list)]
    return (filtered_df,filtered_df_columns)