from typing import Annotated, Dict, Any
import os
import uuid
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver


# Step 1: Install packages (run in terminal)
# pip install -U langgraph langsmith
# pip install -U "langchain[openai]"  # or your preferred provider

# Step 2: Set up your API key
# Choose one of the following based on your preferred provider:

# For OpenAI:
# Get API key from environment variable
api_key = os.environ.get("OPENAI_API_KEY", "")

# Setup error handling for missing API key
if not api_key:
    print("Warning: No OpenAI API key found in environment variables.")
    print("Set the OPENAI_API_KEY environment variable for production use.")
    print("This application requires an OpenAI API key to function properly.")
    
    # In production, log the error but don't crash the application
    # This allows the web server to start and show a proper error message
    if os.environ.get("ENVIRONMENT") == "production":
        print("Running in production without API key - chatbot functionality will be limited")

# Initialize the language model with error handling
try:
    # Only initialize if we have an API key
    if api_key:
        # Use ChatOpenAI with the gpt-4o model
        llm = ChatOpenAI(model="gpt-4o")
    else:
        # Create a placeholder for development without crashing
        from langchain.chat_models.base import BaseChatModel
        class PlaceholderLLM(BaseChatModel):
            def _generate(self, messages, stop=None, run_manager=None, **kwargs):
                return {"content": "API key is required. Please set the OPENAI_API_KEY environment variable."}
        llm = PlaceholderLLM()
        print("Using placeholder LLM due to missing API key")
except Exception as e:
    print(f"Error initializing language model: {e}")
    # Create a fallback model that won't crash the application
    from langchain.chat_models.base import BaseChatModel
    class FallbackLLM(BaseChatModel):
        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            return {"content": f"Error initializing LLM: {str(e)}. Please check server logs."}
    llm = FallbackLLM()

# For Anthropic:
# os.environ["ANTHROPIC_API_KEY"] = "sk-ant-your-key-here"
# llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")

# For Google Gemini:
# os.environ["GOOGLE_API_KEY"] = "your-key-here"
# llm = init_chat_model("google:gemini-1.5-pro")

# Replace this with your actual API key and model choice
#os.environ["ANTHROPIC_API_KEY"] = "your-api-key-here"
#llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")


# Step 2: Define the State
class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


# Step 2: Create StateGraph with memory
# Set up memory components
memory = MemorySaver()  # For short-term memory (conversation history)

graph_builder = StateGraph(State)


# Step 3: Add a chatbot node
def chatbot(state: State):
    # Access the conversation history from state
    messages = state.get('messages', [])
    
    # Generate response using the LLM
    response = llm.invoke(messages)
    
    return {"messages": [response]}


# Add the node to the graph
graph_builder.add_node("chatbot", chatbot)

# Step 4: Add an entry point
graph_builder.add_edge(START, "chatbot")

# Step 5: Compile the graph with memory components
graph = graph_builder.compile(checkpointer=memory)

# Step 6: Visualize the graph (optional)
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


# Step 7: Run the chatbot with memory
def stream_graph_updates(user_input: str, thread_id: str = None):
    """Stream the graph updates for a given user input with memory"""
    # Generate a thread ID if not provided
    if thread_id is None:
        thread_id = str(uuid.uuid4())
    
    # Prepare the config with thread_id for memory persistence
    config = {"configurable": {"thread_id": thread_id}}
    
    # Stream the response with thread_id for memory persistence
    for event in graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="values"
    ):
        print("Assistant:", event["messages"][-1].content)


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
            print("Traceback:", e.__traceback__)
            break


if __name__ == "__main__":
    # Uncomment the line below if you want to see the graph visualization
    # visualize_graph()
    
    main()