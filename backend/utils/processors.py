
from models.files import File
from models.settings import CommonsDep
from parsers.audio import process_audio
from parsers.csv import process_csv
from parsers.docx import process_docx
from parsers.epub import process_epub
from parsers.html import process_html
from parsers.markdown import process_markdown
from parsers.notebook import process_ipnyb
from parsers.odt import process_odt
from parsers.pdf import process_pdf
from parsers.powerpoint import process_powerpoint
from parsers.txt import process_txt

file_processors = {
    ".txt": process_txt,
    ".csv": process_csv,
    ".md": process_markdown,
    ".markdown": process_markdown,
    ".m4a": process_audio,
    ".mp3": process_audio,
    ".webm": process_audio,
    ".mp4": process_audio,
    ".mpga": process_audio,
    ".wav": process_audio,
    ".mpeg": process_audio,
    ".pdf": process_pdf,
    ".html": process_html,
    ".pptx": process_powerpoint,
    ".docx": process_docx,
    ".odt": process_odt,
    ".epub": process_epub,
    ".ipynb": process_ipnyb,
}




async def filter_file(commons: CommonsDep, file: File, enable_summarization: bool, brain_id, openai_api_key):
    await file.compute_file_sha1()
    
    print("file sha1", file.file_sha1)
    if file.file_already_exists( brain_id):
        return {"message": f"🤔 {file.file.filename} already exists in brain {brain_id}.", "type": "warning"}
    elif file.file_is_empty():
        return {"message": f"❌ {file.file.filename} is empty.", "type": "error"}
    else:
        if file.file_extension in file_processors:
            await file_processors[file.file_extension](commons,file, enable_summarization, brain_id ,openai_api_key )
            return {"message": f"✅ {file.file.filename} has been uploaded to brain {brain_id}.", "type": "success"}
        else:
            return {"message": f"❌ {file.file.filename} is not supported.", "type": "error"}

