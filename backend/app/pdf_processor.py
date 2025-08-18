import logging
import os
import asyncio
import time
from typing import Dict, Any, Tuple
from datetime import datetime
import instructor
import httpx
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
load_dotenv()

try:
    from .models.pdf_extraction_models import PDFExtractionResult
except ImportError:
    # For direct execution, try absolute import
    from app.models.pdf_extraction_models import PDFExtractionResult

logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    PDF content extraction using LlamaParse for text extraction and Gemini LLM for structured analysis
    """
    
    def __init__(self):
        """Initialize the PDF processor with LlamaParse and Gemini API"""
        # Configure Gemini API
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure LlamaParse API
        self.llama_api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        if not self.llama_api_key:
            raise ValueError("LLAMA_CLOUD_API_KEY environment variable is required")
        
        # LlamaParse REST API configuration
        self.llama_base_url = "https://api.cloud.llamaindex.ai"
        self.llama_headers = {
            "Authorization": f"Bearer {self.llama_api_key}",
            "Accept": "application/json"
        }
        
        # Initialize Gemini model with Instructor for structured responses
        # Set the API key as environment variable for instructor
        os.environ["GOOGLE_API_KEY"] = gemini_api_key
        self.model = instructor.from_provider(
            "google/gemini-2.5-flash"
        )
        
        # Initialize Jinja2 template environment
        template_dir = "./../prompts"
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    def extract_content(self, pdf_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract structured content from PDF file using LlamaParse and Gemini LLM
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        try:
            logger.info(f"Starting LlamaParse + Gemini PDF extraction for: {pdf_path}")
            
            # Extract text using LlamaParse
            logger.info("Extracting text with LlamaParse...")
            full_text = self._extract_with_llamaparse(pdf_path)
            
            print(f"Full text: {full_text}")
            
            # Get document basic info
            doc_info = self._get_pdf_info(pdf_path)
            
            logger.info(f"LlamaParse extracted {len(full_text)} characters")
            
            # Extract structured content using Gemini
            logger.info("Analyzing content with Gemini...")
            extraction_result = self._extract_with_gemini_text(
                full_text,
                os.path.basename(pdf_path),
                doc_info['page_count']
            )
            
            logger.info("Successfully extracted content using LlamaParse + Gemini")
            
            return full_text, extraction_result
            
        except Exception as e:
            logger.error(f"Error extracting PDF content: {str(e)}")
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    def _extract_with_llamaparse(self, pdf_path: str) -> str:
        """
        Extract text from PDF using LlamaParse REST API
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content as markdown string
        """
        try:
            logger.info(f"Parsing PDF with LlamaParse REST API: {pdf_path}")
            
            # Step 1: Upload the file
            job_id = self._upload_file_to_llamaparse(pdf_path)
            logger.info(f"File uploaded, job ID: {job_id}")
            
            # Step 2: Wait for processing to complete
            self._wait_for_job_completion(job_id)
            
            # Step 3: Get the results
            markdown_content = self._get_job_results(job_id)
            
            logger.info(f"LlamaParse successfully extracted {len(markdown_content)} characters")
            return markdown_content
            
        except Exception as e:
            logger.error(f"Error parsing PDF with LlamaParse: {str(e)}")
            raise Exception(f"LlamaParse extraction failed: {str(e)}")
    
    def _upload_file_to_llamaparse(self, pdf_path: str) -> str:
        """
        Upload file to LlamaParse and return job ID
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Job ID for the parsing task
        """
        try:
            with httpx.Client() as client:
                with open(pdf_path, 'rb') as file:
                    files = {
                        'file': (os.path.basename(pdf_path), file, 'application/pdf')
                    }
                    
                    response = client.post(
                        f"{self.llama_base_url}/api/v1/parsing/upload",
                        headers=self.llama_headers,
                        files=files,
                        timeout=60.0
                    )
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    if 'id' not in result:
                        raise ValueError(f"No job ID returned from LlamaParse: {result}")
                    
                    return result['id']
                    
        except Exception as e:
            logger.error(f"Error uploading file to LlamaParse: {str(e)}")
            raise
    
    def _wait_for_job_completion(self, job_id: str, max_wait_time: int = 300, check_interval: int = 5) -> None:
        """
        Wait for LlamaParse job to complete
        
        Args:
            job_id: The job ID to check
            max_wait_time: Maximum time to wait in seconds (default: 5 minutes)
            check_interval: How often to check status in seconds (default: 5 seconds)
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                with httpx.Client() as client:
                    response = client.get(
                        f"{self.llama_base_url}/api/v1/parsing/job/{job_id}",
                        headers=self.llama_headers,
                        timeout=30.0
                    )
                    
                    response.raise_for_status()
                    job_status = response.json()
                    
                    status = job_status.get('status', 'UNKNOWN')
                    logger.info(f"Job {job_id} status: {status}")
                    
                    if status == 'SUCCESS':
                        return
                    elif status == 'ERROR':
                        error_msg = job_status.get('error', 'Unknown error')
                        raise Exception(f"LlamaParse job failed: {error_msg}")
                    elif status in ['PENDING', 'PROCESSING']:
                        time.sleep(check_interval)
                        continue
                    else:
                        logger.warning(f"Unknown status: {status}, continuing to wait...")
                        time.sleep(check_interval)
                        continue
                        
            except httpx.HTTPError as e:
                logger.error(f"HTTP error checking job status: {str(e)}")
                time.sleep(check_interval)
                continue
        
        raise Exception(f"Job {job_id} did not complete within {max_wait_time} seconds")
    
    def _get_job_results(self, job_id: str) -> str:
        """
        Get the markdown results from a completed LlamaParse job
        
        Args:
            job_id: The completed job ID
            
        Returns:
            Markdown content as string
        """
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.llama_base_url}/api/v1/parsing/job/{job_id}/result/markdown",
                    headers=self.llama_headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                # The result should contain the markdown content
                if 'markdown' in result:
                    return result['markdown']
                elif isinstance(result, str):
                    return result
                else:
                    # Sometimes the result might be in a different format
                    return str(result)
                    
        except Exception as e:
            logger.error(f"Error getting job results: {str(e)}")
            raise
    

    
    def _get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get basic PDF information
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF info
        """
        try:
            # Basic file information
            file_size = os.path.getsize(pdf_path)
            
            # For page count, we'll rely on LlamaParse results or estimate
            # Since we're moving away from PyMuPDF, we'll use a simple approach
            info = {
                "page_count": 1,  # Default, will be updated after parsing
                "metadata": {},
                "is_encrypted": False,  # LlamaParse handles encrypted files
                "file_size": file_size
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting PDF info: {str(e)}")
            return {"page_count": 1, "metadata": {}, "is_encrypted": False, "file_size": 0}
    
    async def _extract_with_gemini_text(self, text_content: str, filename: str, total_pages: int) -> Dict[str, Any]:
        """
        Extract structured content using Gemini LLM with text input
        
        Args:
            text_content: Extracted text from LlamaParse
            filename: Original filename
            total_pages: Total number of pages
            
        Returns:
            PDFExtractionResult with structured content
        """
        try:
            # Render the extraction prompt
            template = self.jinja_env.get_template("pdf_extraction_prompt.j2")
            prompt = template.render(
                filename=filename,
                total_pages=total_pages,
                document_text=text_content
            )
            
            # Call Gemini with structured output using text-only input
            logger.info("Sending text to Gemini for structured analysis...")
            
            # Use instructor with async handling
            response = await self.model.messages.create(
                    messages=[{
                        "role": "user", 
                        "content": prompt
                    }],
                    response_model=PDFExtractionResult,
                    max_retries=3
                )
            
            # Run the async function synchronously
            # response = asyncio.run(_create_response())
            
            logger.info("Successfully received structured response from Gemini")
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Error extracting with Gemini: {str(e)}")
            # Return a basic structure with error information
            raise Exception(f"Error extracting with Gemini: {str(e)}")
    
    def _convert_to_legacy_format(self, extraction_result: PDFExtractionResult) -> Dict[str, Any]:
        """
        Convert the new structured format to the legacy format for backward compatibility
        
        Args:
            extraction_result: PDFExtractionResult object
            
        Returns:
            Dictionary in the legacy format
        """
        
        # Create metadata in legacy format
        metadata = {
            "page_count": extraction_result.metadata.total_pages,
            "title": extraction_result.company_info.company_name or "",
            "word_count": len(extraction_result.full_text.split()) if extraction_result.full_text else 0,
            "quality_score": extraction_result.metadata.quality_score,
            "confidence_score": extraction_result.metadata.confidence_score,
            "extraction_method": "gemini_llm"
        }
        
        # Create the legacy format structure
        legacy_format = {
            "full_text": extraction_result.full_text,
            "tables": tables,
            "images": images,
            "metadata": metadata,
            
            # Add structured business information as additional fields
            "company_info": extraction_result.company_info.dict(),
            "financial_metrics": extraction_result.financial_metrics.dict(),
            "market_info": extraction_result.market_info.dict(),
            "team_info": extraction_result.team_info.dict(),
            "business_model": extraction_result.business_model.dict(),
            "traction_metrics": extraction_result.traction_metrics.dict(),
            "funding_info": extraction_result.funding_info.dict(),
            "risk_factors": extraction_result.risk_factors.dict(),
            
            # Additional insights
            "key_insights": extraction_result.key_insights,
            "missing_information": extraction_result.missing_information,
            "recommendations": extraction_result.recommendations,
            "sections": [
                {
                    "title": section.title,
                    "content": section.content,
                    "page": section.page_number,
                    "key_points": section.key_points
                }
                for section in extraction_result.sections
            ]
        }
        
        return legacy_format
    
    def get_document_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get basic document information (legacy compatibility method)
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Document metadata and basic info
        """
        return self._get_pdf_info(pdf_path)
    
    def get_page_text(self, pdf_path: str, page_num: int) -> str:
        """
        Extract text from a specific page using LlamaParse (legacy compatibility method)
        
        Args:
            pdf_path: Path to the PDF file
            page_num: Page number (0-indexed)
            
        Returns:
            Text content of the page
        """
        try:
            # For page-specific extraction, we'll extract the full document and return the specific page
            # This is a limitation of LlamaParse - it doesn't support single page extraction
            logger.info(f"Extracting page {page_num + 1} text using LlamaParse")
            
            full_text = self._extract_with_llamaparse(pdf_path)
            
            # Since LlamaParse doesn't provide page-specific extraction,
            # we'll return a portion of the text or the full text with a warning
            if page_num == 0:
                return full_text
            else:
                # For non-first pages, return a message indicating the limitation
                logger.warning("LlamaParse doesn't support page-specific extraction. Returning full document text.")
                return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from page {page_num}: {str(e)}")
            raise Exception(f"Page text extraction failed: {str(e)}")

if __name__ == "__main__":
    # Test the PDF processor
    pdf_processor = PDFProcessor()
    
    # Test with a sample PDF file
    test_pdf_path = "CHEELIZZA PIZZA INDIA LTD - INVESTMENT DECK.pdf"  # Replace with actual PDF path for testing
    
    if os.path.exists(test_pdf_path):
        try:
            full_text, extracted_content = pdf_processor.extract_content(test_pdf_path)
            print(f"Full text: {full_text}")
            print(f"Extracted content: {extracted_content}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Test PDF file not found: {test_pdf_path}")
        print("Testing with Gemini API configuration...")
        try:
            processor = PDFProcessor()
            print("✅ Gemini PDF processor initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing processor: {e}")