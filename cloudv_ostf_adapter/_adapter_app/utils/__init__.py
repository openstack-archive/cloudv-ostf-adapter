import re
import uuid


def generate_uuid():
    return str(uuid.uuid4())


def valid_uuid(uid):
    return re.match(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', uid) is not None
