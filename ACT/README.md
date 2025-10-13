
## Description

the core and DNTs Code related to ACT maun engin of E-RATAS

## Getting Started

### 1. Clone the repository:
   ```bash
   git clone [https://github.com/datalab912/E-RATAS]
   ```

### 2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### 3. Set up your OpenAI API key:
   * Obtain an API key from 
   * Set up your API key 

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
