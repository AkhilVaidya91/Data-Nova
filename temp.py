from smolagents import CodeAgent, HfApiModel, DuckDuckGoSearchTool

def create_web_agent(hf_token=None):
    """
    Creates a web agent that can search and process web data using DuckDuckGo search.
    
    Args:
        hf_token (str, optional): HuggingFace API token for accessing gated models
    
    Returns:
        CodeAgent: Configured web agent
    """
    # Initialize the model - using a capable model for better response generation
    model = HfApiModel(
        # model_id="mistralai/Mixtral-8x7B-Instruct-v0.1",  # You can change this to any preferred model
        # token=hf_token
    )
    
    # Create the agent with DuckDuckGoSearchTool
    agent = CodeAgent(
        tools=[DuckDuckGoSearchTool()],
        model=model,
        name="web_search_agent",
        description="A specialized agent that searches the web and generates informative responses based on search results. You respond in a simple markdown format.",
    )
    
    return agent

def query_web_agent(agent, prompt):
    """
    Query the web agent with a prompt and get a response.
    
    Args:
        agent (CodeAgent): The initialized web agent
        prompt (str): User query/prompt
        
    Returns:
        str: Agent's response
    """
    return agent.run(prompt)

# Example usage
if __name__ == "__main__":
    # Initialize the agent
    agent = create_web_agent()
    
    # Example query
    response = query_web_agent(
        agent,
        "Give me short one line description about each of the 17 UN SDGs"
    )
    print(response)