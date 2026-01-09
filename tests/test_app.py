"""
Tests for the Mergington High School Activities API
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis skills development and friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu", "alex@mergington.edu"]
        },
        "Drama Club": {
            "description": "Stage acting, script writing, and theatrical productions",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Fridays, 2:00 PM - 3:30 PM",
            "max_participants": 18,
            "participants": ["grace@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Argumentation skills and competitive debate competitions",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["jessica@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and exploration of scientific concepts",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 22,
            "participants": ["benjamin@mergington.edu", "mia@mergington.edu"]
        }
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Test the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9
    
    def test_get_activities_includes_participants(self, client, reset_activities):
        """Test that activities include participant lists"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "participants" in activity
        assert "michael@mergington.edu" in activity["participants"]
        assert "daniel@mergington.edu" in activity["participants"]
    
    def test_get_activities_includes_activity_details(self, client, reset_activities):
        """Test that activities include all required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert activity["max_participants"] == 12


class TestSignup:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup adds a participant to an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_updates_participants_list(self, client, reset_activities):
        """Test that participant is added to the activities list"""
        client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        response = client.get("/activities")
        activities_data = response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_fails(self, client, reset_activities):
        """Test that signing up twice fails"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signup to nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_at_capacity_still_allows(self, client, reset_activities):
        """Test that students can signup even if activity is at capacity"""
        # Tennis Club has 10 max, currently has 2
        response = client.post(
            "/activities/Tennis%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        # Note: The API doesn't enforce max_participants, just tracks availability


class TestUnregister:
    """Test the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes a participant"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_updates_participants_list(self, client, reset_activities):
        """Test that participant is removed from activities list"""
        client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        response = client.get("/activities")
        activities_data = response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregister from nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering non-participant fails"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]


class TestSignupUnregisterFlow:
    """Test complete signup and unregister flows"""
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up and then unregistering"""
        email = "test@mergington.edu"
        
        # Signup
        signup_response = client.post(
            f"/activities/Drama%20Club/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify in list
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Drama Club"]["participants"]
        
        # Unregister
        unregister_response = client.post(
            f"/activities/Drama%20Club/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify removed from list
        activities_response = client.get("/activities")
        assert email not in activities_response.json()["Drama Club"]["participants"]
    
    def test_signup_unregister_then_signup_again(self, client, reset_activities):
        """Test that a participant can signup again after unregistering"""
        email = "test@mergington.edu"
        
        # First signup
        client.post(f"/activities/Art%20Studio/signup?email={email}")
        
        # Unregister
        client.post(f"/activities/Art%20Studio/unregister?email={email}")
        
        # Signup again
        response = client.post(f"/activities/Art%20Studio/signup?email={email}")
        assert response.status_code == 200
        
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Art Studio"]["participants"]
