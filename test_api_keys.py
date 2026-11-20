"""
Enhanced test script with Keras fix for Sentence-BERT.
"""

import os
os.environ['TF_USE_LEGACY_KERAS'] = '1'  # Fix Keras compatibility

from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("SkillLens API Key Verification (Enhanced)")
print("=" * 60)
print()

# Test 1: API Keys
print("1. Checking API Keys...")
print("-" * 60)

openai_key = os.getenv("OPENAI_API_KEY")
hf_key = os.getenv("HUGGINGFACE_API_KEY")
serp_key = os.getenv("SERPAPI_KEY")

print(f"[OK] OpenAI API Key: {'Present' if openai_key else 'Missing'}")
print(f"[OK] Hugging Face API Key: {'Present' if hf_key else 'Missing'}")
print(f"[OK] SerpAPI Key: {'Present' if serp_key else 'Missing'}")

# Test 2: Sentence-BERT (Critical for SkillLens)
print()
print("2. Testing Sentence-BERT (Core Feature)...")
print("-" * 60)

try:
    from sentence_transformers import SentenceTransformer
    
    print("  Loading model: all-MiniLM-L6-v2")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    # Test encoding
    test_text = "Python developer with 3 years experience in machine learning"
    embeddings = model.encode(test_text)
    
    print(f"[OK] Sentence-BERT is working!")
    print(f"  Embedding dimension: {len(embeddings)}")
    print(f"  Sample values: [{embeddings[0]:.4f}, {embeddings[1]:.4f}, ...]")
    sentence_bert_working = True
    
except Exception as e:
    print(f"[FAIL] Sentence-BERT failed: {str(e)[:200]}")
    sentence_bert_working = False

# Test 3: SerpAPI (Job Market Intelligence)
print()
print("3. Testing SerpAPI (Job Intelligence)...")
print("-" * 60)

try:
    import requests
    
    url = "https://serpapi.com/search"
    params = {
        "api_key": serp_key,
        "engine": "google_jobs",
        "q": "Data Engineer",
        "location": "United States",
        "num": 1
    }
    
    response = requests.get(url, params=params, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] SerpAPI is working!")
        print(f"  Status: {response.status_code}")
        if "search_metadata" in data:
            print(f"  Search time: {data['search_metadata'].get('total_time_taken', 'N/A')}s")
        serp_working = True
    else:
        print(f"[FAIL] SerpAPI status: {response.status_code}")
        serp_working = False
        
except Exception as e:
    print(f"[FAIL] SerpAPI failed: {str(e)[:200]}")
    serp_working = False

# Test 4: OpenAI (Optional - has fallback)
print()
print("4. Testing OpenAI (Optional - System has fallback)...")
print("-" * 60)

try:
    from openai import OpenAI
    client = OpenAI(api_key=openai_key)
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say OK"}],
        max_tokens=5
    )
    
    print(f"[OK] OpenAI is working!")
    print(f"  Response: {response.choices[0].message.content}")
    openai_working = True
    
except Exception as e:
    error_msg = str(e)
    if "429" in error_msg or "quota" in error_msg.lower():
        print(f"[INFO] OpenAI quota exceeded - using template-based fallback")
        print(f"  SkillLens will use rule-based explanations instead")
    else:
        print(f"[FAIL] OpenAI error: {error_msg[:200]}")
    openai_working = False

# Summary
print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)

core_features = {
    "Resume Intelligence (Sentence-BERT)": sentence_bert_working,
    "Job Market Data (SerpAPI)": serp_working,
}

optional_features = {
    "AI Explanations (OpenAI)": openai_working,
}

print()
print("Core Features:")
for feature, status in core_features.items():
    status_text = "[OK]" if status else "[FAIL]"
    print(f"  {status_text} {feature}")

print()
print("Optional Features (have fallbacks):")
for feature, status in optional_features.items():
    status_text = "[OK]" if status else "[FALLBACK]"
    print(f"  {status_text} {feature}")

print()
all_core_working = all(core_features.values())

if all_core_working:
    print("[SUCCESS] All core features are operational!")
    print("SkillLens is ready to run.")
else:
    print("[WARNING] Some core features failed.")
    print("Please check the errors above.")

print("=" * 60)
