import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from utils import selected_image

def show_question():
    return

def submit_answer():
    return

def show_hint():
    return

def layout(Tab,checklist,checklist_key,tab_num,Image):
    
    actions=checklist.T.values.tolist()[0]
    conditionals=checklist.T.values.tolist()[1]
    # Create Master List:
    temp_acts=actions.copy()
    # Create corresponding list containing booleans of order req'd
    order_bools=[]
    for i in range(len(temp_acts)):
        if checklist.T.values.tolist()[2][i]==False:
            order_bools.append(False)
        elif checklist.T.values.tolist()[2][i]==True:
            order_bools.append(True)
    # Remove nan values from temp list (actions+results)
    nan_list=[i for i in temp_acts if type(i)==float]
    while len(nan_list)>0:
        for item in temp_acts:
            if type(item)==float:
                temp_acts.remove(item)
                nan_list.pop()     
    st.session_state.master_list[checklist_key]=[temp_acts,order_bools]
    
    title=''
    for i in checklist_key.split('_'):
        title += ' '+i
   

    with Tab:
        st.header(title)
        outer_cols = st.columns([5,1,10])
        
        with outer_cols[1]:
            click_type=st.radio('Click Type',['On','Off','Check'],key='Radio'+str(checklist_key),label_visibility='collapsed')
        with outer_cols[2]:
            st.session_state.xylist[checklist_key]=streamlit_image_coordinates(Image,use_column_width=True,key='Image'+str(checklist_key),cursor='crosshair')
        selected_image(checklist_key)
        with outer_cols[0]:
            st.markdown(st.session_state.answer[checklist_key])
            for string in st.session_state.answer[checklist_key]:
                st.markdown(string)
    
    return