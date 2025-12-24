<div align="center">

# 🧠 DeepCodeX

### AI-Powered Code Complexity Analyzer with History Tracking

[![Made with Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Supabase](https://img.shields.io/badge/Supabase-Integrated-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)

**Analyze code complexity in real-time, get AI-powered warnings, and save your analysis history.**

[Features](#-features) • [Installation](#-installation) • [Configuration](#-configuration) • [Usage](#-usage) • [Architecture](#-architecture)

</div>

---

## ✨ Features

### 🎯 **Advanced Complexity Analysis**
- **Time Complexity**: Precise Big-O estimation (O(1), O(n log n), O(n²), etc.) using AST and pattern recognition.
- **Space Complexity**: Memory usage analysis including recursion stack depth.
- **Algorithm Detection**: Identifies 20+ algorithms including Graph traversals, DP, and Sorting.

### 💾 **History & Persistence (Supabase)**
- **Analysis Logging**: Automatically saves every analysis to a Supabase database.
- **History View**: Browse past analyses with `code_hash`, complexity metrics, and AI suggestions.
- **Deduplication**: Uses SHA-256 hashing to track unique code submissions.

### 🔍 **Smart Detection**
- **Language Auto-Detection**: Supports Python, Java, C++, JavaScript, Go, Rust, and more.
- **Static Analysis**: Counts lines, functions, loops, and conditionals without executing code.
- **Recursion Analysis**: Distinguishes between Linear, Binary, and Tail recursion.

### 🤖 **AI Intelligence**
- **Gemini / OpenRouter Integration**: Provides actionable refactoring suggestions.
- **Security & Quality**: Flags potential security risks and maintainability processing.

---

## 🛠️ Tech Stack

### Frontend
- **React 19** + **Vite**
- **TypeScript**
- **Monaco Editor** (VS Code-like editing)
- **Recharts** (Data Visualization)
- **Google GenAI SDK**

### Backend
- **Flask** (Python API)
- **Supabase** (PostgreSQL + Auth)
- **Python AST** (Static Analysis)
- **Gemini / OpenRouter API** (LLM)

---

## 🚀 Installation

### Prerequisites
- **Node.js** 18+
- **Python** 3.8+
- **Supabase Account** (for database)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Modepalli-Ravindra/DeepCodeX.git
cd DeepCodeX
```

### 2️⃣ Install Frontend Dependencies
The project uses valid npm workspaces or a single root package structure.
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

---

## ⚙️ Configuration

Create a `.env` file in the **backend** directory (and/or root depending on setup) with the following keys:

```env
# AI Provider Keys
OPENROUTER_API_KEY=your_openrouter_key
GEMINI_API_KEY=your_gemini_key

# Supabase Configuration (Required for History)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

> **Note**: `SUPABASE_SERVICE_ROLE_KEY` is required because the backend writes directly to the `analysis_history` table.

---

## 🏃 Usage

### 1. Start the Backend
Open a terminal in the `backend` folder:
```bash
# Activate venv first!
python app.py
```
*Server runs on `http://localhost:5000`*

### 2. Start the Frontend
Open a new terminal in the root folder:
```bash
npm run dev
```
*App runs on `http://localhost:3000`*

### 3. Analyze Code
1. Navigate to **http://localhost:3000**.
2. Paste code into the editor.
3. Watch as the system detects the language and analyzes complexity.
4. Check the **History** tab to see saved results from Supabase.

---

## 🏗️ Architecture & Database

### Database Schema (Supabase)
The system requires a table named `analysis_history` with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Primary Key |
| `code_hash` | text | Unique SHA-256 hash of the code |
| `language` | text | Detected programming language |
| `time_complexity` | text | e.g., "O(n)" |
| `space_complexity` | text | e.g., "O(1)" |
| `created_at` | timestamp | Record creation time |
| `ai_suggestions` | text | Stored LLM advice |

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze` | content-type: `application/json` - Analyzes code and saves result. |
| `GET` | `/history` | Fetches the last 50 analysis records. |
| `POST` | `/auth/*` | Auth routes (login/signup) if enabled. |

---

## 📁 Project Structure

```
DeepCodeX/
├── frontend/             # React Source Code
│   ├── components/       # UI Components
│   └── pages/            # App Routes (Analysis, Dashboard, History)
├── backend/              # Flask Application
│   ├── analyzer/         # Core Analysis Logic
│   ├── db/               # Supabase Client
│   ├── auth/             # Authentication Routes
│   └── app.py            # Main Entry Point
├── package.json          # Frontend Dependencies
├── vite.config.ts        # Vite Configuration
└── README.md             # Documentation
```

---

## 👨‍💻 Author

**Modepalli Ravindra**
- GitHub: [@Modepalli-Ravindra](https://github.com/Modepalli-Ravindra)

---

<div align="center">
Made with ❤️, ☕, and 🐍
</div>
