from langchain_core.tools import tool
import json

crop_data = {
    "Andhra Pradesh": {
        "Paddy": {
            "Kharif": {"sowing": "May-June", "harvesting": "Nov-Dec"},
            "Rabi": {"sowing": "Nov-Dec", "harvesting": "May-June"},
            "Summer": {"sowing": "March-April", "harvesting": "July-Aug."},
        },
        "Bajra": {"Kharif": {"sowing": "Jun(B)-Jul(M)", "harvesting": "Aug(B)-Oct(B)"}},
        "Arhar/Tur": {
            "Early Kharif": {"sowing": "June (B)-June (M)", "harvesting": "Nov(M)-Dec (E)"},
            "Kharif": {"sowing": "Jun (M)- July (M)", "harvesting": "Dec (M)-Jan.(M)"},
        },
        "Mungbean/Urdbean": {
            "Kharif": {"sowing": "Jun(M)-Jul(E)", "harvesting": "Sept(M)-Oct(M)"},
            "Rabi": {"sowing": "Oct(B)-Nov(B)", "harvesting": "Jan(B)-Feb(B)"},
            "Spring/Summer": {"sowing": "Jan(B)-Feb(B)", "harvesting": "Mar(B)-April(M)"},
        },
        "Soybean": {"Kharif": {"sowing": "June(M)-July(M)", "harvesting": "Sept(E)-Oct(B)"}},
        "Niger": {
            "Kharif": {"sowing": "June(B)-July(E)", "harvesting": "Oct(B)-Nov(M)"},
            "Late Kharif": {"sowing": "Aug(B)-Sept(B)", "harvesting": "Nov(B)-Dec(B)"},
        },
        "Groundnut": {
            "Kharif": {"sowing": "Jun(B)-july(E)", "harvesting": "Sep(M)-Nov(M)"},
            "Rabi": {"sowing": "Nov(M)-Jan(E)", "harvesting": "Feb(E)-May(B)"},
        },
        "Linseed": {"Rabi": {"sowing": "Oct(B)-Oct(E)", "harvesting": "Feb(E)-Mar(E)"}},
        "Sesame": {
            "Kharif": {"sowing": "June(B)-July(E)", "harvesting": "Oct(M)-Nov(M)"},
            "Pre Rabi": {"sowing": "Aug(B)-Sept(M)", "harvesting": "Dec(E)-Jan(M)"},
            "Summer": {"sowing": "Jan(M)-Feb(E)", "harvesting": "Apr(M)-May(E)"},
        },
        "Sunflower": {
            "Kharif": {"sowing": "Jun(B)-Aug(E)", "harvesting": "Sep - Nov"},
            "Rabi": {"sowing": "Oct", "harvesting": "Jan"},
        },
        "Castor": {"Kharif": {"sowing": "Jun(B)-Jul(E)", "harvesting": "Oct-Dec"}},
        "Safflower": {"Rabi": {"sowing": "October", "harvesting": "Feb"}},
        "Cotton": {"Kharif": {"sowing": "Jun(E)-Jul(E)", "harvesting": "Dec(E)-Mar(M)"}},
        "Maize": {
            "Kharif": {"sowing": "Jun(M)-Jul(M)", "harvesting": "Sep(M)-Oct(E)"},
            "Rabi": {"sowing": "Oct(E)-Jan(M)", "harvesting": "Feb(E)-May(B)"},
        },
        "Rapeseed-Mustard": {"Mustard/ Banarasi rai": {"sowing": "Nov(L)-Dec(E)", "harvesting": "Feb-March"}},
        "Sugarcane": {"Kharif": {"sowing": "Dec(E)-Jun(M)", "harvesting": "Dec(E)-May(M)"}},
    },
    "Assam": {
        "Paddy": {
            "Kharif": {"sowing": "Feb-March", "harvesting": "June-July"},
            "Rabi": {"sowing": "June-July", "harvesting": "Nov-Dec"},
            "Summer": {"sowing": "Nov-Dec", "harvesting": "May-June"},
        },
        "Wheat": {"Rabi": {"sowing": "Nov(B)-Dec(M)", "harvesting": "Mar(B)-Apr(E)"}},
        "Mungbean/Urdbean": {
            "Kharif": {"sowing": "July(B)-Aug(E)", "harvesting": "Sep(M)-Oct(E)"},
            "Rabi": {"sowing": "Aug(B)-Sep(M)", "harvesting": "Nov(B)-Dec(M)"},
            "Spring/Summer": {"sowing": "Feb(E)-Mar(M)", "harvesting": "May(B)-May(M)"},
        },
        "Chickpea": {"Rabi": {"sowing": "Oct(M)-Nov(M)", "harvesting": "March(B)-March(E)"}},
        "Groundnut": {"Rabi": {"sowing": "July(B)-Aug(E)", "harvesting": "Nov(B)-Dec(E)"}},
        "Linseed": {"Rabi": {"sowing": "Oct(B)-Nov(B)", "harvesting": "Mar(B)-Apr(E)"}},
        "Rapeseed-Mustard": {"Toria": {"sowing": "Nov(L)-Dec(E)", "harvesting": "Feb-March"}},
        "Sugarcane": {"Kharif": {"sowing": "Mar(B)-Apr(E)", "harvesting": "Dec(B)-Jan(E)"}},
    },
    "Bihar": {
        "Paddy": {
            "Kharif": {"sowing": "Jun-Sept.", "harvesting": ""},
            "Rabi": {"sowing": "Oct-Nov", "harvesting": "April-May"},
            "Summer": {"sowing": "Feb.-March", "harvesting": "July-Aug."},
        },
        "Wheat": {"Rabi": {"sowing": "Nov(M)-Dec(E)", "harvesting": "Mar(M)-Apr(E)"}},
        "Arhar/Tur": {"Kharif": {"sowing": "July (B)- July (E)", "harvesting": "March (M)- April (E)"}},
        "Mungbean/Urdbean": {
            "Kharif": {"sowing": "July(B)-Aug(E)", "harvesting": "Sep(M)-Oct(E)"},
            "Spring/Summer": {"sowing": "Feb(E)-April(B)", "harvesting": "May(B)-June(M)"},
        },
        "Horsegram": {"Kharif": {"sowing": "Aug(M)-Aug(E)", "harvesting": "Oct(E)-Nov(B)"}},
        "Chickpea": {"Rabi": {"sowing": "Oct(M)-Nov(M)", "harvesting": "March(B)-March(E)"}},
        "Pulses/Lentil": {
            "Kharif": {"sowing": "Jun(M)-Jul(B)", "harvesting": "Nov(B)-Dec(E)"},
            "Rabi": {"sowing": "Oct(M)-Nov(M)", "harvesting": "Mar(M)-Apr(M)"},
        },
        "Pea": {"Rabi": {"sowing": "Oct(M)-Nov(M)", "harvesting": "Mar(M)-April(M)"}},
        "Linseed": {"Rabi": {"sowing": "Oct(B)-Nov(B)", "harvesting": "Mar(B)-Apr(E)"}},
        "Rapeseed-Mustard": {
            "Mustard": {"sowing": "Oct(L)-Nov(L)", "harvesting": "Feb-March"},
            "Toria": {"sowing": "Sep(L)-Oct(E)", "harvesting": "Jan-Feb"},
            "Yellow Sarson": {"sowing": "Oct(E)", "harvesting": "Feb-March"},
        },
        "Maize": {
            "Kharif": {"sowing": "Jun(M)-Jul(B)", "harvesting": "Nov(B)-Dec(E)"},
            "Rabi": {"sowing": "Oct(M)-Nov(M)", "harvesting": "Feb(B)-Mar(B)"},
        },
    },
    "Chattisgarh": {
        "Mungbean/Urdbean": {"Kharif": {"sowing": "Jun-Jul", "harvesting": "Sep-Sep"}},
        "Chickpea": {"Rabi": {"sowing": "Oct(B)-Oct(E)", "harvesting": "Feb(E)-March(E)"}},
        "Pulses/Lentil": {
            "Rabi": {"sowing": "Oct(M)-Nov(M)", "harvesting": "Mar(M)-Apr(M)"},
        },
        "Pea": {"Rabi": {"sowing": "Oct(M)-Nov(M)", "harvesting": "Mar(M)-Apr(M)"}},
        "Soybean": {"Kharif": {"sowing": "June(M)-July(M)", "harvesting": "Sept(E)-October(B)"}},
        "Linseed": {"Rabi": {"sowing": "Oct(B)-Nov(M)", "harvesting": "Mar(B)-Mar(E)"}},
        "Rapeseed-Mustard": {
            "Mustard": {"sowing": "Oct(E)-Nov(E)", "harvesting": "March"},
            "Toria": {"sowing": "Sep(L)", "harvesting": "Dec-Jan"},
        },
    },
    "Delhi": {
        "Rapeseed-Mustard": {
            "Mustard": {"sowing": "Oct(L)-Nov(E)", "harvesting": "Feb-March"},
            "Toria": {"sowing": "Sep(L)", "harvesting": "Jan"},
            "Taramira": {"sowing": "Nov(E)", "harvesting": "March"},
        },
    },
    "Goa": {
        "Pulses/Lentil": {
            "Kharif": {"sowing": "Aug(B)-Sep(E)", "harvesting": "Nov(B)-Dec(E)"},
        },
    },
    "Gujarat": {
        "Paddy": {
            "Kharif": {"sowing": "June-July", "harvesting": "Oct-Nov"},
        },
        "Bajra": {
            "Kharif": {"sowing": "Jun(B)-Jul(E)", "harvesting": "Sep(B)-Nov(E)"},
            "Summer": {"sowing": "Feb(B)-Feb(E)", "harvesting": "May(B)-May(E)"},
        },
        "Arhar/Tur": {"Kharif": {"sowing": "June (B)-June (M)", "harvesting": "Nov (M)-Dec (M)"}},
        "Mungbean/Urdbean": {"Kharif": {"sowing": "July(B)-Aug(E)", "harvesting": "Sep(M)-Oct(E)"}},
        "Chickpea": {"Rabi": {"sowing": "Oct(B)-Nov(B)", "harvesting": "Feb(M)-April(M)"}},
        "Groundnut": {
            "Kharif": {"sowing": "Jun(B)-July(E)", "harvesting": "Sep(B)-Nov(E)"},
            "Summer": {"sowing": "Jan(B)-Feb(E)", "harvesting": "Apr(B)May(E)"},
        },
        "Gram": {"Rabi": {"sowing": "Oct(B)-Nov(E)", "harvesting": "Feb(B)-Mar(E)"}},
        "Pulses/Lentil": {
            "Rabi": {"sowing": "Oct(M)-Nov(M)", "harvesting": "Mar(M)-Apr(M)"},
        },
        "Pea": {"Rabi": {"sowing": "Oct(M)-Nov(M)", "harvesting": "Mar(M)-Apr(M)"}},
        "Castor": {"Kharif": {"sowing": "Jul-Aug", "harvesting": "Jan-Feb"}},
        "Cotton": {"Kharif": {"sowing": "May(B)-May(E)", "harvesting": "Oct(B)-Apr(E)"}},
        "Maize": {"Kharif": {"sowing": "Jun(B)-Jul(E)", "harvesting": "Sep(B)-Nov(E)"}},
        "Rapeseed-Mustard": {
            "Mustard": {"sowing": "Oct(L)", "harvesting": "Feb-March"},
            "Yellow Sarson": {"sowing": "Oct(L)", "harvesting": "Feb"},
        },
    },
    "Haryana": {
        "Paddy": {"Kharif": {"sowing": "June-July", "harvesting": "Sept-Oct."}},
        "Bajra": {"Kharif": {"sowing": "Jun(M)-Jul(B)", "harvesting": "Oct(M)-Nov(M)"}},
        "Wheat": {"Rabi": {"sowing": "Oct(E)-Dec(B)", "harvesting": "Apr(M)-Apr(E)"}},
        "Arhar/Tur": {"Early Kharif": {"sowing": "June (B)-June (M)", "harvesting": "Nov (M)- Dec (M)"}},
        "Gram": {"Rabi": {"sowing": "Oct(B)-Oct(M)", "harvesting": "Mar(M)-Mar(E)"}},
        "Pulses/Lentil": {
            "Rabi": {"sowing": "Oct(M)-Nov(M)", "harvesting": "Mar(M)-Apr(M)"},
        },
        "Pea": {"Rabi": {"sowing": "Oct(M)-Nov(M)", "harvesting": "Mar(M)-Apr(M)"}},
        "Rapeseed-Mustard": {
            "Mustard": {"sowing": "Within Oct", "harvesting": "Feb-March"},
            "Toria": {"sowing": "Sep(L)", "harvesting": "Dec-Jan"},
            "Taramira": {"sowing": "Nov(E)", "harvesting": "March"},
        },
        "Cotton": {"Kharif": {"sowing": "Apr(B)-Apr(M)", "harvesting": "Oct(M)-Nov(M)"}},
        "Maize": {"Kharif": {"sowing": "Jul(M)-Aug(B)", "harvesting": "Oct(M)-OctE)"}},
        "Sugarcane": {"Kharif": {"sowing": "Feb(M)-Mar(M)", "harvesting": "Dec(M)-March(E)"}},
    },
    "Himachal Pradesh": {
        "Paddy": {"Kharif": {"sowing": "May-June", "harvesting": "October"}},
        "Wheat": {"Rabi": {"sowing": "Oct(B)-Nov(E)", "harvesting": "Apr(M)-Jun(E)"}},
        "Rapeseed-Mustard": {
            "Mustard": {"sowing": "Oct(L)-Nov(L)", "harvesting": "March-April"},
            "Brown Sarson": {"sowing": "Within Oct", "harvesting": "April"},
            "Gobhi Sarson": {"sowing": "Oct(L)-Nov(L)", "harvesting": "April"},
        },
        "Maize": {"Kharif": {"sowing": "May(M)-Jun(E)", "harvesting": "Sep(M)-Oct(M)"}},
    },
    "J&K": {
        "Paddy": {"Kharif": {"sowing": "April-May", "harvesting": "Sept-Oct."}},
        "Wheat": {"Rabi": {"sowing": "Oct(B)-Dec(E)", "harvesting": "May(B)-May(E)"}},
        "Rapeseed-Mustard": {
            "Mustard": {"sowing": "Oct(L)-Nov(E)", "harvesting": "March-April"},
            "Brown sarson": {"sowing": "Within Oct", "harvesting": "April-May"},
        },
    },
    "Jharkhand": {
        "Mungbean/Urdbean": {"Kharif": {"sowing": "July(B)-Aug(E)", "harvesting": "Sep(M)-Oct(E)"}},
        "Chickpea": {"Rabi": {"sowing": "Oct(M)-Nov(M)", "harvesting": "Mar(M)-Apr(M)"}},
        "Pulses/Lentil": {
            "Rabi": {"sowing": "Oct(M)-Nov(M)", "harvesting": "Mar(M)-Apr(M)"},
        },
        "Pea": {"Rabi": {"sowing": "Oct(M)-Nov(M)", "harvesting": "Mar(M)-Apr(M)"}},
        "Linseed": {"Rabi": {"sowing": "Oct(B)-Nov(B)", "harvesting": "Mar(B)-Apr(E)"}},
        "Rapeseed-Mustard": {
            "Mustard": {"sowing": "Oct(L)", "harvesting": "March"},
            "Toria": {"sowing": "Oct(E)", "harvesting": "Feb-March"},
            "Yellow Sarson": {"sowing": "Oct(E)", "harvesting": "Feb-March"},
        },
    },
    "Karnataka": {
        "Paddy": {
            "Kharif": {"sowing": "May-June", "harvesting": "Sept-Oct."},
            "Rabi": {"sowing": "Sept-Oct.", "harvesting": "Jan.-Feb"},
            "Summer": {"sowing": "Jan.-Feb.", "harvesting": "May-June"},
        },
        "Bajra": {
            "Kharif": {"sowing": "Jul(B)-Sep(E)", "harvesting": "Oct(B)-Nov(E)"},
            "Summer": {"sowing": "Jan(B)-Feb(E)", "harvesting": "Apr(B)-May(E)"},
        },
        "Wheat": {"Rabi": {"sowing": "Oct(B)-Dec(E)", "harvesting": "Jan(B)-Feb(E)"}},
        "Arhar/Tur": {
            "Early Kharif": {"sowing": "June(B)-June(M)", "harvesting": "Nov(B)-Dec(M)"},
            "Kharif": {"sowing": "Jun(M)-July(M)", "harvesting": "Dec(M)-Jan(M)"},
        },
        "Mungbean/Urdbean": {
            "Kharif": {"sowing": "Jun(M)-Jul(E)", "harvesting": "Sept(M)-Oct(M)"},
            "Spring/Summer": {"sowing": "Jan(B)-Feb(B)", "harvesting": "Mar(B)-April(M)"},
        },
        "Gram": {"Rabi": {"sowing": "Oct(B)-Nov(E)", "harvesting": "Jan(B)-Mar(E)"}},
        "Soybean": {"Kharif": {"sowing": "June(M)-July(B)", "harvesting": "Sept(E)-Oct(B)"}},
        "Niger": {
            "Kharif": {"sowing": "June(B)-July(E)", "harvesting": "Oct(B)-Nov(M)"},
            "Late Kharif": {"sowing": "Aug(B)-Sept(B)", "harvesting": "Nov(B)-Dec(B)"},
        },
        "Groundnut": {
            "Kharif": {"sowing": "Jun(B)-jul(E)", "harvesting": "Sep(B)-Oct(E)"},
            "Rabi": {"sowing": "Nov(M)-Jan(E)", "harvesting": "Feb(E)-May(B)"},
            "Summer": {"sowing": "Dec(B)-Jan(E)", "harvesting": "Mar(B)-Apr(E)"},
        },
        "Linseed": {"Rabi": {"sowing": "Oct(B)-Oct(E)", "harvesting": "Feb(B)-Mar(M)"}},
        "Sesame": {"Kharif": {"sowing": "June(B)-July(E)", "harvesting": "Oct(M)-Nov(M)"}},
        "Sunflower": {
            "Kharif": {"sowing": "Jun(B)-Aug(E)", "harvesting": "Sep-Nov"},
            "Rabi": {"sowing": "Oct", "harvesting": "Jan"},
            "Summer/Spring": {"sowing": "Dec-Jan", "harvesting": "Mar-Apr"},
        },
        "Castor": {"Kharif": {"sowing": "Jul-Aug", "harvesting": "Nov-Dec"}},
        "Safflower": {"Rabi": {"sowing": "October", "harvesting": "Feb"}},
        "Rapeseed-Mustard": {"Mustard": {"sowing": "Within Oct", "harvesting": "Feb"}},
        "Maize": {
            "Kharif": {"sowing": "May(B)-Jun(E)", "harvesting": "Sep(B)-Oct(E)"},
            "Rabi": {"sowing": "Sep(B)-Oct(E)", "harvesting": "Jan(B)-Mar(E)"},
        },
        "Sugarcane": {"Kharif": {"sowing": "Dec(B)-Mar(E)*", "harvesting": "Aug(B)-May(E)"}},
    },
    "Kerala": {
        "Paddy": {
            "Kharif": {"sowing": "April-May", "harvesting": "Sept-Oct."},
            "Rabi": {"sowing": "Sept-Oct.", "harvesting": "Dec-Jan."},
            "Summer": {"sowing": "Dec-Jan.", "harvesting": "March-April"},
        },
        "Mungbean/Urdbean": {
            "Kharif": {"sowing": "Jun(M)-Jul(E)", "harvesting": "Sept(M)-Oct(M)"},
            "Spring/Summer": {"sowing": "Jan(B)-Feb(B)", "harvesting": "Mar(B)-April(M)"},
        },
        "Sesame": {
            "Kharif": {"sowing": "June(B)-July(E)", "harvesting": "Oct(M)-Nov(M)"},
            "Summer": {"sowing": "Jan(M)-Feb(E)", "harvesting": "Apr(M)-May(E)"},
        },
        "Cotton": {"Kharif": {"sowing": "Jun(B)-Oct(E)", "harvesting": "Dec(B)-Mar(E)"}},
        "Jute": {"Kharif": {"sowing": "Jun(B)-Oct(E)", "harvesting": "Oct(B)-Jan(E)"}},
    },
    "Madhya Pradesh": {
        "Paddy": {"Kharif": {"sowing": "June-July", "harvesting": "Oct-Nov"}},
        "Wheat": {"Rabi": {"sowing": "Oct(M)-Dec(E)", "harvesting": "Feb(M)Apr(E)"}},
        "Arhar/Tur": {"Kharif": {"sowing": "Jun (M)-July (M)", "harvesting": "Jan (M)- Feb. (M)"}},
        "Mungbean/Urdbean": {
            "Kharif": {"sowing": "Jun(M)-Jul(E)", "harvesting": "Sept(M)-Oct(M)"}
        },
        "Horsegram": {"Kharif": {"sowing": "August (E)", "harvesting": "Oct(E)"}},
        "Chickpea": {"Rabi": {"sowing": "Oct(B)-Oct(E)", "harvesting": "Feb(M)-April(E)"}},
        "Soybean": {"Kharif": {"sowing": "June(M)-July(M)", "harvesting": "Sept(E)-October(B)"}},
        "Niger": {
            "Kharif": {"sowing": "June(B)-July(E)", "harvesting": "Oct(B)-Nov(M)"},
            "Late Kharif": {"sowing": "Aug(B)-Sept(B)", "harvesting": "Nov(B)-Dec(B)"},
        },
        "Groundnut": {"Kharif": {"sowing": "Jun(M)-july(E)", "harvesting": "Sep(M)-Oct(E)"}},
        "Linseed": {"Rabi": {"sowing": "Oct(B)-Nov(M)", "harvesting": "Mar(B)-Mar(E)"}},
        "Sesame": {
            "Kharif": {"sowing": "June(B)-July(E)", "harvesting": "Oct(M)-Nov(M)"},
            "Pre Rabi": {"sowing": "Aug(B)-Sept(M)", "harvesting": "Dec(E)-Jan(M)"},
        },
        "Rapeseed-Mustard": {
            "Mustard": {"sowing": "Within Oct", "harvesting": "Feb-March"},
            "Toria": {"sowing": "Sep(L)", "harvesting": "Dec-Jan"},
        },
        "Maize": {"Kharif": {"sowing": "Jun(M)-Jul(E)", "harvesting": "Sep(M)-Oct(E)"}},
        "Sugarcane": {"Kharif": {"sowing": "Oct(B)-Apr(E)", "harvesting": "Oct(E)-Mar(E)"}},
    },
    "Maharashtra": {
        "Paddy": {"Kharif": {"sowing": "June-July", "harvesting": "Oct-Nov"}},
        "Wheat": {"Rabi": {"sowing": "Oct(B)-Dec(E)", "harvesting": "Feb(B)-Mar(E)"}},
        "Arhar/Tur": {
            "Early Kharif": {"sowing": "June (B)-June (M)", "harvesting": "Dec(M)-Jan (M)"},
            "Kharif": {"sowing": "Jun (M)-July (M)", "harvesting": "Dec(M)-Feb(M)"},
        },
        "Mungbean/Urdbean": {
            "Kharif": {"sowing": "Jun(M)-Jul(E)", "harvesting": "Sept(M)-Oct(M)"},
        },
        "Horsegram": {"Kharif": {"sowing": "Jul(M)", "harvesting": "Oct(M)"}},
        "Chickpea": {"Rabi": {"sowing": "Sept(E)-Oct(E)", "harvesting": "Feb(M)-March(E)"}},
        "Soybean": {"Kharif": {"sowing": "June(M)-July(M)", "harvesting": "Sept(E)-Oct(B)"}},
        "Niger": {
            "Kharif": {"sowing": "June(B)-July(E)", "harvesting": "Oct(B)-Nov(M)"},
            "Late Kharif": {"sowing": "Aug(B)-Sept(B)", "harvesting": "Nov(B)-Dec(B)"},
        },
        "Groundnut": {
            "Kharif": {"sowing": "Jun(E)-Jul(E)", "harvesting": "Oct(B)-Nov(B)"},
            "Summer": {"sowing": "Jan(B)-Feb(E)", "harvesting": "Apr(B)May(E)"},
        },
        "Linseed": {"Rabi": {"sowing": "Oct(B)-Oct(E)", "harvesting": "Mar(B)-Mar(E)"}},
        "Sesame": {
            "Kharif": {"sowing": "June(B)-July(E)", "harvesting": "Oct(M)-Nov(M)"},
            "Pre Rabi": {"sowing": "Aug(B)-Sept(M)", "harvesting": "Dec(E)-Jan(M)"},
            "Summer": {"sowing": "Jan(M)-Feb(E)", "harvesting": "Apr(M)-May(E)"},
        },
        "Sunflower": {
            "Kharif": {"sowing": "Jul(B)-Aug(E)", "harvesting": "Oct-Nov"},
            "Rabi": {"sowing": "Oct", "harvesting": "Jan"},
        },
        "Safflower": {"Rabi": {"sowing": "Sep(M)-Oct(M)", "harvesting": "Feb-Mar"}},
        "Rapeseed-Mustard": {"Mustard": {"sowing": "Oct(L)-Nov(E)", "harvesting": "Feb-March"}},
        "Sugarcane": {"Kharif": {"sowing": "Jul(B)-Aug(E)", "harvesting": "Oct(B)-Nov(E)"}},
    },
    "Manipur": {
        "Rapeseed-Mustard": {
            "Mustard": {"sowing": "Within Nov", "harvesting": "March"},
            "Toria": {"sowing": "Oct(E)", "harvesting": "Feb-March"},
        },
        "Jute": {"Kharif": {"sowing": "Feb-Mar", "harvesting": "Aug-Sep"}},
    },
    "Nagaland": {
        "Linseed": {"Rabi": {"sowing": "Oct(B)-Nov(B)", "harvesting": "Mar(B)-Apr(E)"}},
    },
    "Orissa": {
        "Paddy": {"Kharif": {"sowing": "June-July", "harvesting": "Oct-Nov"}},
        "Wheat": {"Rabi": {"sowing": "Oct(M)-Dec(E)", "harvesting": "Feb(M)Apr(E)"}},
        "Arhar/Tur": {"Kharif": {"sowing": "June (B)-June (M)", "harvesting": "Nov (M)- Dec (M)"}},
        "Mungbean/Urdbean": {
            "Kharif": {"sowing": "Jun(M)-Jul(E)", "harvesting": "Sept(M)-Oct(M)"},
            "Rabi": {"sowing": "Oct(B)-Nov(B)", "harvesting": "Jan(B)-Feb(B)"},
            "Spring/Summer": {"sowing": "Jan(B)-Feb(B)", "harvesting": "Mar(B)-April(M)"},
        },
        "Groundnut": {"Kharif": {"sowing": "Jun(B)-july(E)", "harvesting": "Sep(M)-Nov(M)"}},
        "Linseed": {"Rabi": {"sowing": "Oct(B)-Oct(E)", "harvesting": "Mar(B)-Mar(E)"}},
        "Sesame": {
            "Kharif": {"sowing": "June(B)-July(E)", "harvesting": "Oct(M)-Nov(M)"},
            "Rabi": {"sowing": "Oct(B)-Nov(M)", "harvesting": "Feb(M)-Mar(E)"},
            "Summer": {"sowing": "Jan(M)-Feb(E)", "harvesting": "May(M)-June(M)"},
        },
        "Rapeseed-Mustard": {
            "Mustard": {"sowing": "Oct(L)-Nov(L)", "harvesting": "Feb-March"},
            "Toria": {"sowing": "Oct(E)", "harvesting": "Feb"},
            "Yellow Sarson": {"sowing": "Oct(E)", "harvesting": "Feb-March"},
        },
        "Sugarcane": {"Kharif": {"sowing": "Feb-May", "harvesting": "Nov-Feb"}},
        "Jute": {"Kharif": {"sowing": "May-Jun", "harvesting": "Aug-Sep"}},
    },
    "Punjab": {
        "Paddy": {"Kharif": {"sowing": "May(B)-June(E)", "harvesting": "Oct(B)-Nov(E)"}},
        "Wheat": {"Rabi": {"sowing": "Oct(M)-Dec(E)", "harvesting": "March(E)-April(E)"}},
        "Mungbean/Urdbean": {
            "Kharif": {"sowing": "July(B)-Aug(E)", "harvesting": "Sep(M)-Oct(E)"},
            "Spring/Summer": {"sowing": "Feb(E)-Mar(M)", "harvesting": "May(B)-May(M)"},
        },
        "Chickpea": {"Rabi": {"sowing": "Oct(M)-Nov(E)", "harvesting": "March(M)-April(E)"}},
        "Groundnut": {"Summer/Spring": {"sowing": "Feb", "harvesting": "Apr-May"}},
        "Rapeseed-Mustard": {
            "Mustard": {"sowing": "Oct(L)-Nov(L)", "harvesting": "March-April"},
            "Toria": {"sowing": "Sep(L)", "harvesting": "Dec-Jan"},
        },
        "Sugarcane": {"Kharif": {"sowing": "Feb(B)-Mar(E)", "harvesting": "Nov(B)-Feb(E)"}},
    },
    "Rajasthan": {
        "Paddy": {"Kharif": {"sowing": "June-July", "harvesting": "Oct-Nov"}},
        "Bajra": {"Kharif": {"sowing": "June-July", "harvesting": "Sept-Oct."}},
        "Arhar/Tur": {
            "Early Kharif": {"sowing": "June (B)-June (M)", "harvesting": "Nov (M)-Dec (M)"},
            "Kharif": {"sowing": "Jun (M)-July (M)", "harvesting": "Jan.(M)-Feb. (M)"},
        },
        "Mungbean/Urdbean": {
            "Kharif": {"sowing": "July(B)-Aug(E)", "harvesting": "Sep(M)-Oct(E)"}
        },
        "Chickpea": {"Rabi": {"sowing": "Oct(E)-Nov(M)", "harvesting": "Mar(B)-Apr(M)"}},
        "Pulses/Lentil": {
            "Rabi": {"sowing": "Oct(E)-Nov(M)", "harvesting": "Mar(B)-Apr(M)"},
        },
        "Pea": {"Rabi": {"sowing": "Oct(E)-Nov(M)", "harvesting": "Mar(B)-Apr(M)"}},
        "Soybean": {"Kharif": {"sowing": "June(E)-July(M)", "harvesting": "Sept(E)-October(B)"}},
        "Sesame": {"Kharif": {"sowing": "June(B)-July(E)", "harvesting": "Oct(M)-Nov(M)"}},
        "Rapeseed-Mustard": {
            "Mustard": {"sowing": "Within Oct", "harvesting": "Feb-March"},
            "Taramira": {"sowing": "Nov", "harvesting": "March"},
            "Yellow Sarson": {"sowing": "Oct-Nov", "harvesting": "Feb-March"},
        },
    },
    "Tamil Nadu": {
        "Arhar/Tur": {
            "Early Kharif": {"sowing": "June (B)-JuneM)", "harvesting": "Nov (M)-Dec (M)"},
            "Kharif": {"sowing": "Jun (M)-July (M)", "harvesting": "Jan (M)-Feb.. (M)"},
        },
    },
    "Tripura": {
        "Mungbean/Urdbean": {
            "Kharif": {"sowing": "July(E)-Aug(B)", "harvesting": "Sep(E)-Oct(E)"},
        },
        "Chickpea": {"Rabi": {"sowing": "Oct(E)-Nov(M)", "harvesting": "Mar(B)-Apr(M)"}},
        "Pulses/Lentil": {
            "Rabi": {"sowing": "Oct(E)-Nov(M)", "harvesting": "Mar(B)-Apr(M)"},
        },
        "Pea": {"Rabi": {"sowing": "Oct(E)-Nov(M)", "harvesting": "Mar(B)-Apr(M)"}},
    },
    "Uttar Pradesh": {
        "Paddy": {"Kharif": {"sowing": "Jun(M)-Jul(E)", "harvesting": "Oct(B)-Nov(B)"}},
        "Wheat": {"Rabi": {"sowing": "Oct(M)-Dec(E)", "harvesting": "Mar(M)Apr(E)"}},
        "Arhar/Tur": {
            "Early Kharif": {"sowing": "June (B)-JuneM)", "harvesting": "Dec (M)- Dec. (E)."},
            "Kharif": {"sowing": "July (B)-July (E)", "harvesting": "March (M)-April (E)"},
        },
        "Soybean": {"Kharif": {"sowing": "June(E)-July(M)", "harvesting": "Sept(E)-October(B)"}},
        "Linseed": {"Rabi": {"sowing": "Oct(B)-Nov(B)", "harvesting": "Mar(B)-Apr(E)"}},
        "Rapeseed-Mustard": {
            "Mustard": {"sowing": "Oct(L)-Nov(M)", "harvesting": "Feb-March"},
            "Yellow Sarson": {"sowing": "Oct(E)", "harvesting": "Feb-March"},
        },
    },
    "Uttaranchal": {
        "Arhar/Tur": {"Early Kharif": {"sowing": "June (B)-June (M)", "harvesting": "Nov.(M)-Dec (M)."}},
    },
    "West Bengal": {
        "Linseed": {"Rabi": {"sowing": "Oct(B)-Nov(B)", "harvesting": "Mar(B)-Apr(E)"}},
        "Jute": {"Kharif": {"sowing": "Feb-April", "harvesting": "Aug-Sep"}},
    },
}

@tool
def crop_calendar(state_name: str):
    """
    Provides the crop calendar for a given state in India.
    Args:
        state_name (str): Name of the state in India. Must be Title Case.
    """

    state_name = state_name.strip().title()

    if state_name not in crop_data:
        return "Sorry, information not available."

    return json.dumps(crop_data[state_name])