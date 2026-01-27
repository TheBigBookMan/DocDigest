import json

def parse_lambda(event):
    event_body = event['Records'][0]
    sns_event = event_body['Sns']

    return {
        'event_source': event_body['EventSource'],
        'event_time': sns_event['Timestamp'],
        'event_type': sns_event['Type'],
        'event_message': json.loads(sns_event['Message']),
    }

def build_html_email(session):
    """Build HTML email body"""

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .summary {{ background: #f4f4f4; padding: 15px; margin: 20px 0; }}
        .file {{ border: 1px solid #ddd; margin: 20px 0; padding: 15px; }}
        .file-header {{ background: #2196F3; color: white; padding: 10px; margin: -15px -15px 15px -15px; }}
        .items {{ margin: 15px 0; }}
        .item {{ padding: 10px; border-left: 3px solid #4CAF50; margin: 10px 0; background: #f9f9f9; }}
        .financial {{ background: #fff3cd; padding: 15px; margin-top: 15px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 8px; text-align: left; }}
        th {{ background: #f4f4f4; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>DocDigest Processing Complete</h1>
    </div>

    <div class="summary">
        <p><strong>Session ID:</strong> {session['session_id']}</p>
        <p><strong>Files Processed:</strong> {session['total_files']}</p>
        <p><strong>Completed:</strong> {format_timestamp(session['completed_at'])}</p>
    </div>
"""

    results = session.get('results', {})

    for file_num, (filename, data) in enumerate(results.items(), start=1):
        html += f"""
    <div class="file">
        <div class="file-header">
            <h2>📄 File {file_num} of {len(results)}: {filename}</h2>
        </div>

        <table>
            <tr>
                <th>Vendor</th>
                <td>{data.get('vendor_name', 'N/A')}</td>
            </tr>
            <tr>
                <th>Invoice Number</th>
                <td>{data.get('invoice_number', 'N/A')}</td>
            </tr>
            <tr>
                <th>Date</th>
                <td>{data.get('date', 'N/A')}</td>
            </tr>
            <tr>
                <th>Currency</th>
                <td>{data.get('currency', 'N/A')}</td>
            </tr>
        </table>

        <div class="items">
            <h3>Line Items</h3>
"""

        items = data.get('items', [])
        for item_num, item in enumerate(items, start=1):
            html += f"""
            <div class="item">
                <strong>Item {item_num}:</strong> {item.get('description', 'N/A')}<br>
                Quantity: {item.get('quantity', 'N/A')} | 
                Unit Price: {item.get('unit_price', 'N/A')} | 
                <strong>Total: {item.get('total', 'N/A')}</strong>
            </div>
"""

        html += f"""
        </div>

        <div class="financial">
            <table>
                <tr>
                    <th>Subtotal</th>
                    <td>{data.get('subtotal', 'N/A')}</td>
                </tr>
                <tr>
                    <th>Tax</th>
                    <td>{data.get('tax', 'N/A')}</td>
                </tr>
                <tr style="background: #4CAF50; color: white;">
                    <th><strong>TOTAL</strong></th>
                    <td><strong>{data.get('total', 'N/A')}</strong></td>
                </tr>
            </table>
        </div>
    </div>
"""

    html += """
    <div class="summary" style="text-align: center; margin-top: 30px;">
        <p>Thank you for using DocDigest!</p>
    </div>
</body>
</html>
"""

    return html

def format_timestamp(iso_timestamp):
    """
    Format ISO timestamp for human-readable display

    Args:
        iso_timestamp: ISO format string (e.g., "2026-01-22T14:30:45.123Z")

    Returns:
        str: Formatted timestamp (e.g., "January 22, 2026 at 02:30 PM UTC")
    """
    from dateutil import parser

    # Parse ISO string to datetime object
    dt = parser.parse(iso_timestamp)

    # Format for display
    return dt.strftime('%B %d, %Y at %I:%M %p UTC')