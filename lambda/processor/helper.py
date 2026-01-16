import json
import fitz
import logging

logger = logging.getLogger()


def parse_lambda(event):
    event_body = event['Records'][0]['body']
    s3_event = json.loads(event_body)
    event_records = s3_event['Records'][0]

    return {
        'event_source': event_records['eventSource'],
        'event_time': event_records['eventTime'],
        'event_name': event_records['eventName'],
        's3': event_records['s3'],
    }

def extract_text_from_pdf(pdf_bytes):
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            text += page_text + "\n\n"
            logger.debug(f"Page {page_num + 1}: {len(page_text)} characters")

        doc.close()

        if not text.strip():
            raise ValueError("No text extracted from PDF - might be scanned/image-based")

        return text.strip()

    except Exception as e:
        logger.error(f"PDF text extraction failed: {str(e)}", exc_info=True)
        raise
