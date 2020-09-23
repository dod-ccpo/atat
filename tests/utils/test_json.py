import json

from atat.utils.json import CustomJSONEncoder
from tests.factories import AttachmentFactory

encoder = CustomJSONEncoder()


def test_custom_encoder_serializes_attachments():
    filename = "jar_jar_is_secretly_a_sith_lord.pdf"
    attachment = AttachmentFactory.create(filename=filename)
    encoded = encoder.encode({"file": attachment})
    expected = json.dumps({"file": filename})
    assert encoded == expected
