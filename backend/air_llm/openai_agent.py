import asyncio

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(
  api_key=str(os.getenv("OPENAI_API_KEY"))
)

response = client.responses.create(
  model="gpt-5-nano",
  input="write a haiku about ai",
  store=True,
)

print(response.output_text);

async def simple_agent(query: str):
    """
    A simple custom agent that generates synthetic data
    using Chat Completions API
    """



    prompt = f"""Your task is to generate some synthetic data so that it will be useful to answer the user question. Do not mention this is synthetic data in your answer.\n\n{query}"""
    client = AsyncAIRefinery(api_key=api_key)


    response = await client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="meta-llama/Llama-3.1-70B-Instruct",
    )

    return response.choices[0].message.content
