from phi.agent import Agent
from phi.model.huggingface import HuggingFaceChat
from phi.tools.duckduckgo import DuckDuckGo
from typing import Optional, Any
import os

class WebSearchAgent:
    def __init__(self):
        # Initialize the HuggingFace model
        self.model = HuggingFaceChat(
            id="Qwen/Qwen2.5-Coder-32B-Instruct",
            # max_tokens=4096,
            # temperature=0.7,
            authorization=os.getenv("HF_TOKEN")
        )
        
        # Initialize the agent with the model and tools
        self.agent = Agent(
            name="Web Search Assistant",
            model=self.model,
            tools=[DuckDuckGo()],
            instructions=[
                "Search the web to find relevant information",
                "Always include sources in your responses",
                "Summarize information clearly and concisely",
                "If multiple sources conflict, mention the discrepancy",
            ],
            show_tool_calls=True,
            markdown=True
        )
    
    def search_and_respond(self, query: str, stream: bool = True) -> Optional[Any]:
        """
        Search the web and generate a response based on the query
        
        Args:
            query (str): The user's question or prompt
            stream (bool): Whether to stream the response or return it as a single output
        
        Returns:
            Optional[Any]: The response from the agent if stream=False
        """
        if stream:
            self.agent.print_response(query, stream=True)
        else:
            return self.agent.run(query)

def main():
    # Ensure HF_TOKEN is set
    if "HF_TOKEN" not in os.environ:
        raise EnvironmentError(
            "Please set your HF_TOKEN environment variable. "
            "You can get one from https://huggingface.co/settings/tokens"
        )
    
    # Initialize the web agent
    web_agent = WebSearchAgent()
    
    # Example usage
    while True:
        try:
            user_input = input("\nEnter your question (or 'quit' to exit): ")
            if user_input.lower() in ['quit', 'exit']:
                break
                
            web_agent.search_and_respond(user_input)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()