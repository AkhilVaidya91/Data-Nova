from huggingface_hub import InferenceClient

client = InferenceClient(
	provider="together",
	api_key=""
)

prompt = """
"You are an expert auditor tasked with critically analyzing the annual reports of various companies to validate their alignment with the United Nations Sustainable Development Goals (UN SDGs). "
"I will provide you with excerpts from these reports, and your task is to evaluate whether the projects, initiatives, or actions mentioned in the excerpts align with any of the 17 UN SDGs.\n\n"
"Ensure that the alignment is clear, direct and strong enough for the initiatives to be considered valid and acceptable under the specified goals.\n\n"
"### UN SDGs Overview\n"
"Each SDG has keywords and example projects that may be considered under its domain. The examples are indicative, not exhaustive.\n\n"
The United Nations' 17 Sustainable Development Goals (SDGs) were established in 2015 as part of the 2030 Agenda for Sustainable Development. These goals serve
as a universal call to action to end poverty, protect the planet, and ensure peace and prosperity for all by 2030.
Below is an overview of each SDG, its description, and examples of corporate initiatives contributing to each goal:
1. No Poverty
Description: End poverty in all its forms everywhere.
Corporate Example: Companies can help alleviate global poverty by funding verified results in education, health, and workforce development. Organizations like Village
Enterprise advocate for a payment-by-results model to ensure investments achieve desired outcomes.
2. Zero Hunger
Description: End hunger, achieve food security and improved nutrition, and promote sustainable agriculture.
Corporate Example: Businesses can support sustainable agriculture by investing in technologies that increase crop yields and reduce environmental impact. For
instance, some companies develop precision farming tools that help farmers optimize resource use.
3. Good Health and Well-being
Description: Ensure healthy lives and promote well-being for all at all ages.
Corporate Example: The UN's SDGs include a commitment to end epidemics of AIDS, tuberculosis, malaria, and other communicable diseases by 2030, aiming for
universal health coverage and access to safe, affordable medicines and vaccines.
4. Quality Education
Description: Ensure inclusive and equitable quality education and promote lifelong learning opportunities for all.
Corporate Example: Companies can invest in educational programs and partnerships that enhance digital literacy and provide access to quality education, especially
in underserved communities.
5. Gender Equality
Description: Achieve gender equality and empower all women and girls.
Corporate Example: Businesses can adopt the Women's Empowerment Principles to promote gender equality in the workplace, marketplace, and community.
6. Clean Water and Sanitation
Description: Ensure availability and sustainable management of water and sanitation for all.
Corporate Example: Companies like Kimberly-Clark have aligned with SDG 6 by focusing on water conservation and sanitation initiatives.
7. Affordable and Clean Energy
Description: Ensure access to affordable, reliable, sustainable, and modern energy for all.
Corporate Example: Businesses can invest in renewable energy projects and improve energy efficiency within their operations to support this goal.
8. Decent Work and Economic Growth
Description: Promote sustained, inclusive, and sustainable economic growth, full and productive employment, and decent work for all.
Corporate Example: Companies can create job opportunities and foster inclusive work environments that promote economic growth and decent work conditions.
9. Industry, Innovation, and Infrastructure
Description: Build resilient infrastructure, promote inclusive and sustainable industrialization, and foster innovation.
Corporate Example: Huawei has actively pushed digital technology advances to reduce digital inequality, aligning with SDG 9.
10. Reduced Inequalities
Description: Reduce inequality within and among countries.
Corporate Example: Businesses can support social sustainability by adhering to human rights principles and promoting inclusive policies.
11. Sustainable Cities and Communities
Description: Make cities and human settlements inclusive, safe, resilient, and sustainable.
Corporate Example: Companies can develop sustainable building materials and invest in smart city technologies to enhance urban living conditions.
12. Responsible Consumption and Production
Description: Ensure sustainable consumption and production patterns.
Corporate Example: Nike's "Move to Zero" initiative aims for zero carbon and zero waste, aligning with SDG 12.
13. Climate Action
Description: Take urgent action to combat climate change and its impacts.
Corporate Example: Businesses are increasingly prioritizing sustainability to reduce their environmental impact and align with climate goals.
14. Life Below Water
Description: Conserve and sustainably use the oceans, seas, and marine resources for sustainable development.
Corporate Example: Companies can reduce plastic usage and invest in ocean cleanup projects to protect marine ecosystems.
15. Life on Land
Description: Protect, restore, and promote sustainable use of terrestrial ecosystems, manage forests sustainably, combat desertification, halt and reverse land
degradation, and halt biodiversity loss.
Corporate Example: Businesses can engage in reforestation projects and adopt sustainable sourcing practices to preserve terrestrial ecosystems.
16. Peace, Justice, and Strong Institutions
Description: Promote peaceful and inclusive societies for sustainable development, provide access to justice for all, and build effective, accountable, and inclusive
institutions at all levels.
Corporate Example: Companies can uphold ethical business practices and support initiatives that strengthen legal and institutional frameworks.
17. Partnerships for the Goals
Description: Strengthen the means of implementation and revitalize the global partnership for sustainable development.
Corporate Example: Businesses can collaborate with governments, NGOs, and other stakeholders to advance the SDGs through shared initiatives and resources.
For more detailed information on each SDG, please refer to the United Nations' official website:
"### Excerpts from the reports:\n\n"
ANNUAL REPORT ON CSR ACTIVITIES
[Pursuant to Section 135 of the Companies Act, 2013 read with Companies (Corporate Social
Responsibility Policy) Rules, 2014, as amended]
1. Brief outline on CSR Policy of the Company
 The Company is actively contributing to the social and economic development of the communities in which it
operates. The Company is doing so in sync with the United Nations Sustainable Development Goals to build a
better, sustainable way of life for the weaker sections of society and raise the country’s human development index.
 The Company’s Corporate Social Responsibility (“CSR”) policy conforms to the National Voluntary Guidelines
on Social, Environment and Economic Responsibilities of Business released by the Ministry of Corporate Affairs,
Government of India.
Scope
 The CSR Policy encompasses Formulation, Implementation, Monitoring, Evaluation, Documentation and Reporting
of CSR activities taken up by the Company.
2. Composition of CSR Committee
Sl.
No. Name of Director Designation / Nature of
Directorship
Number of meetings of CSR
Committee held during the year
Number of meetings of CSR
Committee attended during the year
1 Mrs. Rajashree Birla Chairperson 1 1
2 Mrs. Sukanya Kripalu Independent Director 1 1
3 Mr. K. C. Jhanwar Managing Director 1 1
Permanent Invitee: Dr. (Mrs.) Pragnya Ram, Group Executive President, CSR, Legacy, Documentation & Archives
3. Provide the web-link where Composition of CSR committee, CSR Policy and CSR
projects approved by the board are disclosed on the website of the Company
 Composition of CSR Committee: https://www.ultratechcement.com/about-us/board-committees
CSR Policy and CSR Projects: https://www.ultratechcement.com/investors/corporate-governance#policies
4. Provide the details of Impact assessment of CSR projects carried out in pursuance of
sub-rule (3) of rule 8 of the Companies (Corporate Social responsibility Policy) Rules,
2014, if applicable (attach the report)
 The Company has been voluntarily conducting impact assessments through Independent Agencies to screen and
evaluate select CSR programs. The Company takes cognisance of sub-rule 3 of rule 8 of the Companies (Corporate
Social responsibility Policy) Rules, 2014 and shall initiate steps to conduct impact assessment of all applicable
CSR projects.
5. Details of the amount available for set off in pursuance of sub-rule (3) of rule 7 of the
Companies (Corporate Social responsibility Policy) Rules, 2014 and amount required for
set off for the financial year, if any
Sl.
No. Financial Year Amount available for set-off from preceding
financial years (` in crores)
Amount required to be set-off for the financial
year, if any (` in crores)
1 2021-22 46.96 6.60
Annexure III
6. Average net profit of the company as per section 135(5): ` 5,149 crores
7. (a) Two percent of average net profit of the company as per section 135(5) : ` 103 crores
(b) Surplus arising out of the CSR projects or programmes or activities of the previous financial years : Nil
(c) Amount required to be set off for the financial year, if any : ` 6.60 crores
(d) Total CSR obligation for the financial year (7a+7b-7c). : ` 96.40 crores
8. (a) CSR amount spent or unspent for the financial year:
Total Amount Spent for the
Financial Year
(K in crore)
Amount Unspent (K in crore)
Total Amount transferred to Unspent
CSR Account as per section 135(6)
Amount transferred to any fund specified under
Schedule VII as per second proviso to section 135(5)
Amount Date of transfer Name of the Fund Amount Date of transfer
96.40 - - - - -
b) Details of CSR amount spent against ongoing projects for the financial year:
1 2 3 4 5 6 7 8 9 10 11
Sl.
No.
Name
of the
Project
Item from
the list of
activities
in
Schedule
VII to the
Act
Local area
(Yes/No)
Location of the
project
Project
duration
Amount
allocated
for the
project (`
in crores)
Amount
spent
in the
current
financial
Year (` in
crores)
Amount
transferred to
Unspent CSR
Account for the
project as per
Section 135(6)
(` in crores)
Mode of
Implementation
-Direct (Yes/No).
Mode of
ImplementationThrough
Implementing
Agency
State District Name
CSR
Registration
number
- - - - - - - - - - - - -
c) Details of CSR amount spent against other than ongoing projects for the financial year:
1 2 3 4 5 6 7 8
Sl.
No. Name of the Project
Item from
the list of
activities in
Schedule
VII to the
Act
Local
area
(Yes/
No).
Location of the project Amount
spent
for the
project (`
in crores)
Mode of
ImplementationDirect (Yes/No)
Mode of Implementation -
Through Implementing Agency
State District Name
CSR
Registration
number
1 Preschool education
project
Anganwadies / playschools/
crèches, strengthening
Anganwadi Centre
(ii) Yes Rajasthan Jodhpur, Nagaur, Jaipur,
Chittorgarh, Jhalawar,
Baran, Sirohi, Pali
0.92 Both
(Direct and
through
Implementing
agency)
UltraTech
Community
Welfare
Foundation
(“UCWF”)
CSR00006050
Madhya Pradesh Neemuch, Dhar, Rewa
Gujarat Amreli, Bhuj
Maharashtra Chandrapur, Solapur
Chhattisgarh BalodaBazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
94 UltraTech Cement Limited | Integrated Annual Report 2021-22 95
Corporate Overview Value Creation Approach Our Performance Statutory Reports Financial Statements
1 2 3 4 5 6 7 8
Sl.
No. Name of the Project
Item from
the list of
activities in
Schedule
VII to the
Act
Local
area
(Yes/
No).
Location of the project Amount
spent
for the
project (`
in crores)
Mode of
ImplementationDirect (Yes/No)
Mode of Implementation -
Through Implementing Agency
State District Name
CSR
Registration
number
School Education
Program
Enrollment awareness
programs/ event, Formal
schools outside campus
(Company run), Education
Material (Study materials,
Uniform, Books etc),
Scholarship (merit and
need based assistance),
School competitions / best
teacher award, cultural
events, quality of education
(support teachers,
Improve education
methods), specialised
coaching, exposure visits /
awareness, formal schools
inside campus, Support to
Midday Meal Project
(ii) Yes Rajasthan Jodhpur, Nagaur, Jaipur,
Chittorgarh, Sirohi, Pali
28.08 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Madhya Pradesh Neemuch, Dhar, Rewa,
Siddhi, Satna
Gujarat Amreli, Bhuj
Maharashtra Chandrapur, Solapur
Chhattisgarh Baloda Bazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
Himachal Pradesh Solan
Uttar Pradesh Sonebhadra
Tamil Nadu Arriyallur
Education support
programs
Knowledge centre and
library, adult and non formal
education, celebration of
national days / International
days, computer education,
reducing drop-out and
continuing education
(Kasturba balika/ bridge
courses / counseling),
Career counseling and
orientation.
(ii) Yes Rajasthan Jodhpur, Nagaur, Jaipur,
Chittorgarh, Sirohi, Pali
1.20 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Madhya Pradesh Neemuch, Dhar, Rewa,
Siddhi, Satna
Gujarat Amreli, Bhuj
Maharashtra Chandrapur, Solapur
Chhattisgarh Baloda Bazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
Himachal Pradesh Solan
Uttar Pradesh Sonebhadra
Tamil Nadu Arriyallur
West Bengal Hoogly, Bolpur
Odisha Jharsuguda
Haryana Jhajjar, Panipat
Vocational and Technical
Education
Strengthening ITI’s, skills
based individual training
program
(ii) Yes Madhya Pradesh Neemuch, Dhar, Rewa,
Siddh,
5.55 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Gujarat Amreli, Bhuj
Chhattisgarh Baloda Bazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
Uttar Pradesh Sonebhadra
Annexure III (Contd.)
1 2 3 4 5 6 7 8
Sl.
No. Name of the Project
Item from
the list of
activities in
Schedule
VII to the
Act
Local
area
(Yes/
No).
Location of the project Amount
spent
for the
project (`
in crores)
Mode of
ImplementationDirect (Yes/No)
Mode of Implementation -
Through Implementing Agency
State District Name
CSR
Registration
number
School Infrastructure
Buildings and civil
structures (new),
buildings and civil
structures (renovation
and maintenance), school
sanitation / drinking water,
school facilities & fixtures
(furniture/blackboards/
computers)
(ii) Yes Rajasthan Jodhpur, Nagaur, Jaipur,
Chittorgarh, Sirohi, Pali
4.29 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Madhya Pradesh Neemuch, Dhar, Rewa,
Siddhi, Satna
Gujarat Amreli, Bhuj
Maharashtra Chandrapur, Solapur
Chhattisgarh BalodaBazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
Himachal Pradesh Solan
Uttar Pradesh Sonebhadra
Tamil Nadu Arriyallur
West Bengal Hoogly, Bolpur
Odisha Jharsuguda
Haryana Jhajjar, Panipat
2 Preventive Health Care
Immunisation, Pulse
polio immunisation,
Health Check- up camps,
Ambulance Mobile
Dispensary Program,
Malaria / Diarrhoea /
Control programs, Health
& Hygiene awareness
programs, School health /
Eye / Dental camps, Yoga /
fitness classes
(i) Yes Rajasthan Jodhpur, Nagaur, Jaipur,
Chittorgarh, Sirohi, Pali
2.81 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Madhya Pradesh Neemuch, Dhar, Rewa,
Siddhi, Satna
Gujarat Amreli, Bhuj
Maharashtra Chandrapur, Solapur
Chhattisgarh Baloda Bazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
Himachal Pradesh Solan
Uttar Pradesh Sonebhadra
Tamil Nadu Arriyallur
Curative Health Care
General Health camps,
Specialised Health Camps,
Eye camps, Treatment
Camps (Skin, cleft,etc.),
Cleft camp, Homeopathic /
Ayurvedic Camps, Surgical
camps, Tuberculosis /
Leprosy Company operated
hospitals/ dispensaries /
clinic.
(i) Yes Rajasthan Jodhpur, Nagaur, Jaipur,
Chittorgarh, Sirohi, Pali
23.74 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Madhya Pradesh Neemuch, Dhar, Rewa,
Siddhi, Satna
Gujarat Amreli, Bhuj
Maharashtra Chandrapur, Solapur
Chhattisgarh Baloda Bazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
Himachal Pradesh Solan
Uttar Pradesh Sonebhadra
Tamil Nadu Arriyallur
Reproductive and Child
Health Mother and child
health care (ante natal care,
pre natal care and neonatal
care), adolescent health
care, infant and child health
(Healthy baby competition),
support to family planning /
camps, nutritional programs
for mother/child.
(i) Yes Rajasthan Jodhpur, Nagaur, Jaipur,
Chittorgarh, Sirohi, Pali
0.15 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Madhya Pradesh Neemuch, Dhar, Rewa,
Siddhi, Satna
Gujarat Amreli, Bhuj
Maharashtra Chandrapur, Solapur
Chhattisgarh Baloda Bazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
Himachal Pradesh Solan
Uttar Pradesh Sonebhadra
Tamil Nadu Arriyallur
96 UltraTech Cement Limited | Integrated Annual Report 2021-22 97
Corporate Overview Value Creation Approach Our Performance Statutory Reports Financial Statements
1 2 3 4 5 6 7 8
Sl.
No. Name of the Project
Item from
the list of
activities in
Schedule
VII to the
Act
Local
area
(Yes/
No).
Location of the project Amount
spent
for the
project (`
in crores)
Mode of
ImplementationDirect (Yes/No)
Mode of Implementation -
Through Implementing Agency
State District Name
CSR
Registration
number
Quality/ Support Program
Referral services treatment
of BPL, old age or needy
patient, HIV- AIDS
Awareness Program, RTI/
STD Awareness Program,
Support for differently
abled, Ambulance services,
Blood donation camps,
blood grouping
(i) Yes Rajasthan Jodhpur, Nagaur, Jaipur,
Chittorgarh, Sirohi, Pali
0.08 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Madhya Pradesh Neemuch, Dhar, Rewa,
Siddhi, Satna
Gujarat Amreli, Bhuj
Maharashtra Chandrapur
Chhattisgarh Baloda Bazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
Himachal Pradesh Solan
Uttar Pradesh Sonebhadra
Tamil Nadu Arriyallur
Health Infrastructure
Buildings and civil
structures (new),
buildings and civil
structures (renovation
and maintenance), village
community sanitation
(toilets/ drainage), individual
toilets, drinking water new
sources, (Hand pump/ RO/
Water Tank/ well), drinking
water existing sources
(operation/ maintenance),
water source purification.
(i) Yes Rajasthan Jodhpur, Nagaur, Jaipur,
Chittorgarh, Sirohi, Pali
4.00 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Madhya Pradesh Neemuch, Dhar, Rewa,
Siddhi, Satna
Gujarat Amreli, Bhuj
Maharashtra Chandrapur
Chhattisgarh Baloda Bazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
Himachal Pradesh Solan
Uttar Pradesh Sonebhadra
Tamil Nadu Arriyallur
3 Agriculture and Farm
Based
Agriculture & horticulture
training program/
farmers group transfer of
technology-demonstration
plots, support for
horticulture plots, seeds
improvement program,
support for improved
agriculture equipment
and inputs, Exposure
visits / support for
agricultural mela, integrated
agricultural/ horticultural
improvement program/
productivity improvement
programs, soil health and
organic farming.
(iv) Yes Rajasthan Jodhpur, Nagaur, Jaipur,
Chittorgarh, Sirohi, Pali
0.28 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Madhya Pradesh Neemuch, Dhar, Rewa,
Siddhi, Satna
Gujarat Amreli, Bhuj
Maharashtra Chandrapur
Chhattisgarh Baloda Bazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
Himachal Pradesh Solan
Uttar Pradesh Sonebhadra
Tamil Nadu Arriyallur
Animal Husbandry Based
Treatment and vaccination,
breed improvement
productivity, improvement
programs and training.
(iv) Yes Rajasthan Jodhpur, Nagaur, Jaipur,
Chittorgarh, Sirohi, Pali
2.03 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Madhya Pradesh Neemuch, Dhar, Rewa,
Siddhi, Satna
Gujarat Amreli, Bhuj
Maharashtra Chandrapur
Chhattisgarh Baloda Bazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
Annexure III (Contd.)
1 2 3 4 5 6 7 8
Sl.
No. Name of the Project
Item from
the list of
activities in
Schedule
VII to the
Act
Local
area
(Yes/
No).
Location of the project Amount
spent
for the
project (`
in crores)
Mode of
ImplementationDirect (Yes/No)
Mode of Implementation -
Through Implementing Agency
State District Name
CSR
Registration
number
Non-farm & Skills Based
Income generation
program
Capacity building
program-Tailoring, Beauty
Parlour, Mechanical, Rural
Enterprise development
& Income Generation
Programs, Support to
SHGs for entrepreneurial
activities.
(iii) and (iv) Yes Rajasthan Jodhpur, Nagaur, Jaipur,
Chittorgarh, Sirohi, Pali
0.70 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Madhya Pradesh Neemuch, Dhar, Rewa,
Siddhi, Satna
Gujarat Amreli, Bhuj
Maharashtra Chandrapur
Chhattisgarh Baloda Bazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
Himachal Pradesh Solan
Uttar Pradesh Sonebhadra
Tamil Nadu Arriyallur
Natural Resource
conservation programs &
Non-conventional Energy
Bio gas support program,
Solar energy support
and other energy
support programs - (low
smoke wood stoves /
sky light), Plantation /
Green Belt Development
/ Roadside Plantation,
Soil conservation /
Land improvement,
Water conservation and
harvesting (small structures/
bigger structures),
Community Pasture Land
Development / Orchard
Development.
(iv) Yes Rajasthan Jodhpur, Nagaur, Jaipur,
Chittorgarh, Sirohi, Pali
3.61 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Madhya Pradesh Neemuch, Dhar, Rewa,
Siddhi, Satna
Gujarat Amreli, Bhuj
Maharashtra Chandrapur
Chhattisgarh Baloda Bazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
Himachal Pradesh Solan
Uttar Pradesh Sonebhadra
Tamil Nadu Arriyallur
Livelihood Infrastructure (iv) Yes Rajasthan Jodhpur, Nagaur, Jaipur,
Chittorgarh, Sirohi, Pali
0.08 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Madhya Pradesh Neemuch, Dhar, Rewa,
Siddhi, Satna
Gujarat Amreli, Bhuj
Maharashtra Chandrapur
Chhattisgarh Baloda Bazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
Himachal Pradesh Solan
Uttar Pradesh Sonebhadra
Tamil Nadu Arriyallur
98 UltraTech Cement Limited | Integrated Annual Report 2021-22 99
Corporate Overview Value Creation Approach Our Performance Statutory Reports Financial Statements
1 2 3 4 5 6 7 8
Sl.
No. Name of the Project
Item from
the list of
activities in
Schedule
VII to the
Act
Local
area
(Yes/
No).
Location of the project Amount
spent
for the
project (`
in crores)
Mode of
ImplementationDirect (Yes/No)
Mode of Implementation -
Through Implementing Agency
State District Name
CSR
Registration
number
4 Rural Infrastructure
Development other than
for the purpose of health /
education / livelihood
New roads / culverts /
bridges / bus stands, repair
roads/ culverts / bridges /
bus stands community halls
/ housing, other community
assets and shelters.
Support for repairing
Roads / Culverts / Bridges
/ Community Halls / Street
lights and other community
infrastructure
(x) Yes Rajasthan Jodhpur, Nagaur, Jaipur,
Chittorgarh, Sirohi, Pali
11.08 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Madhya Pradesh Neemuch, Dhar, Rewa,
Siddhi, Satna
Gujarat Amreli, Bhuj
Maharashtra Chandrapur,
Chhattisgarh Baloda Bazaar, Raipur
Karnataka Gulbarga
Andhra Pradesh Kurnool, Anantapur
Himachal Pradesh Solan
Uttar Pradesh Sonebhadra
5 Promotion of culture/
sports
Support to rural cultural
program, festivals & melas
support to rural sports.
(vii) Yes Rajasthan
Madhya Pradesh
Gujarat
Maharashtra
Chhattisgarh
Karnataka
Andhra Pradesh
Himachal Pradesh
Uttar Pradesh
Jodhpur, Nagaur, Jaipur,
Chittorgarh, Sirohi, Pali
Neemuch, Dhar, Rewa,
Siddhi, Satna
Amreli, Bhuj
Chandrapur
Baloda Bazaar, Raipur
Gulbarga
Kurnool, Anantapur
Solan
Sonebhadra
2.92 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Institutional building &
strengthening
Strengthening / formation
of community based
organisation (SHGs),
Support to development
organisations, Oldage
Home, Orphanage
(iii) Yes 2.69 Both
(Direct and
through
Implementing
agency)
UCWF CSR00006050
Total 94.21
d) Amount spent in Administrative Overheads: ` 2.19 crores
e) Amount spent on Impact Assessment, if applicable: NIL
f) Total amount spent for the Financial Year (8b+8c+8d+8e) : ` 96.40 crores
g) Excess amount for set off, if any
Sl.
No. Particular Amount
(` in crores)
i) Two percent of average net profit of the company as per section 135(5) 103.00
ii) Total amount spent for the Financial Year 96.40
iii) Excess amount spent for the financial year [(ii)-(i)] (6.60)
iv) Surplus arising out of the CSR projects or programmes or activities of the previous financial years, if any 46.96
v) Amount available for set off in succeeding financial years [(iii)-(iv)] 40.36
Annexure III (Contd.)
9. (a) Details of Unspent CSR amount for the preceding three financial years:
Sl.
No.
Preceding
Financial Year
Amount transferred to
Unspent CSR Account
under section 135 (6)
(` in crores)
Amount spent
in the reporting
Financial Year
(` in crores)
Amount transferred to any fund specified
under Schedule VII as per section 135(6),
if any
Amount remaining to
be spent in succeeding
financial years
Name of (` in crores)
the Fund
Amount
(` in crores)
Date of
transfer
- - - - - - - -
(b) Details of CSR amount spent in the financial year for ongoing projects of the preceding financial year(s):
1 2 3 4 5 6 7 8 9
Sl.
No. Project ID Name of the
Project
Financial Year in
which the project was
commenced
Project
duration
Total amount
allocated for
the project
(` in crores)
Amount spent
on the project
in the reporting
Financial Year
(` in crores)
Cumulative
amount spent
at the end of
reporting Financial
Year (` in crores)
Status of
the project
-Completed/
Ongoing
- - - - - - - - -
10. In case of creation or acquisition of capital asset, furnish the details relating to the asset
so created or acquired through CSR spent in the financial year (asset-wise details)
(a) Date of creation or acquisition of the capital asset(s): None
(b) Amount of CSR spent for creation or acquisition of capital asset: Nil
(c) Details of the entity or public authority or beneficiary under whose name such capital asset is
registered, their address etc.: Not Applicable
(d) Provide details of the capital asset(s) created or acquired (including complete address and
location of the capital asset): Not Applicable
11. Specify the reason(s), if the company has failed to spend two per cent of the average net
profit as per section 135(5): Not Applicable
K. C. Jhanwar Rajashree Birla
Managing Director Chairperson, CSR Committee
Mumbai, 29th April, 2022 (DIN: 01743559) (DIN: 00022995)
100 UltraTech Cement Limited | Integrated Annual Report 2021-22 101
Corporate Overview Value Creation Approach Our Performance Statutory Reports Financial Statements
"### Response Format\n"
"You must always respond in JSON format, using the following structure:\n\n"
"{\n"
"  \"SDG-1\": {\n"
"    \"Presence\": \"Yes\" or \"No\",\n"
"    \"Evidence\": \"string\"\n"
"  },\n"
"  \"SDG-2\": {\n"
"    \"Presence\": \"Yes\" or \"No\",\n"
"    \"Evidence\": \"string\"\n"
"  },\n"
"  ...\n"
"  \"SDG-17\": {\n"
"    \"Presence\": \"Yes\" or \"No\",\n"
"    \"Evidence\": \"string\"\n"
"  }\n"
"}\n\n"
"- **Presence**: Indicate \"Yes\" if the initiative aligns with the respective SDG, otherwise \"No\".\n"
"- **Evidence**: Provide the exact matching text **statement** from the excerpt (10–15 words) **only about a project, action, or initiative** if \"Yes\". Note that the statement should only be from the report's excerpt and not from the original description of the SDGs (don't confuse between the two).\n\n"
"**Important Notes:**\n"
"- Note that when you are considering a particular initiative as an activity under a particular SDG, it should explicitly align with the given SDG and not just sound like one, this is a strict and hard constraint to be followed ensuring that a project is considered as an SDG aligned activity if and only if it perfectly aligns with the SDG. This is an important step to prevent LLM hallucination, don't fill in the gaps, respond only if the information is directly provided."
"- Your response must always include all 17 SDGs, even if the presence is \"No\" for any or all.\n"
"- The response should be directly parsable as a JSON, with all elements (keys and values) enclosed in double quotes.\n"
"- Do not include any text outside the JSON format, such as explanations or backticks, not even the word json.\n\n"
"Please respond in the JSON structure specified."

"""


messages = [
	{
		"role": "user",
		"content": prompt
	}
]

completion = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1", 
	messages=messages, 
	max_tokens=50000
)
# print(completion.choices[0].message)
print(completion.choices[0].message)