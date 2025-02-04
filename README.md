# JD & Resume Parsing Service

This project provides an **AI-powered API** for extracting structured information from **Job Descriptions (JD)** and **Resumes**. It leverages **FastAPI** and **OpenAI's GPT API** to parse documents and return structured JSON data.

---

## 🚀 **Features**
- 📄 **Extract structured information from Resumes**
- 📝 **Parse Job Descriptions (JDs) to extract skills and experience**
- 🏗 **Dynamic duration calculation for education and work experience**
- 📡 **FastAPI-based API with async processing**
- 📂 **Supports PDF & DOCX formats**
- 🔧 **Dockerized for easy deployment**

---

## 📁 **Project Structure**

# Resume & Job Description Parser API

## **Overview**
This project implements a Resume and Job Description Parser API using **FastAPI** and **OpenAI GPT**. The API allows users to upload resumes and job descriptions (in PDF/DOCX formats), which are then parsed and structured into **JSON** format.

The following files are part of the project:

### **1. `main.py`**:
This is the main file that runs the FastAPI application.

#### **Functions and Routes in `main.py`:**
- **`@app.post("/api/parse-resume/")`**: Handles the **Resume Parsing**. It accepts PDF/DOCX files and returns a structured JSON response with extracted information (candidate name, skills, education, experience, etc.).
- **`@app.post("/api/parse-job-description/")`**: Handles the **Job Description Parsing**. It also accepts PDF/DOCX files and returns a structured JSON response with job details, required skills, and experience.

#### **Important Imports:**
- `FastAPI`, `HTTPException` → FastAPI framework to create the REST API.
- `UploadFile`, `File` → Handle file uploads for resume and job description parsing.
- `ResumeParser`, `JobDescriptionParser` → Services for parsing resumes and job descriptions.
- `Logger` → For logging the activities of the server.
- `GPTService` → Used to interact with OpenAI's GPT to generate structured responses from raw texts.

### **2. `schemas.py`**:
Defines the **data structures (schemas)** used for parsing and structuring the data returned by the resume and job description parsers.

#### **Main Classes:**
- **`ResumeSchema`**: Represents the structure of parsed data from resumes.
  - **Attributes**: Candidate name, email, phone number, skills, educations, work experience, and more.
  
- **`JobDescriptionSchema`**: Represents the structure of parsed data from job descriptions.
  - **Attributes**: Job title, description, required skills, minimum work experience, etc.
  
- **`Education`** and **`Experience`**: Represent the education and experience details in the parsed JSON.

### **3. `file_parser.py`**:
Contains utility functions to **parse** PDF and DOCX files.

#### **Functions in `file_parser.py`:**
- **`parse_pdf_or_docx(file_buffer, filename)`**: Decides whether the uploaded file is PDF or DOCX and calls respective functions to parse them.
- **`parse_pdf(file_buffer)`**: Extracts text from PDF files using **PyPDF2**.
- **`parse_docx(file_buffer)`**: Extracts text from DOCX files using **python-docx**.
- **`clean_text(text)`**: Cleans and normalizes the extracted text (e.g., removes excess whitespace).

### **4. `logger.py`**:
Handles **logging** for the application.

#### **Main Functionality:**
- Configures the logger to track **errors**, **info messages**, and **debug logs**.
- Ensures that logs are saved for better debugging and monitoring.

### **5. `config_service.py`**:
Handles the **loading of environment variables** and configuration settings, such as the **OpenAI API key**.

#### **Main Functions:**
- **`ConfigService`**: Reads the `.env` file to load the **API key** for OpenAI, as well as other configuration settings required by the app.

### **6. `gpt_service.py`**:
Handles interactions with the **OpenAI GPT API** to process the resume and job description texts.

#### **Main Functionality:**
- **`GPTService`**: Sends data to OpenAI's API and retrieves parsed, structured output.
- **`extract_with_prompts()`**: Main function that calls OpenAI's API to extract structured information from raw text using prompts.

### **7. `resume_extraction.py`**:
Contains logic for **parsing resumes**.

#### **Functions in `resume_extraction.py`:**
- **`parse_resume(file_buffer, filename)`**: Extracts structured information from resumes (name, skills, education, work experience, etc.) using GPT prompts and OpenAI API.

### **8. `jd_extraction_helper.py`**:
Contains logic for **parsing job descriptions**.

#### **Functions in `jd_extraction_helper.py`:**
- **`parse_job_description(file_buffer, filename)`**: Extracts structured information from job descriptions (title, description, required skills, experience, etc.) using GPT prompts and OpenAI API.

### **9. `requirements.txt`**:
This file contains a list of **dependencies** required for the project.

#### **Dependencies:**
- `fastapi`, `uvicorn`: For building and running the API.
- `openai`: For interacting with OpenAI’s GPT models.
- `python-dotenv`: To load environment variables from `.env`.
- `pydantic`: For data validation.
- `PyPDF2`, `python-docx`: For parsing PDF and DOCX files.
- `aiofiles`: For handling file uploads asynchronously.

### **10. `Dockerfile`**:
This file **containers the application** so that it can be run in any environment (e.g., production) without worrying about dependencies.

#### **Main Steps in `Dockerfile`:**
- Pulls the **Python 3.10** base image.
- Sets the working directory to `/app`.
- Copies the app files into the container.
- Installs dependencies from `requirements.txt`.
- Exposes port `8000` for the API.
- Runs **Uvicorn** to start the FastAPI application.

### **11. `.env.example`**:
This file contains an **example environment configuration** with a placeholder for the **OpenAI API key**. The `.env` file should be created based on this example.

#### **Content in `.env.example`:**
```env
OPENAI_API_KEY=your_openai_api_key_here

Run the FastAPI Server

Run the FastAPI application using Uvicorn:

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

You should see the following output:

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)