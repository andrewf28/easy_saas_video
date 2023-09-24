import boto3
import cv2
import numpy as np
from io import BytesIO
import base64


def decode(encoded_img):
    aux_path = '/tmp/tmp.png'
    with open(aux_path, "wb") as f:
        f.write(base64.b64decode(encoded_img))
        f.close()

    out = cv2.imread(aux_path)

    return out


def decode(encoded_img):
    img_data = base64.b64decode(encoded_img)
    img_array = np.fromstring(img_data, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return img




def draw_frowny_face(image):
    height, width, _ = image.shape
    center_coordinates = (width//2, height//2)
    radius = min(width, height)//8
    smile_radius = radius//2
    circle_center = (width//2, height//2 + radius//8)
    
    color = (0, 0, 255)  # Red color in BGR
    thickness = 2
    
    # Drawing the face
    image = cv2.circle(image, center_coordinates, radius, color, thickness)
    
    # Drawing the eyes
    eye_radius = radius//5
    left_eye_center = (width//2 - radius//3, height//2 - radius//3)
    right_eye_center = (width//2 + radius//3, height//2 - radius//3)
    image = cv2.circle(image, left_eye_center, eye_radius, color, thickness)
    image = cv2.circle(image, right_eye_center, eye_radius, color, thickness)
    
    # Drawing the frowny mouth
    image = cv2.ellipse(image, circle_center, (smile_radius, smile_radius//2), 0, 0, -180, color, thickness)
    
    return image

def draw_angry_face(image):
    height, width, _ = image.shape
    center_coordinates = (width//2, height//2)
    radius = min(width, height)//8
    smile_radius = radius//2
    circle_center = (width//2, height//2 + radius//8)
    
    color = (0, 0, 255)  # Red color in BGR
    thickness = 2
    
    # Drawing the face
    image = cv2.circle(image, center_coordinates, radius, color, thickness)
    
    # Drawing the angry eyes
    eye_radius = radius//5
    left_eye_center = (width//2 - radius//3, height//2 - radius//3)
    right_eye_center = (width//2 + radius//3, height//2 - radius//3)
    left_upper_eyelid_start = (left_eye_center[0] - eye_radius, left_eye_center[1])
    left_upper_eyelid_end = (left_eye_center[0] + eye_radius, left_eye_center[1])
    right_upper_eyelid_start = (right_eye_center[0] - eye_radius, right_eye_center[1])
    right_upper_eyelid_end = (right_eye_center[0] + eye_radius, right_eye_center[1])
    image = cv2.line(image, left_upper_eyelid_start, left_upper_eyelid_end, color, thickness)
    image = cv2.line(image, right_upper_eyelid_start, right_upper_eyelid_end, color, thickness)
    
    # Drawing the angry mouth
    image = cv2.ellipse(image, circle_center, (smile_radius, smile_radius//2), 0, 0, -180, color, thickness)
    
    return image






def draw_smiley(image):
    # Setting the coordinates for the face and the smile
    height, width, _ = image.shape
    center_coordinates = (width//2, height//2)
    radius = min(width, height)//8
    smile_radius = radius//2
    circle_center = (width//2, height//2 + radius//4)

    # Drawing the face
    color = (0, 255, 0)  # Green color in BGR
    thickness = 2
    image = cv2.circle(image, center_coordinates, radius, color, thickness)

    # Drawing the eyes
    eye_radius = radius//5
    left_eye_center = (width//2 - radius//3, height//2 - radius//3)
    right_eye_center = (width//2 + radius//3, height//2 - radius//3)
    image = cv2.circle(image, left_eye_center, eye_radius, color, thickness)
    image = cv2.circle(image, right_eye_center, eye_radius, color, thickness)

    # Drawing the smile
    image = cv2.ellipse(image, circle_center, (smile_radius, smile_radius//2), 0, 0, 180, color, thickness)
    
    return image

def lambda_handler(event, context):
    # Initialize the S3 client
    s3 = boto3.client('s3')

    # Specify the bucket and the key
    bucket_name = 'tutorial-bucket111'
    image = decode(event['body'])
    outKey = f"out_png.png"

    # Draw a smiley face on the image
    image = draw_frowny_face(image)
    
    # Convert the modified image back to bytes
    _, buffer = cv2.imencode('.jpg', image)
    image_bytes = buffer.tobytes()
    
    # Upload the modified image back to S3
    s3.put_object(Bucket=bucket_name, Key=outKey, Body=image_bytes)

    return {
        'statusCode': 200,
        'body': 'Image modified and uploaded successfully'
    }
