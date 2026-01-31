import numpy as np
from agents.dedupe_agent import DeduplicationAgent, CrossReferenceAgent
from agents.extract_agent import extract_need
from models.schema import Need
from datetime import datetime
import json
import os

def load_sample_data():
    """Load disaster posts from file"""
    try:
        with open('data/sample_posts.txt', 'r', encoding='utf-8') as f:
            posts = [line.strip() for line in f if line.strip()]
        
        if not posts:
            raise ValueError("File is empty")
            
        return posts
        
    except FileNotFoundError:
        print("❌ ERROR: data/sample_posts.txt not found!")
        print("Please create the file with disaster reports.")
        print("\nExample content:")
        print("URGENT: Food needed in Andheri East. 50 families affected.")
        print("Medical emergency in Bandra West. Insulin required.")
        exit(1)
        
    except Exception as e:
        print(f"❌ ERROR loading data: {e}")
        exit(1)

def extract_needs_from_posts(posts):
    """
    Extract structured needs from raw posts
    Uses real LLM extraction if available, otherwise manual keyword extraction
    """
    needs = []
    sources = ["twitter", "facebook", "whatsapp", "reddit", "instagram"]
    
    for i, post in enumerate(posts):
        source = sources[i % len(sources)]
        
        # Try LLM extraction first (Groq)
        try:
            need = extract_need(post, source)
            if need:
                needs.append(need)
                continue
        except Exception as e:
            pass  # Fall back to keyword extraction
        
        # Keyword-based extraction (fallback)
        post_lower = post.lower()
        
        # Determine need type
        if "food" in post_lower or "water" in post_lower or "supplies" in post_lower:
            need_type = "food"
        elif "medical" in post_lower or "insulin" in post_lower or "medicine" in post_lower:
            need_type = "medical"
        elif "shelter" in post_lower or "displaced" in post_lower or "homeless" in post_lower:
            need_type = "shelter"
        elif "rescue" in post_lower or "trapped" in post_lower or "stranded" in post_lower:
            need_type = "rescue"
        else:
            need_type = "other"
        
        # Extract location
        location = None
        if "andheri east" in post_lower:
            location = "Andheri East, Mumbai"
        elif "andheri" in post_lower:
            location = "Andheri East, Mumbai"
        elif "bandra west" in post_lower:
            location = "Bandra West"
        elif "bandra" in post_lower:
            location = "Bandra West"
        elif "kurla" in post_lower:
            location = "Kurla Station"
        elif "dadar" in post_lower:
            location = "Dadar"
        elif "thane" in post_lower:
            location = "Thane"
        elif "borivali" in post_lower:
            location = "Borivali"
        elif "powai" in post_lower:
            location = "Powai"
        elif "worli" in post_lower:
            location = "Worli"
        elif "colaba" in post_lower:
            location = "Colaba"
        elif "malad" in post_lower:
            location = "Malad"
        
        # Determine urgency
        if "urgent" in post_lower or "emergency" in post_lower or "immediately" in post_lower or "sos" in post_lower:
            urgency = 5
        elif "critical" in post_lower or "serious" in post_lower or "breaking" in post_lower:
            urgency = 4
        elif "needed" in post_lower or "required" in post_lower:
            urgency = 3
        else:
            urgency = 2
        
        # Create Need object
        need = Need(
            need_type=need_type,
            location=location,
            urgency=urgency,
            summary=post[:100],
            source=source,
            timestamp=datetime.now().isoformat()
        )
        
        needs.append(need)
    
    return needs

def save_results(verified_incidents, needs):
    """Save results to JSON file"""
    try:
        os.makedirs('outputs', exist_ok=True)
        
        output = {
            "timestamp": datetime.now().isoformat(),
            "total_reports": len(needs),
            "unique_incidents": len(verified_incidents),
            "deduplication_rate": f"{((len(needs) - len(verified_incidents)) / len(needs) * 100):.1f}%",
            "incidents": [
                {
                    "id": inc.incident_id,
                    "type": inc.need_type,
                    "location": inc.location,
                    "urgency": inc.urgency,
                    "summary": inc.summary,
                    "confidence": f"{inc.confidence_score:.1%}",
                    "report_count": inc.report_count,
                    "sources": list(set(inc.sources))
                }
                for inc in verified_incidents
            ]
        }
        
        with open('outputs/verified_incidents.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"⚠️ Could not save results: {e}")
        return False

def run_disaster_relief_system():
    """Main system runner"""
    
    print("\n" + "="*70)
    print("🚨 DISASTER RELIEF RESOURCE SCOUT - FEATURE 2")
    print("="*70)
    
    # Load data
    print("\n📥 Loading disaster reports...")
    posts = load_sample_data()
    print(f"✅ Loaded {len(posts)} posts from data/sample_posts.txt")
    
    # Extract structured needs
    print("\n🔄 Processing reports...")
    needs = extract_needs_from_posts(posts)
    print(f"✅ Extracted {len(needs)} structured needs")
    
    if not needs:
        print("❌ No valid needs extracted. Check your input data.")
        return
    
    # Feature 2: Deduplication
    print("\n🔍 Identifying unique incidents...")
    print("⚙️  Using similarity threshold: 0.75")
    print("   (Semantic clustering with DBSCAN)")
    
    dedupe_agent = DeduplicationAgent(similarity_threshold=0.75)
    unique_incidents = dedupe_agent.deduplicate_clustering(needs)
    
    duplicates_removed = len(needs) - len(unique_incidents)
    dedup_rate = (duplicates_removed / len(needs) * 100) if needs else 0
    
    print(f"✅ Identified {len(unique_incidents)} unique incidents")
    print(f"📊 Eliminated {duplicates_removed} duplicates ({dedup_rate:.1f}%)")
    
    # Feature 2: Cross-reference
    print("\n🔍 Cross-referencing and scoring confidence...")
    print("   Factors: Report count + Source diversity + Urgency consensus")
    
    cross_ref_agent = CrossReferenceAgent()
    verified_incidents = cross_ref_agent.verify_incidents(unique_incidents)
    
    # Display results
    print("\n" + "="*70)
    print("📋 VERIFIED UNIQUE INCIDENTS (Ranked by Confidence)")
    print("="*70 + "\n")
    
    for i, incident in enumerate(verified_incidents, 1):
        if incident.confidence_score > 0.7:
            confidence_emoji = "🟢"
        elif incident.confidence_score > 0.4:
            confidence_emoji = "🟡"
        else:
            confidence_emoji = "🔴"
        
        print(f"{confidence_emoji} #{i} [{incident.incident_id}]")
        print(f"   Type: {incident.need_type.upper()}")
        print(f"   Location: {incident.location or 'Unknown'}")
        
        urgency_filled = "🔴" * incident.urgency
        urgency_empty = "⚪" * (5 - incident.urgency)
        print(f"   Urgency: {urgency_filled}{urgency_empty} ({incident.urgency}/5)")
        
        summary_truncated = incident.summary[:80] + "..." if len(incident.summary) > 80 else incident.summary
        print(f"   Summary: {summary_truncated}")
        
        unique_sources = len(set(incident.sources))
        print(f"   📊 Corroboration: {incident.report_count} reports from {unique_sources} sources")
        print(f"   🎯 Confidence: {incident.confidence_score:.1%}")
        
        if incident.report_count > 1:
            print(f"   📱 Sources: {', '.join(set(incident.sources))}")
        
        print("-" * 70)
    
    # Statistics
    print("\n" + "="*70)
    print("📈 SUMMARY STATISTICS")
    print("="*70)
    print(f"Total reports processed: {len(needs)}")
    print(f"Unique incidents identified: {len(unique_incidents)}")
    print(f"Deduplication rate: {dedup_rate:.1f}%")
    
    high_conf = sum(1 for i in verified_incidents if i.confidence_score > 0.7)
    med_conf = sum(1 for i in verified_incidents if 0.4 <= i.confidence_score <= 0.7)
    low_conf = sum(1 for i in verified_incidents if i.confidence_score < 0.4)
    
    print(f"High confidence (>70%): {high_conf} incidents")
    print(f"Medium confidence (40-70%): {med_conf} incidents")
    print(f"Low confidence (<40%): {low_conf} incidents")
    
    # Save results
    print("\n💾 Saving results...")
    if save_results(verified_incidents, needs):
        print("✅ Saved to: outputs/verified_incidents.json")
    
    print(f"\n🕐 Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

if __name__ == "__main__":
    run_disaster_relief_system()