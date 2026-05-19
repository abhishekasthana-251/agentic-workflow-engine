import streamlit as st 
from langgraph_database_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
import uuid



llm=ChatGroq(model='llama-3.3-70b-versatile')

#************************** Utility functions **********************************
def generate_thread_id():
    thread_id=uuid.uuid4() # give as the random thread_id 
    return thread_id

def generate_chat_name(user_message):
    response=llm.invoke(
        f"Give a 4-5 word title for a chat that starts with this message: '{user_message}'. "
        f"Reply with ONLY the title, no punctuation, no quotes, nothing else."
    )
    return response.content.strip()

def reset_chat():
    thread_id=generate_thread_id() #give new thread id
    st.session_state['thread_id']=thread_id #store in session_state 
    add_thread(st.session_state['thread_id']) # add/storing this new thread id , so we can resume it
    st.session_state['message_history']=[] #empty the session_state

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)



def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable':{'thread_id':thread_id}})
    #check if messages key exists in state values, return empty list if not 
    return state.values.get('message',[])

#*********************** Session Setup ***************************************
if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]

if 'thread_id' not in st.session_state:
    st.session_state['thread_id']=generate_thread_id()


if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] =retrieve_all_threads()

if 'thread_names' not in st.session_state:
    st.session_state['thread_names']= {}

add_thread(st.session_state['thread_id'])
#**************************************Sidebar UI******************************


st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header('My conversations')

#display all the thread id 
for thread_id in st.session_state['chat_threads'][::-1]:
    #show Ai name if exists , else show "New chat"
    display_name=st.session_state['thread_names'].get(str(thread_id),"New chat")
    #before first message,shows 'new chat'
    if st.sidebar.button(display_name,key=str(thread_id)):
        st.session_state['thread_id']=thread_id
        messages=load_conversation(thread_id)

        #before passing the messages to message_history , we are converting it format, as we are storing it in our session_state[message_history]

        temp_messages=[]
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role='user'
            else:
                role='assistant'
            
            temp_messages.append({'role':role ,'content':msg.content})

        st.session_state['message_history']=temp_messages

#*************************************MAIN UI ***********************************


for message in  st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])



user_input = st.chat_input("Type here")

if user_input:

    st.session_state['message_history'].append({'role':'user','content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG={'configurable':{'thread_id':st.session_state['thread_id']}}

    # generate ai name only on first message of this threads
    thread_key=str(st.session_state['thread_id'])
    if thread_key not in st.session_state['thread_names']:
        chat_name=generate_chat_name(user_input)
        st.session_state['thread_names'][thread_key]=chat_name

    #response =chatbot.invoke({'message':[HumanMessage(content=user_input)]}, config= CONFIG)

 
#***********stream Response
    with st.chat_message('assistant'):

        ai_message= st.write_stream(
            message_chunk.content 
            for message_chunk, metadata in chatbot.stream(
                { 
                    'message':[HumanMessage(content=user_input)]
                },
                config=CONFIG,
                stream_mode='messages'
            )
        )
    
    st.session_state['message_history'].append({
        'role':'assistant', 
        'content': ai_message
    })

   








