from dataclasses import dataclass, asdict, field
from email.policy import default
from typing import List
import json

@dataclass
class Token:
    name: str
    image: str
    series: str
    collection_name: str
    description: str
    blockchain: str
    attributes: List[dict]
    is_generated: bool = field(default=False)

    def replace_image(self, cid: str):
        self.image = f'https://gateway.pinata.cloud/ipfs/{ cid["IpfsHash"] }/images/{ self.name.split("#")[1] }.jpg/'
        self.is_generated = True
        return self

    def to_json(self):
        return json.dumps({k:v for k,v in asdict(self).items() if v != True}, indent=4)
