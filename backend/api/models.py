# backend/api/models.py
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# --- Generic Model Information ---
# These models are designed to be source-agnostic where possible.


class ModelFile(BaseModel):
    """Represents a file within a model repository."""

    rfilename: str = Field(..., description="The relative name of the file in the repository.")
    size: Optional[int] = Field(None, description="Size of the file in bytes.")


class ModelListItem(BaseModel):
    """Represents a model item in a list (e.g., search results)."""

    id: str = Field(
        ...,
        description="The unique identifier of the model (e.g., 'author/model_name').",
    )
    source: str = Field(..., description="The source of the model (e.g., 'huggingface').")
    author: Optional[str] = Field(None, description="The author or organization of the model.")
    model_name: str = Field(
        ..., description="The name of the model, typically derived from the ID."
    )
    lastModified: Optional[datetime] = Field(
        None, description="Timestamp of the last modification."
    )
    tags: List[str] = Field(
        default_factory=list, description="List of tags associated with the model."
    )
    downloads: Optional[int] = Field(None, description="Number of downloads.")
    likes: Optional[int] = Field(None, description="Number of likes.")


class PaginatedModelListResponse(BaseModel):
    """Response model for a paginated list of models."""

    items: List[ModelListItem]
    page: int
    limit: int
    has_more: bool


class ModelDetails(ModelListItem):
    """Represents detailed information for a specific model."""

    sha: Optional[str] = Field(None, description="The commit hash of the model's repository.")
    private: Optional[bool] = Field(
        None, description="Indicates if the model repository is private."
    )
    gated: Optional[str] = Field(None, description="Gated status (e.g., 'auto', 'manual', 'True').")
    library_name: Optional[str] = Field(
        None, description="The primary library associated with the model."
    )
    pipeline_tag: Optional[str] = Field(
        None, description="The primary pipeline tag (e.g., 'text-generation')."
    )
    siblings: List[ModelFile] = Field(..., description="List of all files in the model repository.")
    readme_content: Optional[str] = Field(
        None, description="The content of the model's README.md file."
    )


# --- Types for FileManager Configuration and Operations ---
# Import from constants to ensure single source of truth
from backend.core.constants.constants import UiNameType, ModelType, UiProfileType, ColorThemeType

UiProfileTypePydantic = UiProfileType
ModelTypePydantic = ModelType
ColorThemeTypePydantic = ColorThemeType
UiNameTypePydantic = UiNameType
ConfigurationModePydantic = Literal["automatic", "manual"]


# --- Models for Path and File Configuration ---
class MalFullConfiguration(BaseModel):
    """
    Represents the full, current configuration of the application, as sent to the frontend.
    """

    base_path: Optional[str]
    ui_profile: Optional[UiProfileTypePydantic] = Field(None, alias="profile")
    custom_model_type_paths: Dict[str, str]
    color_theme: Optional[ColorThemeTypePydantic]
    config_mode: Optional[ConfigurationModePydantic]
    automatic_mode_ui: Optional[UiNameTypePydantic] = Field(None)

    class Config:
        populate_by_name = True


class PathConfigurationRequest(BaseModel):
    """Request model for updating the main settings page configuration."""

    base_path: Optional[str] = Field(None, description="The base path for 'manual' mode.")
    profile: Optional[UiProfileTypePydantic] = Field(None)
    custom_model_type_paths: Optional[Dict[str, str]] = Field(None)
    color_theme: Optional[ColorThemeTypePydantic] = Field(None)
    config_mode: Optional[ConfigurationModePydantic] = Field(None)
    automatic_mode_ui: Optional[UiNameTypePydantic] = Field(
        None, description="The selected UI for 'automatic' mode."
    )


class PathConfigurationResponse(BaseModel):
    """Response model for a configuration update request."""

    success: bool
    message: Optional[str] = None
    current_config: Optional[MalFullConfiguration] = None


# --- Models for File Download ---
class FileDownloadRequest(BaseModel):
    """Request model for downloading a model file."""

    source: str = Field(..., description="The source of the model (e.g., 'huggingface').")
    repo_id: str = Field(..., description="The repository ID (e.g., 'author/model_name').")
    filename: str = Field(..., description="The name of the file to download.")
    model_type: ModelTypePydantic
    custom_sub_path: Optional[str] = Field(None)
    revision: Optional[str] = Field(None)


class FileDownloadResponse(BaseModel):
    """Response for a download request, indicating if it was successfully started."""

    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    download_id: Optional[str] = Field(None, description="The unique ID for tracking the download.")


# --- Models for Local File Management ---


class LocalFileItem(BaseModel):
    """Represents a file or directory within the managed base_path."""

    name: str = Field(..., description="The name of the file or directory.")
    path: str = Field(..., description="The relative path from the base_path.")
    item_type: Literal["file", "directory"] = Field(..., alias="type")
    size: Optional[int] = Field(
        None, description="Size of the file in bytes (null for directories)."
    )
    last_modified: datetime = Field(..., description="Timestamp of the last modification.")

    class Config:
        populate_by_name = True


class LocalFileActionRequest(BaseModel):
    """Request model for actions on a local file or directory."""

    path: str = Field(..., description="The relative path of the item to act upon.")


class LocalFileContentResponse(BaseModel):
    """Response model for fetching the content of a text file."""

    success: bool
    path: str
    content: Optional[str] = None
    error: Optional[str] = None


class FileManagerListResponse(BaseModel):
    """
    The response for a file listing request, including the final path
    after any smart navigation and the items at that path.
    """

    path: Optional[str] = Field(description="The final relative path that is being displayed.")
    items: List[LocalFileItem] = Field(
        description="The list of files and directories at the final path."
    )


# --- Models for Host Directory Scanning ---
class HostDirectoryItem(BaseModel):
    name: str
    path: str
    type: Literal["directory"] = "directory"
    children: Optional[List["HostDirectoryItem"]] = None


HostDirectoryItem.model_rebuild()


class ScanHostDirectoriesResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    data: Optional[List[HostDirectoryItem]] = None


# --- UI Environment Management Models ---


class AvailableUiItem(BaseModel):
    """Represents a UI that is available for installation."""

    ui_name: UiNameTypePydantic = Field(..., description="The unique name of the UI.")
    git_url: str = Field(..., description="The Git URL of the repository.")
    default_profile_name: UiProfileTypePydantic = Field(
        ..., description="The default UI profile associated with this UI."
    )


class UiInstallRequest(BaseModel):
    """Request model for installing a UI environment."""

    ui_name: UiNameTypePydantic
    # An optional user-provided absolute path for the installation.
    custom_install_path: Optional[str] = Field(None)
    # If true, the frontend will be signaled to set this UI as active after success.
    set_as_active: bool = Field(False)


class ManagedUiStatus(BaseModel):
    """Represents the status of a single managed UI environment."""

    ui_name: UiNameTypePydantic
    is_installed: bool = Field(..., description="Indicates if the UI environment directory exists.")
    is_running: bool = Field(..., description="Indicates if the UI process is currently running.")
    install_path: Optional[str] = Field(
        None, description="The absolute installation path on the host."
    )
    running_task_id: Optional[str] = Field(
        None, description="The task_id if the UI is currently running."
    )


class AllUiStatusResponse(BaseModel):
    """Response model for a list of all managed UI statuses."""

    items: List[ManagedUiStatus]


class UiActionResponse(BaseModel):
    """Standard response for actions that trigger a background task (install, run)."""

    success: bool
    message: str
    task_id: str = Field(..., description="The unique ID for tracking the task via WebSocket.")
    # This field signals the frontend to perform a follow-up action on completion.
    set_as_active_on_completion: bool = Field(False)


class UiStopRequest(BaseModel):
    """Request model for stopping a running UI process."""

    task_id: str = Field(..., description="The task_id of the running process to be stopped.")
