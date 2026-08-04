import streamlit as st
import time

def nearest_location():
    print('Nearest Location')
    return

def selected(string,key,conditionals):
    key_len=len(st.session_state.answer[key])
    if len(st.session_state.answer[key])==0:
        st.session_state.answer[key].append(string)
        #st.markdown('Added '+string)
    # Check not in answer already (as last input)
    elif string not in st.session_state.answer[key][-1]:
        st.session_state.answer[key].append(string)
        #st.markdown('Appended '+string)  
    # Remove if last answer
    elif string in st.session_state.answer[key][-1]:
        #st.markdown('Removed '+string)
        st.session_state.answer[key]=st.session_state.answer[key][:-1]
    else:
        pass

    # Create list of output text
    try:
        if conditionals[string][1]==key_len-1:
            string+='\n '+conditionals[string][0]
        elif conditionals[string][1]>key_len-1:
            string+='\n '+conditionals[string][0]
    except:
        pass
    
    # Check if correct use of conditional (Only portray at correct instance)
    if len(st.session_state.selected_lol[key])==0:
        st.session_state.selected_lol[key].append(string)
    elif string not in st.session_state.selected_lol[key][-1]:
        st.session_state.selected_lol[key].append(string)
    elif string in st.session_state.selected_lol[key][-1]:
        st.session_state.selected_lol[key]=st.session_state.selected_lol[key][:-1]
    return

def selected_image(checklist_key,string='on',conditionals=None):
    'Function that adds selected actions from action image'
    # Correct values for reshaped grid 
    value=st.session_state.xylist[checklist_key]
    if not value:
        return
    # Check if recently clicked (else will add/remove previous options on other tabs)
    ut=int(value['unix_time']/1000)
    now=int(time.time())
    if now-ut>5:
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
        selected(action_string,checklist_key,conditionals)
    return



def print_string(checklist_key):
    # Check correctness of selection
    modifier=-1                     # To allow for a misclick (only check last but one selection)
    incorrect_list={}

    for i in range(len(st.session_state.answer[checklist_key])+modifier):

        if st.session_state.answer[checklist_key][i]!=st.session_state.master_list[checklist_key][0][i] and st.session_state.master_list[checklist_key][1][i]!=False:
            incorrect_list[i]=st.session_state.answer[checklist_key][i]
            if [st.session_state.answer[checklist_key][i],i,st.session_state.master_list[checklist_key][0][i]] not in st.session_state.incorrect_list[checklist_key]:
                st.session_state.incorrect_list[checklist_key].append([st.session_state.answer[checklist_key][i],i,st.session_state.master_list[checklist_key][0][i]])
        elif st.session_state.master_list[checklist_key][1][i]==False:
            unordered_list=[]
            # Work down list
            for j in range(len(st.session_state.master_list[checklist_key][0])-i):
                if st.session_state.master_list[checklist_key][1][j+i]==False:
                    unordered_list.append(st.session_state.master_list[checklist_key][0][j+i])
                else:
                    break
                    
            # Work up list
            for j in range(i):
                if st.session_state.master_list[checklist_key][1][i-j]==False:
                    unordered_list.append(st.session_state.master_list[checklist_key][0][i-j])
                else:
                    break
    
            if st.session_state.answer[checklist_key][i] not in unordered_list:
                incorrect_list[i]=st.session_state.answer[checklist_key][i]
                if [st.session_state.answer[checklist_key][i],i,st.session_state.master_list[checklist_key][0][i]] not in st.session_state.incorrect_list[checklist_key]:
                    st.session_state.incorrect_list[checklist_key].append([st.session_state.answer[checklist_key][i],i,st.session_state.master_list[checklist_key][0][i]])

    st.markdown(incorrect_list)
    count=0
    for i in st.session_state.selected_lol[checklist_key]:
        # Check if incorrect + highlight conditionals
        highlight=''
        st.markdown([i,i.splitlines()])
        if i.splitlines()[0] in incorrect_list.values():
            
            i_keys=[key for key, val in incorrect_list.items() if val == i.splitlines()[0]]
            st.markdown([i_keys,count])
            # Check for correct incorrect selection (so does not highlight all instances of action)
            if count in i_keys:
                highlight='Incorrect'
            else:
                pass
        if '\n' in i:
            i_split=i.splitlines()
            if highlight=='':
                st.markdown(i_split[0])
            else:
                st.markdown(':red['+i_split[0]+']')
            st.markdown(':violet['+i_split[1]+']')
        else:
            if highlight=='':
                st.markdown(i)
            else:
                st.markdown(':red['+i+']')
        count+=1
    return