import psycopg2

'''
SELECT *
FROM tmevents
WHERE source = 'EV'
AND map_status IS NULL
AND LOWER(name) NOT LIKE '%parking%'
AND LOWER(name) NOT LIKE '%premium%'
AND LOWER(name) NOT LIKE '%preferred%'
AND LOWER(name) NOT LIKE '%season%'
AND LOWER(name) NOT LIKE '%flex%'
AND LOWER(name) NOT LIKE '%vip%'
AND start_date >= current_date
and start_date <= '2024-01-01'
and max_listings is NULL 
order by tm_venue;

'''

'''
ALL FOOTBALL STADIUMS 

stadium_list_combined = [
    "Amon G. Carter Stadium // Amon G. Carter Stadium",
    "ALLEGIANT STADIUM UNLV FOOTBALL // Allegiant Stadium",
    "Allegacy Federal Credit Union Stadium // Allegacy Federal Credit Union Stadium",
    "Allegiant Stadium - UNLV // Allegiant Stadium",
    "Allen E. Paulson Stadium // Paulson Stadium",
    "Apogee Stadium // DATCU Stadium",
    "App State - Kidd Brewer Stadium // Kidd Brewer Stadium",
    "Arizona Stadium | Tucson, AZ // Arizona Stadium",
    "Arizona Stadium // Arizona Stadium",
    "Ball State - Scheumann Stadium // Scheumann Stadium",
    "Beaver Stadium // Beaver Stadium",
    "Ben Hill Griffin Stadium // Ben Hill Griffin Stadium",
    "Bobby Dodd Stadium at Grant Field // Bobby Dodd Stadium",
    "Boone Pickens Stadium // Boone Pickens Stadium",
    "Brooks Stadium // Brooks Stadium",
    "Brooks Field at Wallace Wade Stadium // Wallace Wade Stadium",
    "BROOKS STADIUM // Brooks Stadium",
    "California Memorial Stadium // California Memorial Stadium",
    "Camp Randall Stadium // Camp Randall Stadium",
    "Canvas Stadium // Canvas Stadium",
    "CEFCU Stadium // CEFCU Stadium",
    "Center Parc Credit Union Stadium // Center Parc Credit Union Stadium",
    "Dana J. Dykhouse Stadium // Dana J. Dykhouse Stadium",
    "Darrell K Royal-Texas Memorial Stadium // Darrell K Royal - Texas Memorial Stadium",
    "David Booth Kansas Memorial Stadium // Memorial Stadium-KS",
    "Davis Wade Stadium // Davis Wade Stadium at Scott Field",
    "Delaware Stadium // Delaware Stadium",
    "Doyt Perry Stadium // Doyt Perry Stadium",
    "Doak S. Campbell Stadium // Doak Campbell Stadium",
    "Dowdy-Ficklen Stadium // Dowdy Ficklen Stadium",
    "Elliott T. Bowers Stadium // Bowers Stadium",
    "Empower Field at Mile High Stadium // Empower Field at Mile High",
    "FAU Stadium // FAU Stadium",
    "Falcon Stadium // Falcon Stadium",
    "Finley Stadium // Carter-Finley Stadium",
    "FirstBank Stadium // FirstBank Stadium",
    "FIU Stadium // Riccardo Silva Stadium",
    "Gerald Ford Stadium // Gerald Ford Stadium",
    "Gerald J. Ford Stadium // Gerald Ford Stadium",
    "Glass Bowl // Glass Bowl Stadium",
    "Goodman Stadium // Goodman Stadium",
    "Greater Zion Stadium // Greater Zion Stadium",
    "H.A. Chapman Stadium // H.A. Chapman Stadium",
    "Hancock Stadium // Hancock Stadium",
    "Houck Stadium // Houck Stadium",
    "Huntington Bank Stadium // Huntington Bank Stadium",
    "Illinois Memorial Stadium // Memorial Stadium-IL",
    "Joan C. Edwards Stadium // Joan C Edwards Stadium",
    "Joe Aillet Stadium // Joe Aillet Stadium",
    "Jordan-Hare Stadium // Jordan-Hare Stadium",
    "Kinnick Stadium // Kinnick Stadium",
    "Kenan Memorial Stadium // Kenan Stadium",
    "L&N Federal Credit Union Stadium // L&N Federal Credit Union Stadium",
    "Lavell Edwards Stadium // LaVell Edwards Stadium",
    "Lane Stadium // Lane Stadium",
    "Marshall - Joan C Edwards Stadium // Joan C Edwards Stadium",
    "Martin Stadium // Gesa Field at Martin Stadium",
    "Maverik Stadium // Merlin Olsen Field at Maverik Stadium",
    "McGuirk Alumni Stadium // Warren McGuirk Alumni Stadium",
    "Memorial Stadium - CA // California Memorial Stadium",
    "Memorial Stadium - IL // Memorial Stadium-IL",
    "Memorial Stadium - SC // Clemson Memorial Stadium",
    "Memorial Stadium Illinois // Memorial Stadium-IL",
    "Memorial Stadium Indiana // Memorial Stadium-IN",
    "Merlin Olsen Field at Maverik Stadium // Merlin Olsen Field at Maverik Stadium",
    "Michigan Stadium // Michigan Stadium",
    "Milan Puskar Stadium // Mountaineer Field",
    "Minnesota Huntington Bank Stadium // Huntington Bank Stadium",
    "MM Roberts Stadium // MM Roberts Stadium",
    "Nippert Stadium // Nippert Stadium",
    "NMC Memorial Stadium (Annapolis, MD) // Navy Marine Corps Memorial Stadium",
    "Notre Dame Stadium // Notre Dame Stadium",
    "Ohio Stadium // Ohio Stadium",
    "Oklahoma Memorial Stadium // Oklahoma Memorial Stadium",
    "Oliver C. Dawson Stadium // Oliver C Dawson Stadium",
    "Peden Stadium // Peden Stadium",
    "Pratt & Whitney Stadium at Rentschler Field // Pratt & Whitney Stadium at Rentschler Field",
    "Protective Stadium // Protective Stadium",
    "RESER STADIUM // Reser Stadium",
    "Reser Stadium | Corvallis, OR // Reser Stadium",
    "Richardson Stadium // Jerry Richardson Stadium",
    "Robert K. Kraft Field at Wien Stadium // Lawrence A. Wien Stadium",
    "Ross-Ade Stadium (Purdue University) // Ross-Ade Stadium",
    "Rice Stadium // Rice Stadium-TX",
    "SANFORD STADIUM // Sanford Stadium",
    "Scott Stadium // Scott Stadium",
    "Spartan Stadium // Spartan Stadium-MI",
    "Stanford Stadium | Stanford, CA // Stanford Stadium",
    "Stewart Stadium // Stewart Stadium",
    "Sun Devil Stadium // Sun Devil Stadium",
    "Texas State - Bobcat Stadium // Bobcat Stadium - TX",
    "University Stadium // University Stadium Albuquerque",
    "VALLEY CHILDREN'S STADIUM // Valley Childrens Stadium",
    "Vaught-Hemingway Stadium // Vaught-Hemingway Stadium",
    "WALDO STADIUM // Waldo Stadium",
    "War Memorial Stadium // War Memorial Stadium-AR // War Memorial Stadium-WY",
    "Williams-Brice Stadium // Williams-Brice Stadium",
    "Wisconsin Camp Randall Stadium // Camp Randall Stadium",
    "Wisconsin - Camp Randall Stadium // Camp Randall Stadium",
    "Yager Stadium // Yager Stadium",
    "Yulman Stadium // Yulman Stadium",
    "Zable Stadium // Zable Stadium",
    "Bobcat Stadium // Bobcat Stadium - TX",
    "DakotaDome // DakotaDome",
    "Homer Bryce Stadium // Homer Bryce Stadium",
    "Mackay Stadium // Mackay Stadium",
    "Mackay Stadium GA // Mackay Stadium",
    "Priore Field at Meade Stadium // Meade Stadium",
    "Veterans Memorial Stadium // Veterans Memorial Stadium - AL"
    "Gesa Field // Gesa Field at Martin Stadium",
    "Husky Stadium // Husky Stadium-WA",
    "SECU STADIUM // SECU Stadium",
    "Rentschler Field // Pratt & Whitney Stadium at Rentschler Field",
    "UNI-Dome // UNI Dome", 
    "Kibbie Dome // Kibbie Dome", 
    "Stewart Stadium // Stewart Stadium", 
    "Roos Field // Roos Field",
    "FOOTBALL // Bridgeforth Stadium",
    "Football // Bryant-Denny Stadium
    "Mountaineer Field // Mountaineer Field",
    "Clarence T. C. Ching Athletics Complex // Clarence TC Ching Athletics Complex"
]
'''

host_name = "database-1-instance-1.cwysyy38ldpw.us-east-2.rds.amazonaws.com"
database = "tryAgain"
username = "isdsar"
password = "Outeclanisdsar123*"
port = "5432"

'''
SELECT DISTINCT ON (tm_venue) name, tm_venue
FROM tmevents
WHERE tm_venue ILIKE '%Stadium%'
    AND source = 'EV'
    AND start_date >= CURRENT_DATE
    AND sb_venue_name IS NULL
ORDER BY tm_venue, start_date;
'''

def add_venue_to_db(tm_venue, sb_venue_name, source):
    conn = psycopg2.connect(
        host=host_name,
        dbname=database,
        user=username,
        password=password,
        port=port
    )

    cur = conn.cursor()

    # You need to replace 'column1', 'column2', and 'column3' with your actual column names
    cur.execute(f"INSERT INTO venues_mapped_new (tm_venue, sb_venue_name, source) VALUES (%s, %s, %s)", 
                (tm_venue, sb_venue_name, source))

    conn.commit()
    cur.close()
    conn.close()

'''
VENUES 

ev_venue // skybox_venue 

Davis Wade Stadium  // "Davis Wade Stadium at Scott Field"
Michigan Stadium // "Michigan Stadium"
SANFORD STADIUM  // "Sanford Stadium"
SPARTAN STADIUM // "Spartan Stadium-MI"
Sun Devil Stadium // "Sun Devil Stadium"
Stewart Stadium // "Stewart Stadium"
Wallace Wade Stadium // "Wallace Wade Stadium"
War Memorial Stadium // "War Memorial Stadium-AR" "War Memorial Stadium-WY"
Washington Grizzly Stadium // "Washington-Grizzly Stadium"
Wisconsin Camp Randall Stadium // "Camp Randall Stadium"
Ross-Ade Stadium // "Ross-Ade Stadium"
Raymond James Stadium // "Raymond James Stadium"
Ohio Stadium // "Ohio Stadium"
Nippert Stadium // "Nippert Stadium"
Minnesota Huntington Bank Stadium // "Huntington Bank Stadium"
Milan Puskar Stadium // "Mountaineer Field"
McLane Stadium // "McLane Stadium"
L&N Federal Credit Union Stadium // "L&N Federal Credit Union Stadium"
Lavell Edwards Stadium // "LaVell Edwards Stadium"
Lane Stadium // "Lane Stadium"
Kinnick Stadium // "Kinnick Stadium"
Kenan Memorial Stadium // "Kenan Stadium"
Jordan-Hare Stadium // "Jordan-Hare Stadium"
Illinois Memorial Stadium // "Memorial Stadium-IL"
Husky Stadium // "Huskie Stadium"
H.A. Chapman Stadium // "H.A. Chapman Stadium"
Greater Zion Stadium // "Greater Zion Stadium"
Glass Bowl // "Glass Bowl Stadium"
Gerald J. Ford Stadium // "Gerald Ford Stadium"
Gaylord Family Oklahoma Memorial Stadium // "Oklahoma Memorial Stadium"
Falcon Stadium // "Falcon Stadium"
Dowdy-Ficklen Stadium // "Dowdy Ficklen Stadium"
Delaware Stadium // "Delaware Stadium"
CALIFORNIA MEMORIAL STADIUM // "California Memorial Stadium"
BRYANT-DENNY STADIUM // "Bryant-Denny Stadium"
Brooks Field at Wallace Wade Stadium // "Wallace Wade Stadium"
Boone Pickens Stadium // "Boone Pickens Stadium"
Ben Hill Griffin Stadium // "Ben Hill Griffin Stadium"
Beaver Stadium // "Beaver Stadium"
Autzen Stadium // "Autzen Stadium"
Arizona Stadium // "Arizona Stadium"
Amon G. Carter Stadium // "Amon G. Carter Stadium"
"Clarence T. C. Ching Athletics Complex // Clarence TC Ching Athletics Complex"
'''

def add_venue_to_db_v2(): 

    # stadium_list = [
    #     "Davis Wade Stadium // Davis Wade Stadium at Scott Field",
    #     "Michigan Stadium // Michigan Stadium",
    #     "SANFORD STADIUM // Sanford Stadium",
    #     "SPARTAN STADIUM // Spartan Stadium-MI",
    #     "Sun Devil Stadium // Sun Devil Stadium",
    #     "Stewart Stadium // Stewart Stadium",
    #     "Wallace Wade Stadium // Wallace Wade Stadium",
    #     "War Memorial Stadium // War Memorial Stadium-AR // War Memorial Stadium-WY",
    #     "Washington Grizzly Stadium // Washington-Grizzly Stadium",
    #     "Wisconsin Camp Randall Stadium // Camp Randall Stadium",
    #     "Ross-Ade Stadium // Ross-Ade Stadium",
    #     "Raymond James Stadium // Raymond James Stadium",
    #     "Ohio Stadium // Ohio Stadium",
    #     "Nippert Stadium // Nippert Stadium",
    #     "Minnesota Huntington Bank Stadium // Huntington Bank Stadium",
    #     "Milan Puskar Stadium // Mountaineer Field",
    #     "McLane Stadium // McLane Stadium",
    #     "L&N Federal Credit Union Stadium // L&N Federal Credit Union Stadium",
    #     "Lavell Edwards Stadium // LaVell Edwards Stadium",
    #     "Lane Stadium // Lane Stadium",
    #     "Kinnick Stadium // Kinnick Stadium",
    #     "Kenan Memorial Stadium // Kenan Stadium",
    #     "Jordan-Hare Stadium // Jordan-Hare Stadium",
    #     "Illinois Memorial Stadium // Memorial Stadium-IL",
    #     "Husky Stadium // Huskie Stadium",
    #     "H.A. Chapman Stadium // H.A. Chapman Stadium",
    #     "Greater Zion Stadium // Greater Zion Stadium",
    #     "Glass Bowl // Glass Bowl Stadium",
    #     "Gerald J. Ford Stadium // Gerald Ford Stadium",
    #     "Gaylord Family Oklahoma Memorial Stadium // Oklahoma Memorial Stadium",
    #     "Falcon Stadium // Falcon Stadium",
    #     "Dowdy-Ficklen Stadium // Dowdy Ficklen Stadium",
    #     "Delaware Stadium // Delaware Stadium",
    #     "CALIFORNIA MEMORIAL STADIUM // California Memorial Stadium",
    #     "BRYANT-DENNY STADIUM // Bryant-Denny Stadium",
    #     "Brooks Field at Wallace Wade Stadium // Wallace Wade Stadium",
    #     "Boone Pickens Stadium // Boone Pickens Stadium",
    #     "Ben Hill Griffin Stadium // Ben Hill Griffin Stadium",
    #     "Beaver Stadium // Beaver Stadium",
    #     "Autzen Stadium // Autzen Stadium",
    #     "Arizona Stadium // Arizona Stadium",
    #     "Amon G. Carter Stadium // Amon G. Carter Stadium"
    # ]

#     stadium_list = [
#     "Allegacy Federal Credit Union Stadium // Allegacy Federal Credit Union Stadium",
#     "Allegiant Stadium - UNLV // Allegiant Stadium",
#     "ALLEGIANT STADIUM UNLV FOOTBALL // Allegiant Stadium",
#     "Allen E. Paulson Stadium // Paulson Stadium",
#     "Apogee Stadium // DATCU Stadium",
#     "App State - Kidd Brewer Stadium // Kidd Brewer Stadium",
#     "Arizona Stadium | Tucson, AZ // Arizona Stadium",
#     "Ball State - Scheumann Stadium // Scheumann Stadium",
#     "Bobby Dodd Stadium at Grant Field // Bobby Dodd Stadium",
#     "Bobcat Stadium // Bobcat Stadium - MT",
#     "Brooks Stadium // Brooks Stadium",
#     "BROOKS STADIUM // Brooks Stadium",
#     "California Memorial Stadium // California Memorial Stadium",
#     "Camp Randall Stadium // Camp Randall Stadium",
#     "Canvas Stadium // Canvas Stadium",
#     "CEFCU Stadium // CEFCU Stadium",
#     "Center Parc Credit Union Stadium // Center Parc Credit Union Stadium",
#     "Dana J. Dykhouse Stadium // Dana J. Dykhouse Stadium",
#     "Darrell K Royal-Texas Memorial Stadium // Darrell K Royal - Texas Memorial Stadium",
#     "David Booth Kansas Memorial Stadium // Memorial Stadium-KS",
#     "Doak S. Campbell Stadium // Doak Campbell Stadium",
#     "Dowdy-Ficklen Stadium // Dowdy Ficklen Stadium",
#     "Doyt Perry Stadium // Doyt Perry Stadium",
#     "Elliott T. Bowers Stadium // Bowers Stadium",
#     "Empower Field at Mile High Stadium // Empower Field at Mile High",
#     "Falcon Stadium // Falcon Stadium",
#     "FAU Stadium // FAU Stadium",
#     "Finley Stadium // Carter-Finley Stadium",
#     "FirstBank Stadium // FirstBank Stadium",
#     "FIU Stadium // Riccardo Silva Stadium",
#     "Goodman Stadium // Goodman Stadium",
#     "Hancock Stadium // Hancock Stadium",
#     "Houck Stadium // Houck Stadium",
#     "Huntington Bank Stadium // Huntington Bank Stadium",
#     "Jerry Richardson Stadium // Jerry Richardson Stadium",
#     "JMU - Bridgeforth Stadium // Bridgeforth Stadium",
#     "Joan C. Edwards Stadium // Joan C Edwards Stadium",
#     "Joe Aillet Stadium // Joe Aillet Stadium",
#     "Kornblau Field at S.B. Ballard Stadium // Kornblau Field at S.B. Ballard Stadium",
#     "Lavell Edwards Stadium // LaVell Edwards Stadium",
#     "Marshall - Joan C Edwards Stadium // Joan C Edwards Stadium",
#     "Martin Stadium // Gesa Field at Martin Stadium",
#     "Maverik Stadium // Merlin Olsen Field at Maverik Stadium",
#     "McGuirk Alumni Stadium // Warren McGuirk Alumni Stadium",
#     "Memorial Stadium Illinois // Memorial Stadium-IL",
#     "Memorial Stadium Indiana // Memorial Stadium-IN",
#     "Merlin Olsen Field at Maverik Stadium // Merlin Olsen Field at Maverik Stadium",
#     "M.M. Roberts Stadium // MM Roberts Stadium",
#     "NMC Memorial Stadium (Annapolis, MD) // Navy Marine Corps Memorial Stadium",
#     "Notre Dame Stadium // Notre Dame Stadium",
#     "Oklahoma Memorial Stadium // Oklahoma Memorial Stadium",
#     "Oliver C. Dawson Stadium // Oliver C Dawson Stadium",
#     "Peden Stadium // Peden Stadium",
#     "Pratt & Whitney Stadium at Rentschler Field // Pratt & Whitney Stadium at Rentschler Field",
#     "Protective Stadium // Protective Stadium",
#     "RESER STADIUM // Reser Stadium",
#     "Reser Stadium | Corvallis, OR // Reser Stadium",
#     "Richardson Stadium // Jerry Richardson Stadium",
#     "Robert K. Kraft Field at Wien Stadium // Lawrence A. Wien Stadium",
#     "Saluki Stadium // Saluki Stadium",
#     "Sanford Stadium - Georgia // Sanford Stadium",
#     "S.B. Ballard Stadium // Kornblau Field at S.B. Ballard Stadium",
#     "Skelly Field at H.A. Chapman Stadium // H.A. Chapman Stadium",
#     "Texas State - Bobcat Stadium // Bobcat Stadium - TX",
#     "University Stadium // University Stadium Albuquerque",
#     "VALLEY CHILDREN'S STADIUM // Valley Childrens Stadium",
#     "Vaught-Hemingway Stadium // Vaught-Hemingway Stadium",
#     "WALDO STADIUM // Waldo Stadium",
#     "War Memorial Stadium // War Memorial Stadium-WY",
#     "Williams-Brice Stadium // Williams-Brice Stadium",
#     "Wisconsin - Camp Randall Stadium // Camp Randall Stadium",
#     "Yager Stadium // Yager Stadium",
#     "Yulman Stadium // Yulman Stadium",
#     "Zable Stadium // Zable Stadium"
# ]

    # stadium_list = [
    #     "Rose Bowl | Pasadena, CA // Rose Bowl Stadium",
    #     "Allegacy Stadium // Allegacy Federal Credit Union Stadium",
    #     "Dowdy-Ficklen Stadium // Dowdy Ficklen Stadium",
    #     "Gerald Ford Stadium // Gerald Ford Stadium",
    #     "H.A. Chapman Stadium // H.A. Champan Stadium",
    #     "Rice Stadium // Rice Stadium-TX",
    #     "Ross-Ade Stadium (Purdue University) // Ross-Ade Stadium",
    #     "Scott Stadium // Scott Stadium",
    #     "Stanford Stadium | Stanford, CA // Stanford Stadium",
    #     "Stewart Stadium // Stewart Stadium",
    #     "University Stadium // University Stadium Albuquerque",
    #     "Veterans Memorial Stadium // Veterans Memorial Stadium - AL",
    #     "Memorial Stadium - CA // California Memorial Stadium",
    #     "Memorial Stadium - IL // Memorial Stadium-IL",
    #     "Memorial Stadium - SC // Clemson Memorial Stadium",
    #     "FAU Stadium // FAU Stadium"
    # ]

    # stadium_list = [
    #     "Bobcat Stadium // Bobcat Stadium - TX",
    #     "DakotaDome // DakotaDome",
    #     "Homer Bryce Stadium // Homer Bryce Stadium",
    #     "Mackay Stadium // Mackay Stadium",
    #     "Mackay Stadium GA // Mackay Stadium",
    #     "Priore Field at Meade Stadium // Meade Stadium",
    #     "Veterans Memorial Stadium // Veterans Memorial Stadium - AL"
    # ]

    '''
        select * 
        from tmevents 
        where source = 'EV'
        and name like '%Football%'
        and url like '%wsu%'
        and start_date >= current_date; 
    '''
    # stadium_list = [
    # "Gesa Field // Gesa Field at Martin Stadium",
    # "Husky Stadium // Husky Stadium-WA",
    # "SECU STADIUM // SECU Stadium",
    # "Rentschler Field // Pratt & Whitney Stadium at Rentschler Field",
    # "UNI-Dome // UNI Dome", # unitix
    # "Kibbie Dome // Kibbie Dome", #govandals 
    # "Stewart Stadium // Stewart Stadium", #weber.evenue 
    # "Roos Field // Roos Field"
    # ] 

    '''
    Unmapped Football

    Allegacy Stadium

    Bobcat Stadium that maps to Bobcat Stadium - MT

    Bass Concert Hall, 2350 Robert Dedman Drive, Austin, Texas

    Bass Concert Hall, 2350 Robert Dedman Dr. 

    Bobcat Stadium --> BUT TEXAS  TXSTATEBOBCATS 

    ** A bunch of volleyball 

    "Centre In The Square" KWTICKETS 

    Clarence T. C. Ching Athletics Complex --> hawaii football

    CU Boulder Volleyball

    DakotaDome ** 

    Finley Stadium ** 

    KRANZBERG ARTS CENTER ** 

    O'Shaughnessy Stadium ** 
    '''

    # stadium_list = [
    # "Centre in the Square // Centre in the Square Ontario",
    # "Clarence T. C. Ching Athletics Complex // Clarence TC Ching Athletics Complex",
    # "DakotaDome // DakotaDome",
    # "Disney on Ice at the Resch Center // Resch Center",
    # "Donald C. Bedell Performance Hall // Bedell Performance Hall",
    # "Finley Stadium // Carter-Finley Stadium",
    # "Main Stage // King Center for the Performing Arts"
    # ] 

    # stadium_list = [
    #     "Alaska Airlines Arena // Alaska Airlines Arena",
    #     "Barnhill Arena // Barnhill Arena",
    #     "Bohler Gymnasium // Bohler Gym",
    #     "Bren Events Center // Bren Events Center",
    #     "BRESLIN // Jack Breslin Student Events Center",
    #     "Crisler Center // Crisler Center",
    #     "Frost Arena // Frost Arena",
    #     "Galen Center // Galen Center",
    #     "Gregory Gym 2101 Speedway Austin, TX // Gregory Gym",
    #     "HAAS PAVILION // Haas Pavilion",
    #     "Holloway Gymnasium // Holloway Gymnasium",
    #     "Johnson Center // Johnson Center - NM",
    #     "Keen Arena // Cliff Keen Arena",
    #     "Maturi Pavilion // Maturi Pavilion",
    #     "Memorial Gym // Memorial Gym - El Paso",
    #     "Moby Arena // Moby Arena",
    #     "Pauley Pavilion presented by Wescom | Los Angeles, CA // Pauley Pavilion - UCLA",
    #     "Reed Arena // Reed Arena",
    #     "Rolle Activity Center // Rolle Activity Center",
    #     "Sanford Coyote Sports Center // Sanford Coyote Sports Center",
    #     "Shelton Gym // Shelton Gym",
    #     "Shroyer Gym // Shroyer Gym",
    #     "SimpliFi Arena at Stan Sheriff Center // Stan Sheriff Center",
    #     "Smith Fieldhouse // Smith Fieldhouse",
    #     "Stuart C. Siegel Center // Stuart C Siegel Center",
    #     "Swenson Gym // Swenson Gym",
    #     "TCU Volleyball at Schollmaier Arena // Schollmaier Arena",
    #     "United Supermarkets Arena // United Supermarkets Arena",
    #     "University Credit Union Center // University Credit Union Center",
    #     "UniWyo Sports Complex // UniWyo Sports Complex",
    #     "Valvano Arena at Reynolds Coliseum // Reynolds Coliseum",
    #     "Wayne Estes Center // Wayne Estes Center",
    #     "Woodling Gymnasium // Woodling Gymnasium",
    #     "WVU Coliseum // West Virginia University Coliseum",
    #     "XFINITY CENTER // Xfinity Center - MD",
    #     "McLeod Center // McLeod Center",
    #     "Ambrose Urbanic Field // Ambrose Urbanic Field",
    #     "Anteater Stadium // Anteater Stadium",
    #     "Buser Family Park // Buser Family Park",
    #     "Carl Lewis International Complex // Carl Lewis International Complex",
    #     "DeMartin Stadium // DeMartin Soccer Complex",
    #     "Elizabeth Lyle Robbie Stadium // Elizabeth Lyle Robbie Stadium",
    #     "Ellis Field // Ellis Field",
    #     "Garvey-Rosenthal Soccer Stadium // Garvey-Rosenthal Soccer Stadium",
    #     "Husky Soccer Stadium // Husky Soccer Stadium",
    #     "JOHN WALKER SOCCER COMPLEX // John Walker Soccer Complex",
    #     "LUDWIG FIELD // Ludwig Field",
    #     "McAlister Field - General Admission // McAlister Field",
    #     "Merlo Field // Merlo Field",
    #     "Murphey Field at Mulcahy Stadium // Mulcahy Soccer Stadium",
    #     "Neal Patterson Stadium // Neal Patterson Stadium",
    #     "Razorback Field // Razorback Field",
    #     "Spry Soccer Stadium // Spry Soccer Stadium",
    #     "UM Soccer Complex // U-M Soccer Complex",
    #     "Wallis Annenberg Stadium // Wallis Annenberg Stadium",
    #     "WMU SOCCER COMPLEX // WMU Soccer Complex",
    #     "Centre in the Square // Centre in the Square Ontario",
    #     "Clarence T. C. Ching Athletics Complex // Clarence TC Ching Athletics Complex",
    #     "DakotaDome // DakotaDome",
    #     "Disney on Ice at the Resch Center // Resch Center",
    #     "Donald C. Bedell Performance Hall // Bedell Performance Hall",
    #     "Finley Stadium // Carter-Finley Stadium", # ***** 
    #     "Main Stage // King Center for the Performing Arts"
    # ]


    # stadium_list = [
    # "Bobcat Stadium - TX // Bobcat Stadium - TX",
    # "Bobcat Stadium - MT // Bobcat Stadium - MT"
    # ] 
    # stadium_list = [
    #     "1STBANK Center // 1stBank Center",
    #     "Abessinio Court at Eleanor R. Baldwin Arena // Eleanor R Baldwin Arena",
    #     "Alpine Valley Music Theatre // Alpine Valley Music Theatre",
    #     "American Legion Memorial Stadium // American Legion Memorial Stadium",
    #     "Ann Nicole Nelson Hall // Ann Nicole Nelson Hall",
    #     "Arthur Ashe Stadium // Arthur Ashe Stadium",
    #     "Artpark Mainstage Theater // Artpark Mainstage Theater",
    #     "B Side at House of Blues Las Vegas // B Side at House of Blues Las Vegas",
    #     "BARTOW ARENA // Bartow Arena",
    #     "Bell Auditorium // Bell Auditorium",
    #     "Bellco Theatre // Bellco Theatre at Colorado Convention Center",
    #     "Bella Concert Hall - Mount Royal University // Bella Concert Hall",
    #     "Billie Jean King National Tennis Center // Billie Jean King National Tennis Center",
    #     "Bishop Arts Theatre Center // Bishop Arts Theatre Center",
    #     "Bob Carpenter Center // Bob Carpenter Center at University of Delaware",
    #     "Bob Devaney Sports Center // Bob Devaney Sports Center",
    #     "BROWN THEATER AT WORTHAM CENTER // Brown Theatre at Wortham Center",
    #     "Canton Civic Center // Canton Civic Center",
    #     "Carlson Center // Carlson Center",
    #     "Casino Nova Scotia, Halifax // Casino Nova Scotia",
    #     "Center Parc Stadium // Center Parc Credit Union Stadium",
    #     "Chicagoland Speedway // Chicagoland Speedway",
    #     "Chiles Center // Chiles Center",
    #     "Circuit of The Americas // Circuit of The Americas",
    #     "Comerica Park // Comerica Park",
    #     "Conte Forum // Conte Forum",
    #     "Cotton Bowl // Cotton Bowl Stadium",
    #     "Credit Union 1 Amphitheatre // Credit Union 1 Amphitheatre",
    #     "Cross Insurance Arena // Cross Insurance Arena",
    #     "Dacotah Bank Center // Dacotah Bank Center",
    #     "Dayton Masonic Center // Dayton Masonic Center",
    #     "Deep Cuts // Deep Cuts",
    #     "Dee Events Center // Dee Events Center",
    #     "District E at Capital One Arena // District E at Capital One Arena",
    #     "Dodger Stadium // Dodger Stadium",
    #     "DuQuoin State Fair // Duquoin State Fair",
    #     "Ellis Park Racing & Gaming // Ellis Park Racing and Gaming",
    #     "Excite Ballpark // Excite Ballpark",
    #     "Farmington Civic Center // Farmington Civic Center",
    #     "Fertitta Center // Fertitta Center",
    #     "FBC Mortgage Stadium // FBC Mortgage Stadium",
    #     "Flynn Center for the Performing Arts // Flynn Center for the Performing Arts",
    #     "Ford Community & Performing Arts Center // Ford Community Performing Arts Center",
    #     "Gallagher Bluedorn // Gallagher Bluedorn Performing Arts Center",
    #     "Gallagher-Iba Arena // Gallagher Iba Arena",
    #     "Gateway DC // Gateway DC",
    #     "GMC Stadium // GMC Stadium",
    #     "Great American Ball Park // Great American Ball Park",
    #     "HALL DES LUMIÈRES // Hall des Lumieres",
    #     "Halas Hall // Halas Hall",
    #     "Harrah's Hoosier Park Terrace Showroom // Harrah's Hoosier Park Terrace Showroom",
    #     "Harris Theater // Harris Theater",
    #     "HAYWARD FIELD // Hayward Field",
    #     "HOMER S. BROWN THEATER AT WORTHAM CENTER // Brown Theatre at Wortham Center",
    #     "Homewood Field // Homewood Field",
    #     "Hughes Stadium // Sacramento City College - Hughes Stadium",
    #     "Irvine Barclay Theatre (4242 Campus Dr., Irvine 92612) // Irvine Barclay Theatre",
    #     "James Brown Arena // James Brown Arena at Augusta Richmond Center",
    #     "Jersey Mike's Arena // Jersey Mike's Arena",
    #     "Jubilee Theater at Horseshoe Las Vegas // Horseshoe Las Vegas",
    #     "KIBBIE DOME // Kibbie Dome",
    #     "Kinnick Stadium // Kinnick Stadium",
    #     "Koka Booth Amphitheatre // Koka Booth Amphitheatre at Regency Park",
    #     "Kraushaar Auditorium // Kraushaar Auditorium",
    #     "Lake Charles Civic Ctr Rosa Hart Theatre // Rosa Hart Theatre - Lake Charles Civic Center",
    #     "Lee Park Church // Lee Park Church",
    #     "Lee's Palace // Lees Palace",
    #     "Lemonade Park // Lemonade Park",
    #     "Lindner Family Tennis Center // Grandstand Court at Lindner Family Tennis Center",
    #     "Lindner Family Tennis Center // Lindner Family Tennis Center",
    #     "Louis Armstrong Stadium // Louis Armstrong Stadium",
    #     "Luxor Theater // Luxor Hotel and Casino",
    #     "Martha's Vineyard Performing Arts Center // Marthas Vineyard Performing Arts Center",
    #     "Martin Luther King Jr. Park at Manhattan Square // Martin Luther King Jr. Memorial Park at Manhattan Square",
    #     "McCamish Pavilion // McCamish Pavilion",
    #     "McFarlin Auditorium // McFarlin Auditorium",
    #     "McKale Center // McKale Center",
    #     "McKelligon Canyon Theatre // McKelligon Canyon Theatre",
    #     "Merlin Olsen Field // Merlin Olsen Field at Maverik Stadium",
    #     "Michelob ULTRA Arena // Michelob ULTRA Arena at Mandalay Bay Resort and Casino",
    #     "Molson Canadian Centre at Casino New/Nouveau Brunswick // Molson Canadian Centre at Casino NB",
    #     "Mullins Center // Mullins Center",
    #     "Mosaic Stadium // Mosaic Stadium at Taylor Field",
    #     "Mt. Horeb Church // Mt Horeb United Methodist Church",
    #     "Mullins Center // Mullins Center",
    #     "Nashville Superspeedway // Nashville Superspeedway",
    #     "New Hampshire Motor Speedway // New Hampshire Motor Speedway",
    #     "New World Brewery // New World Brewery",
    #     "Nutrien Western Event Centre // Nutrien Western Event Centre",
    #     "OceanFirst Bank Center // OceanFirst Bank Center",
    #     "OBrate Stadium // O'Brate Stadium",
    #     "Owensboro Convention Center // Owensboro Convention Center",
    #     "Palmetto Pointe Church // Palmetto Pointe Church",
    #     "Paradise Performing Arts Center // Paradise Performing Arts Center",
    #     "Parkview Field // Parkview Field",
    #     "Promenade Park Stage // Promenade Park Stage",
    #     "Radians Amphitheater // Radians Amphitheater",
    #     "Rafferty Stadium // Rafferty Stadium",
    #     "Ray Fisher Stadium // Wilpon Baseball and Softball Complex - Ray Fisher Stadium",
    #     "Renaissance Hotel // Renaissance Palm Springs Hotel",
    #     "Ricardo Montalban Theatre // Ricardo Montalban Theatre",
    #     "Rickshaw Stop // Rickshaw Stop",
    #     "Riverside Revival // Riverside Revival Nashville",
    #     "Roos Field // Roos Field",
    #     "Saenger Theater Hattiesburg // Hattiesburg Saenger Theater",
    #     "Salle Richard-Sauvageau // Salle Richard-Sauvageau",
    #     "Savage Arena // Savage Arena",
    #     "Schoenberg Hall // Schoenberg Hall - UCLA",
    #     "SECU STADIUM // SECU Stadium",
    #     "Seneca Niagara Resort & Casino Outdoor Venue // Seneca Niagara Casino - Outdoor Venue",
    #     "Shaughnessy Golf and Country Club // Shaughnessy Golf Club",
    #     "Sleeman Centre // Sleeman Centre",
    #     "South Point Arena at South Point Hotel Casino and Spa // South Point Hotel and Casino",
    #     "Stewart Stadium // Stewart Stadium",
    #     "Target Field // Target Field",
    #     "TCO Stadium // TCO Stadium",
    #     "The Atlantis // The Atlantis",
    #     "The Baby G // The Baby G",
    #     "The Bellwether // The Bellwether",
    #     "The Big Top // The Big Top",
    #     "The Canyon Agoura Hills // The Canyon Agoura Hills",
    #     "The Drake Hotel // Drake Hotel Toronto",
    #     "The Fillmore Miami Beach at Jackie Gleason Theater // Fillmore Miami Beach at Gleason Theater",
    #     "The Garrison // The Garrison",
    #     "The Hanover Theatre // Hanover Theatre",
    #     "The Palestra // Palestra",
    #     "The Phoenix Concert Theatre // Phoenix Concert Theatre",
    #     "The Pool at Foxwoods Resort Casino // The Pool at Foxwoods Resort Casino",
    #     "The Rino // The Rino",
    #     "The Wanderers Grounds // Wanderers Grounds",
    #     "Thomas and Mack Center UNLV Basketball // Thomas and Mack Center",
    #     "Tinker Field // Tinker Field",
    #     "Toscano Family Ice Forum // Toscano Family Ice Forum",
    #     "TRI-CITY SPEEDWAY // Tri City Speedway",
    #     "Truist Field // Truist Field Charlotte",
    #     "Vancouver Playhouse // Vancouver Playhouse",
    #     "Venetian Theatre at the Venetian Resort // Venetian Theatre at the Venetian Las Vegas",
    #     "Vernon Downs // Vernon Downs Raceway",
    #     "Villanova Stadium // Villanova Stadium",
    #     "We-Ko-Pa Casino Resort // We-Ko-Pa Casino Resort",
    #     "Welcome Stadium // Welcome Stadium",
    #     "Westchester County Center // Westchester County Center",
    #     "Windham Mountain // Windham Mountain",
    #     "zMAX Dragway // zMAX Dragway"
    # ]
    stadium_list = [
        "3M Arena at Mariucci // 3M Arena at Mariucci",
        "CEFCU Arena // CEFCU Arena",
        "Centre in the Square // Centre in the Square Ontario",
        "Cofrin Family Hall // Weidner Center for the Performing Arts",
        "CU Events Center // CU Events Center",
        "FIELDHOUSE // Fitzgerald Field House",
        "Finley Stadium // Finley Stadium",
        "Gate City Bank Field // Fargodome",
        "George Gervin GameAbove Center // Gervin GameAbove Center",
        "Gesa Field // Gesa Field at Martin Stadium",
        "Hibner Field // Barbara Hibner Soccer Stadium",
        "Horejsi Family Volleyball Arena // Horejsi Family Athletics Center",
        "Huff Hall // University of Illinois - Huff Hall",
        "Husky Stadium // Husky Stadium-WA",
        "Kibbie Dome // Kibbie Dome",
        "LAWSON ARENA // Lawson Ice Arena",
        "Mackay Stadium // Mackay Stadium",
        "Magness Arena // Magness Arena",
        "Memorial Stadium - IL // Memorial Stadium-IL",
        "Memorial Stadium - SC // Clemson Memorial Stadium",
        "MUNN ARENA // Munn Ice Arena",
        "O'Shaughnessy Stadium // O'Shaughnessy Stadium",
        "Rentschler Field // Pratt & Whitney Stadium at Rentschler Field",
        "Ridder Arena // Ridder Arena",
        "SAVE-ON-FOODS MEMORIAL CENTRE // Save on Foods Memorial Centre",
        "Schneider Arena // Schneider Arena",
        "Slater Family Ice Arena // Slater Family Ice Arena",
        "Steve \"Coach\" Cady Arena // Goggin Ice Center", #** 
        "UNITED SUPERMARKETS ARENA // United Supermarkets Arena",
        "UC Davis Health Stadium // Aggie Stadium",
        "UW Field House // Wisconsin Field House",
        "Xtream Arena Hockey // Xtream Arena"
    ]

    stadium_list = [
        "Yost Ice Arena // Yost Arena",
        "Bright-Landry Hockey Center // Bright-Landry Hockey Center",
        "Harvard Stadium // Harvard Stadium",
        "Clune Arena // Clune Arena", #** wrong mapping 
        "Prospera Place // Prospera Place",
        "COMPTON FAMILY ICE ARENA // Compton Family Ice Arena"]

    stadium_list = [
        "Agganis Arena // Agganis Arena",
        "AMSOIL Arena // AMSOIL Arena",
        "Baxter Arena // Baxter Arena",
        "Blue Cross Arena // Blue Cross Arena",
        "CAA Centre // CAA Arena",
        "Clare Drake Arena // Clare Drake Arena",
        "Clearview Arena // Clearview Arena",
        "Covelli Centre // Covelli Centre - Youngstown",
        "Cross Insurance Arena // Cross Insurance Arena",
        "Cross Insurance Arena (Formerly Cumberland County Civic Center) // Cross Insurance Arena",
        "Denny Sanford PREMIER Center // Denny Sanford PREMIER Center",
        "Ed Robson Arena // Ed Robson Arena",
        "Grossinger Motors Arena // Grossinger Motors Arena",
        "HARBORCENTER // HarborCenter",
        "LAWSON ARENA // Lawson Ice Arena",
        "Liberty First Credit Union Arena // Liberty First Credit Union Arena",
        "Madison Square Garden // Madison Square Garden",
        "Magness Arena // Magness Arena",
        "Martire Family Arena // Martire Family Arena",
        "Mayo Clinic Health System Event Center // Mayo Clinic Health System Event Center",
        "Mullett Arena // Mullett Arena",
        "Mullins Center // Mullins Center",
        "Ohio State University Ice Rink // Ohio State Ice Rink",
        "Pegula Ice Arena // Pegula Ice Arena",
        "Peoria Civic Center // Peoria Civic Center",
        "Ralph Engelstad Arena // Ralph Engelstad Arena - Grand Forks",
        "Ridder Arena // Ridder Arena",
        "Saint Thomas Ice Arena // Saint Thomas Ice Arena",
        "Scheels Arena // Scheels Arena",
        "Schottenstein Center // Value City Arena at Schottenstein Center",
        "Scotiabank Arena // Scotiabank Arena",
        "Slater Family Ice Arena // Slater Family Ice Arena",
        "TATE RINK // Tate Rink",
        "The Sanford Center // The Sanford Center",
        "Toscano Family Ice Forum // Toscano Family Ice Forum",
        "Total Mortgage Arena // Total Mortgage Arena",
        "Tucson Arena // Tucson Arena",
        "Xcel Energy Center // Xcel Energy Center",
        "Yost Ice Arena // Yost Arena"
    ]

    stadium_list = [
        "Bass Concert Hall, 2350 Robert Dedman Dr // Bass Concert Hall",
        "Bass Concert Hall // Bass Concert Hall",
        "Bass Concert Hall 2350 Robert Dedman Dr. // Bass Concert Hall",
        "Bud Walton Arena // Bud Walton Arena",
        "Centre in the Square // Centre in the Square Ontario",
        "Centre In The Square // Centre in the Square Ontario",
        "Clune Arena // Clune Arena",
        "Concert Hall-BYU Music Building // BYU School of Music - Recital Hall",
        "Denver Coliseum // Denver Coliseum",
        "First Interstate Center for the Arts // First Interstate Center for the Arts",
        "Ice Arena // Ice Arena at The Monument",
        "ICCU Arena // Idaho Central Credit Union Arena",
        "Jensen Concert Hall - Reserved Seating // Jensen Grand Concert Hall",
        "Jersey Mike's Arena // Jersey Mike's Arena",
        "Kohl Center - Hockey // Kohl Center",
        "Kohl Center - MBB // Kohl Center",
        "Mainstage Theatre - West Campus // West Campus Mainstage Theater - BYU Arts",
        "McLeod Theater // McLeod Theater",
        "Memorial Gym // Vanderbilt Memorial Gym",
        "McKale Center // McKale Center",
        "National Western Events Center // National Western Complex",
        "Resch Center Gamblers Hockey // Resch Center",
        "Steve \"Coach\" Cady Arena // Goggin Ice Center",
        "Studio Theatre // King Center for the Performing Arts",
        "THE SHELDON // The Sheldon Theatre - MN",
        "UNI-Dome // UNI Dome",
        "Wait Chapel // Wait Chapel",
        "Wells Fargo Center - Kirk Franklin // Wells Fargo Center-PA",
        "Wells Fargo Center - Mana // Wells Fargo Center-PA",
        "Wells Fargo Center - Joji // Wells Fargo Center-PA",
        "WESTPORT PLAYHOUSE // The Playhouse at Westport Plaza",
        "Wheelwright Auditorium // Wheelwright Auditorium",
        "Williams Arena // Williams Arena"
    ]

    stadium_list = ["Cullen Performance Hall // Cullen Performance Hall"]

    stadium_list = [
        "Bob Carpenter Center // Bob Carpenter Center at University of Delaware",
        "BRESLIN // Jack Breslin Student Events Center",
        "CHARLES KOCH ARENA-WOMEN'S BASKETBALL // Charles Koch Arena",
        "CHRISTL ARENA // Christl Arena",
        "Crisler Center // Crisler Center",
        "Delta Center // Delta Center",
        "FIFTH THIRD ARENA // Fifth Third Arena at Shoemaker Center",
        "Halton Arena // Halton Arena",
        "KSU Convocation Center<br>590 Cobb Ave NW<br>Kennesaw, GA 30114 // KSU Convocation Center",
        "Mitchell Center // The Mitchell Center",
        "Moby Arena // Moby Arena",
        "NEVILLE ARENA // Neville Arena",
        "PNC Arena // PNC Arena",
        "Purcell Pavilion // Purcell Pavilion at the Joyce Center",
        "Save Mart Center // Save Mart Center",
        "Williams Arena // Williams Arena",
        "Wintrust Arena (200 E. Cermak Rd.) // Wintrust Arena",
        "Wolstein Center // Wolstein Center at CSU",
        "WVU Coliseum // West Virginia University Coliseum",
        "Chiles Center // Chiles Center",
        "Hagan Arena // Michael J Hagan Arena",
        "Convocation Center // Ohio Convocation Center",
        "DICKIES ARENA // Dickies Arena",
        "Halton Arena // Halton Arena",
        "McCarthey Athletic Center // McCarthey Athletic Center",
        "Mackey Arena // Mackey Arena",
        "Humphrey Coliseum // Humphrey Coliseum",
        "Bud Walton Arena // Bud Walton Arena",
        "Gampel Pavilion // Gampel Pavilion",
        "Bartow Arena // Bartow Arena",
        "Strahan Arena at the University Events Center // Strahan Arena at the University Events Center",
        "Reese Court // Reese Court",
        "Gallagher-Iba Arena // Gallagher Iba Arena",
        "FERRELL CENTER // Ferrell Center",
        "Millett Hall // Millett Hall",
        "Trojan Arena // Trojan Arena",
        "Welsh Ryan Arena // Welsh Ryan Arena",
        "McCamish Pavilion // McCamish Pavilion",
        "HTC Center // HTC Center",
        "Conte Forum // Conte Forum",
        "Alex G Spanos Stadium // Alex G Spanos Center",
        "Clune Arena // Clune Arena",
        "Beasley Coliseum // Beasley Coliseum",
        "Cameron Indoor Stadium // Cameron Indoor Stadium",
        "T-Mobile Center // T-Mobile Center",
        "Jersey Mike's Arena // Jersey Mike's Arena",
        "ALLEN FIELDHOUSE // Allen Fieldhouse",
        "CHRISTL ARENA // Christl Arena",
        "John Paul Jones Arena // John Paul Jones Arena",
        "Lloyd Noble Center // Lloyd Noble Center",
        "Dee Glen Smith Spectrum // Dee Glen Smith Spectrum",
        "Moody Center ATX // Moody Center",
        "Moody Coliseum // Moody Coliseum",
        "NEVILLE ARENA // Neville Arena",
        "Carver Hawkeye Arena // Carver-Hawkeye Arena"
    ]


    for stadium in stadium_list:
        venue = stadium.split(" // ")
        ev_venue = "{}".format(venue[0]).strip()
        skybox_venue = "{}".format(venue[1]).strip()
    
        add_venue_to_db(ev_venue, skybox_venue, 'EV')

add_venue_to_db_v2() 
# add_venue_to_db('FAU Stadium','FAU Stadium','EV')