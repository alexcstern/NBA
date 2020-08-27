# Alex Stern
# acs4wq@virginia.edu

# SCRAPE HISTORICAL FANDUEL DATA
# ***current set-up would scrape all fanduel data from the bubble restart***

# import packages
import requests
from bs4 import BeautifulSoup
import pandas as pd
from lxml import html
from lxml.etree import tostring


# earliest year you want to scrape from
YEAR_MIN = 2020
# latest year you want to scrape from
YEAR_MAX = 2020
# earliest month you want to scrape from
MONTH_MIN = 7
# latest month you want to scrape from
MONTH_MAX = 8
# earliest day in the month you want to scrape from
DAY_MIN = 1
# last day in the month you want to scrape from
DAY_MAX = 31

# define letters of the alphabet
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
 
# generate empty dataframe with appropriate columns
df = pd.DataFrame(columns=['name', 'pos',
                           'first_name', 'last_name',
                           'fd', 'price', 'team',
                           'opp', 'pts', 'rbs',
                           'ast', 'sts',
                           'tos', 'treys','fgp', 
                           'fga','ftp', 'fta',
                           'blk','mins', 'game_date']) 

# iterate through specified date ranges
for y in range(YEAR_MIN, YEAR_MAX+1): 
    for m in range(MONTH_MIN, MONTH_MAX+1):
        for d in range(DAY_MIN, DAY_MAX+1):
            if y==2020 and m==8 and d==15: # value error thrown when scraping 8/15/20
                continue 
            # print(str(y)+str(m)+str(d))
            page = requests.get('http://rotoguru1.com/cgi-bin/hyday.pl?game=fd&mon='+
                                str(m)+'&day='+str(d)+'&year='+str(y)) # request
            soup = BeautifulSoup(page.content, 'html.parser') # define HTML parser        
            tree = html.fromstring(page.content) # pull content 
            pos = [] # holds player positions
            name = [] # holds player names
            first_name = [] # player first name 
            last_name = [] # player last name
            fd = [] # fanduel points played earned
            price = [] # price of player
            team = [] # player's team
            opp = [] # opponent team
            pts = [] # player points
            rbs = [] # player rebounds 
            ast = [] # player assists
            sts = [] # player steals
            tos = [] # player turnovers 
            treys = [] # player 3s
            fgp = [] # player fg %
            fga = [] # player field goals attempted
            ftp = [] # player ft %
            fta = [] # player free throws attempted
            blk = [] # player blocks
            mins = [] # player min
            
            all_html = tostring(tree.findall('.//tr')[0])
            
            stop = 0 # instantiate stop count
            for tr in soup.find_all('tr')[10:]: 
                if stop > 5: # break loop if too many lines are un-scrape-able (usually happens when no NBA games were played that day)
                    break 
                
                tds = tr.find_all('td') # list of lines containing player stats/information
                 
                if len(tds) > 2: # check if line actually contains useful information 
                    pos_long_string = str(tds[0]) # position substring
                    pos.append(pos_long_string[pos_long_string.find('<td>')+4:pos_long_string.find('</td>')])
                    name_long_string = str(tds[1]) # name substring 
                    name_string = name_long_string[name_long_string.find('nk">')+4:name_long_string.find('</a>')]
                    comma_index = name_string.find(',') # find comma
                    last = name_string[:comma_index] # last name
                    first = name_string[comma_index+2:] # first name
                    first_name.append(first) # append first name
                    last_name.append(last) # append last name
                    name.append(str(first + " " + last)) # generate full name
                    fd_long_string = str(tds[2]) # fanduel points 
                    fd.append(float(fd_long_string[fd_long_string.find('ter">')+5:fd_long_string.find('</td>')])) # player FanDuel points 
                    price_long_string = str(tds[3]) # line with price in it
                    price_short_string = price_long_string[price_long_string.find('ght">')+6:price_long_string.find('</td>')] # player FanDuel price
                    price.append(int((price_short_string[:price_short_string.find(',')] + price_short_string[price_short_string.find(',')+1:]))) # remove comma and convert to int type     
                    team_long_string = str(tds[4]) # line with team name
                    team.append(team_long_string[team_long_string.find('ter">')+5:team_long_string.find('</td>')]) # get team name
                    opp_long_string = str(tds[5]) # line with opponent team name
                    at_index = opp_long_string.find('@ ') # @ will be present if game is away
                    if at_index < 0: # game is home
                        opp.append(opp_long_string[opp_long_string.find('v ')+2:opp_long_string.find('</td>')]) # find opponent for home game
                    else:
                        opp.append(opp_long_string[at_index+2:opp_long_string.find('</td>')]) # find opponent for away game
                    min_long_string = str(tds[7]) # line with player minutes
                    colon_index = min_long_string.find(':') # colon only exists if player played > 0 minutes
                    if colon_index >= 0: # player played > 0 minutes
                        min_short_string = min_long_string[min_long_string.find('ght">')+5:min_long_string.find('</td')] # shorten string
                        colon_index = min_short_string.find(':') # find colon seperating minutes and seconds
                        minutes = float(min_short_string[:colon_index]) # get minutes
                        seconds = float(min_short_string[colon_index+1:]) # get seconds 
                        mins.append(minutes + (round(seconds/60, 2))) # convert to float for minutes
                    else: 
                        mins.append(0.0) # zero minutes played
                    stats_long_string = str(tds[8]) # line with player box stats
                    stats_long_string = stats_long_string[stats_long_string.find('<td')+20:stats_long_string.find('</td')]
                    pt_index = stats_long_string.find('pt') # 
                    if pt_index >= 0: # one or more points 
                        pts.append(int(stats_long_string[:pt_index])) # get player points
                    else:
                        pts.append(0)  # player scored zero points
                    rb_index = stats_long_string.find('rb')
                    if rb_index >= 0: # one or more rebounds
                        rbs.append(int(str(stats_long_string[rb_index-2:rb_index]).strip(" "))) # get player rebounds
                    else:
                        rbs.append(0) # player had zero rebounds
                    as_index = stats_long_string.find('as')
                    if as_index >= 0: # one or more assists
                        ast.append(int(str(stats_long_string[as_index-2:as_index]).strip(" "))) # get player assists
                    else:
                        ast.append(0) # player had zero assists
                    st_index = stats_long_string.find('st')
                    if st_index >= 0: # one or more steals
                        sts.append(int(str(stats_long_string[st_index-2:st_index]).strip(" "))) # get player steals
                    else:
                        sts.append(0) # player had zero steals
                    to_index = stats_long_string.find('to')
                    if to_index >= 0: # one or more turnovers
                        tos.append(int(str(stats_long_string[to_index-2:to_index]).strip(" "))) # get player turnovers
                    else:
                        tos.append(0) # player had zero turnovers
                    bl_index = stats_long_string.find('bl')
                    if bl_index >= 0: # one or more blocks
                        blk.append(int(str(stats_long_string[bl_index-2:bl_index]).strip(" "))) # get player blocks
                    else:
                        blk.append(0) # player had zero blocks
                    trey_index = stats_long_string.find('tre')
                    if trey_index >= 0: # one or more 3s were made
                        treys.append(int(str(stats_long_string[trey_index-2:trey_index]).strip(" "))) # get player 3s
                    else:
                        treys.append(0) # player had zero 3s
                    fg_index = stats_long_string.find('fg')
                    if fg_index >= 0: # one or more FGs attempted
                        full_fg = str(stats_long_string[fg_index-5:fg_index]) 
                        for letter in ALPHABET: 
                            full_fg = full_fg.replace(letter, '') 
                        full_fg = full_fg.strip(" ")
                        dash = full_fg.find('-')
                        fgm_i = float(full_fg[:dash])
                        fga_i = int(full_fg[dash+1:])
                        fga.append(fga_i)
                        fgp.append(round(fgm_i/fga_i, 4))
                    else:
                        fga.append(0)
                        fgp.append(0.0)
                    ft_index = stats_long_string.find('ft')
                    if ft_index >= 0: # one or more FTs attempted
                        full_ft = str(stats_long_string[ft_index-5:ft_index])
                        for letter in ALPHABET: 
                            full_ft = full_ft.replace(letter, '') 
                        full_ft = full_ft.strip(" ")
                        dash = full_ft.find('-')
                        ftm_i = float(full_ft[:dash])
                        fta_i = int(full_ft[dash+1:])  
                        fta.append(fta_i)
                        ftp.append(round(ftm_i/fta_i, 4))
                    else:
                        fta.append(0)
                        ftp.append(0.0)
                else: 
                    stop += 1 # count un-useable lines
            
            if len(name) > 0: # if data for day is non-empty 
                for i in range(len(name)): # create game_date column
                    m_i = str(m)
                    if len(m_i) < 2: # add zero for single digit month
                        m_i = '0' + m_i
                    d_i = str(d)
                    if len(d_i) < 2: # add zero for single digit day
                        d_i = '0' + d_i
                # game date in format: YYYYMMDD (helps for using < and > when filtering)
                game_date = [int(str(str(y)+m_i+d_i)) for i in range(len(name))]
                # construct data frame with data from day d
                daily_df = pd.DataFrame({'name':name, 'pos':pos,
                                     'first_name':first_name, 'last_name':last_name,
                                     'fd':fd, 'price':price, 'team':team,
                                     'opp':opp, 'pts':pts, 'rbs':rbs,
                                     'ast':ast, 'sts':sts,
                                     'tos':tos, 'treys':treys,
                                     'fgp':fgp, 'fga':fga,
                                     'ftp':ftp, 'fta':fta,
                                     'blk':blk,
                                     'mins':mins, 'game_date':game_date})
                df = pd.concat([df, daily_df]) # concatenate with parent dataframe
            
# write dataframe to current directory 
df.to_csv('my_fanduel_df.csv', index=False) 



















