import time
import random

class LikeManager:
    def __init__(self):
        self.max_retries = 5  # Maximum number of retries
        self.retry_delay = 2  # Delay in seconds before retrying

    def send_like(self):
        # Simulating a like sending process (randomly succeed or fail)
        success = random.choice([True, False])
        return success

    def manage_likes(self):
        for attempt in range(self.max_retries):
            if self.send_like():
                print('Like sent successfully!')
                return True
            else:
                print(f'Attempt {attempt + 1} failed. Retrying in {self.retry_delay} seconds...')
                time.sleep(self.retry_delay)
        print('Failed to send like after maximum retries.')
        return False

# Example usage:
if __name__ == '__main__':
    manager = LikeManager()
    manager.manage_likes()