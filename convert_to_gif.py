from moviepy import VideoFileClip
import os

def convert_mp4_to_gif(mp4_path, gif_path):
    clip = VideoFileClip(mp4_path)
    # Resize to width 320 to match README and reduce file size, limit fps to 12
    # The Isometric one might be 380
    width = 380 if "Isometric" in mp4_path else 320
    clip = clip.resized(width=width)
    clip.write_gif(gif_path, fps=12)
    print(f"Converted {mp4_path} to {gif_path}")

if __name__ == "__main__":
    assets_dir = r"c:\Users\logan\Downloads\LoganthP\assets"
    
    mp4_1 = os.path.join(assets_dir, "Pixel_art_an_old_arcade.mp4")
    gif_1 = os.path.join(assets_dir, "Pixel_art_an_old_arcade_small.gif")
    
    mp4_2 = os.path.join(assets_dir, "Isometric_pixel_art.mp4")
    gif_2 = os.path.join(assets_dir, "Isometric_pixel_art_small.gif")
    
    convert_mp4_to_gif(mp4_1, gif_1)
    convert_mp4_to_gif(mp4_2, gif_2)
