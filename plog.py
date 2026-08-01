import pandas as pd
import streamlit as st
from utils import *
from test import *
import random
### Extract Emergencies

book= 'Tutor_Emergencies.xlsx'
st.session_state.emergency_dict=pd.read_excel(book,sheet_name=None)
action_image=pd.read_excel('Image_Actions.xlsx',sheet_name='Sheet1')
st.session_state.action_dict={}
for i in range(len(action_image)):
            st.session_state.action_dict[i]=[action_image.T.values.tolist()[0][i],action_image.T.values.tolist()[1][i],action_image.T.values.tolist()[2][i],action_image.T.values.tolist()[3][i],action_image.T.values.tolist()[4][i],action_image.T.values.tolist()[5][i]]

st.session_state.Keys=[i for i in st.session_state.emergency_dict.keys()]

##### Randomise Emergencies as required
num_checklist_list=list(np.arange(0,len(st.session_state.Keys),1))
random.shuffle(num_checklist_list)
    
st.markdown(st.session_state.Keys)

for j,i in enumerate(num_checklist_list):
    layout(self.windowlist[j*2],st.session_state.emergency_dict[st.session_state.Keys[num_checklist_list[j]]],st.session_state.Keys[num_checklist_list[j]],j*2)