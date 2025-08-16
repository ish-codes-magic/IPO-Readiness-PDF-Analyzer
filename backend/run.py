#!/usr/bin/env python3
"""
Startup script for IPO Readiness PDF Analyzer Backend
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    # Run the application with increased request size limit
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info",
        limit_max_requests=1000,
        limit_concurrency=100,
        # Allow larger request bodies for PDF uploads (25MB)
        http="h11",
        loop="asyncio"
    )