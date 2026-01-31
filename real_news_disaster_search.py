import requests
import xml.etree.ElementTree as ET
from groq import Groq
from agents.dedupe_agent import DeduplicationAgent, CrossReferenceAgent
from agents.extract_agent import extract_need
from models.schema import Need
from datetime import datetime
from bs4 import BeautifulSoup

client = Groq(api_key="YOUR_GROQ_API_KEY_HERE")  # Replace with your Groq API key

class RealNewsDisasterSearch:
    def __init__(self):
        self.dedupe_agent = DeduplicationAgent(similarity_threshold=0.75)
        self.cross_ref_agent = CrossReferenceAgent()

    # ------------------- CITY SEARCH -------------------
    def search_city(self, city_name: str, return_data=False):
        news = self.search_google_news(city_name)
        all_reports = [n["title"] for n in news]

        if len(all_reports) < 8:
            ai_reports = self.enhance_with_ai(city_name, len(all_reports))
            all_reports.extend(ai_reports)
        else:
            ai_reports = []

        needs = self.extract_needs_from_reports(all_reports, city_name)
        unique_incidents = self.dedupe_agent.deduplicate_clustering(needs)
        verified_incidents = self.cross_ref_agent.verify_incidents(unique_incidents)

        if return_data:
            return {
                "real_news": news,
                "ai_reports": ai_reports,
                "incidents": verified_incidents
            }

        print(f"Real news: {len(news)} | AI reports: {len(ai_reports)} | Incidents: {len(verified_incidents)}")
        return verified_incidents

    def search_google_news(self, city_name: str):
        rss_url = f"https://news.google.com/rss/search?q={city_name}+disaster+OR+emergency&hl=en-IN&gl=IN&ceid=IN:en"
        headlines = []
        try:
            response = requests.get(rss_url, timeout=10)
            if response.status_code != 200:
                return []
            root = ET.fromstring(response.content)
            for item in root.findall('.//item')[:10]:
                title = item.find('title').text
                link = item.find('link').text
                if title and link:
                    headlines.append({"title": title, "link": link})
        except:
            return []
        return headlines

    def enhance_with_ai(self, city_name: str, news_count: int):
        enhance_prompt = f"""Generate {10 - news_count} realistic disaster and emergency reports for {city_name}, India.
Include floods, fires, accidents, medical emergencies, and traffic incidents.
Format each as a social media post or news headline. One report per line."""
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a disaster monitoring AI."},
                    {"role": "user", "content": enhance_prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.8,
                max_tokens=800
            )
            ai_reports = response.choices[0].message.content
            reports = [line.strip() for line in ai_reports.split("\n") if line.strip()]
            return reports
        except:
            return []

    def extract_needs_from_reports(self, reports: list, city_name: str):
        needs = []
        sources = ["google_news", "twitter", "facebook", "whatsapp", "reddit", "instagram"]
        for i, report in enumerate(reports):
            source = sources[i % len(sources)]
            try:
                need = extract_need(report, source)
                if need:
                    needs.append(need)
                    continue
            except:
                pass
            need = self._keyword_extract(report, source, city_name)
            if need:
                needs.append(need)
        return needs

    def _keyword_extract(self, text: str, source: str, city: str):
        text_lower = text.lower()
        if any(k in text_lower for k in ['flood', 'rain', 'water', 'submerged']):
            need_type = "rescue"
        elif any(k in text_lower for k in ['fire', 'blaze', 'burn']):
            need_type = "rescue"
        elif any(k in text_lower for k in ['medical', 'hospital', 'injured', 'health']):
            need_type = "medical"
        elif any(k in text_lower for k in ['food', 'hunger', 'supplies']):
            need_type = "food"
        elif any(k in text_lower for k in ['shelter', 'homeless', 'displaced']):
            need_type = "shelter"
        else:
            need_type = "other"

        if any(k in text_lower for k in ['urgent', 'emergency', 'critical', 'sos']):
            urgency = 5
        elif any(k in text_lower for k in ['serious', 'major', 'severe']):
            urgency = 4
        else:
            urgency = 3

        return Need(
            need_type=need_type,
            location=city,
            urgency=urgency,
            summary=text[:150],
            source=source,
            timestamp=datetime.now().isoformat()
        )

    # ------------------- URL FACT-CHECK -------------------
    def analyze_news_url(self, url: str):
        """Classify news URL as TRUE or FALSE"""
        result = {"status": "unknown", "title": "", "published": None}
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                result["status"] = "unreachable"
                return result

            soup = BeautifulSoup(resp.text, "html.parser")
            title_tag = soup.find("title")
            result["title"] = title_tag.text.strip() if title_tag else "Unknown Title"

            article_text = soup.get_text()[:2000]  # first 2000 chars

            # Fact-check AI prompt
            prompt = f"""
            You are a fact-checking AI. Determine if this news article is TRUE or FALSE.
            Answer ONLY with one word: TRUE or FALSE.
            URL: {url}
            Article Text: {article_text}
            """

            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a fact-checking AI."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0
            )

            verdict = response.choices[0].message.content.strip().upper()
            if verdict in ["TRUE", "FALSE"]:
                result["status"] = verdict.lower()
            else:
                result["status"] = "unknown"

        except Exception as e:
            result["status"] = f"error: {str(e)}"

        return result
