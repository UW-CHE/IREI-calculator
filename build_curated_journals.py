"""
Build a curated list of top 50 journals per research category.
Looks up real metrics from OpenAlex API, then writes curated_journals_by_category.json.

Run once: python build_curated_journals.py
"""

import json
import time
import requests


# Curated journal lists: 50 per category, ordered roughly by prestige/impact.
# "issn" is the preferred ISSN used for direct OpenAlex lookup (faster, more accurate).
# If issn lookup fails the script falls back to a name search.
CURATED_JOURNALS = {

    # -------------------------------------------------------------------------
    "Biotechnology and Biomedical Engineering": [
        {"name": "Nature Biotechnology",                            "issn": "1087-0156"},
        {"name": "Nature Biomedical Engineering",                   "issn": "2157-846X"},
        {"name": "Biotechnology Advances",                          "issn": "0734-9750"},
        {"name": "Bioactive Materials",                             "issn": "2452-199X"},
        {"name": "Journal of Controlled Release",                   "issn": "0168-3659"},
        {"name": "Biomaterials",                                    "issn": "0142-9612"},
        {"name": "Acta Biomaterialia",                              "issn": "1742-7061"},
        {"name": "Biosensors and Bioelectronics",                   "issn": "0956-5663"},
        {"name": "Advanced Healthcare Materials",                   "issn": "2192-2640"},
        {"name": "Biofabrication",                                  "issn": "1758-5090"},
        {"name": "Metabolic Engineering",                           "issn": "1096-7176"},
        {"name": "Journal of Nanobiotechnology",                    "issn": "1477-3155"},
        {"name": "Biomacromolecules",                               "issn": "1525-7797"},
        {"name": "Biomaterials Science",                            "issn": "2047-4830"},
        {"name": "Microbial Cell Factories",                        "issn": "1475-2859"},
        {"name": "Trends in Biotechnology",                         "issn": "0167-7799"},
        {"name": "Applied Microbiology and Biotechnology",          "issn": "0175-7598"},
        {"name": "Biotechnology and Bioengineering",                "issn": "0006-3592"},
        {"name": "Lab on a Chip",                                   "issn": "1473-0197"},
        {"name": "ACS Synthetic Biology",                           "issn": "2161-5063"},
        {"name": "Journal of Biotechnology",                        "issn": "0168-1656"},
        {"name": "Bioconjugate Chemistry",                          "issn": "1043-1802"},
        {"name": "Biochemical Engineering Journal",                 "issn": "1369-703X"},
        {"name": "Microbial Biotechnology",                         "issn": "1751-7915"},
        {"name": "Plant Biotechnology Journal",                     "issn": "1467-7644"},
        {"name": "Frontiers in Bioengineering and Biotechnology",   "issn": "2296-4185"},
        {"name": "Computational and Structural Biotechnology Journal", "issn": "2001-0370"},
        {"name": "Applied Biochemistry and Biotechnology",          "issn": "0273-2289"},
        {"name": "Journal of Industrial Microbiology & Biotechnology", "issn": "1367-5435"},
        {"name": "Biotechnology Journal",                           "issn": "1860-6768"},
        {"name": "Biotechnology Progress",                          "issn": "8756-7938"},
        {"name": "Journal of Chemical Technology & Biotechnology",  "issn": "0268-2575"},
        {"name": "International Journal of Pharmaceutics",          "issn": "0378-5173"},
        {"name": "European Journal of Pharmaceutics and Biopharmaceutics", "issn": "0939-6411"},
        {"name": "Pharmaceutical Research",                         "issn": "0724-8741"},
        {"name": "Tissue Engineering Part A",                       "issn": "1937-3341"},
        {"name": "Journal of Biomedical Materials Research Part A", "issn": "1549-3296"},
        {"name": "Bioprocess and Biosystems Engineering",           "issn": "1615-7591"},
        {"name": "Enzyme and Microbial Technology",                 "issn": "0141-0229"},
        {"name": "Process Biochemistry",                            "issn": "1359-5113"},
        {"name": "ACS Biomaterials Science & Engineering",          "issn": "2373-9878"},
        {"name": "Drug Delivery",                                   "issn": "1071-7544"},
        {"name": "Drug Delivery and Translational Research",        "issn": "2190-393X"},
        {"name": "Cell Systems",                                    "issn": "2405-4712"},
        {"name": "Molecular Systems Biology",                       "issn": "1744-4292"},
        {"name": "Pharmacological Research",                        "issn": "1043-6618"},
        {"name": "mSystems",                                        "issn": "2379-5077"},
        {"name": "Food and Bioproducts Processing",                 "issn": "0960-3085"},
        {"name": "Biotechnology and Applied Biochemistry",          "issn": "0885-4513"},
        {"name": "Molecular Biotechnology",                         "issn": "1073-6085"},
    ],

    # -------------------------------------------------------------------------
    "Electrochemical Engineering": [
        {"name": "Nature Energy",                                   "issn": "2058-7546"},
        {"name": "Energy & Environmental Science",                  "issn": "1754-5692"},
        {"name": "Advanced Energy Materials",                       "issn": "1614-6840"},
        {"name": "ACS Energy Letters",                              "issn": "2380-8195"},
        {"name": "Nano-Micro Letters",                              "issn": "2150-5551"},
        {"name": "Nano Energy",                                     "issn": "2211-2855"},
        {"name": "Energy Storage Materials",                        "issn": "2405-8297"},
        {"name": "Journal of Energy Chemistry",                     "issn": "2095-4956"},
        {"name": "Carbon Energy",                                   "issn": "2637-9368"},
        {"name": "Journal of Energy Storage",                       "issn": "2352-152X"},
        {"name": "Journal of Power Sources",                        "issn": "0378-7753"},
        {"name": "International Journal of Hydrogen Energy",        "issn": "0360-3199"},
        {"name": "Electrochimica Acta",                             "issn": "0013-4686"},
        {"name": "Journal of The Electrochemical Society",          "issn": "0013-4651"},
        {"name": "Electrochemistry Communications",                 "issn": "1388-2481"},
        {"name": "Journal of Electroanalytical Chemistry",          "issn": "0022-0728"},
        {"name": "ChemElectroChem",                                 "issn": "2196-0216"},
        {"name": "Solid State Ionics",                              "issn": "0167-2738"},
        {"name": "Electroanalysis",                                 "issn": "1040-0397"},
        {"name": "Journal of Applied Electrochemistry",             "issn": "0021-891X"},
        {"name": "Journal of Solid State Electrochemistry",         "issn": "1432-8488"},
        {"name": "Corrosion Science",                               "issn": "0010-938X"},
        {"name": "ACS Applied Energy Materials",                    "issn": "2574-0962"},
        {"name": "ECS Journal of Solid State Science and Technology", "issn": "2162-8769"},
        {"name": "Energy Conversion and Management",                "issn": "0196-8904"},
        {"name": "Physical Chemistry Chemical Physics",             "issn": "1463-9076"},
        {"name": "ChemSusChem",                                     "issn": "1864-5631"},
        {"name": "Sustainable Energy & Fuels",                      "issn": "2398-4902"},
        {"name": "Energy Technology",                               "issn": "2194-4296"},
        {"name": "Current Opinion in Electrochemistry",             "issn": "2451-9103"},
        {"name": "Batteries & Supercaps",                           "issn": "2566-6223"},
        {"name": "Battery Energy",                                  "issn": "2766-9890"},
        {"name": "Energy & Environmental Materials",                "issn": "2575-0356"},
        {"name": "EcoMat",                                          "issn": "2567-3173"},
        {"name": "Ionics",                                          "issn": "0947-7047"},
        {"name": "Journal of Physics: Energy",                      "issn": "2515-7655"},
        {"name": "Batteries",                                       "issn": "2313-0105"},
        {"name": "Fuel Cells",                                      "issn": "1615-6846"},
        {"name": "Electrocatalysis",                                "issn": "1868-2529"},
        {"name": "Materials Chemistry Frontiers",                   "issn": "2052-1537"},
        {"name": "npj Computational Materials",                     "issn": "2057-3960"},
        {"name": "Applied Surface Science",                         "issn": "0169-4332"},
        {"name": "Chemical Communications",                         "issn": "1359-7345"},
        {"name": "Journal of Materials Chemistry A",                "issn": "2050-7488"},
        {"name": "Electrochemical Science Advances",                "issn": "2698-5977"},
        {"name": "International Journal of Electrochemical Science","issn": "1452-3981"},
        {"name": "Journal of Electrochemical Science and Engineering", "issn": "2303-4890"},
        {"name": "npj Clean Energy",                                "issn": "2731-8028"},
        {"name": "Energy and AI",                                   "issn": "2666-5468"},
        {"name": "Advanced Power Technology",                       "issn": None},
    ],

    # -------------------------------------------------------------------------
    "Nanotechnology for Advanced Materials": [
        {"name": "Nature Nanotechnology",                           "issn": "1748-3387"},
        {"name": "Nature Materials",                                "issn": "1476-1122"},
        {"name": "Advanced Materials",                              "issn": "0935-9648"},
        {"name": "ACS Nano",                                        "issn": "1936-0851"},
        {"name": "Nano Letters",                                    "issn": "1530-6984"},
        {"name": "Advanced Functional Materials",                   "issn": "1616-301X"},
        {"name": "Nano-Micro Letters",                              "issn": "2150-5551"},
        {"name": "Materials Today",                                 "issn": "1369-7021"},
        {"name": "Small",                                           "issn": "1613-6810"},
        {"name": "ACS Applied Materials & Interfaces",              "issn": "1944-8244"},
        {"name": "Carbon",                                          "issn": "0008-6223"},
        {"name": "Nano Today",                                      "issn": "1748-0132"},
        {"name": "Chemistry of Materials",                          "issn": "0897-4756"},
        {"name": "Nano Research",                                   "issn": "1998-0124"},
        {"name": "Nanoscale",                                       "issn": "2040-3364"},
        {"name": "Matter",                                          "issn": "2590-2385"},
        {"name": "Materials Horizons",                              "issn": "2051-6347"},
        {"name": "Small Methods",                                   "issn": "2366-9608"},
        {"name": "Advanced Optical Materials",                      "issn": "2195-1071"},
        {"name": "ACS Materials Letters",                           "issn": "2639-4979"},
        {"name": "Nanoscale Horizons",                              "issn": "2055-7434"},
        {"name": "2D Materials",                                    "issn": "2053-1583"},
        {"name": "Scripta Materialia",                              "issn": "1359-6462"},
        {"name": "Applied Materials Today",                         "issn": "2352-9407"},
        {"name": "Composites Part B: Engineering",                  "issn": "1359-8368"},
        {"name": "Nano Convergence",                                "issn": "2196-5404"},
        {"name": "Acta Materialia",                                 "issn": "1359-6454"},
        {"name": "Journal of Materials Science",                    "issn": "0022-2461"},
        {"name": "Journal of Alloys and Compounds",                 "issn": "0925-8388"},
        {"name": "Ceramics International",                          "issn": "0272-8842"},
        {"name": "Thin Solid Films",                                "issn": "0040-6090"},
        {"name": "Surface and Coatings Technology",                 "issn": "0257-8972"},
        {"name": "Nanotechnology",                                  "issn": "0957-4484"},
        {"name": "Journal of Nanoparticle Research",                "issn": "1388-0764"},
        {"name": "Physical Review Materials",                       "issn": "2475-9953"},
        {"name": "MRS Bulletin",                                    "issn": "0883-7694"},
        {"name": "npj Quantum Materials",                           "issn": "2397-4648"},
        {"name": "Journal of Physical Chemistry C",                 "issn": "1932-7447"},
        {"name": "Materials Today Physics",                         "issn": "2542-5293"},
        {"name": "FlatChem",                                        "issn": "2452-2627"},
        {"name": "Composites Science and Technology",               "issn": "0266-3538"},
        {"name": "Journal of Colloid and Interface Science",        "issn": "0021-9797"},
        {"name": "ACS Applied Nano Materials",                      "issn": "2574-0970"},
        {"name": "Materials Today Nano",                            "issn": "2588-8420"},
        {"name": "Advanced Materials Technologies",                 "issn": "2365-709X"},
        {"name": "npj 2D Materials and Applications",               "issn": "2397-7132"},
        {"name": "Journal of the European Ceramic Society",         "issn": "0955-2219"},
        {"name": "Environmental Science: Nano",                     "issn": "2051-8153"},
        {"name": "ACS Applied Electronic Materials",                "issn": "2637-6113"},
        {"name": "Extreme Mechanics Letters",                       "issn": "2352-4316"},
    ],

    # -------------------------------------------------------------------------
    "Process Systems Engineering": [
        {"name": "AIChE Journal",                                   "issn": "0001-1541"},
        {"name": "Chemical Engineering Science",                    "issn": "0009-2509"},
        {"name": "Industrial & Engineering Chemistry Research",     "issn": "0888-5885"},
        {"name": "Computers & Chemical Engineering",                "issn": "0098-1354"},
        {"name": "Chemical Engineering Research and Design",        "issn": "0263-8762"},
        {"name": "Separation and Purification Technology",          "issn": "1383-5866"},
        {"name": "Applied Energy",                                  "issn": "0306-2619"},
        {"name": "Energy",                                          "issn": "0360-5442"},
        {"name": "Process Safety and Environmental Protection",     "issn": "0957-5820"},
        {"name": "Journal of Process Control",                      "issn": "0959-1524"},
        {"name": "Automatica",                                      "issn": "0005-1098"},
        {"name": "Chemical Engineering and Processing: Process Intensification", "issn": "0255-2701"},
        {"name": "Control Engineering Practice",                    "issn": "0967-0661"},
        {"name": "ISA Transactions",                                "issn": "0019-0578"},
        {"name": "Digital Chemical Engineering",                    "issn": "2772-5081"},
        {"name": "Computers & Operations Research",                 "issn": "0305-0548"},
        {"name": "International Journal of Production Economics",   "issn": "0925-5273"},
        {"name": "Computers & Industrial Engineering",              "issn": "0360-8352"},
        {"name": "European Journal of Operational Research",        "issn": "0377-2217"},
        {"name": "Applied Mathematical Modelling",                  "issn": "0307-904X"},
        {"name": "IEEE Transactions on Control Systems Technology", "issn": "1063-6536"},
        {"name": "International Journal of Control",                "issn": "0020-7179"},
        {"name": "Annual Reviews in Control",                       "issn": "1367-5788"},
        {"name": "Systems & Control Letters",                       "issn": "0167-6911"},
        {"name": "Chemical Engineering Communications",             "issn": "0098-6445"},
        {"name": "Journal of Chemical Engineering of Japan",        "issn": "0021-9592"},
        {"name": "Chinese Journal of Chemical Engineering",         "issn": "1004-9541"},
        {"name": "Chemometrics and Intelligent Laboratory Systems", "issn": "0169-7439"},
        {"name": "Journal of Industrial and Engineering Chemistry", "issn": "1226-086X"},
        {"name": "Korean Journal of Chemical Engineering",          "issn": "0256-1115"},
        {"name": "Asia-Pacific Journal of Chemical Engineering",    "issn": "1932-2135"},
        {"name": "Brazilian Journal of Chemical Engineering",       "issn": "0104-6632"},
        {"name": "Canadian Journal of Chemical Engineering",        "issn": "0008-4034"},
        {"name": "Journal of Chemical & Engineering Data",          "issn": "0021-9568"},
        {"name": "Engineering Optimization",                        "issn": "0305-215X"},
        {"name": "Optimization and Engineering",                    "issn": "1389-4420"},
        {"name": "Optimal Control Applications and Methods",        "issn": "0143-2087"},
        {"name": "Processes",                                       "issn": "2227-9717"},
        {"name": "International Journal of Chemical Reactor Engineering", "issn": "1542-6580"},
        {"name": "Separation Science and Technology",               "issn": "0149-6395"},
        {"name": "Journal of Cleaner Production",                   "issn": "0959-6526"},
        {"name": "The International Journal of Advanced Manufacturing Technology", "issn": "0268-3768"},
        {"name": "Reaction Chemistry & Engineering",                "issn": "2058-9883"},
        {"name": "Chemical Engineering & Technology",               "issn": "0930-7516"},
        {"name": "Journal of Food Process Engineering",             "issn": "0145-8876"},
        {"name": "Operations Research",                             "issn": "0030-364X"},
        {"name": "Omega",                                           "issn": "0305-0483"},
        {"name": "IISE Transactions",                               "issn": "2472-5854"},
        {"name": "Green Chemical Engineering",                      "issn": "2666-8394"},
        {"name": "Chemical Engineering Journal Advances",           "issn": "2666-8211"},
    ],

    # -------------------------------------------------------------------------
    "Soft Matter & Polymer Engineering": [
        {"name": "Progress in Polymer Science",                     "issn": "0079-6700"},
        {"name": "Macromolecules",                                  "issn": "0024-9297"},
        {"name": "Advanced Fiber Materials",                        "issn": "2524-7921"},
        {"name": "Carbohydrate Polymers",                           "issn": "0144-8617"},
        {"name": "Journal of Membrane Science",                     "issn": "0376-7388"},
        {"name": "Advances in Colloid and Interface Science",       "issn": "0001-8686"},
        {"name": "Polymer Reviews",                                 "issn": "1558-3724"},
        {"name": "International Journal of Biological Macromolecules", "issn": "0141-8130"},
        {"name": "Langmuir",                                        "issn": "0743-7463"},
        {"name": "ACS Macro Letters",                               "issn": "2161-1653"},
        {"name": "Polymer Degradation and Stability",               "issn": "0141-3910"},
        {"name": "Polymer",                                         "issn": "0032-3861"},
        {"name": "European Polymer Journal",                        "issn": "0014-3057"},
        {"name": "Advanced Industrial and Engineering Polymer Research", "issn": "2542-5048"},
        {"name": "Polymers",                                        "issn": "2073-4360"},
        {"name": "Journal of Rheology",                             "issn": "0148-6055"},
        {"name": "Soft Matter",                                     "issn": "1744-683X"},
        {"name": "Rheologica Acta",                                 "issn": "0035-4511"},
        {"name": "Macromolecular Rapid Communications",             "issn": "1521-3927"},
        {"name": "Cellulose",                                       "issn": "0969-0239"},
        {"name": "Polymer Chemistry",                               "issn": "1759-9954"},
        {"name": "Biomacromolecules",                               "issn": "1525-7797"},
        {"name": "ACS Applied Polymer Materials",                   "issn": "2637-6105"},
        {"name": "Journal of Colloid and Interface Science",        "issn": "0021-9797"},
        {"name": "Colloids and Surfaces A",                         "issn": "0927-7757"},
        {"name": "Polymer Testing",                                 "issn": "0142-9418"},
        {"name": "Polymer Composites",                              "issn": "0272-8397"},
        {"name": "Journal of Non-Newtonian Fluid Mechanics",        "issn": "0377-0257"},
        {"name": "Macromolecular Chemistry and Physics",            "issn": "1022-1352"},
        {"name": "Polymer Engineering and Science",                 "issn": "0032-3888"},
        {"name": "Polymer Bulletin",                                "issn": "0170-0839"},
        {"name": "Journal of Applied Polymer Science",              "issn": "0021-8995"},
        {"name": "Polymer International",                           "issn": "0959-8103"},
        {"name": "Polymer Journal",                                 "issn": "0032-3896"},
        {"name": "Reactive and Functional Polymers",                "issn": "1381-5148"},
        {"name": "ACS Polymers Au",                                 "issn": "2692-8752"},
        {"name": "Giant",                                           "issn": "2666-1365"},
        {"name": "Journal of Polymer Research",                     "issn": "1022-9760"},
        {"name": "Colloid & Polymer Science",                       "issn": "0303-402X"},
        {"name": "Liquid Crystals",                                 "issn": "0267-8292"},
        {"name": "Colloids and Surfaces B: Biointerfaces",          "issn": "0927-7765"},
        {"name": "Journal of Polymers and the Environment",         "issn": "1566-2543"},
        {"name": "Journal of Polymer Science",                      "issn": "2642-4150"},
        {"name": "Polymer-Plastics Technology and Materials",       "issn": "2574-0881"},
        {"name": "Carbohydrate Research",                           "issn": "0008-6215"},
        {"name": "Journal of Polymer Engineering",                  "issn": "0334-6447"},
        {"name": "Macromolecular Research",                         "issn": "1598-5032"},
        {"name": "RSC Applied Polymers",                            "issn": "2755-1709"},
        {"name": "International Journal of Polymer Science",        "issn": "1687-9422"},
        {"name": "Polymers from Renewable Resources",               "issn": "2041-2479"},
    ],

    # -------------------------------------------------------------------------
    "Sustainable Reaction Engineering": [
        {"name": "Nature Catalysis",                                "issn": "2520-1158"},
        {"name": "Applied Catalysis B: Environmental",              "issn": "0926-3373"},
        {"name": "ACS Catalysis",                                   "issn": "2155-5435"},
        {"name": "Renewable and Sustainable Energy Reviews",        "issn": "1364-0321"},
        {"name": "Nature Sustainability",                           "issn": "2398-9629"},
        {"name": "Journal of Cleaner Production",                   "issn": "0959-6526"},
        {"name": "Green Chemistry",                                 "issn": "1463-9262"},
        {"name": "Chemical Engineering Journal",                    "issn": "1385-8947"},
        {"name": "ACS Sustainable Chemistry & Engineering",         "issn": "2168-0485"},
        {"name": "Environmental Science & Technology",              "issn": "0013-936X"},
        {"name": "Bioresource Technology",                          "issn": "0960-8524"},
        {"name": "Catalysis Reviews",                               "issn": "0161-4940"},
        {"name": "Journal of Catalysis",                            "issn": "0021-9517"},
        {"name": "Fuel",                                            "issn": "0016-2361"},
        {"name": "Catalysis Today",                                 "issn": "0920-5861"},
        {"name": "Applied Catalysis A: General",                    "issn": "0926-860X"},
        {"name": "Organic Process Research & Development",          "issn": "1083-6160"},
        {"name": "Renewable Energy",                                "issn": "0960-1481"},
        {"name": "Waste Management",                                "issn": "0956-053X"},
        {"name": "ChemCatChem",                                     "issn": "1867-3880"},
        {"name": "Catalysis Science & Technology",                  "issn": "2044-4753"},
        {"name": "Energy & Fuels",                                  "issn": "0887-0624"},
        {"name": "Topics in Catalysis",                             "issn": "1022-5528"},
        {"name": "Solar Energy",                                    "issn": "0038-092X"},
        {"name": "Solar Energy Materials and Solar Cells",          "issn": "0927-0248"},
        {"name": "Resources, Conservation and Recycling",           "issn": "0921-3449"},
        {"name": "Biomass and Bioenergy",                           "issn": "0961-9534"},
        {"name": "Energy Conversion and Management",                "issn": "0196-8904"},
        {"name": "Catalysis Communications",                        "issn": "1566-7367"},
        {"name": "Fuel Processing Technology",                      "issn": "0378-3820"},
        {"name": "International Journal of Green Energy",           "issn": "1543-5075"},
        {"name": "Journal of Environmental Chemical Engineering",   "issn": "2213-3437"},
        {"name": "Sustainable Energy Technologies and Assessments", "issn": "2213-1388"},
        {"name": "SusMat",                                          "issn": "2766-3124"},
        {"name": "Sustainable Production and Consumption",          "issn": "2352-5509"},
        {"name": "Sustainable Energy & Fuels",                      "issn": "2398-4902"},
        {"name": "Advanced Sustainable Systems",                    "issn": "2366-7486"},
        {"name": "RSC Sustainability",                              "issn": "2753-8559"},
        {"name": "Chinese Journal of Catalysis",                    "issn": "0253-9837"},
        {"name": "Waste Management & Research",                     "issn": "0734-242X"},
        {"name": "Environmental Science & Technology Letters",      "issn": "2328-8930"},
        {"name": "Green Energy & Environment",                      "issn": "2096-2797"},
        {"name": "Reaction Chemistry & Engineering",                "issn": "2058-9883"},
        {"name": "Journal of CO2 Utilization",                      "issn": "2212-9820"},
        {"name": "Molecular Catalysis",                             "issn": "2468-8231"},
        {"name": "Sustainable Chemistry and Pharmacy",              "issn": "2352-5541"},
        {"name": "Journal of Analytical and Applied Pyrolysis",     "issn": "0165-2370"},
        {"name": "Combustion and Flame",                            "issn": "0010-2180"},
        {"name": "Clean Technologies and Environmental Policy",     "issn": "1618-954X"},
        {"name": "Green Processing and Synthesis",                  "issn": "2191-9542"},
    ],

    # -------------------------------------------------------------------------
    "Multidisciplinary & Core Engineering": [
        {"name": "Nature",                                          "issn": "0028-0836"},
        {"name": "Science",                                         "issn": "0036-8075"},
        {"name": "Nature Communications",                           "issn": "2041-1723"},
        {"name": "Science Advances",                                "issn": "2375-2548"},
        {"name": "Proceedings of the National Academy of Sciences", "issn": "0027-8424"},
        {"name": "Journal of the American Chemical Society",        "issn": "0002-7863"},
        {"name": "Angewandte Chemie International Edition",         "issn": "1521-3773"},
        {"name": "Advanced Materials",                              "issn": "0935-9648"},
        {"name": "Chemical Reviews",                                "issn": "0009-2665"},
        {"name": "Chemical Society Reviews",                        "issn": "0306-0012"},
        {"name": "Nature Chemistry",                                "issn": "1755-4330"},
        {"name": "Accounts of Chemical Research",                   "issn": "0001-4842"},
        {"name": "Nature Reviews Chemistry",                        "issn": "2397-3358"},
        {"name": "Chem",                                            "issn": "2451-9294"},
        {"name": "ACS Central Science",                             "issn": "2374-7943"},
        {"name": "Nature Chemical Engineering",                     "issn": "2731-0396"},
        {"name": "Communications Chemistry",                        "issn": "2399-3669"},
        {"name": "Chemical Science",                                "issn": "2041-6520"},
        {"name": "Advanced Science",                                "issn": "2198-3844"},
        {"name": "Physical Chemistry Chemical Physics",             "issn": "1463-9076"},
        {"name": "Journal of Physical Chemistry Letters",           "issn": "1948-7185"},
        {"name": "Chemical Communications",                         "issn": "1359-7345"},
        {"name": "RSC Advances",                                    "issn": "2046-2069"},
        {"name": "ACS Omega",                                       "issn": "2470-1343"},
        {"name": "Scientific Reports",                              "issn": "2045-2322"},
        {"name": "iScience",                                        "issn": "2589-0042"},
        {"name": "Cell Reports Physical Science",                   "issn": "2666-3864"},
        {"name": "Chem Catalysis",                                  "issn": "2667-1093"},
        {"name": "One Earth",                                       "issn": "2590-3322"},
        {"name": "Engineering",                                     "issn": "2095-8099"},
        {"name": "National Science Review",                         "issn": "2095-5138"},
        {"name": "PNAS Nexus",                                      "issn": "2752-6542"},
        {"name": "Dalton Transactions",                             "issn": "1477-9226"},
        {"name": "Organic Letters",                                 "issn": "1523-7060"},
        {"name": "Inorganic Chemistry",                             "issn": "0020-1669"},
        {"name": "Journal of Organic Chemistry",                    "issn": "0022-3263"},
        {"name": "ChemPhysChem",                                    "issn": "1439-4235"},
        {"name": "Journal of Hazardous Materials",                  "issn": "0304-3894"},
        {"name": "Chemosphere",                                     "issn": "0045-6535"},
        {"name": "Green Chemistry",                                 "issn": "1463-9262"},
        {"name": "Chemical Engineering Journal",                    "issn": "1385-8947"},
        {"name": "AIChE Journal",                                   "issn": "0001-1541"},
        {"name": "Chemical Engineering Science",                    "issn": "0009-2509"},
        {"name": "Small",                                           "issn": "1613-6810"},
        {"name": "Small Methods",                                   "issn": "2366-9608"},
        {"name": "CCS Chemistry",                                   "issn": "2096-5745"},
        {"name": "Aggregate",                                       "issn": "2692-4560"},
        {"name": "Cell Chemical Biology",                           "issn": "2451-9456"},
        {"name": "Angewandte Chemie",                               "issn": "1433-7851"},
        {"name": "ACS Sustainable Chemistry & Engineering",         "issn": "2168-0485"},
    ],
}


def fetch_journal_metrics(name: str, issn: str | None) -> dict | None:
    """Query OpenAlex for a journal.  Tries ISSN lookup first, then name search."""
    base = "https://api.openalex.org"
    headers = {"User-Agent": "doi-checker/1.0 (mailto:you@example.com)"}

    # 1. Try direct ISSN lookup
    if issn:
        url = f"{base}/sources/issn:{issn}"
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                return _parse_source(r.json())
        except Exception:
            pass

    # 2. Fall back to name search
    try:
        r = requests.get(
            f"{base}/sources",
            params={"search": name, "filter": "type:journal", "per_page": 5},
            headers=headers,
            timeout=15,
        )
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results:
                return _parse_source(results[0])
    except Exception as e:
        print(f"    Search failed for '{name}': {e}")

    return None


def _parse_source(src: dict) -> dict:
    stats = src.get("summary_stats", {})
    counts = src.get("counts_by_year", [])

    # Impact factor proxy: 2yr mean citedness (matches script.py logic)
    impact_factor = round(stats.get("2yr_mean_citedness", 0), 2)

    # works_count for latest full year
    works_count = counts[1]["works_count"] if len(counts) > 1 else src.get("works_count", 0)

    return {
        "name": src.get("display_name", "Unknown"),
        "issn": src.get("issn_l", "N/A"),
        "h_index": stats.get("h_index", 0),
        "impact_factor": impact_factor,
        "publisher": src.get("host_organization_name", "Unknown"),
        "works_count": works_count,
        "cited_by_count": src.get("cited_by_count", 0),
        "openalex_id": src.get("id", ""),
    }


def build_database(delay: float = 0.12) -> dict:
    db = {}
    for category, journals in CURATED_JOURNALS.items():
        print(f"\n{'='*70}")
        print(f"Category: {category}  ({len(journals)} journals)")
        print(f"{'='*70}")
        results = []
        seen_ids = set()

        for j in journals:
            name, issn = j["name"], j.get("issn")
            print(f"  Fetching: {name} ...", end=" ", flush=True)
            data = fetch_journal_metrics(name, issn)
            if data:
                oid = data["openalex_id"]
                if oid in seen_ids:
                    print("duplicate – skipped")
                    continue
                seen_ids.add(oid)
                results.append(data)
                print(f"IF={data['impact_factor']:.2f}  H={data['h_index']}")
            else:
                print("NOT FOUND")
            time.sleep(delay)

        # Sort by impact factor descending
        results.sort(key=lambda x: x["impact_factor"], reverse=True)
        db[category] = results
        print(f"  → {len(results)} journals collected")

    return db


if __name__ == "__main__":
    print("Building curated journal database from OpenAlex…")
    print("This will make ~350 API calls and take ~1–2 minutes.\n")

    db = build_database()

    out_file = "curated_journals_by_category.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved to {out_file}")
    for cat, journals in db.items():
        print(f"  {cat}: {len(journals)} journals")
