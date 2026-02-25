import time
import threading

import google_spread_sheet


class google_sheets_queue:
    def __init__(self, sheet_name):
        self.items = []
        self.sheet_name = sheet_name
        self.is_dequeue_safe = True

    def is_empty(self):
        return len(self.items) == 0

    def enqueue(self, item):
        """
        Since we are working with threads we do not want to dequeue while we are enqueueing
        :param item:
        :return:
        """
        self.is_dequeue_safe = False
        self.items.append(item)
        self.is_dequeue_safe = True

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        raise IndexError("dequeue from empty queue")

    def size(self):
        return len(self.items)

    def peek(self):
        if not self.is_empty():
            return self.items[0]
        raise IndexError("peek from empty queue")

    def worker(self):
        while True:
            try:
                if not self.is_empty() and self.is_dequeue_safe:
                    item = self.dequeue()
                    # Process the item (save to Google Sheets)
                    google_spread_sheet.append_or_create_tab_by_id(self.sheet_name, item)
                else:
                    time.sleep(10)
            except Exception as e:
                print(f"Error in worker: {e}")
                time.sleep(10)

    def start_worker(self):
        worker_thread = threading.Thread(target=self.worker)
        worker_thread.daemon = True
        worker_thread.start()
