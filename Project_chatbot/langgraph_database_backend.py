from langgraph.graph import StateGraph , START, END
from typing import TypedDict ,Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv()

llm= ChatGroq(model="llama-3.3-70b-versatile")

class ChatState(TypedDict):
    message: Annotated[list[BaseMessage], add_messages]


#node functions
def chat_node(state: ChatState):
    message=state['message']
    response=llm.invoke(message)
    return{'message':[response]} # update the message , in the state


#we have to create the sqlite database 

conn=sqlite3.connect(database='chatbot.db', check_same_thread=False) 
#check_same_thread ->false because we have to use multiple thread_id so ,mean we use same database for different threads

checkpointer=SqliteSaver(conn=conn)

#graph
graph=StateGraph(ChatState)

#node 
graph.add_node("chat_node",chat_node)

#edges
graph.add_edge(START,"chat_node")
graph.add_edge("chat_node", END)

chatbot= graph.compile(checkpointer=checkpointer)

#test 
# CONFIG= {'configurable': {'thread_id' : 'thread-1'}}

# response=chatbot.invoke(
#     {'message':[HumanMessage(content="hi my name is Abhishek")]},
#     config=CONFIG
# )

# print(response)

# now on closing of the program, we have the message store in sqlite database
# and the message of thread -1 , store in different section , and the message of thread-2 , is store in different store , so we can access it 


def retrieve_all_threads():
    all_threads=set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    
    return list(all_threads)