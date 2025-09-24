from langchain_core.tools import tool
import json

agriculture_offices = {
    'Andaman & Nicobar': {
        'Main Agriculture Office': {
            'address': 'Director, Directorate of Economics & Statistiacs, Andeman & Nicobar Administration, Quarry Hill, Pronix Bay, PORT BLAIR – 744 101',
            'phone': '+91-3192-232476, +91-3192-234181',
            'fax': '',
            'email': '',
            'website': ''
        }
    },
    'Andhra Pradesh': {
        'Main Agriculture Office': {
            'address': 'Director Directorate of Economics & Statistics, Govt. of Andhra Pradesh, 410, Khairathabad, HYDERABAD-500 004',
            'phone': '+91-40-23317191',
            'fax': '+91-40-23307459',
            'email': 'dir_economics@ap.gov.in',
            'website': 'https://agriculture.ap.gov.in'
        }
    },
    'Arunachal Pradesh': {
        'Main Agriculture Office': {
            'address': 'Director (Agriculture), Govt. of Arunachal Pradesh, Naharlagun, “D” Sector, NEW ITANAGAR-791110',
            'phone': '+91-360-2243935',
            'fax': '+91-360-2244252',
            'email': '',
            'website': 'https://agri.arunachal.gov.in'
        }
    },
    'Assam': {
        'Main Agriculture Office': {
            'address': 'Director Directorate of Economics & Statistics, Govt. of Assam, GUWAHATI – 781 006',
            'phone': '+91-361-2265264',
            'fax': '',
            'email': 'dir-stat-assam@yahoo.co.in',
            'website': 'https://agri.assam.gov.in'
        }
    },
    'Bihar': {
        'Main Agriculture Office': {
            'address': 'Director Bureau of Statistics & Evaluation, Planning Department, Barrack No.17, Old Secretariat, Govt. of Bihar, PATNA – 800 015',
            'phone': '+91-612-221359',
            'fax': '+91-612-2221359',
            'email': '',
            'website': 'https://state.bihar.gov.in/agriculture'
        }
    },
    'Chandigarh': {
        'Main Agriculture Office': {
            'address': 'Joint Secretary(Finance) cum Director, Directorate of Economics & Statistics, Room No. 329-330, 3rd Floor, Deluxe Building, Sector – 9, Chandigarh Administration, U.T. CHANDIGARH',
            'phone': '',
            'fax': '',
            'email': '',
            'website': 'https://agri.chd.gov.in'
        }
    },
    'Chhattisgarh': {
        'Main Agriculture Office': {
            'address': 'Director Deputy Commissioner, Office of Land Records and Settlement, Gandhi Chowk, DKS Bhavan,Govt. of Chhattisgarh, RAIPUR',
            'phone': '+91-771-2234584',
            'fax': '',
            'email': '',
            'website': 'https://agriportal.cg.nic.in'
        }
    },
    'Dadra & Nagar Haveli': {
        'Main Agriculture Office': {
            'address': 'Assistant Secretary (Planning) Deptt. of Planning & Statistics, Sachivalaya, Dadra & Nagar Haveli Administration, SILVASSA – 396 230',
            'phone': '',
            'fax': '',
            'email': '',
            'website': ''
        }
    },
    'Daman & Diu': {
        'Main Agriculture Office': {
            'address': 'Deputy Director, Directorate of Agriculture, Daman & Diu Administration, DAMAN – 396 220',
            'phone': '+91-260-254770',
            'fax': '+91-260-254775',
            'email': '',
            'website': ''
        }
    },
    'Delhi': {
        'Main Agriculture Office': {
            'address': 'Joint Director (Agriculture), Development Department, Police Headquarter, 11th Floor, MSO Building, I.P. Estate,Delhi Administration, Govt. Of NCT of Delhi,New Delhi-110002.',
            'phone': '+91-120-23713399',
            'fax': '',
            'email': '',
            'website': 'https://devcom.delhi.gov.in'
        }
    },
    'Goa': {
        'Main Agriculture Office': {
            'address': 'Director (Agriculture), Agricultural Statistics Wing, Govt. of Goa, PANAJI – 403 001.',
            'phone': '+91-832-226445, +91-832-436851',
            'fax': '+91-832-422243',
            'email': '',
            'website': 'https://agri.goa.gov.in'
        }
    },
    'Gujarat': {
        'Main Agriculture Office': {
            'address': 'Director, Director (Agriculture), Krishi Bhavan, Ist Floor,Gujarat State, Sector No. 10-A, GANDHI NAGAR – 382 010',
            'phone': '+91-79-23256204',
            'fax': '+91-79-23256227, +91-79-23256159',
            'email': 'addl4-dir-agr@guj.gov.in',
            'website': 'https://agri.gujarat.gov.in'
        }
    },
    'Haryana': {
        'Main Agriculture Office': {
            'address': 'Director of Land Records(Haryana), Haryana State,SCO 1122-23, Sector-22B, CHANDIGARH (HARYANA)',
            'phone': '+91-172-705600',
            'fax': '',
            'email': '',
            'website': 'https://agriharyana.gov.in'
        }
    },
    'Himachal Pradesh': {
        'Main Agriculture Office': {
            'address': 'Director ( Land Records ), Govt. of Himachal Pradesh, SDA Complex, Block No. 28, Kasumpati, SHIMLA – 171 002',
            'phone': '+91-177-2623678, +91-177-225041',
            'fax': '+91-177-2626698, +91-177-223683, +91-177-223678',
            'email': 'chamelsingh2002@yahoo.com',
            'website': 'https://agriculture.hp.gov.in'
        }
    },
    'Jammu & Kashmir (Summer Season)': {
        'Main Agriculture Office': {
            'address': 'Shri G.A. Kureshi, Director, Directorate of Econ. & Stats, Deptt. Of Planning & Development,Govt. of Jammu & Kashmir, SDA Colony, Bunian,Old Secretariat, SRINAGAR – 190 001',
            'phone': '+91-191-2552145, +91-191-2538907',
            'fax': '',
            'email': '',
            'website': 'https://diragrikmr.jk.gov.in'
        }
    },
    'Jammu & Kashmir (Winter Season)': {
        'Main Agriculture Office': {
            'address': 'Director, Directorate of Econ. & Stats, Deptt. Of Planning & Development, Govt. of Jammu & Kashmir,Camp Office, Janipura, JAMMU – 180 001',
            'phone': '+91-191-2552145, +91-191-2538907',
            'fax': '',
            'email': '',
            'website': 'https://diragrikmr.jk.gov.in'
        }
    },
    'Jharkhand': {
        'Main Agriculture Office': {
            'address': 'Secretary (Agriculture), Building Dhuruva, Govt. of Jharkhand, RANCHI.',
            'phone': '+91-651-2233549',
            'fax': '+91-651-2490979',
            'email': '',
            'website': 'https://krishi.jharkhand.gov.in'
        }
    },
    'Karnataka': {
        'Main Agriculture Office': {
            'address': 'Director, Bureau of Economics & Statistics, Govt. of Karnataka, Multi-storeyed Building, Dr. B. R. Ambedkar Veedhi, BANGALORE – 560 001',
            'phone': '+91-80-22253758, +91-80-22353870',
            'fax': '+91-80-2281123',
            'email': '',
            'website': 'https://raitamitra.karnataka.gov.in'
        }
    },
    'Kerala': {
        'Agriculture Department': {
            'address': 'Vikas Bhavan, Thiruvananthapuram-695 033, Kerala, India.',
            'phone': '0471-2304480',
            'fax': '0471-2304230, 0471-2304687',
            'email': 'krishidirector@gmail.com',
            'website': 'www.keralaagriculture.gov.in'
        },
        'Animal Husbandry Department': {
            'address': 'Thiruvananthapuram, Kerala',
            'phone': '0471-2302381',
            'fax': '0471-2302283, 0471-2301190',
            'email': 'directorah.ker@nic.in',
            'website': 'www.ahd.kerala.gov.in'
        },
        'Dairy Development Department': {
            'address': 'Thiruvananthapuram, Kerala',
            'phone': '0471-2445749',
            'fax': '0471-2444987',
            'email': 'dairydirector05@yahoo.co.in, dairydirector05@gmail.com',
            'website': 'www.dairy.kerala.gov.in'
        },
        'Fisheries Department': {
            'address': 'Thiruvananthapuram, Kerala',
            'phone': '0471-2303160, 9496007020',
            'fax': '0471-2304355',
            'email': 'fisheriesdirector@gmail.com',
            'website': 'www.fisheries.kerala.gov.in'
        },
        'Coir Development Directorate': {
            'address': 'Many Bhavan, TC No. 9/1694, 9/1695, Sasthamangalam PO, Thiruvananthapuram-695 010, Kerala',
            'phone': '0471-2315287, 0471-2722046, 0471-2724286',
            'fax': '0471-2311370',
            'email': 'directorate@coir.kerala.gov.in',
            'website': 'www.coir.kerala.gov.in'
        },
        'Kuttanad Package Office': {
            'address': 'O/o Project Director, Kuttanad Package, Mangompu, Thekkekkara P. O., Alappuzha, Kerala',
            'phone': '0477-2704400',
            'fax': '0477-2704400',
            'email': 'pokuttanad@yahoo.com',
            'website': ''
        },
        'Kerala State Land Use Board': {
            'address': 'Thiruvananthapuram, Kerala',
            'phone': '0471-2307833, 0471-2307830, 0471-2302231',
            'fax': '0471-2307838',
            'email': 'landuseboard@yahoo.com',
            'website': 'kslub.kerala.gov.in'
        },
        'Ground Water Department': {
            'address': 'Thiruvananthapuram, Kerala',
            'phone': '0471-2434098',
            'fax': '0471-2431824',
            'email': 'gwdkerala@gmail.com',
            'website': 'www.groundwater.kerala.gov.in'
        },
        'Irrigation Department': {
            'address': 'Kozhikode, Kerala',
            'phone': '0495-2380805, 9447700672',
            'fax': '0495-2380672',
            'email': '',
            'website': 'www.irrigation.kerala.gov.in'
        },
        'Kerala State Co-operative Agricultural & Rural Development Bank Ltd.': {
            'address': 'Thiruvananthapuram, Kerala',
            'phone': '',
            'fax': '',
            'email': '',
            'website': 'www.keralacardbank.com'
        }
    },
    'Lakshadweep': {
        'Main Agriculture Office': {
            'address': 'Director (Agriculture), Union Territory of Lakshadweep, KAVARATI ISLANDS , PIN : 678 555',
            'phone': '+91-3592-70787, +91-3592-70018',
            'fax': '+91-3592-31877',
            'email': '',
            'website': ''
        }
    },
    'Madhya Pradesh': {
        'Main Agriculture Office': {
            'address': 'Commissioner (Statistics), Office of Land Records, Govt. of Madhya Pradesh,Moti Mahal, GWALLIOR – 474 007',
            'phone': '',
            'fax': '+91-751-324811, +91-751-324812',
            'email': '',
            'website': 'https://mpkrishi.mp.gov.in'
        }
    },
    'Maharashtra': {
        'Main Agriculture Office': {
            'address': 'Chief Statistician, Office of the Commissioner (Agri.), Govt. of Maharashtra Krishi Bhavan, Shivaji Nagar,PUNE – 411 001',
            'phone': '+91-20-26121041',
            'fax': '+91-20-26126173',
            'email': 'agristat@mah.nic.in',
            'website': 'https://krishi.maharashtra.gov.in'
        }
    },
    'Manipur': {
        'Main Agriculture Office': {
            'address': 'Director (Economics & Statistics), Govt. of Manipur, IMPHAL – 795 001',
            'phone': '+91-385-310202',
            'fax': '+91-385-310419',
            'email': '',
            'website': 'https://agrimanipur.gov.in'
        }
    },
    'Meghalaya': {
        'Main Agriculture Office': {
            'address': 'Director, Directorate of Economics & Statistics, Govt. of Meghalaya, Lower Luchumiere, SHILLONG -793 001',
            'phone': '+91-364-2227520, +91-94361-030316',
            'fax': '+91-364-2222464',
            'email': '',
            'website': 'https://megagriculture.gov.in'
        }
    },
    'Mizoram': {
        'Main Agriculture Office': {
            'address': 'Director, Department of Agriculture, Govt. of Mizoram, AIZWAL – 796 001',
            'phone': '+91-389-322437',
            'fax': '+91-389-322437',
            'email': '',
            'website': 'https://agriculture.mizoram.gov.in'
        }
    },
    'Nagaland': {
        'Main Agriculture Office': {
            'address': 'Director (Agriculture), Govt. of Nagaland,KOHIMA – 797 001',
            'phone': '+91-370-22243116',
            'fax': '+91-370-22243970',
            'email': 'skeitzar@hotmail.com',
            'website': 'https://agri.nagaland.gov.in'
        }
    },
    'Orissa': {
        'Main Agriculture Office': {
            'address': 'Director, Directorate of Economics & Statistics 4th Floor, HOD Building, Govt. of Orissa, BHUBANESHWAR – 751 001',
            'phone': '+91-674-2391295',
            'fax': '+91-674-401327',
            'email': '',
            'website': 'https://agri.odisha.gov.in'
        }
    },
    'Pondicherry': {
        'Main Agriculture Office': {
            'address': 'Director, Department of Economics & Statistics, Govt. of Pondicherry, 505, Kamraj Salai, Saran,PONDICHERRY – 601 001',
            'phone': '+91-413-248816, +91-413-248685',
            'fax': '+91-413-248816',
            'email': '',
            'website': 'https://agri.py.gov.in'
        }
    },
    'Punjab': {
        'Main Agriculture Office': {
            'address': 'Director, Land Records (Punjab), Kapurthala Road, JALANDHAR (Punjab)',
            'phone': '+91-181-254935',
            'fax': '+91-181-254935',
            'email': '',
            'website': 'https://agripb.gov.in'
        }
    },
    'Rajasthan': {
        'Main Agriculture Office': {
            'address': 'Director, Directorate of Economics & Statistics, Department of Planning, Govt. of Rajasthan,Yojana Bhavan, Tilak Marg, JAIPUR – 302 005',
            'phone': '+91-141-2227709',
            'fax': '+91-141-2222740',
            'email': '',
            'website': 'https://agriculture.rajasthan.gov.in'
        }
    },
    'Sikkim': {
        'Main Agriculture Office': {
            'address': 'Secretary, Department of Agriculture,Govt. of Sikkim, Krishi Bhavan, Tadong.GANGTOK – 737 102',
            'phone': '+91-3592-31877',
            'fax': '+91-3592-31877',
            'email': '',
            'website': 'https://sikkimagrisnet.org'
        }
    },
    'Tamil Nadu': {
        'Main Agriculture Office': {
            'address': 'Special Commissioner & Director, Directorate of Economics & Statistics,Govt. of Tamil Nadu, Block – II, Central Building,Teynampet, 259, Anna Salai, CHENNAI – 600 006',
            'phone': '+91-44-24341929',
            'fax': '+91-44-24322871',
            'email': '',
            'website': 'https://www.tnagrisnet.tn.gov.in'
        }
    },
    'Tripura': {
        'Main Agriculture Office': {
            'address': 'Director, State Land Use Board, Directorate of Agriculture, Dte. Of Hort. & Soil Conservation, Govt. of Tripura, AGARTALA-799 001',
            'phone': '+91-381-2323778',
            'fax': '+91-381-2323778',
            'email': 'secretary.agri.got@gmail.com',
            'website': 'https://agri.tripura.gov.in'
        }
    },
    'Uttar Pradesh': {
        'Main Agriculture Office': {
            'address': 'Secretary/Commissioner Revenue Council, Revenue Section-7, Govt. of Uttar Pradesh, Krishi Bhavan, Pandit Madan Mohan Malviya Marg, LUCKNOW -226 001',
            'phone': '+91-522-205210, +91-522-2320768',
            'fax': '+91-522-2206580',
            'email': '',
            'website': 'https://upagripardarshi.gov.in'
        }
    },
    'Uttarakhand': {
        'Main Agriculture Office': {
            'address': '(Principal Secretary/ Chief Revenue Commissioner/ Agriculture Census Commissioner), Govt. of Uttarakhand, 26, E.C. Road, Survey Chowk,DEHARADUN – 248006',
            'phone': '+91-135-2711909, +91-135-2772676',
            'fax': '+91-135-713134, +91-135-713135',
            'email': 'drajay_k_sharma@yahoo.co.in',
            'website': 'https://agriculture.uk.gov.in'
        }
    },
    'West Bengal': {
        'Main Agriculture Office': {
            'address': 'Addl. Director of Agri.(Evaluation), Department of Agri; Govt.of West Bengal, 17, S.P. Mukherjee Road,KOLKATA – 700 025',
            'phone': '+91-33-24761492, +91-33-24758763',
            'fax': '+91-33-24755674, +91-33-2250045',
            'email': 'agrievln@cal2.vsnl.net.in',
            'website': 'https://matirkatha.net'
        }
    }
}

@tool
def govt_offices(state = "Kerala") -> str:
    """
    Returns a dictionary of government agriculture offices for the specified state.

    Args:
        state (str): Name of the state to get the agriculture office details in Title Case. Default is "Kerala".

    Returns:
        JSON string with government agriculture office details
    """

    state_title = state.strip().title()

    if state_title not in agriculture_offices:
        return "Sorry, information not available."

    return json.dumps(agriculture_offices[state_title], indent=2)