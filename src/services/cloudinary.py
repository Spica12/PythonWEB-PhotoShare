import cloudinary
import cloudinary.uploader
import cloudinary.api

# Import to format the JSON responses
# ==============================
import json

# Set configuration parameter: return "https" URLs by setting secure=True
# ==============================
config = cloudinary.config(secure=True)

# Log the configuration
# Copy this URL in a browser tab to generate the image on the fly.
# ==============================
print("****1. Set up and configure the SDK:****\n", config.cloud_name, config.api_key, "\n")


def uploadPhoto():
    # Upload the image and get its URL
    # ==============================

    # Upload the image.
    # Set the asset's public ID and allow overwriting the asset with new versions
    cloudinary.uploader.upload("https://cloudinary-devs.github.io/cld-docs-assets/assets/images/butterfly.jpeg",
                               public_id="quickstart_butterfly", unique_filename=False, overwrite=True)

    # Build the URL for the image and save it in the variable 'srcURL'.
    srcURL = cloudinary.CloudinaryImage("quickstart_butterfly").build_url()

    # Log the image URL to the console.
    print("****2. Upload an image****\nDelivery URL: ", srcURL, "\n")


def getAssetInfo():
    # Get and use details of the image
    # ==============================

    # Get image details and save it in the variable 'image_info'.
    image_info = cloudinary.api.resource("quickstart_butterfly")
    print("****3. Get and use details of the image****\nUpload response:\n", json.dumps(image_info, indent=2), "\n")

    # Assign tags to the uploaded image based on its width. Save the response to the update in the variable 'update_resp'.
    if image_info["width"] > 900:
        update_resp = cloudinary.api.update("quickstart_butterfly", tags="large")
    elif image_info["width"] > 500:
        update_resp = cloudinary.api.update("quickstart_butterfly", tags="medium")
    else:
        update_resp = cloudinary.api.update("quickstart_butterfly", tags="small")

    # Log the new tag to the console.
    print("New tag: ", update_resp["tags"], "\n")


def createPhotoTag():
    # Transform the image
    # ==============================

    # Create an image tag with transformations applied to the src URL.
    imageTag = cloudinary.CloudinaryImage("quickstart_butterfly").image(radius="max", effect="sepia")

    # Log the image tag to the console
    print("****4. Transform the image****\nImage Tag: ", imageTag, "\n")


def main():
    uploadPhoto()
    getAssetInfo()
    createPhotoTag()


main();