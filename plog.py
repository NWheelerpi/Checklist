import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from geopy.distance import great_circle
import airportsdata
#import googlemaps
#gmaps = googlemaps.Client(key=st.secrets['gmapskey'])
#import streamlit_nested_layout

# Create dictionary of airports
airports_icao=airportsdata.load('ICAO')
airports_iata=airportsdata.load('IATA')


###############################################################################################################################################
############################################# WIND/TRACK CALCULATOR ###########################################################################
###############################################################################################################################################
# Calculate heading,groundspeed,time from track+distance+wind
def Wind_Drift(T,Vw,Wd,I):
    track=st.session_state.Trklist[I]
    lg_dist=st.session_state.Distances[I]
    # Check valid data
    if track==None or np.isnan(track):
        return [st.session_state.waypoint_name[I],st.session_state.waypoint_coordinate[I],None,None,None,0,0,0],0

    # Calculate drift correction
    corr_rad = np.arcsin(Vw*np.sin((180-Wd+track)*2*np.pi/360)/T)
    corr=corr_rad*360/(2*np.pi)
    gs=(Vw**2+T**2-2*(Vw)*(T)*np.cos((Wd-track-corr)*2*np.pi/360))**0.5
    
    # Calculate uncorrected drift 
    gs_d_uc=(Vw**2+T**2-2*(Vw)*(T)*np.cos((Wd-track)*2*np.pi/360))**0.5
    drift_uc_rad = np.arcsin(Vw*np.sin((Wd-track)*2*np.pi/360)/gs_d_uc)
    drift_uc=drift_uc_rad*360/(2*np.pi)
    
    # New magnetic heading
    mag_hdg = track+corr+st.session_state.var_val
    while mag_hdg<0:
        mag_hdg+=360
    while mag_hdg>360:
        mag_hdg-=360
    
    # Uncorrected drift heading (psuedo)
    drift_hdg = track-drift_uc
    
    # String of uncorrected drift (L or R)
    if round(drift_uc,1)==0:
        drfuc='0'
    elif drift_uc <0:
        drfuc=str(abs(round(drift_uc,1)))+' R'
    else:
        drfuc=str(abs(round(drift_uc,1)))+' L'

    time=lg_dist/gs*60

    fuel_litres=st.session_state.fburn/60 * time
    fuel_kg=st.session_state.fburn/60 * time * st.session_state.spg
    if not st.session_state.fuel_output:
        fuel=fuel_litres
    else:
        fuel=fuel_kg
    return [st.session_state.waypoint_name[I],st.session_state.waypoint_coordinate[I],int(track),round(mag_hdg,1),round(gs,1),round(lg_dist,1),round(time,1),np.ceil(fuel)],fuel_litres

# Function that creates track+Distance inputs and calculates next coordinate + plots rhumb line points 
def Track_input(I,nmb):

    # Find default track/distance if previously entered
    # If valid data inputted already, use that as default values
    if len(st.session_state['Inputted Vertices'][I+1])!=0 and st.session_state['Inputted Vertices'][I+1][0]!=None:
        default_Track=round(st.session_state['Inputted Vertices'][I+1][3],2)
        default_Dist=round(st.session_state['Inputted Vertices'][I+1][4],2)
    else:
        default_Track=0.0
        default_Dist=0.0
    # Function that calulates final coordinates each leg
    with outer_cols2[2]:
        # Create Track slider 
        inner_cols2=st.columns(2)
        with inner_cols2[0]:
            track = st.number_input('Track '+str(I+1)+' ($\degree$T):',min_value=0.,value=default_Track,max_value=360.,key=I) #,on_change=set_track_true()
        with inner_cols2[1]:
            Dist = st.number_input('Distance (nm):',min_value=0.,value=default_Dist,key=str(I)+'b') #,on_change=set_track_true()
        st.session_state.Trklist[I]=track
        st.session_state.Distances[I]=Dist

        if track!=default_Track or Dist!=default_Dist:
            set_track_true()
        # Calculate new final coordinate
        if st.session_state.SPLats[-1]!=None:
            Init_lat=st.session_state.SPLats[-1]
            Init_long=st.session_state.SPLongs[-1]
        else:
            st.session_state.Trklist[I]=None
            st.session_state.Distances[I]=None
            st.session_state.Vertices.append([None,None,None])
            st.session_state.waypoint_coordinate.append(None)
            st.session_state.waypoint_name.append(None)
            return
        
        # Check nonzero distance:
        string_address='WP'+str(I+1)
        if Dist==0.0:
            for i in st.session_state.Vertices:
                if i[0]==round(st.session_state.SPLats[-1],4) and i[1]==round(st.session_state.SPLongs[-1],4):
                    string_address=i[2]
        Dfrac2=Dist/nmb
        fact=1

        while Dfrac2<0.01 and Dfrac2!=0:
            Dfrac2*=10
            fact*=10
        if nmb/fact<1:
            Dfrac2=Dist
        rhumb_points2=[[Init_lat,Init_long]]
        lati2=Init_lat
        longi2=Init_long
        for i in range(int(np.max([nmb/fact,1]))): #int(np.max([nmb/fact,1]))
            a,b=dest_point(Dfrac2,lati2,longi2,track*2*np.pi/360)
            rhumb_points2.append([a,b])
            lati2=a
            longi2=b
        rhumb_longs2=[point[1] for point in rhumb_points2]
        rhumb_lats2=[point[0] for point in rhumb_points2]
        st.session_state.SPLats=st.session_state.SPLats+rhumb_lats2
        st.session_state.SPLongs=st.session_state.SPLongs+rhumb_longs2
       

        for i in st.session_state['Inputted Vertices']:
            if len(i)!=0:
                if i[0]==round(lati2,4) and i[1]==round(longi2,4):
                    string_address=i[2]

        if st.session_state['track_change']:
                st.session_state['Inputted Vertices'][I+1]=[round(lati2,4),round(longi2,4),string_address,round(track,2),round(Dist,2)]
                st.session_state['track_change']=False
        

        st.session_state.Vertices.append([round(lati2,4),round(longi2,4),string_address])
        latitudestring=str(round(lati2,4))
        longitudestring=str(round(longi2,4))
        st.session_state.waypoint_coordinate.append(latitudestring+' '+longitudestring)
        st.session_state.waypoint_name.append(string_address)
        #st.markdown(st.session_state.SPLats[-1])
        #st.markdown(st.session_state.SPLongs[-1])
        legno=['Leg '+str(I+1) for i in range(len(rhumb_longs2))]
        for i in legno:
            st.session_state.LegNo.append(i)
    return 

def conv_coord2dec(deg,min,sec,nsew):
    dec=np.abs(deg)+(min/60)+(sec/3600)
    if nsew=='S' or nsew=='W':
        f=-1
    else:
        f=1
    return dec*f

# Convert decimal to lat+long (degrees)
def conv_dec2coord(dc):
    if dc==None:
        return None,None,None
    deci=round(abs(dc),9)
    degr=abs(int(deci))
    mint=abs(int(deci*60)%60)
    seco=round(abs((deci*60*60)%60%60),3)
    if dc<0:
        facto=-1
    else:
        facto=1

    if degr!=0:
        degr=degr*facto
    elif mint!=0:
        mint=mint*facto
    elif seco!=0:
        seco=seco*facto
    return degr,mint,seco

# Convert leading degree to standard format (2 for Lat, 3 for Long)
def deg_length(lt,ln,base):
    if lt==None:
        return '',''
    if base=='D':
        ltfac=2
        lnfac=3
    else:
        ltfac=2
        lnfac=2
        
    #ltstring=str(abs(lt))
    #lnstring=str(abs(ln))
    if base!='S': 
        ltstring=str(abs(lt))
        lnstring=str(abs(ln))  
        while len(ltstring)<ltfac:
            ltstring='0'+ltstring
        while len(lnstring)<lnfac:
            lnstring='0'+lnstring
    else:
        ltstring=str(round(abs(lt),2))
        lnstring=str(round(abs(ln),2))
        ltstringsplit=ltstring.split('.')
        lnstringsplit=lnstring.split('.')
        if ltstringsplit[1]=='0':
            ltstringsplit[1]=''
        else:
            ltstringsplit[1]='.'+ltstringsplit[1]
        if lnstringsplit[1]=='0':
            lnstringsplit[1]=''
        else:
            lnstringsplit[1]='.'+lnstringsplit[1]
            
        while len(ltstringsplit[0])<ltfac:
            ltstringsplit[0]='0'+ltstringsplit[0]
        while len(lnstringsplit[0])<lnfac:
            lnstringsplit[0]='0'+lnstringsplit[0]
        ltstring=ltstringsplit[0]+ltstringsplit[1]
        lnstring=lnstringsplit[0]+lnstringsplit[1]
        
    return ltstring,lnstring

# Function that converts text to a float
def string_to_float(text_string):
    try:
        output_float=float(text_string)
    except:
        output_float=None
    
    return output_float

# Functions that increment and decrement number of legs
def add_waypoint():
    st.session_state['numtrks'] += 1
    st.session_state['Inputted Vertices'].append([])
def remove_waypoint():
    if st.session_state['numtrks']!=1:
        st.session_state['numtrks'] -= 1
        st.session_state['Inputted Vertices']=st.session_state['Inputted Vertices'][:-1]

# Functions that determine if default value needs updating
def set_coord_true():
    st.session_state['coord_change']=True
def set_address_true():
    st.session_state['address_change']=True
def set_track_true():
    st.session_state['track_change']=True
# Function that takes initial coordinates and finds next coordinates 'dist' away on track 'trk'
def dest_point(dist,phi1deg,lamb1deg,trk):
    if phi1deg==None:
        return None, None
    phi1=phi1deg*2*np.pi/360
    lamb1=lamb1deg*2*np.pi/360
    R=360*60/(2*np.pi)  # Earth radius
    TRK=trk
    #st.markdown(lamb1*360/2/np.pi)
    #st.markdown(phi1*360/2/np.pi)
    if dist!=0:
        delta=dist/R
        phi2=phi1+delta*np.cos(TRK)
        if trk==np.pi/2 or trk==3*np.pi/2:
            Q=np.cos(phi1)
            s=True
        else:
            delpsi=np.log(np.tan(np.pi/4 + phi2/2)/np.tan(np.pi/4 + phi1/2))
            Q=delta*np.cos(TRK)/delpsi
            s=False
        lamb2=lamb1+delta*np.sin(TRK)/Q
    else:
        phi2=phi1
        lamb2=lamb1
    #st.markdown(Q)
    #st.markdown(lamb1deg*2*np.pi)
    # Check size of result
    if abs(phi2) < 1e-6:
        phi2=0
    if abs(lamb2) <1e-6:
        lamb2=0
    #st.markdown('$ \delta $ {} $\phi_2$ {} Q {} {} Distance {}'.format(delta,phi2,Q,s,dist))
    return phi2*360/2/np.pi,lamb2*360/2/np.pi

# Function that creates an address text input and converts into lat+lon coordinates
def address_2_coord(ID,def_address=None):
    if ID=='initial':
        def_address='EGBG'
    address=st.text_input('Address',value=def_address,key=str(ID)+'Address') #,on_change=set_address_true()
    # Check if address inputted previously
    for i in st.session_state['Inputted Vertices']:
        if len(i)!=0:
            if address==i[2]:
                lat_output=i[0]
                lon_output=i[1]
                return lat_output,lon_output,address
    
    if address!='' and address!=None:
        if address.upper() in airports_icao : # Try airports data
            latcoord=airports_icao[address.upper()]['lat']
            loncoord=airports_icao[address.upper()]['lon']
            address=address.upper()
            
        elif address.capitalize() in airports_icao:
            latcoord=airports_icao[address.capitalize()]['lat']
            loncoord=airports_icao[address.capitalize()]['lon']
        elif address.upper() in airports_iata : # Try airports data
            latcoord=airports_iata[address.upper()]['lat']
            loncoord=airports_iata[address.upper()]['lon']
            address=address.upper()+' '+airports_iata[address.upper()]['icao']
        else:   # Try Google maps
            #### Google maps code ####
            #geocode_result = gmaps.geocode(address)
            #if len(geocode_result)!=0: 
                #latcoord=geocode_result[0]['geometry']['location']['lat']
                #loncoord=geocode_result[0]['geometry']['location']['lng']
            #else:
            latcoord=None
            loncoord=None
    else:
        geocode_result=[]
        latcoord=None
        loncoord=None

    if latcoord!=None:
        lat_output=round(latcoord,4)
        lon_output=round(loncoord,4)
    else:
        lat_output=None
        lon_output=None

    return lat_output,lon_output,address

# Function that calculates rhumb line track+distance between two coordinates
def rhumb_track_distance(lt1,lng1,lt2,lng2):
    dlong=(lng2-lng1)*2*np.pi/360
    dlatt=(lt2-lt1)*2*np.pi/360
    R=360*60/(2*np.pi)  # Earth radius
    # Correct sense angular distance
    dphi=np.abs(dlatt)
    #if dlatt <0:
        #dphi=np.abs(dlatt)
    #else:
        #dphi=dlatt

    # Rhumb line calculation
    # Check for shortest distance (anti-meridian)
    if dlong>np.pi:
        dlam=-1*(2*np.pi-dlong)
        eastwest=3*np.pi/2
    elif dlong<-np.pi:
        dlam=2*np.pi+dlong
        eastwest=np.pi/2
    else:
        dlam=dlong
        eastwest=np.pi-np.sign(dlam)*np.pi/2

    if round(lt2,5)==round(lt1,5):    # Check if moving east-west
        q=np.cos(lt1*2*np.pi/360)
        # Calculate bearing
        rbear=eastwest
    else:
        dpsi=np.log(np.tan(np.pi/4 + lt2*2*np.pi/360/2)/np.tan(np.pi/4 + lt1*2*np.pi/360/2))
        q=dphi/dpsi
        # Calculate bearing
        # Check N-S
        if round(lng2,5)==round(lng1,1) or round(lng2,5)+round(lng1,5)==180: # Check if moving North-South
            rbear=np.pi/2-np.sign(dlatt)*np.pi/2
        else:
            rbear=np.arctan2(dlam,dpsi)
        # Normalise to 360
        if rbear<0:
            rbear=2*np.pi+rbear
        #if rv==True:
            #rbear=2*np.pi-rbear
    rhumb_distance=R*(dphi**2+(q*dlam)**2)**0.5

    return rbear*360/2/np.pi,rhumb_distance

# Function that converts input coordinates to a new leg distance+Track and updates accordingly
def calculate_leg(next_lat,next_long,leg_number,line_number,address_nme):
    # Check valid inputs
    if next_lat==None:
        st.session_state.Trklist[leg_number]=None
        st.session_state.Distances[leg_number]=None
        st.session_state.Vertices.append([None,None,None])
        st.session_state.waypoint_name.append(None)
        st.session_state.waypoint_coordinate.append(None)
        return
    # Extract previous coordinates [If present]:
    start_lat=None
    start_long=None
    for i in st.session_state.Vertices:
        if i[0]!=None:
            start_lat=i[0]
            start_long=i[1]
        #if st.session_state.Vertices[-1][0]!=None:
        #start_lat=st.session_state.Vertices[-1][0]
        #start_long=st.session_state.Vertices[-1][1]
    if start_lat==None:
        st.session_state.Trklist[leg_number]=None
        st.session_state.Distances[leg_number]=None
        st.session_state.Vertices.append([next_lat,next_long,address_nme])
        st.session_state.waypoint_name.append(address_nme)
        latitudestring=str(round(next_lat,4))
        longitudestring=str(round(next_long,4))
        st.session_state.waypoint_coordinate.append(latitudestring+' '+longitudestring)
        return
    
    # Calculate Distance and Track between coordinates
    leg_track,leg_distance=rhumb_track_distance(start_lat,start_long,next_lat,next_long)
    st.session_state.Trklist[leg_number]=leg_track
    st.session_state.Distances[leg_number]=leg_distance
    if len(st.session_state['Inputted Vertices'][leg_number+1])!=0:
        if round(leg_distance,2)!=0.:
            st.session_state['Inputted Vertices'][leg_number+1][3]=round(leg_track,2)
            st.session_state['Inputted Vertices'][leg_number+1][4]=round(leg_distance,2)
        else:
            st.session_state['Inputted Vertices'][leg_number+1][3]=0.
            st.session_state['Inputted Vertices'][leg_number+1][4]=0.

    # Add data to a rhumb line + update new final coordinates
    # Calculate leg step (ensure minimum size)
    Dfrac2=leg_distance/line_number
    fact=1
    while Dfrac2<0.01 and Dfrac2!=0:
        Dfrac2*=10
        fact*=10
    if line_number/fact<1:
        Dfrac2=leg_distance
    rhumb_points2=[[start_lat,start_long]]
    lati2=start_lat
    longi2=start_long
    for i in range(int(np.max([line_number/fact,1]))): #int(np.max([line_number/fact,1]))
        a,b=dest_point(Dfrac2,lati2,longi2,leg_track*2*np.pi/360)
        rhumb_points2.append([a,b])
        lati2=a
        longi2=b
    rhumb_longs2=[point[1] for point in rhumb_points2]
    rhumb_lats2=[point[0] for point in rhumb_points2]
    st.session_state.SPLats=st.session_state.SPLats+rhumb_lats2
    st.session_state.SPLongs=st.session_state.SPLongs+rhumb_longs2
    st.session_state.Vertices.append([next_lat,next_long,address_nme])

    if address_nme!='':
        st.session_state.waypoint_name.append(str(address_nme))
    else:
        st.session_state.waypoint_name.append('')
    latitudestring=str(round(next_lat,4))
    longitudestring=str(round(next_long,4))
    st.session_state.waypoint_coordinate.append(latitudestring+' '+longitudestring)
    legno=['Leg '+str(leg_number+1) for i in range(len(rhumb_longs2))]
    for i in legno:
        st.session_state.LegNo.append(i)

    return

# Function that creates checkbutton for input type [Track+Distance, Coordinates, Address]
def choose_leg_input(leg_Number,line_Number):
    # Find most recent address/coordinate
    latlist=[]
    longlist=[]
    addresslist=[]
    prevlat=None
    prevlong=None
    for i in st.session_state.Vertices:
        if i[0]!=None:
            latlist.append(i[0])
            longlist.append(i[1])
            addresslist.append(i[2])
    
    # If valid data inputted already, use that as default values
    if len(st.session_state['Inputted Vertices'][leg_Number+1])!=0 and st.session_state['Inputted Vertices'][leg_Number+1][0]!=None:
        default_lat=round(st.session_state['Inputted Vertices'][leg_Number+1][0],4)
        default_long=round(st.session_state['Inputted Vertices'][leg_Number+1][1],4)
        default_address=st.session_state['Inputted Vertices'][leg_Number+1][2]
    elif len(latlist)==0:       # If no previous preceding valid values
        default_lat=None
        default_long=None
        default_address=None
    elif latlist[-1]!=None:     # Valid preceding valid values
        default_lat=round(latlist[-1],4)
        default_long=round(longlist[-1],4)
        default_address=addresslist[-1]
    else:
        default_lat=None
        default_long=None
        default_address=None
    
    # Set up three types of input
    with outer_cols2[1]:
        input_type=st.selectbox('Input Type',['Track and Distance','Coordinates','Address'],key=str(leg_Number)+'selectbox')
    if input_type=='Track and Distance':
        Track_input(leg_Number,line_Number)
        return
    elif input_type=='Address':
        with outer_cols2[2]:
            lat,lon,adr=address_2_coord(leg_Number,default_address)
            if adr!=default_address:
                set_address_true()
            if st.session_state['address_change']:
                st.session_state['Inputted Vertices'][leg_Number+1]=[lat,lon,adr,0,0]
                st.session_state['address_change']=False
    elif input_type=='Coordinates':
        with outer_cols2[2]:
            inn_cols=st.columns([1,1])
            with inn_cols[0]:
                latstr=st.text_input('Latitude ',value=str(default_lat),key=str(leg_Number)+'latcoord') #,on_change=set_coord_true()
                lat=string_to_float(latstr)
                #lat=st.number_input('Latitude ',value=default_lat,key=str(leg_Number)+'latcoord',min_value=-90.,max_value=90.,format="%.4f",step=1e-4)
            with inn_cols[1]:
                lonstr=st.text_input('Longitude ',value=str(default_long),key=str(leg_Number)+'loncoord') #,on_change=set_coord_true()
                lon=string_to_float(lonstr)
                #lon=st.number_input('Longitude ',value=default_long,key=str(leg_Number)+'loncoord',min_value=-180.,max_value=180.,format="%.4f",step=1e-4)
        
        if lat!=default_lat or lon!=default_long:
            set_coord_true()

        # Correspond coordinates with address if previously entered/knonw
        adr='WP'+str(leg_Number+1)
        # From previous Vertex
        for i in st.session_state.Vertices:
            if i[0]==lat and i[1]==lon:
                adr=i[2]
        for i in st.session_state['Inputted Vertices']:
            if len(i)!=0:
                if i[0]==lat and i[1]==lon:
                    adr=i[2]
        if st.session_state['coord_change']:
            st.session_state['Inputted Vertices'][leg_Number+1]=[lat,lon,adr,0,0]
            st.session_state['coord_change']=False
    else:
        st.markdown('Leg input type error')
        return
    
    # Calculate distance+track and append to appropriate lists
    calculate_leg(lat,lon,leg_Number,line_Number,adr)
    
    return

# Create tabs
maintab,settingtab=st.tabs(['Input Data','Settings'])


############ Inputs  #######################################################################################
with settingtab:
    outer_cols1=st.columns([1,1])
    
    with outer_cols1[0]:
        inner_cols01=st.columns([1,1])
        with inner_cols01[0]:
            st.markdown('Variation (Value/Sense):  ')
            st.markdown('')
            st.markdown('Contingency (%):')
        with inner_cols01[1]:
            var = st.text_input('Variation (Value/Sense):',value='0.5/E',label_visibility='collapsed')
            st.session_state.contingency=st.number_input('Contingency',step=0.01,min_value=0.,value=10.,label_visibility='collapsed')
        inner_cols3=st.columns([0.5,0.4,0.6])
        with inner_cols3[0]:
            st.markdown('SUTTO Burn: ')
            st.markdown('')
            st.markdown('Arrival Burn: ')
            st.markdown('')
            st.markdown('Fuel Burn:  ')
            st.markdown('')
            st.markdown('Fuel Reserve:  ')
        with inner_cols3[1]:
            st.session_state.sutto=st.number_input('SUTTO',step=1,min_value=0,value=10,label_visibility='collapsed')
            st.session_state.arrival=st.number_input('Arrival',step=1,min_value=0,value=7,label_visibility='collapsed')
            st.session_state.fburn=st.number_input('Fuel Burn (lts/hour)',step=1,min_value=0,value=40,label_visibility='collapsed')
            st.session_state.freserve=st.number_input('Fuel Reserve (lts)',step=1,min_value=0,value=20,label_visibility='collapsed')
        with inner_cols3[2]:
            ftype_sutto=st.selectbox('Mass/Volume Sutto',['lts','kg'],label_visibility='collapsed')
            ftype_arrival=st.selectbox('Mass/Volume Arrival',['lts','kg'],label_visibility='collapsed')
            ftype=st.selectbox('Mass/Volume',['lts/hr','kg/hr'],label_visibility='collapsed')
            reserve=st.selectbox('Time/Volume',['Litres','Kilograms','Minutes'],label_visibility='collapsed')

    with outer_cols1[1]:
        fuel_type=st.radio('Fuel type:',['Avgas','Mogas','Jet A1','Specify Sp.G'],horizontal=True)
        ftype_dicts={'Avgas':0.72,'Mogas':0.75,'Jet A1':0.8}
        if fuel_type in ftype_dicts:
            st.session_state.spg=ftype_dicts[fuel_type]
        else:
            st.session_state.spg=st.number_input('Sp.G: ',step=0.01,min_value=0.,value=0.,label_visibility='collapsed')
        
        st.session_state.fuel_output=st.toggle('Output fuel in kg')

        # Convert all fuel inputs to litres
        if ftype=='kg/hr':
            st.session_state.fburn=st.session_state.fburn/st.session_state.spg
        if ftype_sutto=='kg':
            st.session_state.sutto=st.session_state.sutto/st.session_state.spg
        if ftype_arrival=='kg':
            st.session_state.arrival=st.session_state.arrival/st.session_state.spg
        if reserve=='Minutes':
            st.session_state.freserve=st.session_state.freserve/60*st.session_state.fburn
        elif reserve=='Kilograms':
            st.session_state.freserve=st.session_state.freserve/st.session_state.spg

with maintab:
    st.header('Input Data',divider='blue')
        
    outer_cols2=st.columns([0.48,0.25,0.28])
    # Input data onto left
    with outer_cols2[0]:
        st.markdown('Initial position')
        # Choose to input an address (google maps api) or a decimal coordinate
        toggle_column=st.columns([0.235,1])
        with toggle_column[0]:
            st.markdown('Address')
        with toggle_column[1]:
            init_posit=st.toggle('   Coordinates',value=True)
        if init_posit==True:
            inner_cols00=st.columns([1,1])
            # Latitude data, decimal notation
            with inner_cols00[0]:
                lat12=st.number_input(' Latitude ',value=52.6078,key='lad12',min_value=-90.,max_value=90.,format="%.4f",step=1e-4)
            with inner_cols00[1]:
                lon12=st.number_input(' Longitude ',value=-1.0319,key='lond12',min_value=-180.,max_value=180.,format="%.4f",step=1e-4)
            if lat12==52.6078 and lon12==-1.0319:
                adn='EGBG'
            else:
                adn='Start'      # For displaying vertex address (in thas case nothing)
        else: # Google maps api
            lat12,lon12,adn=address_2_coord('initial')

        if 'Inputted Vertices' in st.session_state:
            st.session_state['Inputted Vertices'][0]=[lat12,lon12,adn]

        if lat12==None:
            NS12=''
        elif lat12<0:
            NS12='S'
        else:
            NS12='N'
        if lon12==None:
            EW12=''
        elif lon12<0:
            EW12='W'
        else:
            EW12='E'

        # Display initial coordinate in degree, minutes, seconds
        a22,b22,c22=conv_dec2coord(lat12)
        d22,e22,f22=conv_dec2coord(lon12)
        a22str2,d22str2=deg_length(a22,d22,'D')
        b22str2,e22str2=deg_length(b22,e22,'M')
        c22str2,f22str2=deg_length(c22,f22,'S')

        if a22 !=None:
            st.markdown('$ {} {}\degree {}\' {}\'\' \ \ {} {}\degree {}\' {}\'\' $ '.format(NS12,a22str2,b22str2,c22str2,EW12,d22str2,e22str2,f22str2))


        #notrks = st.number_input('Number of Legs', step=1,min_value=1)
        #inc_wind=st.toggle('Include Wind')

        # Add wind+fuel data
        inner_cols1=st.columns([1.2,1])
        with inner_cols1[0]:
            st.markdown('True AirSpeed (kts):  ')
            st.markdown('')
            st.markdown('Wind (Heading/Velocity):  ')
        with inner_cols1[1]:
            TAS = st.number_input('True AirSpeed (kts):',step=1,value=80,label_visibility='collapsed')
            vwstr = st.text_input('Wind vector and velocity (Heading/Velocity):',value='000/00',label_visibility='collapsed')
            
        
        # Calculate Wind direction from string input
        if '/' in vwstr:
            vw_split=vwstr.split('/')
        elif '|' in vwstr:
            vw_split=vwstr.split('|') 
        elif '\\' in vwstr:
            vw_split=vwstr.split('\\')
        elif ' ' in vwstr:
            vw_split=vwstr.split(' ')
        else:
            st.markdown('Check wind input')
            pass
        vw=float(vw_split[1])             # Wind velocity
        wd=float(vw_split[0])         # Wind direction ##### 360-
        if vw<0:
            wd+=180
        if '/' in var:
            var_split=var.split('/')
        elif '|' in var:
            var_split=var.split('|') 
        elif '\\' in var:
            var_split=var.split('\\')
        elif ' ' in var:
            var_split=var.split(' ')
        else:
            st.markdown('Check variation input')
            pass
        st.session_state.var_val=float(var_split[0])
        sense=str(var_split[1])
        if 'W' in sense or 'w' in sense or '-' in sense:
            st.session_state.var_val*=-1
        while wd>360:
            wd-=360
        while wd<0:
            wd+=360
        #st.session_state.Wind=pd.DataFrame(data={'Track': [],'Mag Heading': [], 'Groundspeed': [], 'Uncorrected Drift': [], 'Uncorrected Groundspeed': [] , 'Time':[], 'Fuel':[]})
        st.session_state.Wind=pd.DataFrame(data={'To Waypoint: ': [], 'Coordinate': [], 'Track': [],'Mag Heading': [], 'Groundspeed': [], 'Distance': [], 'Time':[], 'Fuel':[]})


        numb=1000 # Number points per track (For plotting purposes)
        # Initialise session variables with first point
        if 'numtrks' not in st.session_state:
            st.session_state['numtrks'] = 1
        st.session_state.Trklist=np.zeros(st.session_state['numtrks'])   # No Tracks
        if 'Inputted Vertices' not in st.session_state:
            st.session_state['Inputted Vertices'] = [[lat12,lon12,adn],[]]
        if 'coord_change' not in st.session_state:
            st.session_state['coord_change']=False
        if 'address_change' not in st.session_state:
            st.session_state['address_change']=False
        if 'track_change' not in st.session_state:
            st.session_state['track_change']=False
        st.session_state.Trklist=np.zeros(st.session_state['numtrks'])   # No Tracks
        if lat12!=None:
            st.session_state.SPLats=[lat12] # Rhumb line points (lat)
            st.session_state.SPLongs=[lon12] # Rhumb line points (long)
            st.session_state.Vertices=[[lat12,lon12,adn]]
        else:
            st.session_state.SPLats=[None] # Rhumb line points (lat)
            st.session_state.SPLongs=[None] # Rhumb line points (long)
            st.session_state.Vertices=[[None,None,None]]
        st.session_state.Distances=np.zeros(st.session_state['numtrks'])
        st.session_state.waypoint_name=[]
        st.session_state.waypoint_coordinate=[]
        st.session_state.LegNo=['Start']
        st.session_state.count = 0
        #notrks=st.session_state['numtrks']
        #st.markdown(notrks)
        # Create Track input
        for i in range(st.session_state['numtrks']):
            choose_leg_input(i,numb)
            #Track_input(i,numb)
            st.session_state.count+=1
        with outer_cols2[1]:
            st.button('Add waypoint', on_click=add_waypoint,type='primary')
            st.button('Remove waypoint', on_click=remove_waypoint)

    st.header('Results',divider='blue')
    # Print Results of each vertex
    for i in range(len(st.session_state.Trklist)):
        a22,b22,c22=conv_dec2coord(st.session_state.Vertices[i+1][0])
        d22,e22,f22=conv_dec2coord(st.session_state.Vertices[i+1][1])
        a22str2,d22str2=deg_length(a22,d22,'D')
        b22str2,e22str2=deg_length(b22,e22,'M')
        c22str2,f22str2=deg_length(c22,f22,'S')
        if a22!=None:
            if np.sign(a22)==-1:
                ns22='S'
            else:
                ns22='N'
            if np.sign(d22)==-1 or np.sign(e22)==-1 or np.sign(f22)==-1:
                ew22='W'
            else:
                ew22='E'
            address_name=st.session_state.Vertices[i+1][2]
            st.markdown('Waypoint '+ str(i+1)+':'+'  $ {} {}\degree {}\' {}\'\' \ \ {} {}\degree {}\' {}\'\'  $   {}'.format(ns22,a22str2,b22str2,c22str2,ew22,d22str2,e22str2,f22str2,address_name))
            
            #st.markdown()
        else:
            st.markdown('Waypoint '+ str(i+1)+': Null Address')

    # Check if wind calc required
    #if inc_wind:
    st.session_state.fuel=0
    st.session_state.time=0
    #st.markdown('**Track** $\ \ $ **Mag Heading** $\ \ $ **Groundspeed** $\ \ $ **Uncorrected Drift** $\ \ $ **Uncorrected Groundspeed**')
    for i in range(st.session_state['numtrks']):
        add_row,add_fuel=Wind_Drift(TAS,vw,wd,i)
        st.session_state.Wind.loc[len(st.session_state.Wind)]=add_row
        st.session_state.fuel+=np.round(add_fuel,2)   # In litres
        st.session_state.time+=add_row[-2]

    ftotal=((st.session_state.fuel+st.session_state.sutto+st.session_state.arrival)*(1+st.session_state.contingency/100)+st.session_state.freserve)
    # Convert output as required kg/lts
    if not st.session_state.fuel_output:
        Fuel_total=np.ceil(ftotal)
        Fuel=np.ceil(st.session_state.fuel)
        Fuel_sutto=np.ceil(st.session_state.sutto)
        Fuel_arrival=np.ceil(st.session_state.arrival)
        funit='l'
    else:
        Fuel_total=np.ceil(round(ftotal*st.session_state.spg,2))
        Fuel=np.ceil(round(st.session_state.fuel*st.session_state.spg,2))    
        Fuel_sutto=np.ceil(round(st.session_state.sutto*st.session_state.spg,2))
        Fuel_arrival=np.ceil(round(st.session_state.arrival*st.session_state.spg,2))
        funit='kg'

    # Print resultsa
    st.dataframe(st.session_state.Wind)
    st.markdown('Fuel Total: {} {}, [Trip Fuel: {} {}]'.format(Fuel_total,funit,Fuel,funit))
    st.markdown('EET: {} minutes'.format(round(st.session_state.time,1)))
    st.markdown('Includes {}{} for SUTTO, {}{} for arrival, +{}% contingency'.format(Fuel_sutto,funit,Fuel_arrival,funit,st.session_state.contingency))
    ####################### Plots ##############################
    st.header('Plots',divider='blue')

    typ2=st.session_state.LegNo

    # Remove None Values
    latvals=[]
    longvals=[]
    for i in st.session_state.SPLats:
        #st.markdown([i,type(i)])
        if i != None:
            latvals.append(i)
    for i in st.session_state.SPLongs:
        if i != None:
            longvals.append(i)
    if len(latvals)==len(st.session_state.SPLats):
        llg=pd.DataFrame(data={'lat':st.session_state.SPLats,'long':st.session_state.SPLongs,'type':typ2})
    elif len(latvals)!=0:
        llg=pd.DataFrame(data={'lat':latvals,'long':longvals})
    else:
        llg=None

    #st.markdown(llg)
    #projectio=st.radio('Projection type',['map','orthographic','equirectangular','natural earth'],horizontal=True,key=st.session_state.count)

    if type(llg)!=type(None):
        #if projectio != 'map':
            #st.plotly_chart(plot_spherical_distance(llg,projectio),use_container_width=True)
        #else:
        st.map(data=llg,latitude='lat',longitude='long')
    else:
        st.markdown('No values')
