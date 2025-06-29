# AI Model Tools

Verktyg för att söka, jämföra och hitta AI-modeller på Hugging Face och andra plattformar.

## 🤗 Hugging Face Model Finder

Sök och hitta AI-modeller på Hugging Face.

### Installation

```bash
pip install -r requirements.txt
```

### Användning

```bash
python3 huggingface_model_finder.py
```

### Funktioner

1. **Sök modeller** - Sök efter modeller med olika filter:
   - Sökterm (t.ex. "swedish", "code", "chat")
   - Uppgift (text-generation, translation, etc.)
   - Språk (en, sv, etc.)
   - Bibliotek (transformers, pytorch, tensorflow)

2. **Hitta liknande modeller** - Ange en modell och hitta liknande:
   - Exempel: Hitta modeller liknande "gpt2"
   - Baserat på uppgift och taggar

3. **Populära modeller per kategori** - Se toppmodeller för varje kategori

### Exempel på sökningar

```
🤗 Hugging Face Model Finder
============================================================

Välj en åtgärd:
1. Sök modeller
2. Hitta liknande modeller
3. Populära modeller per kategori
4. Avsluta

Val (1-4): 1

--- SÖK MODELLER ---
Sökterm: swedish
Välj uppgift: 2 (text-classification)

Hittade 15 modeller:
1. KBLab/bert-base-swedish-cased - token-classification (1,234,567 downloads)
2. AI-Sweden/gpt-sw3-126m - text-generation (456,789 downloads)
...
```

## 🔍 AI Model Comparison Tool

Jämför olika AI-modeller och deras egenskaper.

### Användning

```bash
python3 compare_ai_models.py
```

### Funktioner

1. **Visa alla modeller** - Komplett lista kategoriserad efter typ
2. **Filtrera modeller** - Hitta modeller baserat på:
   - Open Source vs Proprietary
   - Företag (OpenAI, Meta, Google, etc.)
   - Storlek (<10B, 10-50B, etc.)
   - Användningsområde

3. **Jämför modeller** - Detaljerad jämförelse av populära modeller
4. **Rekommendationer** - Få förslag baserat på användningsfall

### Modellkategorier

#### Large Language Models (LLMs)
- **GPT-serien** (OpenAI): GPT-4, GPT-3.5, ChatGPT
- **Claude-serien** (Anthropic): Opus, Sonnet, Haiku
- **Llama-serien** (Meta): Llama 2 70B/13B/7B, Code Llama
- **Mistral**: Mixtral 8x7B, Mistral 7B
- **Google**: Gemini, PaLM 2, FLAN-T5

#### Specialiserade modeller
- **Kod**: GitHub Copilot, Code Llama, StarCoder, DeepSeek Coder
- **Multimodala**: GPT-4V, DALL-E 3, Stable Diffusion, CLIP
- **Svenska**: GPT-SW3, KB-BERT

### Rekommendationer per användningsfall

| Användningsfall | Rekommenderade modeller |
|----------------|------------------------|
| General Assistant | Claude 3 Sonnet, GPT-3.5, Llama 2 13B |
| Kodgenerering | GPT-4, Code Llama, DeepSeek Coder |
| Lokal körning | Llama 2 7B, Mistral 7B, StableLM |
| Långa dokument | Claude 3, GPT-4-32K, MPT-30B |
| Budget | Mistral 7B, Llama 2 7B, FLAN-T5 |
| Svenska | GPT-SW3, GPT-4, Claude 3 |

## Tips för val av modell

### Open Source vs Proprietary
- **Open Source**: Kan köras lokalt, anpassningsbar, ingen API-kostnad
- **Proprietary**: Ofta bättre prestanda, enkel att använda, API-kostnader

### Storlek vs Prestanda
- **< 7B params**: Kan köras på konsument-GPU
- **7-13B params**: Bra balans, kräver bättre hårdvara
- **> 30B params**: Bäst prestanda, kräver professionell hårdvara

### Användningsområden
- **Allmän text**: GPT-3.5, Claude Sonnet, Llama 2
- **Kod**: Code Llama, StarCoder, DeepSeek Coder
- **Svenska**: GPT-SW3, svensk-finetunead Llama
- **Bilder**: Stable Diffusion, DALL-E 3, Midjourney

## Exempel på Hugging Face modell-IDs

```
# Text Generation
meta-llama/Llama-2-7b-hf
mistralai/Mistral-7B-v0.1
google/flan-t5-base

# Svenska modeller
KBLab/bert-base-swedish-cased
AI-Sweden/gpt-sw3-126m

# Kod
codellama/CodeLlama-7b-Python-hf
Salesforce/codegen-350M-mono

# Multimodal
openai/clip-vit-base-patch32
Salesforce/blip-image-captioning-base
```

## Resurser

- [Hugging Face Model Hub](https://huggingface.co/models)
- [Open LLM Leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)
- [LLM Explorer](https://llm.extractum.io/)
- [AI Model Database](https://www.aimodels.fyi/)