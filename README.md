<div align="center">

# 🧠 DeepCodeX

### AI-Powered Code Complexity Analyzer

[![Made with Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)

**Analyze code complexity in real-time with pattern recognition, AST parsing, and AI-powered suggestions.**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture)

</div>

---

## ✨ Features

### 🎯 **Complexity Analysis**
- **Time Complexity**: Accurate Big-O estimation (O(1), O(log n), O(n), O(n²), O(2ⁿ), etc.)
- **Space Complexity**: Memory usage analysis based on data structures and recursion
- **Pattern Recognition**: Detects 20+ common algorithms automatically

### 🔍 **Automatic Language Detection**
Supports 10 programming languages with real-time detection:

| Language | Icon | Detection Markers |
|----------|------|-------------------|
| Python | 🐍 | `def`, `import`, `print()` |
| Java | ☕ | `public class`, `System.out.print` |
| C++ | ⚡ | `#include`, `std::`, `cout` |
| C | 🔧 | `printf`, `malloc`, `#include <stdio.h>` |
| JavaScript | 📜 | `function`, `const`, `console.log` |
| TypeScript | 📘 | Type annotations, `interface` |
| Go | 🐹 | `func`, `package main`, `:=` |
| Rust | 🦀 | `fn`, `let mut`, `impl` |
| Ruby | 💎 | `def`, `puts`, `end` |
| PHP | 🐘 | `<?php`, `$variable`, `echo` |

### 📊 **Visual Analytics**
- **Structural Metrics**: Lines of code, functions, loops, conditionals
- **Cyclomatic Complexity**: Code maintainability score
- **Refactor Potential**: Optimization percentage with donut chart
- **Quality Score**: Overall code quality rating (0-100)

### 🤖 **AI-Powered Suggestions**
- Refactoring recommendations via LLM integration
- Performance optimization tips
- Code structure improvements

---

## 🎬 Demo

### Dashboard
![Dashboard](https://via.placeholder.com/800x400?text=Dashboard+Preview)

### Code Analysis
![Analysis](https://via.placeholder.com/800x400?text=Code+Analysis+Preview)

---

## 🚀 Installation

### Prerequisites
- **Node.js** 18+ 
- **Python** 3.8+
- **npm** or **yarn**

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Modepalli-Ravindra/DeepCodeX.git
cd DeepCodeX
```

### 2️⃣ Install Frontend Dependencies
```bash
npm install
```

### 3️⃣ Set Up Backend
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables
Create a `.env` file in the root directory:
```env
OPENROUTER_API_KEY=your_openrouter_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### 5️⃣ Run the Application

**Terminal 1 - Backend (Flask):**
```bash
cd backend
.\venv\Scripts\activate  # Windows
python app.py
```

**Terminal 2 - Frontend (Vite):**
```bash
npm run dev
```

### 6️⃣ Open in Browser
Navigate to: **http://localhost:3000**

---

## 📖 Usage

1. **Paste Code**: Copy your code into the Monaco editor
2. **Auto-Detection**: Language is automatically detected and displayed
3. **Click Analyze**: Or wait for auto-analysis (2 second debounce)
4. **View Results**: See time/space complexity, metrics, and suggestions

### Supported Algorithms (Pattern Detection)

| Category | Algorithms |
|----------|------------|
| **Sorting** | Merge Sort, Quick Sort, Heap Sort, Bubble Sort, Selection Sort |
| **Search** | Binary Search |
| **Graph** | BFS, DFS, Dijkstra, Floyd-Warshall, Bellman-Ford, Kruskal's MST |
| **Dynamic Programming** | TSP (Bitmask DP), Subset Sum |
| **Combinatorial** | Permutations |
| **Array** | Kadane's Algorithm, Find Max/Min, Frequency Count |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + Vite)                  │
│  ├── Monaco Editor (Code Input)                              │
│  ├── Language Detection Badge                                │
│  └── Recharts (Visualizations)                               │
├─────────────────────────────────────────────────────────────┤
│                      API (REST)                              │
│                   POST /analyze                              │
├─────────────────────────────────────────────────────────────┤
│                   BACKEND (Flask)                            │
│  ├── Static Analyzer (AST for Python, Regex for others)     │
│  ├── Pattern Analyzer (20+ algorithm patterns)              │
│  ├── Complexity Rules Engine (Fallback estimation)          │
│  └── LLM Integration (AI suggestions)                       │
└─────────────────────────────────────────────────────────────┘
```

### Backend Modules

| Module | Description |
|--------|-------------|
| `static_analyzer.py` | AST parsing for Python, regex for other languages |
| `pattern_analyzer.py` | Detects known algorithm patterns |
| `pattern_confidence.py` | Validates pattern detection accuracy |
| `complexity_map.py` | Maps patterns to exact Big-O |
| `complexity_rules.py` | Rule-based fallback for unknown code |
| `llm.py` | LLM integration for suggestions |

---

## 🛠️ Tech Stack

### Frontend
- **React 19** - UI Framework
- **TypeScript** - Type Safety
- **Vite** - Build Tool
- **Monaco Editor** - Code Editor
- **Recharts** - Data Visualization
- **Lucide React** - Icons

### Backend
- **Flask** - Web Framework
- **Python AST** - Abstract Syntax Tree Parsing
- **Regex** - Pattern Matching
- **OpenRouter/Gemini** - LLM API

---

## 📁 Project Structure

```
DeepCodeX/
├── frontend/
│   ├── components/
│   │   ├── Layout.tsx
│   │   ├── Logo.tsx
│   │   └── ui/Loader.tsx
│   ├── pages/
│   │   ├── CodeAnalysis.tsx    # Main analysis page
│   │   ├── Dashboard.tsx       # Overview dashboard
│   │   └── History.tsx         # Analysis history
│   ├── services/
│   │   └── apiService.ts       # API calls
│   └── types.ts                # TypeScript types
├── backend/
│   ├── analyzer/
│   │   ├── static_analyzer.py     # AST/Regex analysis
│   │   ├── pattern_analyzer.py    # Pattern detection
│   │   ├── pattern_confidence.py  # Confidence validation
│   │   ├── complexity_map.py      # Pattern → Big-O
│   │   ├── complexity_rules.py    # Fallback rules
│   │   └── fallback.py            # Main analysis pipeline
│   ├── ai/
│   │   └── llm.py                 # LLM integration
│   ├── auth/
│   │   └── auth.py                # Authentication
│   └── app.py                     # Flask server
├── .env                           # Environment variables
├── package.json                   # NPM dependencies
└── vite.config.ts                 # Vite configuration
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Modepalli Ravindra**

- GitHub: [@Modepalli-Ravindra](https://github.com/Modepalli-Ravindra)

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ and ☕

</div>
