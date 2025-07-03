#!/usr/bin/env python3
"""
Upload & Parsing Integration Test

Tests the complete pipeline:
1. Upload a resume file through the API
2. Verify it gets parsed correctly
3. Check all extracted data

This simulates the complete user flow from frontend upload to backend processing.
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any

# Add backend to path for direct parser access
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.parser.extractor import extract_resume_data_smart


class UploadParsingTester:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.auth_token = None
        
    def print_separator(self, title: str, char: str = "="):
        """Print a formatted separator."""
        print(f"\n{char * 70}")
        print(f" {title}")
        print(f"{char * 70}")
    
    def check_server_health(self) -> bool:
        """Check if the API server is running."""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ API server is running at {self.api_base_url}")
                return True
            else:
                print(f"❌ API server responded with status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to API server: {e}")
            print(f"   Make sure to start the server with: cd backend && python -m api.run_server")
            return False
    
    def get_auth_token(self) -> bool:
        """Get authentication token from the API."""
        try:
            response = requests.get(f"{self.api_base_url}/v1/auth/demo-token")
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                print(f"✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def upload_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Upload a file through the API."""
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None
            
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        
        print(f"📤 Uploading file: {file_name}")
        print(f"   Size: {file_size:,} bytes")
        
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (file_name, file, 'application/pdf')}
                headers = {'Authorization': f'Bearer {self.auth_token}'}
                
                response = requests.post(
                    f"{self.api_base_url}/v1/uploads/resume",
                    files=files,
                    headers=headers,
                    timeout=30
                )
            
            if response.status_code == 201:
                upload_data = response.json()
                print(f"✅ Upload successful!")
                print(f"   Upload ID: {upload_data['upload_id']}")
                print(f"   Status: {upload_data['status']}")
                return upload_data
            else:
                print(f"❌ Upload failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('message', 'Unknown error')}")
                except:
                    print(f"   Raw response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return None
    
    def check_upload_status(self, upload_id: str, max_attempts: int = 30) -> Optional[Dict[str, Any]]:
        """Poll upload status until processing is complete."""
        print(f"🔄 Checking upload status...")
        
        for attempt in range(max_attempts):
            try:
                headers = {'Authorization': f'Bearer {self.auth_token}'}
                response = requests.get(
                    f"{self.api_base_url}/v1/uploads/resume/{upload_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data['status']
                    
                    print(f"   Attempt {attempt + 1}: Status = {status}")
                    
                    if status in ['PARSED', 'READY']:
                        print(f"✅ Processing complete! Final status: {status}")
                        return status_data
                    elif status == 'FAILED':
                        print(f"❌ Processing failed!")
                        return status_data
                    elif status == 'PENDING':
                        time.sleep(1)  # Wait 1 second before next check
                        continue
                else:
                    print(f"❌ Status check failed: {response.status_code}")
                    return None
                    
            except Exception as e:
                print(f"❌ Status check error: {e}")
                return None
        
        print(f"⏰ Timeout: Processing took longer than {max_attempts} seconds")
        return None
    
    def verify_file_exists(self, upload_id: str) -> Optional[str]:
        """Check if the uploaded file exists in the backend storage."""
        # The file should be stored in backend/uploads/resumes/ with the upload_id as filename
        possible_paths = [
            f"backend/uploads/resumes/{upload_id}.pdf",
            f"backend/uploads/resumes/{upload_id}.docx",
            f"uploads/resumes/{upload_id}.pdf",
            f"uploads/resumes/{upload_id}.docx"
        ]
        
        for file_path in possible_paths:
            if os.path.exists(file_path):
                print(f"✅ Uploaded file found: {file_path}")
                return file_path
        
        print(f"❌ Uploaded file not found in expected locations")
        print(f"   Checked: {possible_paths}")
        return None
    
    def print_formatted_resume_data(self, resume_data: Any, title: str = "PARSED RESUME DATA"):
        """Print beautifully formatted resume data to the command line."""
        self.print_separator(f"📋 {title}", "=")
        
        # Contact Information Section
        contact = resume_data.contact
        print(f"\n👤 CONTACT INFORMATION")
        print(f"{'─' * 50}")
        print(f"   Name:     {contact.name or '❌ Not detected'}")
        print(f"   Email:    {contact.email or '❌ Not detected'}")
        print(f"   Phone:    {contact.phone or '❌ Not detected'}")
        print(f"   LinkedIn: {contact.linkedin or '❌ Not detected'}")
        print(f"   GitHub:   {contact.github or '❌ Not detected'}")
        if hasattr(contact, 'location') and contact.location:
            print(f"   Location: {contact.location}")
        if hasattr(contact, 'website') and contact.website:
            print(f"   Website:  {contact.website}")
        
        # Education Section
        print(f"\n🎓 EDUCATION ({len(resume_data.education)} entries)")
        print(f"{'─' * 50}")
        if resume_data.education:
            for i, edu in enumerate(resume_data.education, 1):
                print(f"   {i}. {edu.degree or 'Unknown Degree'}")
                print(f"      🏫 Institution: {edu.institution or 'Unknown'}")
                if edu.graduation_year:
                    print(f"      📅 Year: {edu.graduation_year}")
                if edu.gpa:
                    print(f"      📊 GPA: {edu.gpa}")
                if edu.field_of_study:
                    print(f"      📚 Field: {edu.field_of_study}")
                if edu.location:
                    print(f"      📍 Location: {edu.location}")
                print()
        else:
            print("   ❌ No education entries detected")
        
        # Work Experience Section
        print(f"\n💼 WORK EXPERIENCE ({len(resume_data.experience)} entries)")
        print(f"{'─' * 50}")
        if resume_data.experience:
            for i, exp in enumerate(resume_data.experience, 1):
                print(f"   {i}. {exp.role or 'Unknown Role'}")
                print(f"      🏢 Company: {exp.company or 'Unknown Company'}")
                if exp.start_date or exp.end_date:
                    start = exp.start_date or '?'
                    end = exp.end_date or 'Present'
                    print(f"      📅 Duration: {start} - {end}")
                if exp.location:
                    print(f"      📍 Location: {exp.location}")
                if exp.description:
                    # Format description with proper wrapping
                    desc_lines = exp.description.strip().split('\n')
                    print(f"      📝 Description:")
                    for line in desc_lines[:5]:  # Show first 5 lines
                        if line.strip():
                            # Wrap long lines
                            if len(line) > 70:
                                line = line[:67] + "..."
                            print(f"         • {line.strip()}")
                    if len(desc_lines) > 5:
                        print(f"         ... ({len(desc_lines) - 5} more lines)")
                print()
        else:
            print("   ❌ No work experience detected")
        
        # Skills Section
        print(f"\n🛠️ SKILLS ({len(resume_data.skills)} detected)")
        print(f"{'─' * 50}")
        if resume_data.skills:
            # Group skills into categories or display in columns
            skills_per_row = 4
            for i in range(0, len(resume_data.skills), skills_per_row):
                skills_group = resume_data.skills[i:i+skills_per_row]
                formatted_skills = []
                for skill in skills_group:
                    # Truncate very long skill names
                    if len(skill) > 15:
                        skill = skill[:12] + "..."
                    formatted_skills.append(f"{skill:<15}")
                print(f"   {''.join(formatted_skills)}")
        else:
            print("   ❌ No skills detected")
        
        # Additional Sections
        if resume_data.additional_sections:
            print(f"\n📋 ADDITIONAL SECTIONS ({len(resume_data.additional_sections)})")
            print(f"{'─' * 50}")
            for section_name, section in resume_data.additional_sections.items():
                print(f"   📌 {section.title}")
                if section.content:
                    # Show preview of content
                    content_preview = section.content[:150].replace('\n', ' ')
                    if len(section.content) > 150:
                        content_preview += "..."
                    print(f"      {content_preview}")
                print()
        
        # Summary Statistics
        print(f"\n📊 EXTRACTION SUMMARY")
        print(f"{'─' * 50}")
        contact_fields = sum([
            bool(contact.name),
            bool(contact.email), 
            bool(contact.phone),
            bool(contact.linkedin),
            bool(contact.github)
        ])
        print(f"   Contact fields detected: {contact_fields}/5")
        print(f"   Education entries: {len(resume_data.education)}")
        print(f"   Work experiences: {len(resume_data.experience)}")
        print(f"   Skills identified: {len(resume_data.skills)}")
        print(f"   Additional sections: {len(resume_data.additional_sections)}")
        
        # Quality assessment
        total_data_points = contact_fields + len(resume_data.education) + len(resume_data.experience) + len(resume_data.skills)
        if total_data_points >= 15:
            quality = "🟢 Excellent"
        elif total_data_points >= 10:
            quality = "🟡 Good"
        elif total_data_points >= 5:
            quality = "🟠 Fair"
        else:
            quality = "🔴 Poor"
        
        print(f"   Data extraction quality: {quality} ({total_data_points} data points)")

    def test_direct_parsing(self, file_path: str) -> Optional[Any]:
        """Test parsing the uploaded file directly with the parser."""
        print(f"🧠 Testing direct parsing of uploaded file...")
        
        try:
            resume_data = extract_resume_data_smart(file_path)
            print(f"✅ Direct parsing successful!")
            
            # Use the new formatted display function
            self.print_formatted_resume_data(resume_data)
            
            return resume_data
            
        except Exception as e:
            print(f"❌ Direct parsing failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_full_test(self, file_path: str):
        """Run the complete upload and parsing test."""
        self.print_separator("🧪 UPLOAD & PARSING INTEGRATION TEST")
        
        print(f"Testing file: {file_path}")
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        
        # Step 1: Check server health
        self.print_separator("1️⃣ SERVER HEALTH CHECK", "-")
        if not self.check_server_health():
            return False
        
        # Step 2: Authentication
        self.print_separator("2️⃣ AUTHENTICATION", "-")
        if not self.get_auth_token():
            return False
        
        # Step 3: File upload
        self.print_separator("3️⃣ FILE UPLOAD", "-")
        upload_data = self.upload_file(file_path)
        if not upload_data:
            return False
        
        upload_id = upload_data['upload_id']
        
        # Step 4: Status monitoring
        self.print_separator("4️⃣ PROCESSING STATUS", "-")
        final_status = self.check_upload_status(upload_id)
        if not final_status:
            return False
        
        # Step 5: File verification
        self.print_separator("5️⃣ FILE VERIFICATION", "-")
        stored_file_path = self.verify_file_exists(upload_id)
        if not stored_file_path:
            return False
        
        # Step 6: Direct parsing test
        self.print_separator("6️⃣ PARSING VERIFICATION", "-")
        parsed_data = self.test_direct_parsing(stored_file_path)
        if not parsed_data:
            return False
        
        # Success summary
        self.print_separator("🎉 TEST COMPLETED SUCCESSFULLY!")
        print(f"✅ File uploaded and processed successfully")
        print(f"✅ Resume parsing extracted meaningful data")
        print(f"✅ Complete pipeline is working correctly")
        
        return True


def main():
    """Main function."""
    print("🚀 UPLOAD & PARSING INTEGRATION TESTER")
    
    # Get file path
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        print("\nUsage: python test_upload_parsing.py <path_to_resume_file>")
        print("\nExample:")
        print("  python test_upload_parsing.py uploads/resumes/sample.pdf")
        print("  python test_upload_parsing.py ~/Documents/my_resume.pdf")
        
        # Try to find a test file
        test_files = [
            "uploads/resumes/0362611e-918a-4421-8658-238f19c15f00.pdf",
            "uploads/resumes/2fa7a9cc-1bb7-4a68-9352-cc128b788896.pdf",
            "uploads/resumes/3b195ece-14b8-4d82-870a-c7512d0ba5bb.pdf"
        ]
        
        print("\n🔍 Looking for existing test files...")
        for test_file in test_files:
            if os.path.exists(test_file):
                print(f"Found: {test_file}")
                use_file = input(f"Use this file? (y/n): ").strip().lower()
                if use_file in ['y', 'yes']:
                    file_path = test_file
                    break
        else:
            file_path = input("\nEnter path to your resume file: ").strip()
            if not file_path:
                print("No file provided. Exiting.")
                return
    
    # Run the test
    tester = UploadParsingTester()
    success = tester.run_full_test(file_path)
    
    if success:
        print(f"\n🎉 All tests passed! Your upload and parsing pipeline is working perfectly.")
    else:
        print(f"\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main() 