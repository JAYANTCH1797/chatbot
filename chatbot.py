from typing import Annotated
import os
import uuid
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver


# Step 1: Install packages (run in terminal)
# pip install -U langgraph langchain-openai langchain-core

# Step 2: Set up your API key
# Get API key from environment variable
api_key = os.environ.get("OPENAI_API_KEY", "")

# Setup error handling for missing API key
if not api_key:
    print("Warning: No OpenAI API key found in environment variables.")
    print("Set the OPENAI_API_KEY environment variable for production use.")
    print("This application requires an OpenAI API key to function properly.")
    
    # In production, log the error but don't crash the application
    if os.environ.get("ENVIRONMENT") == "production":
        print("Running in production without API key - chatbot functionality will be limited")

# Initialize the language model with error handling
try:
    # Only initialize if we have an API key
    if api_key:
        # Use ChatOpenAI with the gpt-4o model
        llm = ChatOpenAI(model="gpt-4o")
    else:
        # Create a placeholder that returns a proper message format
        class PlaceholderLLM:
            def invoke(self, messages):
                from langchain_core.messages import AIMessage
                return AIMessage(content="API key is required. Please set the OPENAI_API_KEY environment variable.")
        
        llm = PlaceholderLLM()
        print("Using placeholder LLM due to missing API key")
        
except Exception as e:
    print(f"Error initializing language model: {e}")
    # Create a fallback model that won't crash the application
    class FallbackLLM:
        def invoke(self, messages):
            from langchain_core.messages import AIMessage
            return AIMessage(content=f"Error initializing LLM: {str(e)}. Please check server logs.")
    
    llm = FallbackLLM()


# Step 2: Define the State
class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


# Step 3: Create StateGraph with memory
# Set up memory components
memory = MemorySaver()  # For short-term memory (conversation history)

graph_builder = StateGraph(State)


# Step 4: Add a chatbot node
def chatbot(state: State):
    """Chatbot node that processes messages and returns a response"""
    # Access the conversation history from state
    messages = state.get('messages', [])
    
    # Generate response using the LLM
    response = llm.invoke(messages)
    
    # Return the response in the correct format
    return {"messages": [response]}


# Add the node to the graph
graph_builder.add_node("chatbot", chatbot)

# Step 5: Add edges - from START to chatbot, and chatbot to END
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# Step 6: Compile the graph with memory components
graph = graph_builder.compile(checkpointer=memory)


# Step 7: Visualize the graph (optional)
def visualize_graph():
    """Optional function to visualize the graph"""
    try:
        from IPython.display import Image, display
        display(Image(graph.get_graph().draw_mermaid_png()))
    except Exception:
        print("Graph visualization requires additional dependencies.")
        print("You can install them with: pip install -U 'langgraph[drawing]'")
        # Show ASCII representation as fallback
        try:
            print(graph.get_graph().draw_ascii())
        except:
            print("Could not display graph visualization.")


# Step 8: Run the chatbot with memory
def stream_graph_updates(user_input: str, thread_id: str = None):
    """Stream the graph updates for a given user input with memory"""
    # Generate a thread ID if not provided
    if thread_id is None:
        thread_id = str(uuid.uuid4())
    
    # Prepare the config with thread_id for memory persistence
    config = {"configurable": {"thread_id": thread_id}}
    
    # Create a proper HumanMessage
    user_message = HumanMessage(content=user_input)
    
    # Stream the response with thread_id for memory persistence
    try:
        for event in graph.stream(
            {"messages": [user_message]},
            config,
            stream_mode="values"
        ):
            # Get the last message from the assistant
            if event["messages"]:
                last_message = event["messages"][-1]
                # Only print if it's not the user's message
                if hasattr(last_message, 'content') and last_message.content != user_input:
                    print("Assistant:", last_message.content)
    except Exception as e:
        print(f"Error during conversation: {e}")


def main():
    """Main function to run the chatbot with memory"""
    print("🤖 LangGraph Chatbot with Memory is ready!")
    print("Type 'quit', 'exit', or 'q' to end the conversation.")
    print("Type 'new' to start a new conversation thread.")
    print("-" * 50)
    
    # Generate a thread ID for this conversation
    current_thread_id = str(uuid.uuid4())
    print(f"Starting conversation with thread ID: {current_thread_id}")
    
    while True:
        try:
            user_input = input("User: ")
            
            # Handle exit commands
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
                
            # Handle new thread command
            if user_input.lower() == "new":
                current_thread_id = str(uuid.uuid4())
                print(f"Starting new conversation with thread ID: {current_thread_id}")
                continue
            
            # Process the user input with the current thread ID
            stream_graph_updates(user_input, current_thread_id)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break


if __name__ == "__main__":
    # Uncomment the line below if you want to see the graph visualization
    # visualize_graph()
    
    main()