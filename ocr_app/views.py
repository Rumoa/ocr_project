import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Disable CUDA globally


from django.shortcuts import render

from .forms import ImageUploadForm
from pix2text import Pix2Text
import os
from django.conf import settings


import base64
from django.core.files.base import ContentFile
from .forms import ImageUploadForm
from pix2text import Pix2Text
import os
from django.conf import settings

import base64
from django.core.files.base import ContentFile
from pix2text import Pix2Text
from django.conf import settings
from django.shortcuts import render
import os
import uuid


# def upload_image(request):
#     if request.method == "POST":
#         image_data = request.POST.get("image")

#         if image_data:
#             # Decode the base64 image data
#             format, imgstr = image_data.split(";base64,")
#             ext = format.split("/")[-1]
#             # Create a unique file name using uuid
#             image_name = str(uuid.uuid4()) + "." + ext
#             image_path = os.path.join(settings.MEDIA_ROOT, image_name)

#             # Save the decoded image
#             image = ContentFile(base64.b64decode(imgstr), name=image_name)
#             with open(image_path, "wb") as f:
#                 f.write(image.read())

#             # Run OCR on the image using Pix2Text
#             p2t = Pix2Text(provider="CPUExecutionProvider")
#             # latex_code = p2t.detect(image_path)  # Extract LaTeX code

#             latex_code = p2t.recognize_formula(image_path)

#             # Return the LaTeX to the user
#             return render(request, "result.html", {"latex_code": latex_code})

#     return render(request, "upload.html")


import base64
from django.core.files.base import ContentFile
from django.conf import settings
from django.shortcuts import render
import os
import uuid
from pix2text import Pix2Text
from datetime import datetime


# Define maximum number of saved images
MAX_IMAGES = 2  # Adjust this number as needed


def upload_image(request):
    if request.method == "POST":
        image_data = None
        image_file = None

        # Check if an image was pasted
        if request.POST.get("image"):
            image_data = request.POST.get("image")

        # Check if an image was uploaded
        if request.FILES.get("file"):
            image_file = request.FILES["file"]

        if image_data:
            # Handle base64 pasted image
            format, imgstr = image_data.split(";base64,")
            ext = format.split("/")[-1]
            image_name = str(uuid.uuid4()) + "." + ext
            image_path = os.path.join(settings.MEDIA_ROOT, image_name)

            # Save the image
            image = ContentFile(base64.b64decode(imgstr), name=image_name)
            with open(image_path, "wb") as f:
                f.write(image.read())

        elif image_file:
            # Handle uploaded image
            image_name = image_file.name
            image_path = os.path.join(settings.MEDIA_ROOT, image_name)

            # Save the uploaded image
            with open(image_path, "wb+") as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

        # Perform OCR
        if image_path:
            p2t = Pix2Text()
            latex_code = p2t.recognize_formula(image_path)
            print(latex_code)

            # latex_code = p2t.recognize(image_path)

            # Return the result
            cleanup_old_images()
            return render(request, "result.html", {"latex_code": latex_code})
    return render(request, "upload.html")


def cleanup_old_images():
    media_folder = settings.MEDIA_ROOT
    # media_folder = os.path.join(
    #     settings.MEDIA_ROOT, "media"
    # )  # Adjust this path as necessary
    print(media_folder)
    if not os.path.exists(media_folder):
        return

    # List all files in the media folder
    files = os.listdir(media_folder)

    # Get full paths for each file
    file_paths = [
        os.path.join(media_folder, f)
        for f in files
        if f.endswith((".png", ".jpg", ".jpeg"))
    ]

    # Sort files by creation time (oldest first)
    file_paths.sort(key=os.path.getctime)

    # Delete files if we exceed the maximum number of images
    while len(file_paths) > MAX_IMAGES:
        os.remove(file_paths[0])  # Remove the oldest file
        file_paths.pop(0)  # Remove the path from the list
