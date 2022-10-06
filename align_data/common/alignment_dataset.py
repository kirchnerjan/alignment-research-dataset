from dataclasses import dataclass , field
from collections import UserDict
import hashlib
import json
from typing import List, Optional
import os
import logging
import jsonlines
import sys

INIT_DICT = {
    "source" : None,
    "id" : None,
    "text" : None,
    "date_published" : None,
    "title" : None,
    "url" : None,
}

TEXT_LEN = 1000


logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s',
                    level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class AlignmentDataset:
    name : str
    done_ids = []

    def setup(self) -> None:

        self.write_jsonl_path = os.path.join(os.path.abspath( os.path.dirname( __file__ ) ) , "../../data/" + self.name + ".jsonl")
        
        if not os.path.exists(self.write_jsonl_path):
            logger.info(f"No previous data found at {self.write_jsonl_path}")
            return None
        
        with jsonlines.open(self.write_jsonl_path, mode='r') as reader:
            for ii , entry in enumerate(reader):
                logger.info(f"Found {entry['title']}")
                self.done_ids.append((self.name , ii))
    
    def __str__(self) -> str:
        return f"{self.name} dataset will be written to {self.write_jsonl_path}"

    def fetch_entries(self):
        raise NotImplementedError

    def _entry_done(self , entry):
        """
        Check if entry is already done
        """
        return entry in self.done_ids


class DataEntry(UserDict):
    def __init__(self , *args , **kwargs):
        super().__init__(*args , **kwargs)
        for k , v in INIT_DICT.items():
            if k not in self:
                self[k] = v
                
    def add_id(self):
        assert self["text"] is not None , "Entry is missing text"
        text_excerpt = self["text"][:TEXT_LEN].encode("utf-8")
        self["id"] = hashlib.md5(text_excerpt).hexdigest()
        
    def _verify_id(self):
        assert self["id"] is not None , "Entry is missing id"
        assert self["text"] is not None , "Entry is missing text"
        text_excerpt = self["text"][:TEXT_LEN].encode("utf-8")
        assert self["id"] == hashlib.md5(text_excerpt).hexdigest() , "Entry id does not match text"
                
    def toJSON(self):
        for k , _ in INIT_DICT.items():
            assert self[k] is not None , f"Entry is missing key {k}"
        self._verify_id()
        return dict(self.data)
