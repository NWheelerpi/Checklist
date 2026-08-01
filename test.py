import streamlit as st

def show_question():
    return

def submit_answer():
    return

def show_hint():
    return

def layout(Tab,checklist,checklist_key,tab_num):
    
    actions=checklist.T.values.tolist()[0]
    conditionals=checklist.T.values.tolist()[1]

    title=[i for i in checklist_key.split('_')]

    with Tab:
        st.header(title)
    return