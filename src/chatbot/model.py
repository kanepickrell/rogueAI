import torch
from transformers import TextStreamer
import time
# from unsloth import FastLanguageModel  # Commented out for local testing

class ChatModel:
    def __init__(self, model_name="gopher93/lora_model", max_seq_length=512, use_gpu=True):
        self.model_name = model_name
        self.max_seq_length = max_seq_length
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.model = None
        self.tokenizer = None
        
    @classmethod
    def mock_model(cls):
        """Create a mock model instance for testing"""
        instance = cls()
        instance.model = None
        instance.tokenizer = None
        return instance
        
    def load(self):
        """Load the model and tokenizer"""
        print("Loading model...")
        t0 = time.time()

        try:
            # Initialize model and tokenizer using Unsloth
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.model_name,
                max_seq_length=self.max_seq_length,
                dtype=torch.float16,
                load_in_4bit=False
            )

            # Enable faster inference
            FastLanguageModel.for_inference(self.model)
            print(f"Model load time: {time.time() - t0:.2f}s")
            return True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False

    def generate_response(self, context: str, query: str, 
                         conversation_history=None, max_length: int = 128) -> str:
        """Generate a response based on context and query"""
        t0 = time.time()

        # If model is disabled, return mock response
        if self.model is None:
            return f"This is a mock response. Model is disabled for local testing.\nQuery: {query}\nContext length: {len(context)} characters"

        # Build conversation history string
        conversation_context = ""
        if conversation_history:
            conversation_context = "\n\nPrevious conversation:\n"
            for prev_q, prev_a in conversation_history:
                conversation_context += f"Q: {prev_q}\nA: {prev_a}\n"

        # Format messages
        messages = [
            {"role": "system", "content": "Provide direct, concise answers based on the given context without repeating the context itself."},
            {"role": "user", "content": f"Based on this context: {context}\n{conversation_context}\nQuestion: {query}"}
        ]

        # Tokenize
        t1 = time.time()
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        )
        
        if self.use_gpu:
            inputs = inputs.to("cuda")

        t2 = time.time()

        # Generate
        outputs = self.model.generate(
            input_ids=inputs,
            max_new_tokens=max_length,
            use_cache=True,
            temperature=1.5
        )
        
        # Decode
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract assistant's response
        if "assistant" in response.lower():
            response = response.split("assistant")[-1].strip()

        t3 = time.time()
        print(f"\nTimings:\nPrompt: {t1-t0:.2f}s\nTokenize: {t2-t1:.2f}s\nGenerate: {t3-t2:.2f}s")
        
        return response

    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None and self.tokenizer is not None