# Running a Python Program with a Virtual Environment

## Navigate to the Program Folder

* Use `ls` to list folders and files in the current location.

* Use `cd myfolder` to move into a folder named "myfolder."

* Use `cd ..` to go back to the previous directory.

## Activate the Environment and Run the Program

Note: After setting up the environment, you can run the program.

### Backend

1. **Activate the environment** or check if you're already inside one. You'll know you're in an environment if the command line interface (CLI) shows `(env)` at the beginning. "env" is the environment name, but it can vary.
   - `.env/Scripts/activate`

### Frontend

## Setting Up the Environment for the First Time

**Note:** This setup process only needs to be done the first time on a specific computer. If you want to run the program on a different computer, follow these steps again.

1. **Create a virtual environment.** This is where we’ll install all required modules to run the code.

   - `python -m venv env`

   Here, "env" is the name of the environment.
2. **Activate the environment.**

   - `env/Scripts/activate`

   You’ll know you’re in the environment when `(env)` appears in the CLI.
3. **Install necessary modules from the `requirements.txt` file.**

   - `pip install -r requirements.txt`
