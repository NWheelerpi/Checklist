import streamlit as st

def nearest_location():
    print('Nearest Location')
    return

def selected(string,key):
    st.markdown(string)
    return
def selected_image(checklist_key,string='on'):
    'Function that adds selected actions from action image'
    # Calculate nearest 'action'
    # Correct values for reshaped grid 
    value=st.session_state.xylist[checklist_key]
    st.markdown(value)
    xval=value['x']*860/value['width']
    yval=value['y']*640/value['height']
    dist_dict={}
    for i in st.session_state.action_dict:
        Distance=(xval-st.session_state.action_dict[i][1])**2+(yval-st.session_state.action_dict[i][2])**2
        dist_dict[Distance]=i
    # Check close enough to a switch 
    #print(dist_dict[sorted(dist_dict)[0]],st.session_state.action_dict[dist_dict[sorted(dist_dict)[0]]])
    if dist_dict[sorted(dist_dict)[0]] <=100:   
        action_index=dist_dict[sorted(dist_dict)[0]]
    else:
        action_index=None
        
    # Create correct string
    action_string=None
    if action_index!=None:
        if string=='on' and type(st.session_state.action_dict[action_index][3])!=float and st.session_state.action_dict[action_index][3]!='NONE':
            action_string=st.session_state.action_dict[action_index][3]
        elif string=='off' and type(st.session_state.action_dict[action_index][4])!=float and st.session_state.action_dict[action_index][4]!='NONE':
            action_string=st.session_state.action_dict[action_index][4]
        elif string=='check' and type(st.session_state.action_dict[action_index][5])!=float and st.session_state.action_dict[action_index][5]!='NONE':
            action_string=st.session_state.action_dict[action_index][5]
    else:
        pass
    st.markdown(action_string)
    #print(xval,yval,string,action_string)
    
    # Add/remove from text
    if action_string!=None:
        selected(action_string,checklist_key)
    return



