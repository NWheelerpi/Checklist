import streamlit as st

def nearest_location():
    print('Nearest Location')
    return

def selected(string,key):
    key_len=len(st.session_state.answer[key])
    if len(st.session_state.answer[key])==0:
        st.session_state.answer[key].append(string)
        st.markdown('Added '+string)
    # Check not in answer already (as last input)
    elif string not in st.session_state.answer[key][-1]:
        st.session_state.answer[key].append(string)
        st.markdown('Appended '+string)  
    # Remove if last answer
    elif string in st.session_state.answer[key][-1]:
        st.markdown('Removed '+string)
        st.session_state.answer[key]=st.session_state.answer[key][:-1]
    else:
        pass

    return

def selected_image(checklist_key,string='on'):
    'Function that adds selected actions from action image'

    # Correct values for reshaped grid 
    value=st.session_state.xylist[checklist_key]
    
    st.markdown(st.session_state.xylist)
    # Delete Image to ensure no repeated selection when another tab used
    del st.session_state.xylist
    st.markdown(st.session_state.xylist)
    if not value:
        return
    xval=value['x']*860/value['width']
    yval=value['y']*640/value['height']
    # Calculate nearest 'action'
    dist_dict={}
    for i in st.session_state.action_dict:
        Distance=(xval-st.session_state.action_dict[i][1])**2+(yval-st.session_state.action_dict[i][2])**2
        dist_dict[Distance]=i
    # Check close enough to a switch 
    if dist_dict[sorted(dist_dict)[0]] <=100:   
        action_index=dist_dict[sorted(dist_dict)[0]]
    else:
        action_index=None
    
    string=st.session_state['Radio'+str(checklist_key)]
    # Create correct string
    action_string=None
    if action_index!=None:
        if string=='On' and type(st.session_state.action_dict[action_index][3])!=float and st.session_state.action_dict[action_index][3]!='NONE':
            action_string=st.session_state.action_dict[action_index][3]
        elif string=='Off' and type(st.session_state.action_dict[action_index][4])!=float and st.session_state.action_dict[action_index][4]!='NONE':
            action_string=st.session_state.action_dict[action_index][4]
        elif string=='Check' and type(st.session_state.action_dict[action_index][5])!=float and st.session_state.action_dict[action_index][5]!='NONE':
            action_string=st.session_state.action_dict[action_index][5]
    else:
        pass
    #print(xval,yval,string,action_string)
    
    # Add/remove from text
    if action_string!=None:
        selected(action_string,checklist_key)
    return



