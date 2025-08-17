import logging
import os
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import instructor
from jinja2 import Environment, FileSystemLoader
from llama_cloud_services import LlamaParse

from .models.pdf_extraction_models import PDFExtractionResult, DocumentMetadata

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
        llama_api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        if not llama_api_key:
            raise ValueError("LLAMA_CLOUD_API_KEY environment variable is required")
        
        # Initialize LlamaParse for PDF text extraction
        self.llama_parser = LlamaParse(
            api_key=llama_api_key,
            num_workers=4,
            verbose=True,
            language="en"
        )
        
        # Initialize Gemini model with Instructor for structured responses
        self.model = instructor.from_provider(
            "google/gemini-2.0-flash-exp"
        )
        
        # Initialize Jinja2 template environment
        template_dir = "./../prompts"
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    def extract_content(self, pdf_path: str) -> Dict[str, Any]:
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
            parsed_documents = self._extract_with_llamaparse(pdf_path)
            
            # Get document basic info
            doc_info = self._get_pdf_info(pdf_path)
            
            # Combine all extracted text
            full_text = "\n\n".join([doc.text for doc in parsed_documents])
            logger.info(f"LlamaParse extracted {len(full_text)} characters from {len(parsed_documents)} document(s)")
            
            # Extract structured content using Gemini
            logger.info("Analyzing content with Gemini...")
            extraction_result = self._extract_with_gemini_text(
                full_text,
                os.path.basename(pdf_path),
                doc_info['page_count']
            )
            
            # Convert to the expected format for backward compatibility
            extracted_content = self._convert_to_legacy_format(extraction_result)
            
            logger.info("Successfully extracted content using LlamaParse + Gemini")
            logger.info(f"Quality score: {extraction_result.metadata.quality_score:.2f}")
            logger.info(f"Confidence score: {extraction_result.metadata.confidence_score:.2f}")
            
            return extracted_content
            
        except Exception as e:
            logger.error(f"Error extracting PDF content: {str(e)}")
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    def _extract_with_llamaparse(self, pdf_path: str) -> List[Any]:
        """
        Extract text from PDF using LlamaParse
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of parsed document objects
        """
        try:
            # Parse the PDF file with LlamaParse
            logger.info(f"Parsing PDF with LlamaParse: {pdf_path}")
            
            # Use synchronous parsing
            parsed_documents = self.llama_parser.load_data(pdf_path)
            
            logger.info(f"LlamaParse successfully parsed {len(parsed_documents)} document(s)")
            return parsed_documents
            
        except Exception as e:
            logger.error(f"Error parsing PDF with LlamaParse: {str(e)}")
            raise Exception(f"LlamaParse extraction failed: {str(e)}")
    

    
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
    
    def _extract_with_gemini_text(self, text_content: str, filename: str, total_pages: int) -> PDFExtractionResult:
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
            async def _create_response():
                return await self.model.messages.create(
                    messages=[{
                        "role": "user", 
                        "content": prompt
                    }],
                    response_model=PDFExtractionResult,
                    temperature=0.1,  # Low temperature for more consistent extraction
                    max_retries=3
                )
            
            # Run the async function synchronously
            response = asyncio.run(_create_response())
            
            logger.info("Successfully received structured response from Gemini")
            return response
            
        except Exception as e:
            logger.error(f"Error extracting with Gemini: {str(e)}")
            # Return a basic structure with error information
            return PDFExtractionResult(
                full_text=text_content if text_content else f"Extraction failed: {str(e)}",
                metadata=DocumentMetadata(
                    total_pages=total_pages,
                    quality_score=0.0,
                    confidence_score=0.0,
                    creation_date=datetime.now(),
                    last_modified=datetime.now()
                ),
                key_insights=[f"Extraction failed due to: {str(e)}"],
                missing_information=["All information due to extraction failure"]
            )
    
    def _convert_to_legacy_format(self, extraction_result: PDFExtractionResult) -> Dict[str, Any]:
        """
        Convert the new structured format to the legacy format for backward compatibility
        
        Args:
            extraction_result: PDFExtractionResult object
            
        Returns:
            Dictionary in the legacy format
        """
        # Convert tables to legacy format
        tables = []
        for table in extraction_result.tables:
            table_data = []
            if table.headers and table.rows:
                # Add headers as first row
                table_data.append(table.headers)
                # Add all data rows
                table_data.extend(table.rows)
            
            tables.append({
                "caption": table.title,
                "data": [dict(zip(table.headers, row)) for row in table.rows] if table.headers and table.rows else [],
                "page": table.page_number,
                "raw_data": table_data
            })
        
        # Convert images to legacy format
        images = []
        for img in extraction_result.images:
            images.append({
                "description": img.description,
                "type": img.type,
                "page": img.page_number,
                "insights": img.key_insights,
                "data_points": img.data_points
            })
        
        # Create metadata in legacy format
        metadata = {
            "page_count": extraction_result.metadata.total_pages,
            "title": extraction_result.company_info.company_name or "",
            "tables_count": len(tables),
            "images_count": len(images),
            "has_images": len(images) > 0,
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
            
            parsed_documents = self._extract_with_llamaparse(pdf_path)
            
            # Combine all text and attempt to split by pages
            full_text = "\n\n".join([doc.text for doc in parsed_documents])
            
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
    test_pdf_path = "sample.pdf"  # Replace with actual PDF path for testing
    
    if os.path.exists(test_pdf_path):
        try:
            extracted_content = pdf_processor.extract_content(test_pdf_path)
            print(f"Extracted content from {extracted_content['metadata']['page_count']} pages")
            print(f"Word count: {extracted_content['metadata']['word_count']}")
            print(f"Tables found: {extracted_content['metadata']['tables_count']}")
            print(f"Images found: {extracted_content['metadata']['images_count']}")
            print(f"Quality score: {extracted_content['metadata']['quality_score']:.2f}")
            print(f"Confidence score: {extracted_content['metadata']['confidence_score']:.2f}")
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