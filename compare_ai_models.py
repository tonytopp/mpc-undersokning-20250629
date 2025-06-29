#!/usr/bin/env python3
"""
AI Model Comparison Tool
Jämför olika AI-modeller och deras egenskaper
"""

# Kategorisering av populära AI-modeller
AI_MODELS = {
    "Large Language Models (LLMs)": {
        "GPT-serien": [
            {"name": "GPT-4", "params": "1.76T", "company": "OpenAI", "type": "Proprietary", "strengths": "Mest avancerad, multimodal"},
            {"name": "GPT-3.5", "params": "175B", "company": "OpenAI", "type": "Proprietary", "strengths": "Snabb, kostnadseffektiv"},
            {"name": "ChatGPT", "params": "20B", "company": "OpenAI", "type": "Proprietary", "strengths": "Optimerad för dialog"},
        ],
        "Claude-serien": [
            {"name": "Claude 3 Opus", "params": "?", "company": "Anthropic", "type": "Proprietary", "strengths": "Mycket stor kontext, säker"},
            {"name": "Claude 3 Sonnet", "params": "?", "company": "Anthropic", "type": "Proprietary", "strengths": "Balanserad prestanda"},
            {"name": "Claude 3 Haiku", "params": "?", "company": "Anthropic", "type": "Proprietary", "strengths": "Snabb, kostnadseffektiv"},
        ],
        "Llama-serien": [
            {"name": "Llama 2 70B", "params": "70B", "company": "Meta", "type": "Open Source", "strengths": "Kraftfull, open source"},
            {"name": "Llama 2 13B", "params": "13B", "company": "Meta", "type": "Open Source", "strengths": "Bra balans storlek/prestanda"},
            {"name": "Llama 2 7B", "params": "7B", "company": "Meta", "type": "Open Source", "strengths": "Kan köras lokalt"},
            {"name": "Code Llama", "params": "7-34B", "company": "Meta", "type": "Open Source", "strengths": "Specialiserad på kod"},
        ],
        "Mistral-serien": [
            {"name": "Mixtral 8x7B", "params": "56B", "company": "Mistral AI", "type": "Open Source", "strengths": "MoE arkitektur, effektiv"},
            {"name": "Mistral 7B", "params": "7B", "company": "Mistral AI", "type": "Open Source", "strengths": "Liten men kraftfull"},
        ],
        "Google-modeller": [
            {"name": "Gemini Ultra", "params": "?", "company": "Google", "type": "Proprietary", "strengths": "Multimodal, konkurrerar med GPT-4"},
            {"name": "Gemini Pro", "params": "?", "company": "Google", "type": "Proprietary", "strengths": "Balanserad prestanda"},
            {"name": "PaLM 2", "params": "340B", "company": "Google", "type": "Proprietary", "strengths": "Multilingual, reasoning"},
            {"name": "FLAN-T5", "params": "11B", "company": "Google", "type": "Open Source", "strengths": "Instruction-tuned"},
        ],
        "Andra open source": [
            {"name": "Falcon 180B", "params": "180B", "company": "TII", "type": "Open Source", "strengths": "Stor open source modell"},
            {"name": "MPT-30B", "params": "30B", "company": "MosaicML", "type": "Open Source", "strengths": "Lång kontext (8k)"},
            {"name": "StableLM", "params": "3-7B", "company": "Stability AI", "type": "Open Source", "strengths": "Liten, effektiv"},
            {"name": "Vicuna", "params": "7-33B", "company": "LMSYS", "type": "Open Source", "strengths": "Fine-tuned Llama"},
            {"name": "Alpaca", "params": "7B", "company": "Stanford", "type": "Open Source", "strengths": "Instruction-following"},
        ],
        "Kinesiska modeller": [
            {"name": "Qwen", "params": "7-72B", "company": "Alibaba", "type": "Open Source", "strengths": "Multilingual, stark på kinesiska"},
            {"name": "ChatGLM", "params": "6-130B", "company": "Tsinghua", "type": "Open Source", "strengths": "Kinesisk-engelsk"},
            {"name": "Baichuan", "params": "7-13B", "company": "Baichuan", "type": "Open Source", "strengths": "Kinesisk fokus"},
        ],
    },
    "Specialized Models": {
        "Kod-modeller": [
            {"name": "GitHub Copilot", "params": "12B", "company": "GitHub/OpenAI", "type": "Proprietary", "strengths": "IDE-integration"},
            {"name": "Code Llama", "params": "7-34B", "company": "Meta", "type": "Open Source", "strengths": "Specialiserad kodgenerering"},
            {"name": "StarCoder", "params": "15B", "company": "BigCode", "type": "Open Source", "strengths": "Tränad på Github"},
            {"name": "CodeGen", "params": "16B", "company": "Salesforce", "type": "Open Source", "strengths": "Multi-language support"},
            {"name": "DeepSeek Coder", "params": "33B", "company": "DeepSeek", "type": "Open Source", "strengths": "Stark kodförståelse"},
        ],
        "Multimodala": [
            {"name": "GPT-4V", "params": "?", "company": "OpenAI", "type": "Proprietary", "strengths": "Text + bild förståelse"},
            {"name": "DALL-E 3", "params": "?", "company": "OpenAI", "type": "Proprietary", "strengths": "Text-till-bild generering"},
            {"name": "Midjourney", "params": "?", "company": "Midjourney", "type": "Proprietary", "strengths": "Konstnärlig bildgenerering"},
            {"name": "Stable Diffusion", "params": "1B", "company": "Stability AI", "type": "Open Source", "strengths": "Open source bildgenerering"},
            {"name": "CLIP", "params": "400M", "company": "OpenAI", "type": "Open Source", "strengths": "Bild-text matching"},
        ],
        "Svenska modeller": [
            {"name": "GPT-SW3", "params": "126M-40B", "company": "AI Sweden", "type": "Open Source", "strengths": "Tränad på svenska data"},
            {"name": "KB-BERT", "params": "110M", "company": "KB Lab", "type": "Open Source", "strengths": "Svensk BERT-modell"},
        ],
    },
    "Embedding Models": [
        {"name": "text-embedding-ada-002", "params": "?", "company": "OpenAI", "type": "Proprietary", "strengths": "Hög kvalitet, 1536 dim"},
        {"name": "all-MiniLM-L6-v2", "params": "22M", "company": "Sentence Transformers", "type": "Open Source", "strengths": "Snabb, bra kvalitet"},
        {"name": "e5-large", "params": "335M", "company": "Microsoft", "type": "Open Source", "strengths": "Multilingual"},
        {"name": "bge-large", "params": "335M", "company": "BAAI", "type": "Open Source", "strengths": "Topp-rankad"},
    ],
}

def print_colored(text, color="default"):
    """Skriv ut färgad text"""
    colors = {
        "header": "\033[95m",
        "blue": "\033[94m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "bold": "\033[1m",
        "default": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['default']}")

def display_model_comparison():
    """Visa jämförelse av AI-modeller"""
    print_colored("="*80, "header")
    print_colored("AI MODEL COMPARISON GUIDE", "header")
    print_colored("="*80, "header")
    
    for category, subcategories in AI_MODELS.items():
        print_colored(f"\n{category}", "bold")
        print_colored("-"*len(category), "blue")
        
        if isinstance(subcategories, dict):
            for subcat, models in subcategories.items():
                print_colored(f"\n  {subcat}:", "green")
                for model in models:
                    print(f"    • {model['name']} ({model['params']}) - {model['company']}")
                    print(f"      Type: {model['type']} | Strengths: {model['strengths']}")
        else:
            for model in subcategories:
                print(f"  • {model['name']} ({model['params']}) - {model['company']}")
                print(f"    Type: {model['type']} | Strengths: {model['strengths']}")

def find_models_by_criteria():
    """Hitta modeller baserat på kriterier"""
    print_colored("\nFIND MODELS BY CRITERIA", "header")
    print("1. Open Source only")
    print("2. Proprietary only")
    print("3. By company")
    print("4. By size")
    print("5. By use case")
    
    choice = input("\nChoose criteria (1-5): ").strip()
    
    all_models = []
    for category, subcategories in AI_MODELS.items():
        if isinstance(subcategories, dict):
            for subcat, models in subcategories.items():
                all_models.extend(models)
        else:
            all_models.extend(subcategories)
    
    if choice == "1":
        filtered = [m for m in all_models if m["type"] == "Open Source"]
        print_colored("\nOPEN SOURCE MODELS:", "green")
    elif choice == "2":
        filtered = [m for m in all_models if m["type"] == "Proprietary"]
        print_colored("\nPROPRIETARY MODELS:", "yellow")
    elif choice == "3":
        company = input("Enter company name: ").strip()
        filtered = [m for m in all_models if company.lower() in m["company"].lower()]
        print_colored(f"\nMODELS BY {company.upper()}:", "blue")
    elif choice == "4":
        print("Size categories: 1) <10B  2) 10-50B  3) 50-100B  4) >100B")
        size_choice = input("Choose size: ").strip()
        # Size filtering logic here
        filtered = all_models  # Simplified
        print_colored("\nMODELS BY SIZE:", "blue")
    elif choice == "5":
        print("Use cases: 1) General  2) Code  3) Images  4) Swedish")
        use_choice = input("Choose use case: ").strip()
        # Use case filtering logic here
        filtered = all_models  # Simplified
        print_colored("\nMODELS BY USE CASE:", "blue")
    else:
        filtered = []
    
    for model in filtered:
        print(f"• {model['name']} ({model['params']}) - {model['company']}")
        print(f"  {model['strengths']}")

def compare_specific_models():
    """Jämför specifika modeller"""
    print_colored("\nMODEL COMPARISON MATRIX", "header")
    
    # Exempel på detaljerad jämförelse
    comparison = {
        "Model": ["GPT-4", "Claude 3", "Llama 2 70B", "Mistral 7B"],
        "Context Window": ["8K-32K", "200K", "4K", "8K"],
        "Speed": ["Slow", "Medium", "Medium", "Fast"],
        "Cost": ["High", "Medium", "Free*", "Free*"],
        "Strengths": ["Most capable", "Long context", "Open source", "Efficient"],
        "Best for": ["Complex tasks", "Long documents", "Self-hosting", "Local use"]
    }
    
    # Print comparison table
    for key, values in comparison.items():
        print(f"\n{key:15}", end="")
        for value in values:
            print(f"{value:15}", end="")
    print("\n" + "-"*75)
    print("* Free to use if self-hosted, may have API costs through providers")

def recommendations():
    """Ge rekommendationer baserat på användningsfall"""
    print_colored("\nRECOMMENDATIONS BY USE CASE", "header")
    
    use_cases = {
        "General Assistant": ["Claude 3 Sonnet", "GPT-3.5", "Llama 2 13B"],
        "Code Generation": ["GPT-4", "Code Llama", "DeepSeek Coder"],
        "Local/Offline Use": ["Llama 2 7B", "Mistral 7B", "StableLM"],
        "Long Documents": ["Claude 3 (any)", "GPT-4-32K", "MPT-30B"],
        "Budget Conscious": ["Mistral 7B", "Llama 2 7B", "FLAN-T5"],
        "Swedish Content": ["GPT-SW3", "GPT-4", "Claude 3"],
        "Image Generation": ["DALL-E 3", "Midjourney", "Stable Diffusion"],
        "Embeddings": ["text-embedding-ada-002", "bge-large", "e5-large"]
    }
    
    for use_case, models in use_cases.items():
        print_colored(f"\n{use_case}:", "green")
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model}")

if __name__ == "__main__":
    while True:
        print_colored("\n" + "="*50, "blue")
        print_colored("AI MODEL COMPARISON TOOL", "bold")
        print_colored("="*50, "blue")
        print("\n1. View all models")
        print("2. Find models by criteria")
        print("3. Compare specific models")
        print("4. Get recommendations")
        print("5. Exit")
        
        choice = input("\nChoose option (1-5): ").strip()
        
        if choice == "1":
            display_model_comparison()
        elif choice == "2":
            find_models_by_criteria()
        elif choice == "3":
            compare_specific_models()
        elif choice == "4":
            recommendations()
        elif choice == "5":
            break
        else:
            print_colored("Invalid choice!", "red")
        
        input("\nPress Enter to continue...")