# Project Documentation

## Project Name
**strava-hr-zones**

## Description
Proof of concept - weekly heart zones for activities recorded in Strava.

## Project Structure
strava-hr-zones/ 
├── .gitignore 
├── .streamlit/
│ └── secrets.toml 
├── app.py
├── README.md 
├── requirements.txt  
└── strava.py

## Files and Directories

### `.gitignore`
Specifies files and directories that should be ignored by Git.

### `.streamlit/secrets.toml`
Contains sensitive information such as API keys and secrets. This file should not be committed to version control.

### `README.md`
Provides an overview of the project, including its purpose and usage.

### `requirements.txt`
Lists the dependencies required for the project.

### `app.py`
Contains the source code for the stramlite application.

#### `strava.py`
Contains functions related to Strava API interactions.

## Setup and Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/strava-hr-zones.git
    ```

2. Navigate to the project directory:
    ```sh
    cd strava-hr-zones
    ```

3. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

4. Activate the virtual environment:
    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```

5. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the main script:
    ```sh
    python src/main.py
    ```

## Contributing
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## License
This project is licensed under the MIT License - see the `LICENSE` file for details.