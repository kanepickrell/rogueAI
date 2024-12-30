from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)

class SimpleLLM:
    def __init__(self, model_name="meta-llama/Llama-3.2-1B-Instruct"):
        """Initialize the LLM with model"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        torch_dtype = torch.float16 if self.device.type == "cuda" else torch.float32
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
            device_map="auto" if self.device.type == "cuda" else None,
            low_cpu_mem_usage=True
        )
        
        if self.device.type == "cpu":
            self.model = self.model.to(self.device)

    def get_answer(self, query, context, max_length=500):
        prompt = f"""<|system|>You are an AI assistant specializing in cybersecurity. Use the provided context to provide an answer the question:

{context}

Answer directly and precisely.</s><|user|>{query}</s><|assistant|>"""

        prompt_encoded = self.tokenizer(prompt, truncation=True, padding=False, return_tensors="pt")
        input_ids = prompt_encoded.input_ids.to(self.device)
        attention_mask = prompt_encoded.attention_mask.to(self.device)
        
        self.model.eval()
        with torch.no_grad():
            output = self.model.generate(
                input_ids=input_ids,
                max_new_tokens=max_length,
                attention_mask=attention_mask,
                temperature=0.3,
                pad_token_id=self.tokenizer.pad_token_id
            )
        
        answer = self.tokenizer.decode(output[0], skip_special_tokens=True)
        # Split on assistant tag and take the last part
        parts = answer.split("<|assistant|>")
        return parts[-1].strip() if len(parts) > 1 else "Unable to generate response"

query = "What can you tell me about Mystery 31?"
context = """
|   0 | 1         | 2    | 3        | 4                     | 5             | 6      | 7           | 8                  |
|----:|:----------|:-----|:---------|:----------------------|:--------------|:-------|:------------|:-------------------|
|     |           |      |          |                       |               |        | Mystery-31  |                    |
|     |           |      |          |                       |               |        | live.       |                    |
|  32 | 12/7/2022 | APT3 | MYSTERY￾ | Enumerate             | Network       | T1135  | N/A         | N/A                |
|     | 1556      |      | 31       | Network               | Share         |        |             |                    |
|     |           |      |          | Shares                | Discovery     |        |             |                    |
|  33 | 12/7/2022 | APT3 | MYSTERY￾ | Collect               | Data from     | T1039  | N/A         | N/A                |
|     | 0752      |      | 31       | data from             | Network       |        |             |                    |
|     |           |      |          | shares                | Shared Drive  |        |             |                    |
|  34 | 12/7/2022 | APT3 | MYSTERY￾ | Package               | Archive       | T1560. | N/A         |                    |
|     | 1604      |      | 31       | data for exfiltration | Collected     | 001    |             | ckup.zip           |
|     |           |      |          |                       | Data: Archive |        |             |                    |
|     |           |      |          |                       | via Utility   |        |             |                    |
|  35 | 12/7/2022 | APT3 | MYSTERY￾ | Exfiltrate            | Exfiltration  | T1041  | N/A         | N/A                |
|     | 1604      |      | 31       | Data                  | Over C2       |        |             |                    |
|     |           |      |          |                       | Channel       |        |             |                    |
|  36 | 12/7/2022 | APT3 |          |                       |               |        | Exit all    |                    |
|     | 1606      |      |          |                       |               |        | beacons but |                    |
|     |           |      |          |                       |               |        | MUGGLE￾     |                    |
|     |           |      |          |                       |               |        | 16          |                    |
"""

# Run the model
llm = SimpleLLM()
answer = llm.get_answer(query, context)
print("\nQuestion:", query)
print("\nContext:", context)
print("\nAnswer:", answer)