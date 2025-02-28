import os 
from openai import OpenAI


import dotenv



dotenv.load_dotenv()

class GPTService():
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        pass



    def construct_prompt(self, query, contexts):
        prompt = """You are an educational assistant that helps students understand lecture material. 
        You will be given a question and relevant context from lecture slides and materials.
        Please answer the question based on the provided context. If the context doesn't contain 
        relevant information to answer the question, state that and don't make up information.

        Relevant lecture materials:
        """

        # Add contexts
        for i, context in enumerate(contexts):
            print(f"CONTEXT OBJECT: {context}")
            prompt += f"\nContext {i+1} (from {context['metadata']['filename']}):\n{context['text']}\n"

        # Add the query
        prompt += f"\nQuestion: {query}\n\nAnswer:"

        return prompt

    def generate_answer(self, prompt):
        response = self.client.chat.completions.create(model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful educational assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,  # Lower temperature for more factual responses
        max_tokens=1000)

        return response.choices[0].message.content
