import os
from datetime import datetime
from fpdf import FPDF
from pathlib import Path

class FileGenerator:
    """Generates files in different formats (PDF, Text, Markdown)"""

    def __init__(self, download_folder='downloads'):
        self.download_folder = download_folder
        Path(download_folder).mkdir(exist_ok=True)

    def generate_filename(self, topic_name, content_title, format_type):
        """Generate a safe filename"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = f"{content_title}_{timestamp}".replace(' ', '_')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '_-')
        return f"{safe_name}.{format_type}"

    def generate_pdf(self, topic_name, content):
        """Generate PDF file"""
        filename = self.generate_filename(topic_name, content['title'], 'pdf')
        filepath = os.path.join(self.download_folder, filename)

        pdf = FPDF()
        pdf.add_page()

        # Set fonts
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f"Topic: {topic_name}", ln=True, align='C')

        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, content['title'], ln=True)
        pdf.ln(5)

        # Explanation
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Explanation:', ln=True)
        pdf.set_font('Arial', '', 11)

        # Handle multi-line text
        pdf.multi_cell(0, 5, content['explanation'])
        pdf.ln(5)

        # Code Examples
        if content.get('code_examples'):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Code Examples:', ln=True)
            pdf.set_font('Courier', '', 10)
            pdf.multi_cell(0, 4, content['code_examples'])

        # Add footer
        pdf.set_font('Arial', 'I', 8)
        pdf.ln(5)
        pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", align='C')

        pdf.output(filepath)
        return filename, filepath

    def generate_text(self, topic_name, content):
        """Generate plain text file"""
        filename = self.generate_filename(topic_name, content['title'], 'txt')
        filepath = os.path.join(self.download_folder, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"TOPIC: {topic_name}\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"TITLE: {content['title']}\n")
            f.write("-" * 80 + "\n\n")

            f.write("EXPLANATION:\n")
            f.write("-" * 80 + "\n")
            f.write(content['explanation'])
            f.write("\n\n")

            if content.get('code_examples'):
                f.write("CODE EXAMPLES:\n")
                f.write("-" * 80 + "\n")
                f.write(content['code_examples'])
                f.write("\n\n")

            f.write("-" * 80 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n")

        return filename, filepath

    def generate_markdown(self, topic_name, content):
        """Generate Markdown file"""
        filename = self.generate_filename(topic_name, content['title'], 'md')
        filepath = os.path.join(self.download_folder, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {topic_name}\n\n")
            f.write(f"## {content['title']}\n\n")

            f.write("### Explanation\n\n")
            f.write(content['explanation'])
            f.write("\n\n")

            if content.get('code_examples'):
                f.write("### Code Examples\n\n")
                f.write("```\n")
                f.write(content['code_examples'])
                f.write("\n```\n\n")

            f.write(f"---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        return filename, filepath

    def generate_file(self, topic_name, content, format_type='pdf'):
        """Generate file in specified format"""
        format_type = format_type.lower()

        if format_type == 'pdf':
            return self.generate_pdf(topic_name, content)
        elif format_type == 'text' or format_type == 'txt':
            return self.generate_text(topic_name, content)
        elif format_type == 'markdown' or format_type == 'md':
            return self.generate_markdown(topic_name, content)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def generate_pdf_from_wikipedia(self, title, content, url):
        """Generate PDF from Wikipedia content"""
        filename = self.generate_filename(title, title, 'pdf')
        filepath = os.path.join(self.download_folder, filename)

        try:
            pdf = FPDF('P', 'mm', 'A4')
            pdf.add_page()
            pdf.set_margins(10, 10, 10)

            # Title
            pdf.set_font('Helvetica', 'B', 16)
            pdf.cell(0, 10, "Wikipedia Article", ln=True, align='C')
            pdf.ln(5)

            # Article title
            pdf.set_font('Helvetica', 'B', 12)
            title_clean = title[:50] if len(title) > 50 else title
            pdf.cell(0, 8, title_clean, ln=True)
            pdf.ln(2)

            # URL - shortened
            pdf.set_font('Helvetica', 'I', 8)
            url_display = url[:60] + "..." if len(url) > 60 else url
            pdf.cell(0, 6, f"Source: {url_display}", ln=True)
            pdf.ln(3)

            # Content
            pdf.set_font('Helvetica', '', 9)
            
            # Clean and shorten content for PDF
            lines = content.split('\n')
            char_count = 0
            max_chars = 5000  # Limit content size
            
            for line in lines:
                if char_count > max_chars:
                    pdf.cell(0, 6, "[...content truncated...]", ln=True)
                    break
                    
                if line.strip():
                    # Remove problematic unicode
                    clean_line = ''.join(c if ord(c) < 128 else '?' for c in line.strip())
                    if clean_line:
                        pdf.multi_cell(0, 4, clean_line, max_lines=2)
                        char_count += len(clean_line)
                else:
                    pdf.ln(2)

            pdf.ln(4)

            # Footer
            pdf.set_font('Helvetica', 'I', 7)
            pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

            pdf.output(filepath)
            return filename, filepath
            
        except Exception as e:
            # If PDF fails, at least create a txt version
            print(f"PDF generation warning: {str(e)}")
            # Create text version as fallback
            return self.generate_text_from_wikipedia(title, content, url)
    
    def generate_markdown_from_wikipedia(self, title, content, url):
        """Generate Markdown from Wikipedia content"""
        filename = self.generate_filename(title, title, 'md')
        filepath = os.path.join(self.download_folder, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Source:** [{url}]({url})\n\n")
            f.write(f"---\n\n")
            f.write(content)
            f.write(f"\n\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        return filename, filepath
    
    def generate_text_from_wikipedia(self, title, content, url):
        """Generate plain text from Wikipedia content"""
        filename = self.generate_filename(title, title, 'txt')
        filepath = os.path.join(self.download_folder, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"WIKIPEDIA ARTICLE: {title}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Source: {url}\n\n")
            f.write("-" * 80 + "\n\n")
            f.write(content)
            f.write("\n\n")
            f.write("-" * 80 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n")

        return filename, filepath

    def remove_file(self, filename):
        """Remove a generated file"""
        filepath = os.path.join(self.download_folder, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    def cleanup_old_files(self, days=7):
        """Remove files older than specified days"""
        import time

        cutoff_time = time.time() - (days * 24 * 60 * 60)

        for filename in os.listdir(self.download_folder):
            filepath = os.path.join(self.download_folder, filename)
            if os.path.isfile(filepath):
                if os.stat(filepath).st_mtime < cutoff_time:
                    os.remove(filepath)
