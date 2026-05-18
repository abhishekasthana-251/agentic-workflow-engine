from langgraph.graph import StateGraph , START, END
from typing import TypedDict ,Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver

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


#checkpoints-> store in Snapshot of node in the RAM 
checkpointer=InMemorySaver()

#graph
graph=StateGraph(ChatState)

#node 
graph.add_node("chat_node",chat_node)

#edges
graph.add_edge(START,"chat_node")
graph.add_edge("chat_node", END)

chatbot= graph.compile(checkpointer=checkpointer)

#2 improvement
#streaming -> we are using before chatbot.invoke(), now we use

# stream=chatbot.stream(
#     { 'message':[HumanMessage(content='what is the recipe to make pasta')]
#     },
#     config={'configurable':{'thread_id': 'thread-1'}},
#     streams_mode='messages'
# )

#print(type(stream)) -> <class 'generator'>