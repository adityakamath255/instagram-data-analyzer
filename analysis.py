import json
import re
import codecs
from datetime import datetime
from collections import defaultdict
from pathlib import Path

class Message:
    def __init__(self, text, timestamp, sender):
        self.text = text
        self.timestamp = timestamp
        self.sender = sender

    @property
    def length(self):
        return len(self.text)

class ConversationAnalyzer:
    def __init__(self, messages):
        self.messages = sorted(messages, key=lambda m: m.timestamp)

    @classmethod
    def from_json_files(cls, file_paths):
        messages = []
        
        def decode_unicode_escapes(match):
            hex_str = match.group(0).replace(r'\u00', '')
            buffer = codecs.decode(hex_str, "hex")
            try:
                return buffer.decode('utf8')
            except Exception as e:
                print(f"Failed to decode text")
                return ''

        for file_path in file_paths:
            try:
                raw_data = file_path.read_text(encoding='utf-8')
                cleaned_data = re.sub(r'(?i)(?:\\u00[\da-f]{2})+', decode_unicode_escapes, raw_data)
                data = json.loads(cleaned_data)

                for msg in data['messages']:
                    if 'content' not in msg or msg.get('content', '').startswith(('Reacted ', 'Liked ')):
                        continue
                    
                    messages.append(Message(
                        text=msg['content'],
                        timestamp=datetime.fromtimestamp(msg['timestamp_ms'] / 1000),
                        sender=msg['sender_name']
                    ))
            except Exception as e:
                print(f"Error processing file {file_path}: {str(e)}")
                continue

        return cls(messages)

    def get_activity_metrics(self):
        metrics = {
            'daily': self._aggregate_by_date(),
            'hourly': self._aggregate_by_hour(),
            'monthly': self._aggregate_by_month(),
        }
        return metrics

    def _aggregate_by_date(self):
        activity = defaultdict(int)
        for msg in self.messages:
            activity[msg.timestamp.date()] += msg.length
        return dict(activity)

    def _aggregate_by_hour(self):
        activity = defaultdict(int)
        for msg in self.messages:
            activity[msg.timestamp.hour] += msg.length
        return dict(sorted(activity.items()))

    def _aggregate_by_month(self):
        activity = defaultdict(int)
        for msg in self.messages:
            month_key = f"{msg.timestamp.month}-{str(msg.timestamp.year)[-2:]}"
            activity[month_key] += msg.length
        return dict(activity)

class FollowAnalyzer:
    @staticmethod
    def identify_unfollowers(following_path, followers_path):
        try:
            with following_path.open() as f:
                following = {
                    user['string_list_data'][0]['value'] 
                    for user in json.load(f)['relationships_following']
                }

            with followers_path.open() as f:
                followers = {
                    user['string_list_data'][0]['value'] 
                    for user in json.load(f)
                }

            return list(following - followers)
        except Exception as e:
            print(f"Error analyzing Instagram data: {str(e)}")
            return []
