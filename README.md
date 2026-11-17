# Data Cleaning Agent

An AI-powered data cleaning agent that automatically cleans messy datasets using LangChain and LangGraph. The agent uses an LLM to generate and execute Python code for common data cleaning tasks like handling missing values, removing duplicates, and dropping low-quality columns.

## How It Works

The agent follows a simple workflow:
1. **Analyze**: Examines your dataset structure and identifies data quality issues
2. **Generate**: Uses an LLM to create custom Python cleaning code based on the data
3. **Execute**: Runs the generated code to clean your data
4. **Retry**: Automatically fixes errors if the generated code fails (up to 3 attempts)

This approach combines the flexibility of LLMs with the reliability of pandas operations.

## Setup

### Prerequisites

- **Python 3.9 or higher** (3.9, 3.10, 3.11, 3.12, or 3.13) - **Note**: Python 3.9.7 is not supported due to a Streamlit compatibility issue
- **Poetry** (dependency manager)
- **OpenAI API Key**

### Installation Steps

1. **Install Poetry** (if not already installed):
   
   **Windows (PowerShell)**:
   ```powershell
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
   ```
   
   **macOS/Linux**:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
   
   After installation, restart your terminal. If `poetry` command is not found:
   - **Windows**: Add `%APPDATA%\Python\Scripts` to your system PATH
   - **macOS/Linux**: Add `export PATH="$HOME/.local/bin:$PATH"` to your `~/.bashrc` or `~/.zshrc`

2. **Install dependencies**:
   ```bash
   poetry install
   ```
   
   This will install all dependencies with the exact versions specified in `poetry.lock`, ensuring consistency across all environments.

3. **Set up your OpenAI API key**:
   
   **Windows**:
   ```powershell
   copy .env.example .env
   ```
   
   **macOS/Linux**:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

### Multiple Python Versions?

If you have multiple Python versions installed and want to use a specific one:

```bash
# Tell Poetry which Python to use
poetry env use python3.11  # or python3.9, python3.10, python3.12, etc.

# Then install dependencies
poetry install
```

Poetry will create a virtual environment with your chosen Python version.

## Usage

### Streamlit Web Interface

The easiest way to use the agent is through the web interface:

```bash
poetry run streamlit run app.py
```

Then:
1. Upload your CSV file
2. Click "Clean Data"
3. Download the cleaned dataset

#### Cleaned data: original missing values

The `Cleaned data` section shows the **original number of missing values for every column** of the uploaded dataset:

- The counts are calculated before any cleaning operation (column removal, missing-value imputation, duplicate-row removal and datatype fixation).
- They are displayed before the dataframe shape (number of rows and columns).
- They describe the original uploaded dataset, not the cleaned dataset.

#### Basic metrics of Data Cleaning

The `Basic metrics of Data Cleaning` section contains a dropdown with two options:

- **Non-numerical variables**: displays the mode of `department` and the mode of `city`. The mode is the most frequently occurring value in a column. If several values are tied for the highest frequency, all tied modes are displayed.
- **Numerical variables**: displays basic descriptive metrics: the minimum and maximum value of `age`, and the minimum and maximum value of `salary`.

### Docker Deployment (Windows, Docker Desktop)

The application can also be built and run as a Docker container using the included `Dockerfile`.

#### Prerequisites

- Docker Desktop installed and running.
- The project repository downloaded or cloned locally.
- An OpenAI API key configured through a `.env` file in the project root, containing:
  ```
  OPENAI_API_KEY=your_actual_api_key
  ```
  Keep your actual API key private and do not commit `.env` to GitHub (it is already listed in `.gitignore`).

#### Build the Docker image

Run from the project root:

```bash
docker build -t data-cleaning-agent .
```

This builds the Docker image using the `Dockerfile`.

#### Run the Docker container

```bash
docker run -d -p 8501:8501 --env-file .env --name data-cleaning-agent-container data-cleaning-agent
```

- `-d` runs the container in the background.
- `-p 8501:8501` maps the application port.
- `--env-file .env` supplies the environment variables, including the OpenAI API key.
- `--name` assigns a name to the container.

#### Access the application

Open [http://localhost:8501](http://localhost:8501) in your browser.

#### Verify the running container

```bash
docker ps
```

This lists the running containers.

#### Stop the container

```bash
docker stop data-cleaning-agent-container
```

#### Restart an existing stopped container

```bash
docker start data-cleaning-agent-container
```

#### Rebuild after modifying application files

The application files are copied into the image at build time. If you modify `app.py` or files inside `data_cleaning_agent/`, rebuild the image and recreate the container to use the updated application:

```bash
docker stop data-cleaning-agent-container
docker rm data-cleaning-agent-container
docker build -t data-cleaning-agent .
docker run -d -p 8501:8501 --env-file .env --name data-cleaning-agent-container data-cleaning-agent
```

### Python API

For programmatic use or integration into data pipelines:

```python
import pandas as pd
from langchain_openai import ChatOpenAI
from data_cleaning_agent import LightweightDataCleaningAgent

# Initialize the agent with an LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = LightweightDataCleaningAgent(model=llm)

# Load your messy data
df = pd.read_csv("your_data.csv")

# Run the cleaning agent
agent.invoke_agent(data_raw=df)

# Get the cleaned dataset
cleaned_df = agent.get_data_cleaned()

# Save or use the cleaned data
cleaned_df.to_csv("cleaned_data.csv", index=False)
```

**Optional: Provide custom instructions**

```python
# Give specific cleaning instructions to the agent
agent.invoke_agent(
    data_raw=df,
    user_instructions="Remove columns with more than 30% missing values and standardize date formats"
)
```

## Project Structure

```
data-cleaning-agent/
├── data_cleaning_agent/
│   ├── __init__.py
│   ├── data_cleaning_agent.py  # Main agent class
│   └── utils.py                # Utility functions
├── app.py                      # Streamlit interface
├── pyproject.toml              # Dependencies configuration
├── poetry.lock                 # Locked dependency versions
└── README.md
```

**Important**: The `poetry.lock` file is committed to ensure all users get identical, tested dependency versions.
