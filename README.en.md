# We-Library

We-Library is an integrated multimedia resource management system designed to help users efficiently manage content such as images, files, web resources, music, videos, and more. It combines a backend API with a frontend interface and supports functionalities including file upload, album management, tag classification, metadata maintenance, and web resource management.

## Feature Overview

- **Album Management**: Create, update, and delete albums, with support for folder locking and unlocking.
- **File Management**: Upload, delete, and rename files, with support for extracting file metadata (e.g., EXIF information).
- **Tag System**: Classify and manage resources using tags.
- **Metadata Management**: Store and query resource metadata.
- **Web Resource Management**: Add, update, and delete web resource information.
- **Map Location**: Support querying image location information via latitude and longitude.
- **Logging System**: Provides advanced logging configuration and supports runtime logging.
- **Database Operations**: Implements database connection, querying, pagination, insertion, and update operations using SQLite.

## Technology Stack

- **Python**: The backend API is written in Python using the FastAPI framework.
- **SQLite**: Used for storing and managing resource data.
- **Vue.js**: Frontend interface framework.
- **Element Plus**: UI component library offering rich interface controls.
- **El-Table, El-Form, El-Dialog**: Used for data display, form operations, and modal interactions.
- **Custom Utility Classes**: Path formatting, file handling, configuration file operations, and more.

## Installation

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the API Service

```bash
python run_api.py
```

### Run the Web Frontend

```bash
python run_web.py
```

## Usage Instructions

### Album Management

- `Get List of Non-Locked Folders`: Send a GET request to retrieve folders available for operations.
- `Update Album`: Update multiple albums by ID.
- `Delete Album`: Delete an album by specifying its ID.
- `Create Folder`: Create a new album folder.
- `Upload File`: Upload files and automatically categorize them into specified folders.

### File Management

- `Extract EXIF Data`: Automatically extract important metadata when uploading files.
- `Rename File`: Modify the filename.
- `Delete File`: Delete the specified file.
- `Path Handling`: Automatically handle Windows path formats.

### Database Management

- The `SQLiteDB` class encapsulates basic functions such as database connection, querying, and pagination.
- `build_code.py` provides functionality to generate corresponding data model classes from database tables.

### Web Resource Management

- `WebsiteResource` is used to manage web-related resource information.
- `WebsiteTitle` is used to manage website title categories.

### Map Location Functionality

- Provides an interface to query image location information via latitude and longitude.

## Contribution Guide

Developers are welcome to contribute by submitting PRs or reporting bugs. Please ensure you follow the project's coding style and keep the code clean and clear.

## License

This project follows the MIT License. Please refer to the LICENSE file for detailed information.