# 🚀 Optimize

A flexible data optimization and transformation tool designed to streamline JSON data and automate enhancement workflows.

---

## 📖 Table of Contents

* [About](#about)
* [Features](#features)
* [Tech Stack](#tech-stack)
* [Getting Started](#getting-started)
* [Usage](#usage)
* [Examples](#examples)
* [Project Structure](#project-structure)
* [Configuration](#configuration)
* [Contributing](#contributing)
* [License](#license)
* [Author](#author)

---

## 📌 About

**Optimize** is a modular tool that allows developers and data engineers to:

* Compress and normalize JSON-like datasets
* Remove redundancies
* Clean, deduplicate, and standardize key structures
* Send processed data to APIs

It is useful in data migration, preprocessing pipelines, and API communication tasks.

---

## ✅ Features

* 📦 JSON Data Optimization
* 🔁 Deduplication and Structure Unification
* 🔧 Custom Key Mapping & Transformation
* 🔐 API Integration (with token or bearer support)
* 🧪 Local and Remote Testing
* 📂 Support for `.env` configuration

---

## 🧰 Tech Stack

| Layer       | Technology                       |
| ----------- | -------------------------------- |
| Language    | Python 3.10+                     |
| Packaging   | `pip`, `requirements.txt`        |
| Environment | dotenv (`python-dotenv`)         |
| HTTP Calls  | `requests`                       |
| Utilities   | `os`, `json`, `argparse`, `uuid` |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Marwanelaks/optimize.git
cd optimize
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Create a `.env` file in the root directory and add your API and token configurations:

```env
API_URL=http://localhost:8000/api/data
API_KEY=your_api_token_here
```

---

## ⚙️ Usage

### Run Optimizer:

```bash
python optimize.py --input data.json --output cleaned_data.json
```

### Available Options:

| Option       | Description                         |
| ------------ | ----------------------------------- |
| `--input`    | Input JSON file                     |
| `--output`   | Output filename (optional)          |
| `--url`      | Endpoint to send optimized data     |
| `--token`    | API Token or Bearer key             |
| `--simulate` | Run without actually posting to API |
| `--debug`    | Enable debug logging                |

---

## 🔍 Examples

### Example 1: Optimize and Save

```bash
python optimize.py --input example/input.json --output example/output.json
```

### Example 2: Optimize and Post to API

```bash
python optimize.py --input users.json --url https://api.example.com/submit --token abc123
```

---

## 📁 Project Structure

```plaintext
optimize/
├── example/                # Sample input and output files
│   ├── input.json
│   └── output.json
├── core/                   # Main logic and helper functions
│   ├── __init__.py
│   ├── parser.py           # CLI parsing
│   ├── cleaner.py          # JSON cleaning logic
│   └── sender.py           # API integration logic
├── .env                    # Environment variables
├── optimize.py             # Main script entry point
├── requirements.txt
└── README.md
```

---

## ⚙️ Configuration

Use `.env` to configure default behavior:

```env
DEFAULT_API_URL=http://localhost:8000/api
USE_BEARER=true
```

In code, retrieve them with `os.getenv('VAR_NAME')`.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch:

   ```bash
   git checkout -b feat/your-feature-name
   ```
3. Commit your changes:

   ```bash
   git commit -am 'Add your feature'
   ```
4. Push to the branch:

   ```bash
   git push origin feat/your-feature-name
   ```
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---


