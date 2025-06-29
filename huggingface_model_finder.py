#!/usr/bin/env python3
"""
Hugging Face Model Finder
Sök och jämför AI-modeller på Hugging Face
"""
import requests
import json
from typing import List, Dict, Optional
import webbrowser
from datetime import datetime

class HuggingFaceModelFinder:
    def __init__(self):
        self.base_url = "https://huggingface.co/api"
        self.models_url = f"{self.base_url}/models"
        
    def search_models(self, 
                     query: str = "", 
                     task: Optional[str] = None,
                     library: Optional[str] = None,
                     language: Optional[str] = None,
                     sort: str = "downloads",
                     limit: int = 20) -> List[Dict]:
        """
        Sök modeller på Hugging Face
        
        Args:
            query: Sökterm
            task: Uppgift (text-generation, text-classification, etc)
            library: Bibliotek (transformers, pytorch, tensorflow)
            language: Språk (en, sv, etc)
            sort: Sortering (downloads, likes, modified)
            limit: Max antal resultat
        """
        params = {
            "search": query,
            "sort": sort,
            "limit": limit,
            "full": True
        }
        
        if task:
            params["filter"] = task
        if library:
            params["library"] = library
        if language:
            params["language"] = language
            
        try:
            response = requests.get(self.models_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []
    
    def get_model_details(self, model_id: str) -> Dict:
        """Hämta detaljer om en specifik modell"""
        try:
            response = requests.get(f"{self.models_url}/{model_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching model details: {e}")
            return {}
    
    def find_similar_models(self, reference_model: str, limit: int = 10) -> List[Dict]:
        """Hitta modeller liknande en referensmodell"""
        # Hämta detaljer om referensmodellen
        ref_details = self.get_model_details(reference_model)
        if not ref_details:
            return []
        
        # Extrahera egenskaper
        task = ref_details.get("pipeline_tag", "")
        tags = ref_details.get("tags", [])
        
        # Sök liknande modeller
        similar = []
        
        # Sök baserat på task
        if task:
            task_models = self.search_models(task=task, limit=limit*2)
            similar.extend(task_models)
        
        # Sök baserat på tags
        for tag in tags[:3]:  # Använd top 3 tags
            tag_models = self.search_models(query=tag, limit=limit)
            similar.extend(tag_models)
        
        # Ta bort dubbletter och referensmodellen
        seen = set()
        unique_similar = []
        for model in similar:
            model_id = model.get("modelId", "")
            if model_id and model_id != reference_model and model_id not in seen:
                seen.add(model_id)
                unique_similar.append(model)
        
        return unique_similar[:limit]
    
    def print_model_info(self, model: Dict):
        """Skriv ut modellinformation"""
        print(f"\n{'='*60}")
        print(f"Model: {model.get('modelId', 'Unknown')}")
        print(f"{'='*60}")
        print(f"Task: {model.get('pipeline_tag', 'N/A')}")
        print(f"Downloads: {model.get('downloads', 0):,}")
        print(f"Likes: {model.get('likes', 0)}")
        print(f"Language: {', '.join(model.get('languages', ['N/A']))}")
        print(f"Tags: {', '.join(model.get('tags', [])[:5])}")
        print(f"Library: {model.get('library_name', 'N/A')}")
        print(f"Updated: {model.get('lastModified', 'N/A')}")
        print(f"URL: https://huggingface.co/{model.get('modelId', '')}")
        
        if model.get('description'):
            desc = model['description'][:200] + "..." if len(model.get('description', '')) > 200 else model['description']
            print(f"Description: {desc}")
    
    def interactive_search(self):
        """Interaktiv sökning"""
        print("🤗 Hugging Face Model Finder")
        print("="*60)
        
        while True:
            print("\nVälj en åtgärd:")
            print("1. Sök modeller")
            print("2. Hitta liknande modeller")
            print("3. Populära modeller per kategori")
            print("4. Avsluta")
            
            choice = input("\nVal (1-4): ").strip()
            
            if choice == "1":
                self.search_interactive()
            elif choice == "2":
                self.find_similar_interactive()
            elif choice == "3":
                self.show_popular_by_category()
            elif choice == "4":
                break
            else:
                print("Ogiltigt val!")
    
    def search_interactive(self):
        """Interaktiv sökning"""
        print("\n--- SÖK MODELLER ---")
        query = input("Sökterm (eller enter för alla): ").strip()
        
        print("\nVälj uppgift (task):")
        tasks = [
            "text-generation",
            "text-classification", 
            "token-classification",
            "question-answering",
            "summarization",
            "translation",
            "conversational",
            "fill-mask",
            "zero-shot-classification",
            "table-question-answering",
            "sentence-similarity",
            "text-to-image",
            "image-classification",
            "object-detection",
            "audio-classification",
            "automatic-speech-recognition",
            "text-to-speech"
        ]
        
        print("0. Alla uppgifter")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")
        
        task_choice = input("\nVälj uppgift (0-17): ").strip()
        task = None
        if task_choice.isdigit() and 1 <= int(task_choice) <= len(tasks):
            task = tasks[int(task_choice) - 1]
        
        # Språkval
        language = input("Språk (en, sv, etc. eller enter för alla): ").strip() or None
        
        # Sök
        print("\nSöker...")
        models = self.search_models(query=query, task=task, language=language)
        
        if not models:
            print("Inga modeller hittades!")
            return
        
        print(f"\nHittade {len(models)} modeller:")
        for i, model in enumerate(models[:20], 1):
            print(f"{i}. {model.get('modelId')} - {model.get('pipeline_tag', 'N/A')} ({model.get('downloads', 0):,} downloads)")
        
        # Visa detaljer
        detail_choice = input("\nVisa detaljer för modell (nummer eller enter för att hoppa över): ").strip()
        if detail_choice.isdigit() and 1 <= int(detail_choice) <= len(models):
            self.print_model_info(models[int(detail_choice) - 1])
            
            # Öppna i webbläsare
            open_web = input("\nÖppna i webbläsare? (j/n): ").strip().lower()
            if open_web == 'j':
                model_id = models[int(detail_choice) - 1].get('modelId')
                webbrowser.open(f"https://huggingface.co/{model_id}")
    
    def find_similar_interactive(self):
        """Hitta liknande modeller interaktivt"""
        print("\n--- HITTA LIKNANDE MODELLER ---")
        reference = input("Ange modell-ID (t.ex. 'gpt2', 'bert-base-uncased'): ").strip()
        
        if not reference:
            print("Du måste ange ett modell-ID!")
            return
        
        print(f"\nSöker modeller liknande '{reference}'...")
        similar = self.find_similar_models(reference)
        
        if not similar:
            print("Inga liknande modeller hittades!")
            return
        
        print(f"\nHittade {len(similar)} liknande modeller:")
        for i, model in enumerate(similar[:10], 1):
            print(f"{i}. {model.get('modelId')} - {model.get('pipeline_tag', 'N/A')} ({model.get('downloads', 0):,} downloads)")
        
        # Visa detaljer
        detail_choice = input("\nVisa detaljer för modell (nummer eller enter för att hoppa över): ").strip()
        if detail_choice.isdigit() and 1 <= int(detail_choice) <= len(similar):
            self.print_model_info(similar[int(detail_choice) - 1])
    
    def show_popular_by_category(self):
        """Visa populära modeller per kategori"""
        print("\n--- POPULÄRA MODELLER PER KATEGORI ---")
        
        categories = {
            "Text Generation": "text-generation",
            "Text Classification": "text-classification",
            "Translation": "translation",
            "Summarization": "summarization",
            "Question Answering": "question-answering",
            "Image Classification": "image-classification",
            "Object Detection": "object-detection",
            "Speech Recognition": "automatic-speech-recognition"
        }
        
        for name, task in categories.items():
            print(f"\n{name}:")
            models = self.search_models(task=task, limit=5)
            for i, model in enumerate(models[:3], 1):
                print(f"  {i}. {model.get('modelId')} ({model.get('downloads', 0):,} downloads)")
    
    def export_results(self, models: List[Dict], filename: str):
        """Exportera sökresultat till JSON"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "count": len(models),
            "models": models
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Resultat exporterade till {filename}")

# Exempel på användning av olika modelltyper
def print_model_examples():
    """Visa exempel på populära modeller"""
    print("\n🤗 EXEMPEL PÅ POPULÄRA AI-MODELLER")
    print("="*60)
    
    examples = {
        "Text Generation (LLM)": [
            "meta-llama/Llama-2-7b-hf - Llama 2 från Meta",
            "mistralai/Mistral-7B-v0.1 - Mistral 7B",
            "google/flan-t5-base - Google's FLAN-T5",
            "EleutherAI/gpt-neo-2.7B - GPT-Neo open source",
            "bigscience/bloom - BLOOM multilingual"
        ],
        "Svenska modeller": [
            "KBLab/bert-base-swedish-cased - Svensk BERT",
            "AI-Sweden/gpt-sw3-126m - GPT-SW3 svensk",
            "Tungsten/gpt-sw3-1b - Svensk GPT variant"
        ],
        "Coding/Programming": [
            "codellama/CodeLlama-7b-Python-hf - Code Llama för Python",
            "microsoft/codebert-base - CodeBERT",
            "Salesforce/codegen-350M-mono - CodeGen"
        ],
        "Text Classification": [
            "distilbert-base-uncased-finetuned-sst-2-english - Sentiment",
            "cardiffnlp/twitter-roberta-base-sentiment - Twitter sentiment",
            "ProsusAI/finbert - Financial sentiment"
        ],
        "Computer Vision": [
            "openai/clip-vit-base-patch32 - CLIP vision+text",
            "google/vit-base-patch16-224 - Vision Transformer",
            "microsoft/resnet-50 - ResNet-50"
        ],
        "Multimodal": [
            "Salesforce/blip-image-captioning-base - Image captioning",
            "microsoft/layoutlmv3-base - Document understanding",
            "openai/whisper-base - Speech recognition"
        ]
    }
    
    for category, models in examples.items():
        print(f"\n{category}:")
        for model in models:
            print(f"  • {model}")
    
    print("\n" + "="*60)
    print("Tips: Använd model finder för att hitta fler modeller!")

if __name__ == "__main__":
    # Visa exempel först
    print_model_examples()
    
    # Starta interaktiv sökning
    finder = HuggingFaceModelFinder()
    finder.interactive_search()