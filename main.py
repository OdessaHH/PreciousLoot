from pytube import Playlist, YouTube
from datetime import datetime
import os
from moviepy.editor import AudioFileClip
import essentia.standard as es


def get_video_links(playlist_url):
    """
    Fetches video links from a YouTube playlist.

    :param playlist_url: YouTube playlist URL
    :return: list of video URLs and the playlist title
    """
    playlist = Playlist(playlist_url)
    playlist._video_regex = r"\"url\":\"(/watch\?v=[\w-]*)"  # type: ignore

    video_links = [f"https://www.youtube.com{url}" for url in playlist.video_urls]
    return video_links, playlist.title


def create_output_folders(playlist_title):
    """
    Creates output folders for storing downloaded and converted files.

    :param playlist_title: title of the playlist
    :return: paths to the MP4 and WAV folders
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_folder = os.path.join("/home/user/Documents/Privat/DJ HELP/MATERIAL", f"{playlist_title}_{timestamp}")
    mp4_folder = os.path.join(base_folder, "MP4")
    wav_folder = os.path.join(base_folder, "WAV")

    os.makedirs(mp4_folder, exist_ok=True)
    os.makedirs(wav_folder, exist_ok=True)

    return mp4_folder, wav_folder


def download_audio(url, output_path):
    """
    Downloads the audio stream of a YouTube video.

    :param url: YouTube video URL
    :param output_path: path to store the downloaded file
    """
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()

        if not audio_stream:
            print("No audio stream available.")
            return

        audio_stream.download(output_path)
        print("Download complete.")
    except Exception as e:
        print("An error occurred:", e)


def iterate_through_playlist(playlist, output_path):
    """
    Iterates through a list of URLs to download audio streams.

    :param playlist: list of YouTube video URLs
    :param output_path: path to store the downloaded files
    """
    for url in playlist:
        download_audio(url, output_path)


def convert_to_wav(mp4_file, output_folder):
    """
    Converts an MP4 file to WAV format.

    :param mp4_file: path to the MP4 file
    :param output_folder: path to store the converted WAV file
    """
    try:
        audio_clip = AudioFileClip(mp4_file)
        base_filename = os.path.splitext(os.path.basename(mp4_file))[0]
        wav_file = os.path.join(output_folder, f"{base_filename}.wav")
        audio_clip.write_audiofile(wav_file)
        audio_clip.close()
        print(f"Converted {mp4_file} to {wav_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


def calculate_bpm(wav_file):
    """ 
    Calculates the BPM of a WAV file.

    :param wav_file: path to the WAV file
    :return: calculated BPM value
    """
    loader = es.MonoLoader(filename=wav_file)
    audio = loader()
    rhythm_extractor = es.RhythmExtractor2013()
    results = rhythm_extractor(audio)
    bpm = results[0]

    # Drum & Bass tracks are usually around 170 BPM, so we multiply by two to get the actual BPM value
    if bpm < 100:
        bpm *= 2
    return bpm




def analyze_folder(folder_path):
    """
    Analyzes a folder of WAV files to calculate and sort tracks by BPM.

    :param folder_path: path to the folder containing WAV files
    :return: dictionary of sorted tracks with their respective BPM values
    """
    tracks = {}
    total_files = sum(1 for f in os.listdir(folder_path) if f.lower().endswith(".wav"))

    print(f"Processing {total_files} files...")
    processed_files = 0

    for file in os.listdir(folder_path):
        if file.lower().endswith(".wav"):
            wav_file = os.path.join(folder_path, file)
            bpm = calculate_bpm(wav_file)
            if bpm is not None:
                tracks[file] = bpm
                processed_files += 1
                print(f"Processed {processed_files}/{total_files} files")

    print("Sorting tracks based on BPM values...")
    sorted_tracks = dict(sorted(tracks.items(), key=lambda item: item[1]))
    print("Sorting done!")

    return sorted_tracks


if __name__ == "__main__":
    playlist_url = input("Enter your YT playlist: ")
    video_links, playlist_title = get_video_links(playlist_url)

    print("Video Links:")
    print(video_links)

    mp4_folder, wav_folder = create_output_folders(playlist_title)
    iterate_through_playlist(video_links, mp4_folder)

    for file in os.listdir(mp4_folder):
        if file.lower().endswith(".mp4"):
            mp4_file = os.path.join(mp4_folder, file)
            convert_to_wav(mp4_file, wav_folder)

    sorted_tracks = analyze_folder(wav_folder)

    print("Final sorted tracks:")
    for track, bpm in sorted_tracks.items():
        print(f"{track}: BPM = {bpm:.2f}")


