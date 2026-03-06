
from PIL import Image, ExifTags
import re
from datetime import datetime
import config
import ffmpeg
import traceback
import pathlib
import os


def navigate_photos_dirs():

    countdir = 0
    for item in config.photos_dir.iterdir():

        countdir += 1
        if countdir > 0 and countdir < 400:
            if item.is_dir() and '2026-02' in item.name:

                print(f"Dir: {item.name}")
                count = 0
                for photo in item.iterdir():
                    if count < 5000000:
                        if photo.is_file():
                            update_exif_from_filename(photo)
                            count += 1

    



def update_exif_from_filename(image_path):
    """
    Updates the EXIF DateTimeOriginal tag of an image based on its filename.
    Assumes filename format: YYYY-MM-DD_HH-MM-SS.jpg
    """
    try:

        photo_name = image_path.name
        
        fullfile_name = str(image_path)

        if '.gif' in photo_name:
            return


        print('photo_name',photo_name)

        match1 = re.search(r'\d{8}', photo_name)
        match2 = re.search(r'(\d{4}-\d{2}-\d{2})', photo_name)

        if not match1 and not match2:
            date_str = datetime.today().strftime('%Y:%m:%d')
            date_str2 = datetime.today().strftime('%Y-%m-%d')
            print('date not found for:', photo_name)
        if match1:
            date_str = match1.group(0)[0:4] + ':' + match1.group(0)[4:6] + ':' + match1.group(0)[6:8]
            date_str2 = date_str.replace(':', '-')
        if match2:
            date_str2 = match2.group(0)
            date_str = match2.group(0).replace('-', ':') # Exif date format is YYYY:MM:DD

        match_time1 = re.search(r'\d{8}_\d{6}', photo_name)
        match_time2 = re.search(r'\d{8}-\d{6}', photo_name)

        if not match_time1 and not match_time2:
            time_str = "00:00:00"
        if match_time1:
            time_str = match_time1.group(0)[9:11] + ':' + match_time1.group(0)[11:13] + ':' + match_time1.group(0)[13:15]
        if match_time2:
            time_str = match_time2.group(0)[9:11] + ':' + match_time2.group(0)[11:13] + ':' + match_time2.group(0)[13:15]


        exif_datetime_str = f"{date_str} {time_str}"
        exif_datetime_str2 = f"{date_str2} {time_str}"

        print('exif_datetime_str2', exif_datetime_str2)
        

        if ".mp4" in photo_name:
            change_codec_and_datetime(fullfile_name, exif_datetime_str2)
            return

        with Image.open(fullfile_name) as img:
            exif_data = img.getexif()

            # Find the tag for DateTimeOriginal
            for tag, name in ExifTags.TAGS.items():
                if name == 'DateTime':
                    datetime_original_tag = tag
                    #print('exif_data[datetime_original_tag]', exif_data[datetime_original_tag])
                    break
            else:
                print("DateTimeOriginal tag not found in ExifTags.TAGS.")
                return

            if datetime_original_tag in exif_data:
                print(exif_data[datetime_original_tag])
            else:
                exif_data[datetime_original_tag] = exif_datetime_str
                img.save(fullfile_name, exif=exif_data)

            print('exif_data')
            print(exif_data)

            # Save the image with updated EXIF data
            # You might want to save to a new file or overwrite the original
            
            #print(f"Updated EXIF DateTimeOriginal for {filename} to {exif_datetime_str}")

    except Exception as e:
        print(f"Error processing {image_path}: {e}")

# Example usage:
# image_file = "2023-10-26_14-30-55.jpg"
# update_exif_from_filename(image_file)



def change_codec_and_datetime(input_file, exif_datetime_str2):
    """
    Changes the video codec and creation datetime metadata of an MP4 file.

    :param input_file: Path to the input MP4 file.
    :param output_file: Path for the output MP4 file.
    :param new_codec: The new video codec (e.g., 'libx264', 'libx265', 'mp4v').
    :param new_datetime_str: The new creation time in ISO 8601 format (e.g., '2025-12-10 16:30:00').
    """
    codec = 'h264' 

    '''
    probe_data = ffmpeg.probe(input_file)

    
    video_codec = probe_data['streams'][0].get('codec_name')

    if video_codec

    # Extract video stream information
    video_stream = next((s for s in probe_data['streams'] if s['codec_type'] == 'video'), None)
    if video_stream:
        video_codec = video_stream.get('codec_name')
        print(f"Video Codec: {video_codec}")
    '''
    input_path = pathlib.Path(input_file)
    output_file = str(pathlib.Path(input_path.parent, 'AA_'+ input_path.name))

    if os.path.isfile(input_file):
        print('yes file')

    print('input_path', input_file)
    print('output_file', output_file)

    try:
        # Use ffmpeg-python to create the new file with updated parameters
        (
            ffmpeg
            .input(input_file)
            .output(
                output_file,
                vcodec=codec,  # Set the new video codec
                metadata=f'creation_time={exif_datetime_str2}', # Set the new metadata
                acodec='copy' # Copy the audio stream without re-encoding
            )
            .run(overwrite_output=True)
        )
        print(f"Successfully processed video. New file saved as '{input_file}'")

        os.remove(input_file)
        os.rename(output_file, input_file)

    except Exception as e:
        traceback.print_exc()
        print(f"An unexpected error occurred: {e}")


def rename_files_directory():

    for item in config.rename_directory.iterdir():

        if item.is_file():

            new_name = 'AA_'+item.name
            new_path = pathlib.Path(item.parent,new_name)

            print('str(new_path)', str(new_path))

            os.rename(str(item), str(new_path))



if __name__ == "__main__":
    navigate_photos_dirs()
    #rename_files_directory()
