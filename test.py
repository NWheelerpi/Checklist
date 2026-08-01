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
        st.image(Image,width=800)
    return