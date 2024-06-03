# import logging
# import io
# import sys
from interpreter import interpreter

# Configure logging to log to both file and console
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)y

# Create file handler which logs messages
# fh = logging.FileHandler('chat.log')
# fh.setLevel(logging.INFO)

# # Create console handler with a higher log level
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)

# # Create formatter and add it to the handlers
# formatter = logging.Formatter('%(asctime)s - %(message)s')
# fh.setFormatter(formatter)
# ch.setFormatter(formatter)

# # Add the handlers to logger
# logger.addHandler(fh)
# logger.addHandler(ch)

# # Create a string stream to capture the output
# output_capture = io.StringIO()

# # Redirect stdout to capture output
# original_stdout = sys.stdout
# sys.stdout = output_capture

# Run the interpreter chat function
interpreter.chat("Please look for local O-JRC folder and read its code. What do you think this mmWave development software platform ?")

# Reset stdout
# sys.stdout = original_stdout

# Get the captured output
# captured_output = output_capture.getvalue()

# Log the captured output
# logger.info(captured_output)


# Log the captured output
# logging.info(f'Terminal Output: {captured_output}')
# logging.info(f'Result: {result}')

# sed -i '/export OPENAI_API_KEY=/d' ~/.basy
# hrc
# echo '\nexport OPENAI_API_KEY=your_api_key' >> ~/.bashrc
# source ~/.bashrc