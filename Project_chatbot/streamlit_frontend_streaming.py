import streamlit as st 
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
#3_ we use st.session_state is already a dict , so we add a key message_history  and the value is list  -> because after pressing the enter  the value of the dict will not disappear, it will only reset when we manually reload the page 
CONFIG={'configurable':{'thread_id':'thread_1'}}

if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]




#2_as each time i run the code it update the code , because it running from start to end , so we will create a dict of messages ,and store it in a list, which store the converstation of this
#like these {'role' : 'user', 'content' :'hi'}

#message_history=[]
#first we loading the history to display
for message in  st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])



user_input = st.chat_input("Type here")

if user_input:

    #2_first add the message to message_history then display
    st.session_state['message_history'].append({'role':'user','content': user_input})
    with st.chat_message('user'):
        st.text(user_input)


    response =chatbot.invoke({'message':[HumanMessage(content=user_input)]}, config= CONFIG)

 
    #2_first add the message to message_history then display
    #st.session_state['message_history'].append({'role':'assistant', 'content': ai_message})

    with st.chat_message('assistant'):

        ai_message= st.write_stream(
            message_chunk.content 
            for message_chunk, metadata in chatbot.stream(
                { 
                    'message':[HumanMessage(content=user_input)]
                },
                config={'configurable':{'thread_id': 'thread-1'}},
                stream_mode='messages'
            )
        )
    
    st.session_state['message_history'].append({'role':'assistant', 'content': ai_message})

   








#1_ to understand the streamlit

#****************************************************
# #chat_message -> show a messages
# #chat_input-> asking the user for input

# import streamlit as st 

# with st.chat_message('User'):
#     st.text('hi')

# user_input=  st.chat_input("type here ")

# if user_input:
#     with st.chat_message("User"):
#         st.text(user_input)  



# Streaming -> in llms, streaming means the model starts sending tokens(words) as soon as they're generated, instead of waiting for the entire response to be ready before returing it 
# have message_chunk , metadata 
# why streaming 
  #fast response 
  #mimics human 
  #importand for multi-model
  # better UK for long output
  # you can cencel midway saying token
  # you can interleave 

#generator
  # IN python, a generator is a special type of iterator that allows you to generate values on the fly , one at a time, using the yield keyword  instead of return  , in code we write graph.invoke , now we will write graph.stream