import time
import random
from datetime import datetime

class RealtimeSimulator:
    """Simulates real-time disaster reports for demo"""
    
    def __init__(self):
        self.templates = [
            "URGENT: {disaster} in {location}. {count} {victims} need {need}.",
            "Emergency {need} required in {location}. {disaster} has affected {count} {victims}.",
            "{count} {victims} stranded in {location} due to {disaster}. Need {need} urgently.",
            "Breaking: {disaster} hits {location}. {count} {victims} require immediate {need}.",
            "SOS: {disaster} in {location} area. Approximately {count} {victims} desperately need {need}.",
            "{location} crisis: {disaster} leaves {count} {victims} without {need}. Help needed now!",
            "Disaster alert - {disaster} in {location}. {count} {victims} require urgent {need} assistance.",
            "Critical situation: {count} {victims} affected by {disaster} in {location}. {need} needed ASAP.",
        ]
        
        self.disasters = [
            "Flood", "Earthquake", "Building collapse", "Fire", "Landslide",
            "Cyclone", "Heavy rain", "Gas leak", "Bridge collapse"
        ]
        
        self.locations = [
            "Andheri East", "Bandra West", "Kurla Station", "Dadar", "Thane",
            "Borivali", "Powai", "Worli", "Colaba", "Malad"
        ]
        
        self.needs = [
            "food and water", "medical supplies", "shelter", "rescue",
            "blankets", "first aid", "evacuation", "ambulance services",
            "clean water", "emergency medicine"
        ]
        
        self.victims = [
            "families", "people", "individuals", "residents", "citizens",
            "children", "elderly persons", "workers", "commuters"
        ]
    
    def generate_post(self):
        """Generate one realistic disaster post"""
        template = random.choice(self.templates)
        
        post = template.format(
            disaster=random.choice(self.disasters),
            location=random.choice(self.locations),
            count=random.choice([15, 20, 30, 40, 50, 75, 100, 150, 200]),
            victims=random.choice(self.victims),
            need=random.choice(self.needs)
        )
        
        return post
    
    def generate_batch(self, count=10):
        """Generate multiple posts at once"""
        return [self.generate_post() for _ in range(count)]
    
    def stream_to_file(self, duration_seconds=30, posts_per_minute=4, filename='data/sample_posts.txt'):
        """
        Simulate real-time stream
        
        Args:
            duration_seconds: How long to run (30 for demo)
            posts_per_minute: Rate of incoming posts
            filename: Output file path
        """
        
        interval = 60 / posts_per_minute
        end_time = time.time() + duration_seconds
        
        posts = []
        
        print(f"🔴 LIVE: Streaming disaster reports for {duration_seconds}s...")
        print(f"📊 Rate: {posts_per_minute} posts/minute\n")
        
        post_count = 0
        while time.time() < end_time:
            post = self.generate_post()
            posts.append(post)
            post_count += 1
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 📥 #{post_count}: {post[:70]}...")
            
            time.sleep(interval)
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            for post in posts:
                f.write(post + '\n')
        
        print(f"\n✅ Captured {len(posts)} posts → {filename}")
        print("▶️  Ready to process with: python main.py")
        
        return posts
    
    def save_batch_to_file(self, count=10, filename='data/sample_posts.txt'):
        """Generate and save a batch of posts instantly"""
        posts = self.generate_batch(count)
        
        with open(filename, 'w', encoding='utf-8') as f:
            for post in posts:
                f.write(post + '\n')
        
        print(f"✅ Generated {len(posts)} posts → {filename}")
        return posts


if __name__ == "__main__":
    simulator = RealtimeSimulator()
    simulator.stream_to_file(duration_seconds=30, posts_per_minute=4)