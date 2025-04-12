from llama_index.readers.file import ImageReader, PptxReader, PDFReader, DocxReader, VideoAudioReader, PandasCSVReader, EpubReader, MarkdownReader, MboxReader, IPYNBReader

def file_extractor():
    return {
        ".pdf": PDFReader(),
        ".docx": DocxReader(),
        ".pptx": PptxReader(),
        ".jpg": ImageReader(parse_text=True), # optional field keep_image=True this will return the image in the document as base64 encoded string
        ".png": ImageReader(parse_text=True),
        ".jpeg": ImageReader(parse_text=True),
        ".mp3": VideoAudioReader(), # you can pass Openai whisper model `model_version` to this
        ".mp4": VideoAudioReader(),
        ".csv": PandasCSVReader(),
        ".epub": EpubReader(),
        ".md": MarkdownReader(),
        ".mbox": MboxReader(),
        ".ipynb": IPYNBReader(),
    }
