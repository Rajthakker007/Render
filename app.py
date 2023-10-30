from flask import Flask, render_template, request, send_from_directory, jsonify
from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip, vfx, concatenate_videoclips, VideoFileClip
from datetime import datetime
import threading
from PIL import Image, ImageDraw, ImageFont
import os
import gtts 


app = Flask(__name__)

# Variables to track progress and time
progress = 0
start_time = None
end_time = None

# Lock for controlling access to progress variable
progress_lock = threading.Lock()

# Directory to store temporary files
temp_dir = "temp"
os.makedirs(temp_dir, exist_ok=True)

@app.route("/")
def index():
    return render_template("imagetovideo.html")

@app.route("/process", methods=["POST"])
def process():
    global progress, start_time, end_time

    def update_progress():
        global progress, start_time, end_time
        while progress < 100:
            with progress_lock:
                if start_time and progress > 0:
                    end_time = datetime.now()
                    elapsed_time = (end_time - start_time).total_seconds()
                    estimated_total_time = elapsed_time / (progress / 100)
                    time_left = round(estimated_total_time - elapsed_time, 1)
                else:
                    time_left = "Calculating..."
            time.sleep(1)  # Update every 1 second

    num_images = int(request.form["num_images"])

    # List to store generated video file paths
    video_paths = []

    # Set the frames per second (fps) for the video
    fps = 24

    # Start the progress update thread
    progress_thread = threading.Thread(target=update_progress)
    progress_thread.daemon = True
    progress_thread.start()

    start_time = datetime.now()  # Start timing the process

    for i in range(1, num_images + 1):
        audio_text = request.form[f"audio{i}"]
        image = request.files[f"image{i}"]

        # Skip empty image uploads
        if not image:
            continue

        # Save the uploaded image to the temporary directory
        image_path = os.path.join(temp_dir, image.filename)
        image.save(image_path)

        # Add text to the image
        text = request.form[f"text{i}"]
        image_with_text_path = add_text_to_image(image_path, text, i)

        # Create a GTTS speech
        speech = gtts.gTTS(audio_text, lang="en", slow=False, tld="co.in")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Add timestamp
        mp3_file_name = f"new{i}_{timestamp}.mp3"  # Add timestamp to the file name
        speech.save(os.path.join(temp_dir, mp3_file_name))

        # Load the audio and image
        speech1 = AudioFileClip(os.path.join(temp_dir, mp3_file_name))
        image1 = ImageClip(image_with_text_path).set_duration(10)

        # Generate video
        video = CompositeVideoClip([image1.set_duration(speech1.duration).set_audio(speech1)]).fx(vfx.speedx, 1.2)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Add timestamp
        video_file_name = f"video{i}_{timestamp}.mp4"  # Add timestamp to the file name
        video_path = os.path.join(temp_dir, video_file_name)
        video.write_videofile(video_path, codec='libx264', fps=fps)

        # Store the video path
        video_paths.append(video_path)

        # Clean up temporary files
        os.remove(image_with_text_path)
        os.remove(os.path.join(temp_dir, mp3_file_name))

        with progress_lock:
            progress = (i / num_images) * 100

    # Stop timing the process
    end_time = datetime.now()

    # Concatenate all generated videos into one
    combined_video = concatenate_videoclips([VideoFileClip(path) for path in video_paths], method="compose")

    # Provide a link to download the combined video
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%dH%M%S")  # Add timestamp
    combined_video_file_name = f"combined_video_{timestamp}.mp4"  # Add timestamp to the file name
    combined_video_path = os.path.join(output_dir, combined_video_file_name)
    combined_video.write_videofile(combined_video_path, codec='libx264', fps=fps)

    return f"Combined video generated. <a href='/download/{combined_video_file_name}' download>Download Combined Video</a>"

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory("output", filename)

# Function to add text to the image
def add_text_to_image(image_path, text, image_number):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font_size = 50
    font = ImageFont.truetype("arial.ttf", font_size) # You can customize the font
    position = (10, 10)
    color = (0, 0, 0)  # black color
    draw.text(position, text, fill=color, font=font)

    modified_image_path = os.path.join(temp_dir, f"modified_image{image_number}.png")
    image.save(modified_image_path)

    return modified_image_path

@app.route("/progress")
def get_progress():
    global progress
    time_left = update_progress(progress)
    return jsonify({"progress": progress, "time_left": time_left})

if __name__ == "__main__":
    app.run(debug=True)