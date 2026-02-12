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
