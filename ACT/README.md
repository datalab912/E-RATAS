# Yirigaa_NLP
## Description

Yirigaa_NLP is a repository for my major project on Natural Language Processing.

## Getting Started

### 1. Clone the repository:
   ```bash
   git clone https://github.com/dannguyen99/Yirigaa_NLP
   ```

### 2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### 3. Set up your OpenAI API key:
   * Obtain an API key from [https://beta.openai.com/account/api-keys](https://beta.openai.com/account/api-keys)
   * Set up your API key [https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key)

   On MacOs:
   * Export the key as an environment variable `OPENAI_API_KEY`:
     ```bash
     export OPENAI_API_KEY=your_api_key
     ```

### 4. Build the project:

```bash
pip install -e .
```

### 5. Run Redis and RQ Worker:

```bash
redis-server
rq worker --with-scheduler
```