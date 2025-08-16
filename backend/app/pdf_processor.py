import logging
from typing import Dict, Any
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
# from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.pipeline_options import smolvlm_picture_description
from docling.document_converter import DocumentConverter, PdfFormatOption
import tempfile
import os


logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    PDF content extraction using Docling
    """
    
    def __init__(self):
        """Initialize the PDF processor with optimized pipeline options"""
        # Configure pipeline options for better extraction
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True  # Enable OCR for scanned documents
        pipeline_options.ocr_options.use_gpu = False
        pipeline_options.do_table_structure = True  # Extract table structure
        pipeline_options.table_structure_options.do_cell_matching = True
        # pipeline_options.do_formula_enrichment = True
        # pipeline_options.generate_picture_images = True
        # pipeline_options.images_scale = 2
        # pipeline_options.do_picture_classification = True
        # pipeline_options.do_picture_description = True
        pipeline_options.picture_description_options = smolvlm_picture_description
        
        # Configure document converter
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
    
    def extract_content(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract structured content from PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        try:
            logger.info(f"Starting PDF extraction for: {pdf_path}")
            
            # Convert document
            result = self.converter.convert(pdf_path)
            
            print(f"Result: {result.document}")
            
            logger.info(f"Result: {result.document}")
            
            # Extract text content
            full_text = result.document.export_to_markdown()
            
            # Extract tables if any
            tables = []
            for table in result.document.tables:
                table_data = {
                    "caption": getattr(table, 'caption', ''),
                    "data": table.export_to_dataframe().to_dict('records') if hasattr(table, 'export_to_dataframe') else []
                }
                tables.append(table_data)
            
            # Extract key-value pairs and metadata
            metadata = {
                "page_count": len(result.document.pages),
                "title": getattr(result.document, 'title', ''),
                "tables_count": len(tables),
                "has_images": len(result.document.pictures) > 0,
                "word_count": len(full_text.split()) if full_text else 0
            }
            
            # Structure the extracted content
            extracted_content = {
                "full_text": full_text,
                "tables": tables,
                "metadata": metadata,
                "sections": self._identify_sections(full_text)
            }
            
            logger.info(f"Successfully extracted {metadata['word_count']} words from {metadata['page_count']} pages")
            return extracted_content
            
        except Exception as e:
            logger.error(f"Error extracting PDF content: {str(e)}")
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    def _identify_sections(self, text: str) -> Dict[str, str]:
        """
        Identify and extract key sections from the text
        
        Args:
            text: Full extracted text
            
        Returns:
            Dictionary with identified sections
        """
        sections = {}
        
        if not text:
            return sections
        
        # Common section headers to look for in pitch decks
        section_keywords = {
            "company_overview": [
                "company overview", "about us", "about the company", "introduction",
                "company profile", "who we are"
            ],
            "business_model": [
                "business model", "revenue model", "how we make money",
                "monetization", "business strategy"
            ],
            "market_opportunity": [
                "market opportunity", "market size", "tam", "total addressable market",
                "market analysis", "opportunity"
            ],
            "financial_projections": [
                "financial projections", "financials", "revenue projections",
                "financial forecast", "financial outlook", "p&l", "profit and loss"
            ],
            "traction": [
                "traction", "milestones", "achievements", "growth metrics",
                "customer acquisition", "user growth"
            ],
            "team": [
                "team", "leadership", "founders", "management team",
                "key personnel", "advisory board"
            ],
            "funding": [
                "funding", "investment", "capital requirements", "use of funds",
                "fundraising", "valuation"
            ],
            "competitive_advantage": [
                "competitive advantage", "differentiation", "moat", "unique value proposition",
                "competitive landscape", "competitive analysis"
            ]
        }
        
        text_lower = text.lower()
        lines = text.split('\n')
        
        for section_name, keywords in section_keywords.items():
            section_content = []
            capture_mode = False
            
            for i, line in enumerate(lines):
                line_lower = line.lower().strip()
                
                # Check if this line starts a new section
                if any(keyword in line_lower for keyword in keywords):
                    capture_mode = True
                    section_content = [line.strip()]
                    continue
                
                # Check if we've hit another section (stop capturing)
                elif capture_mode and any(
                    any(kw in line_lower for kw in other_keywords)
                    for other_section, other_keywords in section_keywords.items()
                    if other_section != section_name
                ):
                    break
                
                # Capture content if we're in capture mode
                elif capture_mode and line.strip():
                    section_content.append(line.strip())
                    
                    # Stop if we've captured enough content (prevent over-capturing)
                    if len(section_content) > 50:  # Limit section size
                        break
            
            if section_content:
                sections[section_name] = '\n'.join(section_content)
        
        return sections
    
if __name__ == "__main__":
    pdf_processor = PDFProcessor()
    pdf_path = "CHEELIZZA PIZZA INDIA LTD - INVESTMENT DECK.pdf"
    extracted_content = pdf_processor.extract_content(pdf_path)
    # print(extracted_content)