from swarm import Agent, Swarm
from swarm.core import Result  # Adjusted import

def reward_function(context_variables, last_message: str):
    """
    A simple reward function that assigns a score based on whether the last message
    includes any positive keywords.
    """
    positive_keywords = ["thank", "good", "great", "excellent", "happy"]
    reward = 0.0
    for word in positive_keywords:
        if word in last_message.lower():
            reward += 0.2  # Increase reward for each positive keyword
    reward = min(reward, 1.0)
    context_variables["reward"] = reward
    return Result(value=last_message, context_variables=context_variables)

# Create an agent whose role is to evaluate a response.
reward_agent = Agent(
    name="Reward Evaluator",
    instructions="You are an evaluator that assigns a reward to an agent's response.",
    functions=[reward_function],
)

client = Swarm()

# Example message from another agent that we want to score.
messages = [{
    "role": "assistant", 
    "content": "Thank you for your inquiry. I'm happy to help you today."
}]

response = client.run(
    agent=reward_agent,
    messages=messages,
    context_variables={}
)

print("Evaluated Reward:", response.context_variables.get("reward"))
