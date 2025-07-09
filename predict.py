# Prediction interface for Cog ⚙️
# https://cog.run/python

from cog import BasePredictor, Input, Path
import os
from typing import List
from moviepy.editor import VideoFileClip, concatenate_videoclips

class Predictor(BasePredictor):
    def setup(self) -> None:
        """Load the model into memory to make running multiple predictions efficient"""
        pass

    def predict(
        self,
        video_files: List[Path] = Input(description="List of video files to concatenate"),
        keep_audio: bool = Input(
            description="Whether to keep audio in the output video",
            default=True,
        ),
        width: int = Input(
            description="Output video width. If not specified, uses first video's width",
            default=0,
        ),
        height: int = Input(
            description="Output video height. If not specified, uses first video's height",
            default=0,
        ),
        fps: int = Input(
            description="Output video frame rate. If not specified, uses first video's fps",
            default=0,
        ),
    ) -> Path:
        """Run video concatenation"""
        # Cleanup past runs
        out_dir = "/tmp/output"
        os.makedirs(out_dir, exist_ok=True)
        
        if len(video_files) < 2:
            raise ValueError("At least two video files are required for concatenation")

        # Load all video clips
        clips = []
        base_width = width
        base_height = height
        base_fps = fps
        for video_file in video_files:
            clip = VideoFileClip(str(video_file))
            # If dimensions/fps not specified, use first video's properties
            if base_width == 0:  # Changed from 'is' to '=='
                base_width = int(clip.w)
            if base_height == 0:  # Changed from 'is' to '=='
                base_height = int(clip.h)
            if base_fps == 0:  # Changed from 'is' to '=='
                base_fps = float(clip.fps)

            # Resize clip if needed
            if clip.w != base_width or clip.h != base_height:
                clip = clip.resize(width=base_width, height=base_height)
            
            # Handle audio
            if not keep_audio:
                clip = clip.without_audio()

            clips.append(clip)

        # Concatenate all clips
        final_clip = concatenate_videoclips(clips)

        # Set frame rate if specified
        if fps != 0 and abs(final_clip.fps - fps) > 0.01:  # Changed condition
            final_clip = final_clip.set_fps(fps)

        # Create output path
        out_path = os.path.join(out_dir, "output.mp4")
        
        # Clean up existing file if it exists
        if os.path.exists(out_path):
            os.remove(out_path)

        # Write final video
        final_clip.write_videofile(
            str(out_path),
            codec='libx264',
            audio_codec='aac' if keep_audio else None,
            fps=base_fps
        )

        # Clean up
        final_clip.close()
        for clip in clips:
            clip.close()

        return Path(out_path)