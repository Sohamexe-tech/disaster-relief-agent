from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
import numpy as np
from models.schema import Need, UniqueIncident
from typing import List
import hashlib

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

class DeduplicationAgent:
    def __init__(self, similarity_threshold=0.75):
        self.similarity_threshold = similarity_threshold
    
    def get_embedding(self, text: str):
        """Generate semantic embedding for text"""
        return embedding_model.encode(text)
    
    def are_similar(self, need1: Need, need2: Need) -> bool:
        """Check if two needs describe the same incident"""
        if need1.need_type != need2.need_type:
            return False
        
        if need1.location and need2.location:
            loc_similarity = self._text_similarity(need1.location, need2.location)
            if loc_similarity < 0.7:
                return False
        
        summary_sim = self._text_similarity(need1.summary, need2.summary)
        return summary_sim >= self.similarity_threshold
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        return cosine_similarity([emb1], [emb2])[0][0]
    
    def deduplicate_clustering(self, needs: List[Need]) -> List[UniqueIncident]:
        """Advanced clustering-based deduplication"""
        if len(needs) < 2:
            return self.deduplicate_simple(needs)
        
        embeddings = np.array([self.get_embedding(need.summary) for need in needs])
        
        clustering = DBSCAN(
            eps=1 - self.similarity_threshold,
            min_samples=1,
            metric='cosine'
        ).fit(embeddings)
        
        clusters = {}
        for idx, label in enumerate(clustering.labels_):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(needs[idx])
        
        unique_incidents = []
        for cluster_id, cluster_needs in clusters.items():
            primary = cluster_needs[0]
            incident_id = self._generate_id(primary)
            
            unique_incidents.append(
                UniqueIncident(
                    incident_id=incident_id,
                    need_type=primary.need_type,
                    location=primary.location,
                    urgency=max(n.urgency for n in cluster_needs),
                    summary=primary.summary,
                    report_count=len(cluster_needs),
                    sources=[n.source for n in cluster_needs],
                    original_reports=cluster_needs
                )
            )
        
        return unique_incidents
    
    def deduplicate_simple(self, needs: List[Need]) -> List[UniqueIncident]:
        """Simple pairwise deduplication"""
        unique_incidents = []
        
        for need in needs:
            matched = False
            
            for incident in unique_incidents:
                if self.are_similar(need, incident.original_reports[0]):
                    incident.original_reports.append(need)
                    incident.report_count += 1
                    incident.sources.append(need.source)
                    matched = True
                    break
            
            if not matched:
                incident_id = self._generate_id(need)
                unique_incidents.append(
                    UniqueIncident(
                        incident_id=incident_id,
                        need_type=need.need_type,
                        location=need.location,
                        urgency=need.urgency,
                        summary=need.summary,
                        sources=[need.source],
                        original_reports=[need]
                    )
                )
        
        return unique_incidents
    
    def _generate_id(self, need: Need) -> str:
        """Generate unique incident ID"""
        content = f"{need.need_type}_{need.location}_{need.summary[:50]}"
        return f"INC_{hashlib.md5(content.encode()).hexdigest()[:8].upper()}"


class CrossReferenceAgent:
    """Validates incidents by checking corroboration across sources"""
    
    def calculate_confidence(self, incident: UniqueIncident) -> float:
        """
        Calculate confidence score based on:
        - Number of independent reports
        - Source diversity
        - Urgency consistency
        """
        score = 0.0
        
        # Base score from report count (max 0.5)
        report_score = min(incident.report_count / 5.0, 0.5)
        score += report_score
        
        # Source diversity bonus (max 0.3)
        unique_sources = len(set(incident.sources))
        source_score = min(unique_sources / 3.0, 0.3)
        score += source_score
        
        # Urgency consensus (max 0.2)
        if incident.report_count > 1:
            urgencies = [n.urgency for n in incident.original_reports]
            urgency_variance = np.var(urgencies)
            
            if urgency_variance < 0.5:
                score += 0.2
            elif urgency_variance < 1.0:
                score += 0.1
        else:
            score += 0.1
        
        return min(score, 1.0)
    
    def verify_incidents(self, incidents: List[UniqueIncident]) -> List[UniqueIncident]:
        """Add confidence scores to all incidents"""
        for incident in incidents:
            incident.confidence_score = self.calculate_confidence(incident)
        
        incidents.sort(key=lambda x: x.confidence_score, reverse=True)
        return incidents