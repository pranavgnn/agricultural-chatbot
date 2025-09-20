from langchain_core.tools import tool

schemes = {
    "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)": "Launched on February 24, 2019, this central sector scheme provides a financial benefit of Rs. 6,000 per year in three equal installments to eligible land-holding farmers. So far, Rs. 2.81 lakh crores have been transferred to over 11 crore beneficiaries.",

    "Pradhan Mantri Kisan MaanDhan Yojana (PM-KMY)": "A central sector contributory pension scheme launched on September 12, 2019, for small and marginal farmers aged 18 to 40. Members contribute between Rs. 55 and Rs. 200 per month and receive a monthly pension of Rs. 3,000 after turning 60. As of the document, 23.38 lakh farmers have enrolled.",

    "Pradhan Mantri Fasal Bima Yojana (PMFBY)": "A central sector scheme launched in 2016 that provides comprehensive crop insurance. Since its inception, 5549.40 lakh farmer applications have been insured, and Rs. 150,589.10 crore has been paid in claims.",

    "Modified Interest Subvention Scheme (MISS)": "A central sector scheme that provides concessional short-term agri-loans up to Rs. 3 lakh at a 7% interest rate. An additional 3% subvention is given for timely repayment, reducing the effective interest rate to 4%. As of January 5, 2024, 465.42 lakh new Kisan Credit Card (KCC) applications have been sanctioned.",

    "Agriculture Infrastructure Fund (AIF)": "A central sector scheme with a corpus of Rs. 1 lakh crore that provides medium-to-long-term debt financing for post-harvest management and community farming assets. It offers a 3% interest subvention and credit guarantee. As of December 31, 2023, Rs. 33,209 crore has been sanctioned for 44,912 projects.",

    "Formation & Promotion of 10,000 FPOs": "A central sector scheme launched in 2020 with a budgetary outlay of Rs. 6,865 crores to support the formation of Farmer Producer Organizations (FPOs). FPOs receive financial assistance of up to Rs. 18 lakh over three years. As of December 31, 2023, 7,774 FPOs have been registered.",

    "National Beekeeping and Honey Mission (NBHM)": "A central sector scheme launched in 2020 to promote scientific beekeeping. Achievements include sanctioning 4 world-class honey testing labs, registering 23 lakh bee colonies, and 88 Honey FPOs.",

    "Market Intervention Scheme and Price Support Scheme (MIS-PSS)": "A central sector scheme where the PSS procures pulses, oilseeds, and copra, while the MIS procures perishable agricultural and horticultural commodities to prevent distress sales by farmers.",

    "Namo Drone Didi": "A central sector scheme with an outlay of Rs. 1,261 crores for 2024-25 to 2025-26, providing drones to 15,000 Women Self Help Groups (SHGs) for rental services to farmers.",

    "Rashtriya Krishi Vikas Yojana (RKVY)": "A centrally sponsored scheme that focuses on creating pre and post-harvest infrastructure and provides financial support to states. Since 2019-20, 1,524 agri-startups have been selected.",

    "Soil Health Card (SHC)": "A centrally sponsored scheme that provides information on soil nutrient status. The government aims to collect 5 crore soil samples between 2023-24 and 2025-26 to create a nationwide soil fertility map.",

    "Rainfed Area Development (RAD)": "A centrally sponsored scheme implemented since 2014-15 that promotes Integrated Farming Systems. An amount of Rs. 1673.58 crores has been released, covering 7.13 lakh hectares.",

    "Per Drop More Crop (PDMC)": "A centrally sponsored scheme launched in 2015-16 that promotes micro-irrigation to increase water use efficiency. An area of 78 lakh hectares has been covered under this scheme.",

    "Micro Irrigation Fund (MIF)": "A centrally sponsored fund with an initial corpus of Rs. 5,000 crore to facilitate states in expanding micro-irrigation coverage. Loans worth Rs. 4,710.96 crore have been approved. The fund is to be doubled to Rs. 10,000 crore and is now merged with the PDMC scheme.",

    "Paramparagat Krishi Vikas Yojana (PKVY)": "A centrally sponsored scheme that aims to increase soil fertility."
}

@tool
def all_government_schemes():
    """
    Fetch a list of all government agricultural scheme names in India.
    Returns a comma-separated string of scheme names.
    """

    return ", ".join(schemes.keys())