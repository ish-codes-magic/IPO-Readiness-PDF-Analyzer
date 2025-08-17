# IPO Readiness PDF Analyzer

A comprehensive AI-powered platform that analyzes SME pitch deck PDFs and provides detailed IPO readiness scoring and insights.

![IPO Analyzer](https://img.shields.io/badge/Status-Ready-green)
![Next.js](https://img.shields.io/badge/Frontend-Next.js-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![Gemini](https://img.shields.io/badge/AI-Gemini-orange)

## 🚀 Features

### Core Functionality
- **PDF Upload & Analysis**: Drag-and-drop interface for pitch deck uploads
- **AI-Powered Content Extraction**: Using Gemini LLM with vision capabilities for intelligent PDF analysis
- **Comprehensive IPO Scoring**: 8-criteria evaluation system with detailed rationale
- **Interactive Visualizations**: Charts and graphs using Recharts
- **Detailed Reports**: Executive summaries, risk assessments, and actionable recommendations

### Evaluation Criteria (Equal Weight: 12.5% each)
1. **Basic Company Info** - Company background and key information
2. **Mission & Core Business** - Business model clarity and strategic focus
3. **Defensibility / IP / MOAT** - Competitive advantages and intellectual property
4. **Regulatory Approvals & Compliance** - Industry compliance and regulatory readiness
5. **Commercial Traction & Validation** - Market validation and customer traction
6. **Segment-level Unit Economics** - Financial metrics and unit economics analysis
7. **Equity Cap Table** - Ownership structure and equity distribution
8. **Key Risks & Information Gaps** - Risk assessment and information completeness

### Output Features
- Overall IPO readiness score (0-100)
- Per-criterion scores with detailed rationale
- Strengths and weaknesses identification
- Risk assessment and gap analysis
- Follow-up questions for next meetings
- Executive summary with recommendations

## 🛠️ Tech Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety and better development experience
- **Tailwind CSS** - Utility-first CSS framework
- **Radix UI** - Accessible UI components
- **Recharts** - Data visualization library
- **Lucide React** - Beautiful icons
- **React Dropzone** - File upload handling

### Backend
- **FastAPI** - Modern Python web framework
- **Gemini LLM + Vision** - AI-powered PDF content extraction and analysis
- **Google Gemini API** - Large language model for analysis
- **Instructor** - Structured response validation
- **Jinja2** - Template engine for prompts
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server

## 📁 Project Structure

```
IPO-Readiness-PDF-Analyzer/
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   └── components/      # React components
│   ├── package.json
│   └── vercel.json
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── pdf_processor.py # PDF content extraction
│   │   ├── ipo_analyzer.py  # AI analysis logic
│   │   └── models/         # Pydantic models
│   ├── prompts/            # Jinja2 templates
│   ├── utils/              # Utility functions
│   ├── pyproject.toml      # Python dependencies
│   └── run.py              # Startup script
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- uv (Python package manager)
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env and add your Gemini API key
   ```

4. **Run the backend server**
   ```bash
   uv run python run.py
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

### Environment Variables

#### Backend (.env)
```env
GEMINI_API_KEY=your_gemini_api_key_here
CORS_ORIGINS=http://localhost:3000
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 Usage

1. **Upload PDF**: Drag and drop your pitch deck PDF or click to browse
2. **Analysis**: The system will extract content and analyze across 8 criteria
3. **Results**: View comprehensive scoring, insights, and recommendations
4. **Export**: Download detailed reports (coming soon)
5. **Chat**: Ask questions about the analysis (coming soon)

## 🔧 API Endpoints

### Backend API

- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /analyze-pdf` - Upload and analyze PDF
- `GET /criteria` - Get evaluation criteria information

### Example API Response

```json
{
  "analysis_id": "uuid",
  "filename": "pitch_deck.pdf",
  "overall_ipo_score": 72.5,
  "readiness_level": "Ready",
  "criterion_scores": [...],
  "executive_summary": {...},
  "risk_assessment": {...},
  "follow_up_questions": {...}
}
```

## 🚀 Deployment

### Frontend (Vercel)

1. **Connect your repository to Vercel**
2. **Set the root directory to `frontend`**
3. **Configure environment variables**
4. **Deploy**

### Backend (Railway/Render/DigitalOcean)

1. **Set up your hosting platform**
2. **Configure environment variables**
3. **Deploy using Docker or direct Python deployment**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation
- Review the API endpoints

## 🔮 Roadmap

- [ ] Interactive chat interface for Q&A
- [ ] Secondary research integration
- [ ] Report export functionality
- [ ] Multi-language support
- [ ] Advanced visualization options
- [ ] Batch processing capabilities
- [ ] Integration with CRM systems

---

**Built with ❤️ for better investment decision making**