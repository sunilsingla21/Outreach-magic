import os

from flask import render_template_string
from markupsafe import Markup

from app.extensions import storage_client


def svg(static_file, class_=''):
    static_folder = os.path.abspath('./app/static')
    file_path = os.path.join(static_folder, static_file)
    with open(file_path) as f:
        svg = f.read()
    return Markup(render_template_string(svg, class_=class_))


def upload_to_bucket(blob_name, file, bucket_name):
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(blob_name)
    blob.upload_from_file(file, )
    blob.make_public()

    return blob.public_url
