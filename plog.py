import pandas as pd
import streamlit as st
from utils import *
from test import *
import random
import numpy as np


st.set_page_config(layout="wide")

## Create Reset Button
reset=st.button("Reset")
# Handle the reset action before creating the tabs
if reset:
  if 'num_checklist_list' not in st.session_state:
    pass
  else:
    for key in list(st.session_state.keys()):
        if 'Radio' in key:
            st.session_state[key]='On'
        del st.session_state[key]
    st.rerun()  # Forces immediate recreation with a new order

### Extract Emergencies
book= 'Tutor_Emergencies.xlsx'
action_image=pd.read_excel('Image_Actions.xlsx',sheet_name='Sheet1')

## Initialise various variables
st.session_state.emergency_dict=pd.read_excel(book,sheet_name=None)     # Dictionary of emergencies
st.session_state.action_dict={}                                         # Dictionary of actions
st.session_state.xylist={}                                              # Dictionary of image coordinates (based on Cockpit image)
st.session_state.master_list={}                                         # Dictionary of correct Bold Face Actions per emergency
if 'answer' not in st.session_state:  
    st.session_state.answer={}                                          # Dictionary of answered options per emergency
    st.session_state.incorrect_list={}                                  # Dictionary of incorrect answers
    st.session_state.selected_lol={}                                    # List of output (answers + following associated If statements)
    st.session_state.submitted={}                                       # Dictionary of submitted emergencies
st.session_state.Keys=[]                                                # List of Emergency Titles

# Create keys
Raw_Keys=[i for i in st.session_state.emergency_dict.keys()]
# Randomise order
if 'num_checklist_list' not in st.session_state: # Check first attempt to randomise (else will randomise continuously).
    st.session_state.num_checklist_list=list(np.arange(0,len(Raw_Keys),1))
    random.shuffle(st.session_state.num_checklist_list)

for i in st.session_state.num_checklist_list:
    st.session_state.Keys.append(Raw_Keys[i])

for i in range(len(action_image)):
    st.session_state.action_dict[i]=[action_image.T.values.tolist()[0][i],action_image.T.values.tolist()[1][i],action_image.T.values.tolist()[2][i],action_image.T.values.tolist()[3][i],action_image.T.values.tolist()[4][i],action_image.T.values.tolist()[5][i]]
    
### Create correct number of Tabs
Tabs=st.tabs([str(i+1) for i in range(len(st.session_state.Keys))])


# Create list of actions for button (not associated with image)
non_image_actions=[]
col_list=[2]
flatlist=[j for i in list(st.session_state.action_dict.values()) for j in i]  
for j,i in enumerate(st.session_state.num_checklist_list):
    actions=st.session_state.emergency_dict[st.session_state.Keys[j]].T.values.tolist()[0]
    for i in actions:
        if i not in flatlist and i not in non_image_actions:
            non_image_actions.append(i)
            col_list.append(1)
st.markdown(actions)
st.markdown(flatlist)
# Create Master list, Answer list and set layout of each tab (layout also runs through image click effects)
for j,i in enumerate(st.session_state.num_checklist_list):
    st.session_state.master_list[st.session_state.Keys[j]]=[]
    if st.session_state.Keys[j] not in st.session_state.answer.keys(): 
        st.session_state.answer[st.session_state.Keys[j]]=[]
        st.session_state.incorrect_list[st.session_state.Keys[j]]=[]
        st.session_state.selected_lol[st.session_state.Keys[j]]=[]
        st.session_state.submitted[st.session_state.Keys[j]]=False
    layout(Tabs[j],st.session_state.emergency_dict[st.session_state.Keys[j]],st.session_state.Keys[j],j,'Cockpit.png',col_list,non_image_actions) 

