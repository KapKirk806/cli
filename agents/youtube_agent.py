"""
YouTube Channel Analysis Agent

This agent downloads and analyzes YouTube channel content including:
- Video transcripts
- Video metadata (title, description, views, likes, etc.)
- Comments and replies
- Upload dates and engagement metrics

Uses Gemini File Search for intelligent chatting with the collected data.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from googleapiclient.discovery import build
    import google.generativeai as genai
except ImportError:
    # These will be installed via requirements.txt
    pass

from agents.base import BaseAgent, AgentConfig
from utils.ui import UI, Color
from utils.gemini_file_search import FileSearchManager, FileSearchChat


class YouTubeAgent(BaseAgent):
    """Agent for downloading and chatting with YouTube channel content."""

    def __init__(self):
        """Initialize YouTube agent with default configuration."""
        config = AgentConfig(
            id="youtube_analyzer",
            name="YouTube Channel Analyzer",
            description="Download and chat with YouTube channel content (transcripts, comments, metadata)",
            personality="You are a helpful YouTube content analyst. You're enthusiastic about helping users understand YouTube creators' content patterns, themes, and audience engagement.",
            system_prompt="""You have access to comprehensive data about a YouTube channel including:
- Complete video transcripts
- Video metadata (titles, descriptions, views, likes, upload dates)
- Comments and replies with engagement metrics

Your role is to help users understand:
- Content themes and topics
- Creator's style and approach
- Audience sentiment and engagement patterns
- Trends over time
- Specific information from videos

Always cite specific videos/comments when providing information.""",
            model="gemini-1.5-pro",
            temperature=0.7,
            knowledge_base_path=Path("data/youtube_analyzer")
        )
        super().__init__(config)

        self.youtube_api = None
        self.file_search_manager = None
        self.file_search_store_id = None

    def run(self, ui: UI):
        """Run the YouTube agent."""
        ui.print_header(f"{self.name}")
        print(f"{Color.GRAY}{self.description}{Color.RESET}\n")

        # Check for API keys
        if not self._check_api_keys(ui):
            return

        # Main menu
        while True:
            print(f"\n{Color.BOLD}What would you like to do?{Color.RESET}")
            print(f"  {Color.CYAN}1.{Color.RESET} Download channel data")
            print(f"  {Color.CYAN}2.{Color.RESET} Chat with channel content")
            print(f"  {Color.CYAN}3.{Color.RESET} View downloaded channels")
            print(f"  {Color.CYAN}0.{Color.RESET} Back to main menu")
            print()

            choice = ui.get_input("Select option")

            if choice == "0":
                break
            elif choice == "1":
                self._download_channel_data(ui)
            elif choice == "2":
                self._chat_with_content(ui)
            elif choice == "3":
                self._view_channels(ui)
            else:
                ui.print_error("Invalid option. Please try again.")

    def _check_api_keys(self, ui: UI) -> bool:
        """Check if required API keys are configured."""
        import os

        gemini_key = os.getenv('GEMINI_API_KEY')
        youtube_key = os.getenv('YOUTUBE_API_KEY')

        missing = []
        if not gemini_key:
            missing.append("GEMINI_API_KEY")
        if not youtube_key:
            missing.append("YOUTUBE_API_KEY")

        if missing:
            ui.print_error(f"Missing API keys: {', '.join(missing)}")
            ui.print_info("Please set these environment variables:")
            for key in missing:
                print(f"  export {key}='your-key-here'")
            return False

        # Initialize APIs
        genai.configure(api_key=gemini_key)
        self.youtube_api = build('youtube', 'v3', developerKey=youtube_key)
        self.file_search_manager = FileSearchManager(api_key=gemini_key)

        return True

    def _download_channel_data(self, ui: UI):
        """Download all data from a YouTube channel."""
        ui.print_header("DOWNLOAD CHANNEL DATA")

        # Get channel identifier
        channel_input = ui.get_input("Enter YouTube channel URL or ID")
        if not channel_input:
            ui.print_warning("No input provided.")
            return

        # Extract channel ID
        channel_id = self._extract_channel_id(channel_input, ui)
        if not channel_id:
            return

        ui.print_info(f"Channel ID: {channel_id}")

        try:
            # Get channel info
            ui.print_step("Fetching channel information...")
            channel_info = self._get_channel_info(channel_id)

            if not channel_info:
                ui.print_error("Could not fetch channel information.")
                return

            channel_name = channel_info['title']
            ui.print_success(f"Found channel: {channel_name}")

            # Create channel directory
            channel_dir = self.knowledge_base_path / self._sanitize_filename(channel_name)
            channel_dir.mkdir(parents=True, exist_ok=True)

            # Save channel info
            with open(channel_dir / 'channel_info.json', 'w', encoding='utf-8') as f:
                json.dump(channel_info, f, indent=2, ensure_ascii=False)

            # Get all video IDs
            ui.print_step("Fetching video list...")
            video_ids = self._get_channel_videos(channel_id)
            ui.print_success(f"Found {len(video_ids)} videos")

            # Download data for each video
            all_data = {
                'channel_info': channel_info,
                'videos': []
            }

            for idx, video_id in enumerate(video_ids, 1):
                ui.print_step(f"Processing video {idx}/{len(video_ids)}: {video_id}")

                video_data = self._download_video_data(video_id, ui)
                if video_data:
                    all_data['videos'].append(video_data)

                    # Save individual video data
                    video_file = channel_dir / f"video_{video_id}.json"
                    with open(video_file, 'w', encoding='utf-8') as f:
                        json.dump(video_data, f, indent=2, ensure_ascii=False)

            # Save complete dataset
            complete_file = channel_dir / 'complete_data.json'
            with open(complete_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)

            ui.print_success(f"\n✓ Download complete! Data saved to: {channel_dir}")

            # Ask if user wants to upload to File Search
            if ui.confirm("\nUpload to Gemini File Search for chatting?"):
                self._upload_to_file_search(channel_dir, channel_name, ui)

        except Exception as e:
            ui.print_error(f"Error downloading channel data: {e}")
            import traceback
            traceback.print_exc()

    def _download_video_data(self, video_id: str, ui: UI) -> Optional[Dict]:
        """Download all data for a single video."""
        try:
            video_data = {
                'video_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}'
            }

            # Get video details
            video_details = self._get_video_details(video_id)
            if video_details:
                video_data.update(video_details)

            # Get transcript
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                video_data['transcript'] = transcript
                video_data['transcript_text'] = ' '.join([entry['text'] for entry in transcript])
            except Exception as e:
                video_data['transcript'] = None
                video_data['transcript_error'] = str(e)

            # Get comments
            comments = self._get_video_comments(video_id)
            video_data['comments'] = comments
            video_data['comment_count'] = len(comments)

            return video_data

        except Exception as e:
            ui.print_warning(f"  Error processing video {video_id}: {e}")
            return None

    def _get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """Get channel information."""
        try:
            response = self.youtube_api.channels().list(
                part='snippet,statistics,contentDetails',
                id=channel_id
            ).execute()

            if response['items']:
                item = response['items'][0]
                return {
                    'id': channel_id,
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'subscriber_count': item['statistics'].get('subscriberCount'),
                    'video_count': item['statistics'].get('videoCount'),
                    'view_count': item['statistics'].get('viewCount'),
                    'uploads_playlist_id': item['contentDetails']['relatedPlaylists']['uploads']
                }
        except Exception as e:
            print(f"Error getting channel info: {e}")
        return None

    def _get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[str]:
        """Get all video IDs from a channel."""
        video_ids = []

        try:
            # First get the uploads playlist ID
            channel_info = self._get_channel_info(channel_id)
            if not channel_info:
                return video_ids

            uploads_playlist_id = channel_info['uploads_playlist_id']

            # Get videos from uploads playlist
            next_page_token = None

            while True:
                playlist_response = self.youtube_api.playlistItems().list(
                    part='contentDetails',
                    playlistId=uploads_playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()

                for item in playlist_response['items']:
                    video_ids.append(item['contentDetails']['videoId'])

                next_page_token = playlist_response.get('nextPageToken')

                if not next_page_token or len(video_ids) >= max_results:
                    break

            return video_ids[:max_results]

        except Exception as e:
            print(f"Error getting channel videos: {e}")
            return video_ids

    def _get_video_details(self, video_id: str) -> Optional[Dict]:
        """Get detailed information about a video."""
        try:
            response = self.youtube_api.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()

            if response['items']:
                item = response['items'][0]
                return {
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'tags': item['snippet'].get('tags', []),
                    'view_count': item['statistics'].get('viewCount'),
                    'like_count': item['statistics'].get('likeCount'),
                    'comment_count': item['statistics'].get('commentCount'),
                    'duration': item['contentDetails']['duration']
                }
        except Exception as e:
            print(f"Error getting video details: {e}")
        return None

    def _get_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict]:
        """Get comments and replies for a video."""
        comments = []

        try:
            next_page_token = None

            while len(comments) < max_results:
                response = self.youtube_api.commentThreads().list(
                    part='snippet,replies',
                    videoId=video_id,
                    maxResults=min(100, max_results - len(comments)),
                    pageToken=next_page_token,
                    order='relevance'
                ).execute()

                for item in response['items']:
                    top_comment = item['snippet']['topLevelComment']['snippet']

                    comment_data = {
                        'text': top_comment['textDisplay'],
                        'author': top_comment['authorDisplayName'],
                        'like_count': top_comment['likeCount'],
                        'published_at': top_comment['publishedAt'],
                        'replies': []
                    }

                    # Get replies if they exist
                    if 'replies' in item:
                        for reply in item['replies']['comments']:
                            reply_snippet = reply['snippet']
                            comment_data['replies'].append({
                                'text': reply_snippet['textDisplay'],
                                'author': reply_snippet['authorDisplayName'],
                                'like_count': reply_snippet['likeCount'],
                                'published_at': reply_snippet['publishedAt']
                            })

                    comments.append(comment_data)

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

        except Exception as e:
            # Some videos have comments disabled
            print(f"Could not fetch comments: {e}")

        return comments

    def _extract_channel_id(self, input_str: str, ui: UI) -> Optional[str]:
        """Extract channel ID from URL or return as-is if already an ID."""
        # If it's already a channel ID (starts with UC and is 24 chars)
        if input_str.startswith('UC') and len(input_str) == 24:
            return input_str

        # Try to extract from URL patterns
        patterns = [
            r'youtube\.com/channel/([^/?]+)',
            r'youtube\.com/@([^/?]+)',
            r'youtube\.com/c/([^/?]+)',
            r'youtube\.com/user/([^/?]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, input_str)
            if match:
                identifier = match.group(1)

                # If it's a @handle or username, we need to look it up
                if not identifier.startswith('UC'):
                    try:
                        # Search for the channel
                        response = self.youtube_api.search().list(
                            part='snippet',
                            q=identifier,
                            type='channel',
                            maxResults=1
                        ).execute()

                        if response['items']:
                            return response['items'][0]['snippet']['channelId']
                    except Exception as e:
                        ui.print_error(f"Error looking up channel: {e}")
                        return None
                else:
                    return identifier

        ui.print_error("Could not extract channel ID from input.")
        ui.print_info("Please provide a valid YouTube channel URL or ID.")
        return None

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem."""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Limit length
        return filename[:100]

    def _upload_to_file_search(self, channel_dir: Path, channel_name: str, ui: UI):
        """Upload channel data to Gemini File Search."""
        ui.print_step("Uploading to Gemini File Search...")

        try:
            # Create File Search Store
            store_name = f"youtube_{self._sanitize_filename(channel_name)}"
            display_name = f"{channel_name} - YouTube Data"

            ui.print_step(f"Creating File Search store: {display_name}")
            store_id = self.file_search_manager.create_store(
                name=store_name,
                display_name=display_name
            )

            ui.print_success(f"Store created: {store_id}")

            # Upload all JSON files
            ui.print_step("Uploading files...")
            file_ids = self.file_search_manager.upload_directory(
                directory=channel_dir,
                store_id=store_id,
                pattern="*.json"
            )

            ui.print_success(f"Uploaded {len(file_ids)} files to File Search!")

            # Save store ID for later use
            store_info_file = channel_dir / '.file_search_store'
            with open(store_info_file, 'w') as f:
                f.write(store_id)

            ui.print_info(f"File Search store ID saved. You can now chat with this content!")

        except Exception as e:
            ui.print_error(f"Error uploading to File Search: {e}")
            ui.print_info("You can still chat using local data (without citations).")

    def _chat_with_content(self, ui: UI):
        """Chat with downloaded channel content using Gemini."""
        ui.print_header("CHAT WITH CHANNEL")

        # List available channels
        channels = list(self.knowledge_base_path.glob('*/'))

        if not channels:
            ui.print_warning("No channels downloaded yet. Please download a channel first.")
            return

        print("Available channels:")
        for idx, channel_dir in enumerate(channels, 1):
            print(f"  {Color.CYAN}{idx}.{Color.RESET} {channel_dir.name}")

        print()
        choice = ui.get_input("Select a channel (number)")

        try:
            channel_idx = int(choice) - 1
            if 0 <= channel_idx < len(channels):
                channel_dir = channels[channel_idx]
                self._start_chat_session(channel_dir, ui)
            else:
                ui.print_error("Invalid selection.")
        except ValueError:
            ui.print_error("Please enter a valid number.")

    def _start_chat_session(self, channel_dir: Path, ui: UI):
        """Start an interactive chat session with channel data."""
        ui.print_header(f"CHAT: {channel_dir.name}")

        # Load complete data
        complete_file = channel_dir / 'complete_data.json'
        if not complete_file.exists():
            ui.print_error("Channel data not found.")
            return

        with open(complete_file, 'r', encoding='utf-8') as f:
            channel_data = json.load(f)

        ui.print_success("Channel data loaded!")
        ui.print_info(f"Videos: {len(channel_data['videos'])}")

        # Check if File Search is available
        store_info_file = channel_dir / '.file_search_store'
        use_file_search = store_info_file.exists()

        if use_file_search:
            with open(store_info_file, 'r') as f:
                store_id = f.read().strip()

            ui.print_success(f"Using File Search (with citations!) - Store: {store_id}")

            # Create File Search chat
            chat = FileSearchChat(
                file_search_manager=self.file_search_manager,
                store_id=store_id,
                model=self.config.model,
                system_instruction=self.get_system_prompt()
            )

            print(f"\n{Color.GRAY}Type 'quit' or 'exit' to end the chat.{Color.RESET}\n")

            while True:
                user_input = ui.get_input("\nYou")

                if user_input.lower() in ['quit', 'exit', 'q']:
                    ui.print_success("Chat ended.")
                    break

                if not user_input:
                    continue

                try:
                    response_text = chat.send_message(user_input)
                    print(f"\n{Color.GREEN}Agent:{Color.RESET} {response_text}")

                except Exception as e:
                    ui.print_error(f"Error: {e}")

        else:
            # Fallback to local data mode (no File Search)
            ui.print_warning("File Search not enabled. Using local data mode (no citations).")
            ui.print_info("To enable File Search, re-download the channel and upload when prompted.")

            print(f"\n{Color.GRAY}Type 'quit' or 'exit' to end the chat.{Color.RESET}\n")

            # Initialize Gemini model
            model = genai.GenerativeModel(
                model_name=self.config.model,
                system_instruction=self.get_system_prompt()
            )

            # Create context from data
            context = self._create_context_from_data(channel_data)

            # Start chat
            chat = model.start_chat(history=[])

            while True:
                user_input = ui.get_input("\nYou")

                if user_input.lower() in ['quit', 'exit', 'q']:
                    ui.print_success("Chat ended.")
                    break

                if not user_input:
                    continue

                try:
                    # Include context in the query
                    full_prompt = f"""Based on the following YouTube channel data, answer the question.

CHANNEL DATA:
{context}

USER QUESTION:
{user_input}

Provide a detailed answer with specific examples and citations from the videos/comments when possible."""

                    response = chat.send_message(full_prompt)

                    print(f"\n{Color.GREEN}Agent:{Color.RESET} {response.text}")

                except Exception as e:
                    ui.print_error(f"Error: {e}")

    def _create_context_from_data(self, channel_data: Dict) -> str:
        """Create a context summary from channel data."""
        context_parts = []

        # Channel info
        ch_info = channel_data['channel_info']
        context_parts.append(f"Channel: {ch_info['title']}")
        context_parts.append(f"Subscribers: {ch_info.get('subscriber_count', 'N/A')}")
        context_parts.append(f"Total Videos: {len(channel_data['videos'])}")
        context_parts.append("")

        # Video summaries (limit to avoid token limits)
        context_parts.append("VIDEOS:")
        for video in channel_data['videos'][:20]:  # Limit to first 20 videos
            context_parts.append(f"\nTitle: {video.get('title', 'N/A')}")
            context_parts.append(f"Views: {video.get('view_count', 'N/A')}, Likes: {video.get('like_count', 'N/A')}")
            context_parts.append(f"Published: {video.get('published_at', 'N/A')}")

            if video.get('transcript_text'):
                # Include first 500 chars of transcript
                transcript_preview = video['transcript_text'][:500]
                context_parts.append(f"Transcript preview: {transcript_preview}...")

            # Include top comments
            if video.get('comments'):
                context_parts.append(f"Top comments:")
                for comment in video['comments'][:3]:
                    context_parts.append(f"  - {comment['text'][:100]}... (👍 {comment['like_count']})")

        return '\n'.join(context_parts)

    def _view_channels(self, ui: UI):
        """View list of downloaded channels."""
        ui.print_header("DOWNLOADED CHANNELS")

        channels = list(self.knowledge_base_path.glob('*/'))

        if not channels:
            ui.print_warning("No channels downloaded yet.")
            return

        for channel_dir in channels:
            print(f"\n{Color.CYAN}●{Color.RESET} {Color.BOLD}{channel_dir.name}{Color.RESET}")

            # Try to load channel info
            info_file = channel_dir / 'channel_info.json'
            if info_file.exists():
                with open(info_file, 'r') as f:
                    info = json.load(f)
                    print(f"  Subscribers: {info.get('subscriber_count', 'N/A')}")
                    print(f"  Total Videos: {info.get('video_count', 'N/A')}")

            # Count downloaded videos
            video_files = list(channel_dir.glob('video_*.json'))
            print(f"  Downloaded: {len(video_files)} videos")
            print(f"  Path: {channel_dir}")
