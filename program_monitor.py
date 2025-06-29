import psutil
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import requests
from pathlib import Path
import threading


class ProgramMonitor:
    """Övervakar ett program och skickar data till DeepSeek API"""
    
    def __init__(self, process_name: str, deepseek_api_key: str, 
                 google_sheets_credentials: Optional[str] = None,
                 monitor_interval: int = 5):
        """
        Initialiserar programövervakning
        
        Args:
            process_name: Namnet på processen att övervaka
            deepseek_api_key: API-nyckel för DeepSeek
            google_sheets_credentials: Sökväg till Google Sheets credentials
            monitor_interval: Intervall i sekunder mellan mätningar
        """
        self.process_name = process_name
        self.deepseek_api_key = deepseek_api_key
        self.monitor_interval = monitor_interval
        self.google_credentials = google_sheets_credentials
        
        # Konfigurera logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('program_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.monitoring = False
        self.monitor_thread = None
        self.metrics_history = []
        
    def find_process(self) -> Optional[psutil.Process]:
        """Hittar processen baserat på namn"""
        for proc in psutil.process_iter(['pid', 'name']):
            if self.process_name.lower() in proc.info['name'].lower():
                return proc
        return None
    
    def collect_metrics(self, process: psutil.Process) -> Dict:
        """Samlar in metrics från processen"""
        try:
            with process.oneshot():
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'pid': process.pid,
                    'name': process.name(),
                    'cpu_percent': process.cpu_percent(interval=0.1),
                    'memory_info': {
                        'rss': process.memory_info().rss / 1024 / 1024,  # MB
                        'vms': process.memory_info().vms / 1024 / 1024,  # MB
                        'percent': process.memory_percent()
                    },
                    'num_threads': process.num_threads(),
                    'status': process.status(),
                    'create_time': datetime.fromtimestamp(process.create_time()).isoformat()
                }
                
                # Försök få IO-statistik (kan misslyckas på vissa system)
                try:
                    io_counters = process.io_counters()
                    metrics['io_counters'] = {
                        'read_bytes': io_counters.read_bytes,
                        'write_bytes': io_counters.write_bytes,
                        'read_count': io_counters.read_count,
                        'write_count': io_counters.write_count
                    }
                except (psutil.AccessDenied, AttributeError):
                    pass
                
                return metrics
                
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            self.logger.error(f"Fel vid insamling av metrics: {e}")
            return None
    
    def analyze_with_deepseek(self, metrics: List[Dict]) -> Dict:
        """Analyserar metrics med DeepSeek API"""
        try:
            # Förbered data för analys
            analysis_prompt = f"""
            Analysera följande programprestanda-data och ge insikter:
            
            Program: {self.process_name}
            Antal mätpunkter: {len(metrics)}
            
            Senaste metrics:
            {json.dumps(metrics[-10:], indent=2)}
            
            Ge en analys av:
            1. Prestandatrender
            2. Potentiella problem
            3. Optimeringsförslag
            """
            
            # Anropa DeepSeek API
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.deepseek_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': 'Du är en expert på systemövervakning och prestandaanalys.'},
                        {'role': 'user', 'content': analysis_prompt}
                    ],
                    'temperature': 0.7
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result['choices'][0]['message']['content']
                return {
                    'timestamp': datetime.now().isoformat(),
                    'analysis': analysis,
                    'metrics_count': len(metrics)
                }
            else:
                self.logger.error(f"DeepSeek API-fel: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Fel vid DeepSeek-analys: {e}")
            return None
    
    def write_to_google_sheets(self, data: Dict):
        """Skriver data till Google Sheets"""
        if not self.google_credentials:
            self.logger.warning("Google Sheets credentials inte konfigurerade")
            return
        
        try:
            # Här skulle du implementera Google Sheets API-integration
            # För nu, sparar vi bara till en JSON-fil
            output_file = Path('monitoring_data.json')
            
            existing_data = []
            if output_file.exists():
                with open(output_file, 'r') as f:
                    existing_data = json.load(f)
            
            existing_data.append(data)
            
            with open(output_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
                
            self.logger.info(f"Data sparad till {output_file}")
            
        except Exception as e:
            self.logger.error(f"Fel vid skrivning till Google Sheets: {e}")
    
    def _monitor_loop(self):
        """Huvudloop för övervakning"""
        while self.monitoring:
            process = self.find_process()
            
            if process:
                metrics = self.collect_metrics(process)
                if metrics:
                    self.metrics_history.append(metrics)
                    self.logger.info(f"Metrics insamlade: CPU={metrics['cpu_percent']}%, "
                                   f"Memory={metrics['memory_info']['rss']:.1f}MB")
                    
                    # Analysera var 10:e mätpunkt
                    if len(self.metrics_history) % 10 == 0:
                        analysis = self.analyze_with_deepseek(self.metrics_history[-50:])
                        if analysis:
                            self.write_to_google_sheets({
                                'type': 'analysis',
                                'data': analysis
                            })
                    
                    # Spara metrics
                    self.write_to_google_sheets({
                        'type': 'metrics',
                        'data': metrics
                    })
            else:
                self.logger.warning(f"Process '{self.process_name}' hittades inte")
            
            time.sleep(self.monitor_interval)
    
    def start_monitoring(self):
        """Startar övervakning i bakgrundstråd"""
        if self.monitoring:
            self.logger.warning("Övervakning redan igång")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.logger.info(f"Övervakning startad för '{self.process_name}'")
    
    def stop_monitoring(self):
        """Stoppar övervakning"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("Övervakning stoppad")
    
    def get_summary(self) -> Dict:
        """Hämtar sammanfattning av insamlade metrics"""
        if not self.metrics_history:
            return {'status': 'Inga metrics insamlade'}
        
        cpu_values = [m['cpu_percent'] for m in self.metrics_history]
        memory_values = [m['memory_info']['rss'] for m in self.metrics_history]
        
        return {
            'total_measurements': len(self.metrics_history),
            'monitoring_duration': (
                datetime.fromisoformat(self.metrics_history[-1]['timestamp']) -
                datetime.fromisoformat(self.metrics_history[0]['timestamp'])
            ).total_seconds(),
            'cpu_stats': {
                'average': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory_stats': {
                'average': sum(memory_values) / len(memory_values),
                'max': max(memory_values),
                'min': min(memory_values)
            }
        }


def example_usage():
    """Exempel på användning"""
    # OBS: Du behöver en riktig DeepSeek API-nyckel
    monitor = ProgramMonitor(
        process_name="python",  # Ändra till programmet du vill övervaka
        deepseek_api_key="din-deepseek-api-nyckel-här",
        monitor_interval=5
    )
    
    try:
        monitor.start_monitoring()
        print("Övervakning startad. Tryck Ctrl+C för att stoppa...")
        
        # Kör i 60 sekunder som exempel
        time.sleep(60)
        
    except KeyboardInterrupt:
        print("\nStoppar övervakning...")
    finally:
        monitor.stop_monitoring()
        summary = monitor.get_summary()
        print(f"\nÖvervakning sammanfattning:")
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    example_usage()