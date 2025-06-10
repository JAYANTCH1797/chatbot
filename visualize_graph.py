from chatbot import graph
import os

def visualize_graph():
    """Function to visualize the graph and save it as a PNG file"""
    try:
        # Create a directory for the visualization if it doesn't exist
        os.makedirs("visualizations", exist_ok=True)
        
        # Get the graph visualization as PNG data
        png_data = graph.get_graph().draw_mermaid_png()
        
        # Save the PNG data to a file
        with open("visualizations/chatbot_graph.png", "wb") as f:
            f.write(png_data)
        
        print(f"Graph visualization saved to visualizations/chatbot_graph.png")
        
        # Try to display the ASCII representation
        try:
            print("\nASCII representation of the graph:")
            print(graph.get_graph().draw_ascii())
        except Exception as e:
            print(f"Could not display ASCII graph: {e}")
        
    except Exception as e:
        print(f"Error visualizing graph: {e}")
        print("Make sure you have graphviz and the required dependencies installed.")
        print("You can install them with: pip install 'langgraph[drawing]' graphviz pydot")

if __name__ == "__main__":
    visualize_graph()
