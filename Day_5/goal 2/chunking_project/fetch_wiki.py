import os
import wikipediaapi

# Create corpus directory
os.makedirs("data/corpus", exist_ok=True)

# Initialize Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia(
    user_agent="MyEvalProject/1.0 (your-email@example.com)",
    language="en"
)

# List of topics (first 50)
topics = [
    "Python (programming language)", "Artificial intelligence", "Machine learning",
    "Deep learning", "Natural language processing", "Computer vision", "Robotics",
    "Data science", "Big data", "Cloud computing", "Internet of things",
    "Cybersecurity", "Blockchain", "Quantum computing", "Virtual reality",
    "Augmented reality", "Autonomous car", "Speech recognition", "Recommender system",
    "Search engine", "Social media", "E-commerce", "Online advertising",
    "Digital marketing", "Web development", "Mobile app", "Operating system",
    "Database", "Computer network", "Software engineering", "Agile software development",
    "DevOps", "Containerization", "Microservices", "API", "GraphQL",
    "REST", "JSON", "XML", "HTML", "CSS", "JavaScript", "TypeScript",
    "React (software)", "Angular (web framework)", "Vue.js", "Node.js",
    "Django (web framework)", "Flask (web framework)", "Spring Framework",
    "Git", "Docker", "Kubernetes", "Linux", "Windows", "macOS"
]

count = 0
for topic in topics:
    if count >= 50:
        break
    page = wiki_wiki.page(topic)
    if page.exists():
        filename = f"data/corpus/{topic.replace('/', '_')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {topic}\n\n{page.text}")
        print(f"Saved: {topic}")
        count += 1
    else:
        print(f"Not found: {topic}")

print(f"Downloaded {count} documents to data/corpus/")