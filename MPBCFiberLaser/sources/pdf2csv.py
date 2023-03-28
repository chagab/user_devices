import pdfminer.high_level


def pdf_to_text(input_path, output_path):
    # Extract text from the PDF file using pdfminer
    text = pdfminer.high_level.extract_text(input_path)

    # Save the extracted text to a file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)


# Example usage
input_path = "MPB_commands.pdf"
output_path = "example.txt"
pdf_to_text(input_path, output_path)
