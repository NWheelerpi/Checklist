import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates


def show_question():
    return

def submit_answer():
    return

def show_hint():
    return

def layout(Tab,checklist,checklist_key,tab_num,Image):
    
    actions=checklist.T.values.tolist()[0]
    conditionals=checklist.T.values.tolist()[1]
    
    title=''
    for i in checklist_key.split('_'):
        title += ' '+i
   

    with Tab:
        st.header(title)
        outer_cols = st.columns([3,1,5])

        with outer_cols[1]:
            click_type=st.radio('Click Type',['On','Off','Check'],key='Radio'+str(tab_num),label_visibility='collapsed',width=50)
        with outer_cols[2]:
            xy=streamlit_image_coordinates(Image,use_column_width=True,key='Image'+str(tab_num),cursor='crosshair')
            st.session_state.xylist[checklist_key]=xy
    return