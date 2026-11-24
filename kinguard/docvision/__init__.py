"""Reading photographed medical and insurance documents.

Classification and extraction in one call; the image kept privately so every
extracted fact stays checkable against the paper it came from.

The function is exported as `read_document`, not `read`. A re-export named
`read` shadows the `kinguard.docvision.read` MODULE, so
`from kinguard.docvision import read` silently hands back a function where a
caller expects a module. The bills package had exactly this bug, it was fixed
there, and it was then reintroduced here within the hour — hence the name and
this note.
"""

from kinguard.docvision.ingest import DocumentRejected, ingest_document_image
from kinguard.docvision.read import KINDS, Reading, image_sha256
from kinguard.docvision.read import read as read_document

__all__ = ["KINDS", "DocumentRejected", "Reading", "image_sha256",
           "ingest_document_image", "read_document"]
