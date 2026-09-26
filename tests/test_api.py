from fastapi.testclient import TestClient
from backend.main import app

client=TestClient(app)

def setup_module():
    import subprocess,sys
    subprocess.run([sys.executable,'backend/database/seed.py'],check=True)

def test_health(): assert client.get('/health').json()['status']=='ok'
def test_student():
    r=client.get('/api/students/101'); assert r.status_code==200; assert r.json()['name']=='Rahul'
def test_assessment():
    r=client.get('/api/assessments/1'); assert r.status_code==200; assert len(r.json()['questions'])>0
def test_attempt():
    r=client.post('/api/assessments/2/attempt',json={'student_id':102,'question_id':1,'answer':'x = 4','time_taken':20})
    assert r.status_code==200; assert r.json()['correct'] is False
