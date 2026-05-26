# Bilibili Dynamic Auto Liker

## Overview
This project is designed to automate the liking of dynamic posts on Bilibili, a popular Chinese video-sharing platform. The goal is to enhance user engagement by automatically liking posts based on predefined criteria.

## Features
- **Automatic Liking**: Automatically like dynamic posts based on user-defined settings.
- **Criteria-Based Selection**: Customize selection criteria for which posts should be liked.
- **User Authentication**: Securely authenticate with Bilibili’s API to perform actions on user behalf.
- **Logging**: Keep track of liked posts and any errors encountered during the process.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/iiaowro/bilibili-dynamic-auto-liker.git
   ```
2. Navigate to the project directory:
   ```bash
   cd bilibili-dynamic-auto-liker
   ```
3. Install necessary packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
- Create a configuration file (`config.json`) in the root directory.
- Example `config.json`:
   ```json
   {
       "username": "your_username",
       "password": "your_password",
       "criteria": {
           "min_likes": 10,
           "min_comments": 5
       }
   }
   ```

## Usage
Run the script to start the auto liking process:
```bash
python main.py
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue if you'd like to contribute.
   
## License
This project is licensed under the MIT License. See the LICENSE file for details.

 
