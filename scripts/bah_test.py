from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def setup_model(model_name="meta-llama/Llama-3.2-1B-Instruct"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True
    )
    return model, tokenizer

def generate_response(model, tokenizer, context, query, max_length=200):
    prompt = f"""<|system|>You are a helpful AI assistant. Here is some context to help answer the question:
{context}</s>
<|user|>{query}</s>
<|assistant|>"""
    
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(model.device)
    
    outputs = model.generate(
        inputs.input_ids,
        max_new_tokens=max_length,
        temperature=0.7,
        do_sample=True,
        top_p=0.9,
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.split("<|assistant|>")[-1].strip()

def main():
    model, tokenizer = setup_model()
    
    # Example context - edit this
    context = """France is a country in Western Europe.
Its capital is Paris, with a population of over 2 million people."""
    
    print("Chat initialized. Type 'exit' to quit.")
    while True:
        query = input("\nQuestion: ").strip()
        if query.lower() == 'exit':
            break
            
        response = generate_response(model, tokenizer, context, query)
        print("\nAnswer:", response)

if __name__ == "__main__":
    main()