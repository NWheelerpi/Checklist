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
        outer_cols = st.columns([3,1])

        with outer_cols[0]:
            xy=streamlit_image_coordinates(Image,key='Image'+str(tab_num))
            st.write(xy)
    return