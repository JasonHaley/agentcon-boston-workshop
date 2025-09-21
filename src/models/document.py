import os
import re
from typing import IO, Optional

class Page:
    def __init__(self, page_num: int, offset: int, text: str):
        self.page_num = page_num
        self.offset = offset
        self.text = text

class File:
    def __init__(self, content: IO, acls: Optional[dict[str, list]] = None, url: Optional[str] = None):
        self.content = content
        self.acls = acls or {}
        self.url = url

    def filename(self):
        return os.path.basename(self.content.name)

    def file_extension(self):
        return os.path.splitext(self.content.name)[1]   

    def close(self):
        if self.content:
            self.content.close()

    def filename_to_id(self):
        filename_ascii = re.sub("[^0-9a-zA-Z_-]", "_", self.filename())
        return f"file-{filename_ascii}"