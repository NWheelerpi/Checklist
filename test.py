import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from utils import selected_image,print_string

def show_question():
    return

def submit_answer():
    return

def show_hint(check_key,conds):
    'Function that reveals next step in checklist'
    # Check if nil selected
    lowest_correct=len(st.session_state.answer[check_key])
    if len(st.session_state.answer[check_key])==0:
        pass
    # Check if first incorrect
    elif len(st.session_state.answer[check_key])==1:
        if st.session_state.answer[check_key][0]!=st.session_state.master_list[check_key][0][0]:
            st.session_state.selected(st.session_state.answer[check_key][0],check_key,conds)
            lowest_correct=0
    # parse through from end to start removing incorrect values:
    else:
        # find lowest correct value (sequence from start to first incorrect)
        for i in range(len(st.session_state.answer[check_key])-1,0,-1):
            if st.session_state.answer[check_key][i]!=st.session_state.master_list[check_key][0][i]:
                #st.session_state.selected(st.session_state.answer[check_key][i],tab_number,check_key)
                lowest_correct=i
        # Remove all values afterwards
        for i in range(len(st.session_state.answer[check_key])-1,lowest_correct-1,-1):
            st.session_state.selected(st.session_state.answer[check_key][i],check_key,conds)
    # Add new value
    st.session_state.selected(st.session_state.master_list[check_key][0][lowest_correct],check_key,conds)
    return

def layout(Tab,checklist,checklist_key,tab_num,Image):
    
    actions=checklist.T.values.tolist()[0]
    conditionals=checklist.T.values.tolist()[1]
    # Create dictionary of conditional actions
    # Check if first value conditional
    cond_dict={}
    if type(actions[0])==float  and type(conditionals[0])!=float:
        cond_dict['prompt']=conditionals[0]
    for i in range(len(actions)):
        if type(conditionals[i])!=float and type(actions[i])!=float:
            cond_dict[str(actions[i])]=[conditionals[i],i]
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
        hint=st.button('Hint',key='Hint'+str(checklist_key))
        if hint:
            show_hint(checklist_key,cond_dict)
        outer_cols = st.columns([5,1,10])
        
        with outer_cols[1]:
            click_type=st.radio('Click Type',['On','Off','Check'],key='Radio'+str(checklist_key),label_visibility='collapsed')
        with outer_cols[2]:
            xy=streamlit_image_coordinates(Image,use_column_width=True,key='Image'+str(checklist_key),cursor='crosshair')
            st.session_state.xylist[checklist_key]=xy
        selected_image(checklist_key,cond_dict)
        with outer_cols[0]:
            print_string(checklist_key)
            #for string in st.session_state.answer[checklist_key]:
                

    
    return