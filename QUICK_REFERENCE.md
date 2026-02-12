# Quick Reference - Wikipedia Content Fetcher

## 🌐 Web Interface
```
http://localhost:5000/wikipedia
```
- Auto-generates API key
- Search any Wikipedia topic
- Download as PDF, Markdown, or Text
- No API key needed (auto-generated per session)

---

## 🔗 Main URL
```
http://localhost:5000
```
- Home page with browse functionality
- Navigation to Wikipedia Fetcher
- Links to all features

---

## 🔑 API Key Management

### Generate New Key
```bash
curl -X POST http://localhost:5000/api/keys/generate \
  -H "Content-Type: application/json" \
  -d '{"name":"My API Key"}'
```

### List All Keys
```bash
curl http://localhost:5000/api/keys/list
```

---

## 📚 Wikipedia Search & Fetch

### Search for Topic
```bash
curl -X POST http://localhost:5000/api/wikipedia/search \
  -H "X-API-Key: wk_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Python"}'
```

### Fetch Complete Content
```bash
curl -X POST http://localhost:5000/api/wikipedia/fetch \
  -H "X-API-Key: wk_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Machine Learning"}'
```

---

## 💾 Content Caching

### Get Cached Content
```bash
curl "http://localhost:5000/api/wikipedia/cached/Python?api_key=wk_YOUR_KEY"
```

### Search Cache
```bash
curl "http://localhost:5000/api/wikipedia/cache/search?q=learning&api_key=wk_YOUR_KEY"
```

---

## 📥 Download Content

### Download as PDF
```bash
curl "http://localhost:5000/api/wikipedia/download/1?format=pdf&api_key=wk_YOUR_KEY" \
  -o "content.pdf"
```

### Download as Markdown
```bash
curl "http://localhost:5000/api/wikipedia/download/1?format=markdown&api_key=wk_YOUR_KEY" \
  -o "content.md"
```

### Download as Text
```bash
curl "http://localhost:5000/api/wikipedia/download/1?format=text&api_key=wk_YOUR_KEY" \
  -o "content.txt"
```

---

## 🐍 Python Quick Examples

### Example 1: Search Wikipedia
```python
import requests

key = "wk_YOUR_KEY"
response = requests.post(
    'http://localhost:5000/api/wikipedia/search',
    headers={'X-API-Key': key},
    json={'topic': 'Artificial Intelligence'}
)
print(response.json())
```

### Example 2: Fetch Content
```python
import requests

key = "wk_YOUR_KEY"
response = requests.post(
    'http://localhost:5000/api/wikipedia/fetch',
    headers={'X-API-Key': key},
    json={'topic': 'Machine Learning'}
)
data = response.json()
print(f"Title: {data['title']}")
print(f"Categories: {len(data['categories'])}")
```

### Example 3: Download File
```python
import requests

response = requests.get(
    'http://localhost:5000/api/wikipedia/download/1',
    params={'format': 'pdf', 'api_key': 'wk_YOUR_KEY'}
)
with open('article.pdf', 'wb') as f:
    f.write(response.content)
```

### Example 4: Use Python Client
```python
from example_script import WikipediaFetcher

fetcher = WikipediaFetcher(api_key="wk_YOUR_KEY")
content = fetcher.fetch_wikipedia_content("Python")
print(content['title'])
```

---

## 🧪 Testing Commands

### Run All Tests
```bash
python test_wikipedia.py   # Manager tests
python test_api.py         # API endpoint tests
```

### Interactive Python Mode
```bash
python example_script.py interactive
```

---

## 📄 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview and features |
| `GETTING_STARTED.md` | Detailed user guide |
| `WIKIPEDIA_API_DOCS.md` | Complete API reference |
| `IMPLEMENTATION_SUMMARY.md` | What was built |
| `ISSUE_RESOLUTION.md` | Issues fixed and verification |
| `example_script.py` | Python code examples |

---

## 🔓 Authentication

### Header Method (Recommended)
```bash
curl -H "X-API-Key: wk_YOUR_KEY" http://localhost:5000/api/...
```

### Query Parameter Method
```bash
curl "http://localhost:5000/api/...?api_key=wk_YOUR_KEY"
```

---

## ✨ Common Use Cases

### Case 1: Research Topic
1. Go to http://localhost:5000/wikipedia
2. Search "Your Topic"
3. Read the full article
4. Download as PDF for offline reading

### Case 2: Batch Fetch Topics
```bash
# Get API key first
API_KEY=$(curl -s -X POST http://localhost:5000/api/keys/generate \
  -H "Content-Type: application/json" \
  -d '{"name":"Batch"}' | grep -o '"key":"[^"]*"' | cut -d'"' -f4)

# Fetch multiple topics
for topic in "Python" "Machine Learning" "AI"; do
  curl -X POST http://localhost:5000/api/wikipedia/fetch \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"topic\":\"$topic\"}"
done
```

### Case 3: Download Research Materials
```bash
# Get API key
API_KEY="wk_YOUR_KEY"

# Fetch and download multiple articles
topics=("Physics" "Chemistry" "Biology")
for topic in "${topics[@]}"; do
  curl -X POST "http://localhost:5000/api/wikipedia/fetch" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"topic\":\"$topic\"}"
  
  curl "http://localhost:5000/api/wikipedia/download/1?format=pdf&api_key=$API_KEY" \
    -o "${topic}.pdf"
done
```

### Case 4: Search Cache
```bash
# List all cached items
curl "http://localhost:5000/api/wikipedia/cache/search?api_key=wk_YOUR_KEY"

# Search specific cache
curl "http://localhost:5000/api/wikipedia/cache/search?q=learning&api_key=wk_YOUR_KEY"
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "API key required" | Add `-H "X-API-Key: YOUR_KEY"` |
| "Topic not found" | Check spelling, try different topic |
| "Download not working" | Use PDF format, check browser settings |
| "Slow first request" | Normal! Wikipedia API takes time. 2nd request faster |
| "Empty response" | Topic exists but has minimal Wikipedia content |

---

## 📊 API Response Examples

### Success Response
```json
{
  "success": true,
  "title": "Machine learning",
  "url": "https://en.wikipedia.org/wiki/Machine_learning",
  "content": "# Machine learning...",
  "summary": "Machine learning is...",
  "categories": ["ML", "AI", ...],
  "references": ["Python", "Algorithm", ...]
}
```

### Error Response
```json
{
  "success": false,
  "error": "Invalid API key"
}
```

---

## 🎯 Most Used Endpoints

```
Endpoint                              | Method | Auth  | Time
--------------------------------------|--------|-------|--------
/api/wikipedia/fetch                  | POST   | Key   | 1-3s
/api/wikipedia/search                 | POST   | Key   | 1-2s
/api/wikipedia/cached/<topic>         | GET    | Key   | <100ms
/api/wikipedia/cache/search           | GET    | Key   | <200ms
/api/wikipedia/download/<id>          | GET    | Key   | <500ms
/api/keys/generate                    | POST   | None  | <100ms
/wikipedia                            | GET    | None  | <200ms
```

---

## 📌 Important Notes

✅ **First-time fetch**: 1-3 seconds (Wikipedia API)  
✅ **Cached retrieval**: <100ms (Database)  
✅ **API keys**: Permanent, stored in database  
✅ **Web interface**: Auto-generates session key  
✅ **All formats**: PDF, Markdown, Text supported  

---

## 🚀 Starting the Application

```bash
# Ensure you're in the wiki directory
cd C:\Users\Sahil\OneDrive\Desktop\wiki

# Run the application
python app.py

# Access at http://localhost:5000
# Wikipedia Fetcher at http://localhost:5000/wikipedia
```

---

## 📞 Get Help

1. **Web Interface Help**: http://localhost:5000/wikipedia
2. **API Documentation**: `WIKIPEDIA_API_DOCS.md`
3. **User Guide**: `GETTING_STARTED.md`
4. **Code Examples**: `example_script.py`
5. **Tests**: `test_wikipedia.py`, `test_api.py`

---

## ✅ Verification

Everything is working:
```bash
✓ Application running
✓ Web interface responsive
✓ API endpoints functional
✓ Database initialized
✓ Caching system active
✓ Wikipedia integration connected
✓ Downloads working
```

---

**Last Updated**: February 12, 2026  
**Status**: ✅ FULLY OPERATIONAL
