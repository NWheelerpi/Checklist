import streamlit as st

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
        outer_cols = st.columns([2,1])

        with outer_cols[0]:
            st.image(Image,width='stretch')
    return