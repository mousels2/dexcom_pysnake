import pydexcom
from dotenv import load_dotenv
import os
import pygame
import time
from datetime import datetime
import argparse
import logging

TESTING = False  # Testing Switch
CHECK_TIMER = 300  # Time (in seconds) between each check
DROPPED_THRESHOLD = 2

# Initialise Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialise Pygame mixer
pygame.mixer.init()

# Load environment variables from .env file
load_dotenv()

# Fetch the credentials from environment variables
ACCOUNT = os.getenv('ACCOUNT')
PASSWORD = os.getenv('PASSWORD')

# Load empty array
readings = []

# Colour codes
good = (0, 255, 0)
bad = (255, 0, 0)
warning = (255, 255, 0)
no_reading = (80, 80, 80)
no_reading_line = (0,0,255)

stop_sound = pygame.mixer.Sound('crit_stop.wav')
startup_sound = pygame.mixer.Sound('tada.wav')

def colour_check(reading):
    if reading is None or reading == "--":
        return no_reading
    if isinstance(reading, pydexcom.GlucoseReading):
        reading = reading.mmol_l  # Access the glucose value
    elif isinstance(reading, str) and reading == "--":
        return no_reading
    elif reading > 15 or reading < 3:
        return bad
    elif reading < 4 or reading > 13:
        return warning
    else:
        return good

def add_reading(new_reading):
    if len(readings) > 5:
        readings.pop(0)
    readings.append(new_reading)

def simulate_readings():
    # Simulate various readings for testing
    simulated_data = [10, 16, 3, "--", 8, 6, 6, 12, 19, 5, 24, 99]
    for reading in simulated_data:
        yield reading

def calculate_y_coordinate(reading, chart_height):
    max_value = 30  # Fixed max value for Y axis
    min_value = 0   # Fixed min value for Y axis
    return int(400 - ((reading - min_value) / (max_value - min_value)) * chart_height)

def display_readings(test_mode=False):
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Live Blood Glucose Monitoring")
    font_large = pygame.font.Font(None, 74)
    font_small = pygame.font.Font(None, 50)
    running = True

    # Track time for periodic updates
    last_update_time = time.time()
    timer = CHECK_TIMER
    first_run = True

    # Simulated readings generator
    if test_mode:
        simulated_readings = simulate_readings()

    # Main loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("Closing program")
                    if readings:
                        print(readings)
                    running = False

        # Clear screen
        screen.fill((0, 0, 0))

        # Get the current glucose reading if it's time to update
        if time.time() - last_update_time > CHECK_TIMER or first_run:
            if test_mode:
                try:
                    reading = next(simulated_readings)
                except StopIteration:
                    reading = "--"  # No more simulated readings
            else:
                reading = dexcom.get_current_glucose_reading()

            if first_run:
                startup_sound.play()
                dropped_readings = 0
                first_run = False
            
            if reading != "--" and reading is not None:
                dropped_readings = 0
                glucose_value = reading if isinstance(reading, (int, float)) else reading.mmol_l
                glucose_text_color = colour_check(glucose_value)
                if glucose_text_color == bad:
                    stop_sound.play()
                glucose_text = font_large.render(f"Glucose Level: {glucose_value} mmol/L", True, glucose_text_color)
                add_reading(glucose_value)
            else:
                glucose_text_color = no_reading
                dropped_readings = dropped_readings + 1
                glucose_text = font_large.render(f"Glucose Level: -- mmol/L", True, glucose_text_color)
                add_reading(0)  # Add a flat line as if a 0 was received for "--"
                if dropped_readings >= DROPPED_THRESHOLD:
                    stop_sound.play()
            last_update_time = time.time()

            timer = CHECK_TIMER  # Reset timer
            current_timestamp = datetime.now()
            print(f"{readings}, {current_timestamp}")

        # Draw the updated chart with transparency support behind the text
        numeric_readings = [r for r in readings if isinstance(r, (int, float))]
        
        if len(numeric_readings) > 1:
            chart_height = 200
            chart_width = len(numeric_readings) * (800 // len(numeric_readings))
            graph_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
            graph_surface.set_alpha(128)  # Set transparency for the graph
            
            for i in range(len(numeric_readings) - 1):
                x1 = i * (chart_width // len(numeric_readings))
                y1 = calculate_y_coordinate(numeric_readings[i], chart_height)
                x2 = (i + 1) * (chart_width // len(numeric_readings))
                y2 = calculate_y_coordinate(numeric_readings[i + 1], chart_height)
                line_color = colour_check(numeric_readings[i + 1]) if i + 1 < len(numeric_readings) else colour_check(numeric_readings[i])
                pygame.draw.line(graph_surface, line_color, (x1, y1), (x2, y2), 5)
            
            screen.blit(graph_surface, (0, 0))

        # Display the glucose reading text on top of the graph
        screen.blit(glucose_text, (screen.get_width() // 2 - glucose_text.get_width() // 2, 250))

        # Display the timer text on top of the graph
        timer_text_color = (255, 255, 255)
        timer_text = font_small.render(f"Update in: {timer}s", True, timer_text_color)
        screen.blit(timer_text, (screen.get_width() // 2 - timer_text.get_width() // 2, 350))

        # Display the last 5 readings text on top of the graph
        readings_text_color = (50, 50, 50)
        readings_text = font_small.render(f"Readings: {readings}", True, readings_text_color)
        screen.blit(readings_text, (screen.get_width() // 2 - readings_text.get_width() // 2, 550))
        
        pygame.display.flip()

        # Wait for 1 second to update timer correctly
        pygame.time.wait(1000)
        timer -= 1  # Decrement timer

    pygame.quit()

def main(test_mode=False):
    print("Running BM Check")

    if test_mode:
        print("Running Test Mode")
    else:
        print("Running Live Mode")
        global dexcom
        dexcom = pydexcom.Dexcom(username=ACCOUNT, password=PASSWORD, region="ous")
        
    display_readings(test_mode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Live Blood Glucose Monitoring')
    parser.add_argument('-t', '--test', action='store_true', help='Run the script in test mode with simulated readings.')
    args = parser.parse_args()

    if args.test:
        TESTING = True
        CHECK_TIMER = 10

    main(test_mode=TESTING)
