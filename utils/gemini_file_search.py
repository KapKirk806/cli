"""
Gemini File Search integration utilities.

This module provides a wrapper around Google's Gemini File Search API
for easy RAG (Retrieval Augmented Generation) capabilities.
"""

import os
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    import google.generativeai as genai
except ImportError:
    pass


class FileSearchManager:
    """Manager for Gemini File Search operations."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize File Search Manager.

        Args:
            api_key: Gemini API key. If None, uses GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)

        self.stores: Dict[str, Any] = {}

    def create_store(self, name: str, display_name: Optional[str] = None) -> str:
        """
        Create a new File Search store.

        Args:
            name: Internal name for the store
            display_name: Display name for the store (optional)

        Returns:
            Store ID
        """
        try:
            # Using the Gemini API's file search store creation
            # Note: The exact API may vary - this is based on the documented approach
            store = genai.create_file_search_store(
                name=name,
                display_name=display_name or name
            )

            store_id = store.name
            self.stores[name] = store_id

            return store_id

        except Exception as e:
            raise Exception(f"Failed to create File Search store: {e}")

    def upload_file(self, file_path: Path, store_id: str, display_name: Optional[str] = None) -> str:
        """
        Upload a file to a File Search store.

        Args:
            file_path: Path to the file to upload
            store_id: ID of the File Search store
            display_name: Display name for the file (optional)

        Returns:
            File ID
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Upload file
            uploaded_file = genai.upload_file(
                path=str(file_path),
                display_name=display_name or file_path.name
            )

            # Wait for processing
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(1)
                uploaded_file = genai.get_file(uploaded_file.name)

            if uploaded_file.state.name == "FAILED":
                raise Exception(f"File processing failed: {uploaded_file.state}")

            # Add to File Search store
            # Note: This is the conceptual approach - actual API may vary
            genai.add_file_to_store(
                file_id=uploaded_file.name,
                store_id=store_id
            )

            return uploaded_file.name

        except Exception as e:
            raise Exception(f"Failed to upload file: {e}")

    def upload_directory(self, directory: Path, store_id: str, pattern: str = "*.json") -> List[str]:
        """
        Upload all matching files from a directory to a File Search store.

        Args:
            directory: Directory containing files
            store_id: ID of the File Search store
            pattern: Glob pattern for files to upload (default: *.json)

        Returns:
            List of uploaded file IDs
        """
        file_ids = []

        for file_path in directory.glob(pattern):
            if file_path.is_file():
                try:
                    file_id = self.upload_file(file_path, store_id)
                    file_ids.append(file_id)
                except Exception as e:
                    print(f"Warning: Failed to upload {file_path}: {e}")

        return file_ids

    def query(
        self,
        query: str,
        store_id: str,
        model: str = "gemini-1.5-pro",
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Query a File Search store.

        Args:
            query: User's question/query
            store_id: ID of the File Search store
            model: Gemini model to use
            system_instruction: Optional system instruction for the model

        Returns:
            Model's response
        """
        try:
            # Create model with File Search tool
            model_instance = genai.GenerativeModel(
                model_name=model,
                system_instruction=system_instruction,
                tools=[
                    genai.Tool(
                        file_search=genai.FileSearch(
                            store_ids=[store_id]
                        )
                    )
                ]
            )

            # Generate response
            response = model_instance.generate_content(query)

            return response.text

        except Exception as e:
            raise Exception(f"Query failed: {e}")

    def create_chat_session(
        self,
        store_id: str,
        model: str = "gemini-1.5-pro",
        system_instruction: Optional[str] = None
    ):
        """
        Create a chat session with File Search.

        Args:
            store_id: ID of the File Search store
            model: Gemini model to use
            system_instruction: Optional system instruction for the model

        Returns:
            Chat session object
        """
        try:
            # Create model with File Search tool
            model_instance = genai.GenerativeModel(
                model_name=model,
                system_instruction=system_instruction,
                tools=[
                    genai.Tool(
                        file_search=genai.FileSearch(
                            store_ids=[store_id]
                        )
                    )
                ]
            )

            # Start chat
            chat = model_instance.start_chat()

            return chat

        except Exception as e:
            raise Exception(f"Failed to create chat session: {e}")

    def delete_store(self, store_id: str):
        """
        Delete a File Search store.

        Args:
            store_id: ID of the File Search store
        """
        try:
            genai.delete_file_search_store(store_id)

            # Remove from local tracking
            for name, sid in list(self.stores.items()):
                if sid == store_id:
                    del self.stores[name]

        except Exception as e:
            raise Exception(f"Failed to delete store: {e}")

    def list_stores(self) -> List[Dict[str, Any]]:
        """
        List all File Search stores.

        Returns:
            List of store information
        """
        try:
            stores = genai.list_file_search_stores()
            return [
                {
                    'id': store.name,
                    'display_name': store.display_name,
                    'create_time': store.create_time
                }
                for store in stores
            ]
        except Exception as e:
            raise Exception(f"Failed to list stores: {e}")


class FileSearchChat:
    """
    Interactive chat interface with File Search.
    """

    def __init__(
        self,
        file_search_manager: FileSearchManager,
        store_id: str,
        model: str = "gemini-1.5-pro",
        system_instruction: Optional[str] = None
    ):
        """
        Initialize File Search chat.

        Args:
            file_search_manager: FileSearchManager instance
            store_id: ID of the File Search store
            model: Gemini model to use
            system_instruction: Optional system instruction
        """
        self.manager = file_search_manager
        self.store_id = store_id
        self.chat = file_search_manager.create_chat_session(
            store_id=store_id,
            model=model,
            system_instruction=system_instruction
        )

    def send_message(self, message: str) -> str:
        """
        Send a message in the chat.

        Args:
            message: User's message

        Returns:
            Model's response
        """
        try:
            response = self.chat.send_message(message)
            return response.text
        except Exception as e:
            raise Exception(f"Failed to send message: {e}")

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get chat history.

        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        history = []
        for message in self.chat.history:
            history.append({
                'role': message.role,
                'content': message.parts[0].text if message.parts else ''
            })
        return history
