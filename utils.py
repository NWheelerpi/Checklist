def nearest_location():
    print('Nearest Location')
    return

def selected_image(checklist_key):
    'Function that adds selected actions from action image'
    # Calculate nearest 'action'
    # Correct values for reshaped grid 
    value=st.session_state.xylist[checklist_key]
    st.markdown(value)
    '''
    xval*=860/self.xval
    yval*=640/self.yval
    dist_dict={}
    for i in self.action_dict:
        Distance=(xval-self.action_dict[i][1])**2+(yval-self.action_dict[i][2])**2
        dist_dict[Distance]=i
    # Check close enough to a switch 
    #print(dist_dict[sorted(dist_dict)[0]],self.action_dict[dist_dict[sorted(dist_dict)[0]]])
    if dist_dict[sorted(dist_dict)[0]] <=100:   
        action_index=dist_dict[sorted(dist_dict)[0]]
    else:
        action_index=None
        
    # Create correct string
    action_string=None
    if action_index!=None:
        if string=='on' and type(self.action_dict[action_index][3])!=float and self.action_dict[action_index][3]!='NONE':
            action_string=self.action_dict[action_index][3]
        elif string=='off' and type(self.action_dict[action_index][4])!=float and self.action_dict[action_index][4]!='NONE':
            action_string=self.action_dict[action_index][4]
        elif string=='check' and type(self.action_dict[action_index][5])!=float and self.action_dict[action_index][5]!='NONE':
            action_string=self.action_dict[action_index][5]
    else:
        pass
    
    #print(xval,yval,string,action_string)
    
    # Add/remove from text
    if action_string!=None:
        self.selected(action_string,tabnum,Key)
    '''
     return


