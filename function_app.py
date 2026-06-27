import logging
import os
import azure.functions as func

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

@app.blob_trigger(
    arg_name="myblob",
    path="raw-images/{name}",
    connection="AzureWebJobsStorage"
)
def AddWatermarkFunction(myblob: func.InputStream):

    logging.info(f"Processing: {myblob.name}")

    image = Image.open(BytesIO(myblob.read()))

    draw = ImageDraw.Draw(image)

    watermark = "Rahul"

    width, height = image.size

    font = ImageFont.truetype("arial.ttf",60)

    #postion 
    x = width - 250 
    y = height - 80

    draw.text(
        (x,y),
        watermark,
        font = font,
        fill=(255, 255, 255)
    )

    output = BytesIO()
    image.save(output, format="JPEG")
    output.seek(0)

    connection_string = os.getenv("AzureWebJobsStorage")

    blob_service = BlobServiceClient.from_connection_string(
        connection_string
    )

    container = blob_service.get_container_client(
        "processed-images"
    )

    container.upload_blob(
        name=os.path.basename(myblob.name),
        data=output,
        overwrite=True
    )

    logging.info("Watermark added successfully")