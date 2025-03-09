import json
import os
import random

class QuestionBank:
    """Manages the question bank for the medical physics game."""
    
    def __init__(self, data_file="data/game_questions.json"):
        """Initialize the question bank."""
        self.data_file = data_file
        self.questions = self._load_questions()
    
    def _load_questions(self):
        """Load questions from the data file, or create a default set if none exists."""
        if not os.path.exists(self.data_file):
            # Create default questions if file doesn't exist
            default_questions = self._create_default_questions()
            self._save_questions(default_questions)
            return default_questions
        
        try:
            with open(self.data_file, 'r') as file:
                data = json.load(file)
                return data.get("questions", [])
        except (json.JSONDecodeError, IOError):
            # Return default questions if file is corrupted
            return self._create_default_questions()
    
    def _save_questions(self, questions):
        """Save questions to the data file."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        with open(self.data_file, 'w') as file:
            json.dump({"questions": questions}, file, indent=2)
    
    def _create_default_questions(self):
        """Create a default set of questions."""
        return [
            # Dosimetry Questions
            {
                "id": "dosimetry-1",
                "category": "dosimetry",
                "difficulty": 1,
                "question": "What is the correction factor for temperature and pressure called in TG-51?",
                "options": [
                    "PTP",
                    "kTP",
                    "CTP",
                    "PTC"
                ],
                "correct_answer": 1,
                "explanation": "kTP is the temperature-pressure correction factor in TG-51 that adjusts for the difference between calibration and measurement conditions."
            },
            {
                "id": "dosimetry-2",
                "category": "dosimetry",
                "difficulty": 1,
                "question": "Which of the following chambers is typically used for reference dosimetry in external beam radiotherapy?",
                "options": [
                    "Parallel plate chamber",
                    "Farmer-type cylindrical chamber",
                    "Micro-chamber",
                    "Diamond detector"
                ],
                "correct_answer": 1,
                "explanation": "Farmer-type cylindrical chambers are commonly used for reference dosimetry in external beam radiotherapy due to their stability and well-characterized response."
            },
            {
                "id": "dosimetry-3",
                "category": "dosimetry",
                "difficulty": 2,
                "question": "What is the tissue-phantom ratio (TPR) used for?",
                "options": [
                    "To convert percentage depth dose to different source-to-surface distances",
                    "To account for inverse square law effects in treatment planning",
                    "To measure the quality of the beam",
                    "To describe the dose at a point relative to the dose at a reference depth"
                ],
                "correct_answer": 3,
                "explanation": "The tissue-phantom ratio (TPR) describes the dose at a point in a phantom relative to the dose at a reference depth, with the same source-to-detector distance."
            },
            {
                "id": "dosimetry-4",
                "category": "dosimetry",
                "difficulty": 2,
                "question": "Which of the following electron beam parameters is characterized by R50?",
                "options": [
                    "The practical range",
                    "The depth of maximum dose",
                    "The half-value depth",
                    "The depth where the dose falls to 50% of its maximum value"
                ],
                "correct_answer": 3,
                "explanation": "R50 is the depth where the electron dose falls to 50% of its maximum value, and it is used to characterize the electron beam quality."
            },
            {
                "id": "dosimetry-5",
                "category": "dosimetry",
                "difficulty": 3,
                "question": "A 10×10 cm² field is measured to have a PDD(10) of 66.8%. What is the approximate beam quality specifier (TPR20,10) for this beam?",
                "options": [
                    "0.628",
                    "0.668",
                    "0.733",
                    "0.768"
                ],
                "correct_answer": 2,
                "explanation": "The approximate conversion from PDD(10) to TPR20,10 for a 10×10 cm² field is given by TPR20,10 ≈ 1.2661 × PDD(10) - 0.0595, which gives 0.733 for a PDD(10) of 66.8%."
            },
            
            # QA Questions
            {
                "id": "qa-1",
                "category": "qa",
                "difficulty": 1,
                "question": "Which of the following is typically measured in monthly linac QA?",
                "options": [
                    "Electron contamination",
                    "Output constancy",
                    "Leakage radiation",
                    "Housing integrity"
                ],
                "correct_answer": 1,
                "explanation": "Output constancy is a critical parameter checked during monthly QA to ensure the linac is delivering the expected dose."
            },
            {
                "id": "qa-2",
                "category": "qa",
                "difficulty": 1,
                "question": "According to TG-142, what is the tolerance for photon beam flatness constancy during monthly QA?",
                "options": [
                    "±1%",
                    "±2%",
                    "±3%",
                    "±5%"
                ],
                "correct_answer": 1,
                "explanation": "According to TG-142, the tolerance for photon beam flatness constancy during monthly QA is ±2%."
            },
            {
                "id": "qa-3",
                "category": "qa",
                "difficulty": 2,
                "question": "A Winston-Lutz test is primarily used to verify what parameter?",
                "options": [
                    "MLC positioning accuracy",
                    "Dose linearity",
                    "Radiation isocenter accuracy",
                    "CT-simulator laser alignment"
                ],
                "correct_answer": 2,
                "explanation": "The Winston-Lutz test is used to verify the coincidence of the radiation isocenter with the mechanical isocenter of the treatment machine."
            },
            {
                "id": "qa-4",
                "category": "qa",
                "difficulty": 2,
                "question": "Which pattern is typically used for MLC QA to test the positioning accuracy of MLC leaves?",
                "options": [
                    "Diagonal pattern",
                    "Checkerboard pattern",
                    "Picket fence pattern",
                    "Garden fence pattern"
                ],
                "correct_answer": 2,
                "explanation": "The picket fence pattern consists of narrow fields with small gaps between them, resembling a picket fence. It is commonly used to test MLC positioning accuracy."
            },
            {
                "id": "qa-5",
                "category": "qa",
                "difficulty": 3,
                "question": "According to TG-218, what is the recommended gamma criteria for IMRT/VMAT patient-specific QA?",
                "options": [
                    "2%/1mm with 95% passing rate",
                    "3%/2mm with 90% passing rate",
                    "3%/3mm with 95% passing rate",
                    "5%/3mm with 90% passing rate"
                ],
                "correct_answer": 2,
                "explanation": "TG-218 recommends a gamma criteria of 3%/3mm with a 95% passing rate, but also notes that each clinic should establish its own action levels based on their specific equipment and procedures."
            },
            
            # Radiation Safety Questions
            {
                "id": "radiation-1",
                "category": "radiation",
                "difficulty": 1,
                "question": "What is the annual effective dose limit for radiation workers?",
                "options": [
                    "5 mSv",
                    "20 mSv",
                    "50 mSv",
                    "100 mSv"
                ],
                "correct_answer": 1,
                "explanation": "The annual effective dose limit for radiation workers is 20 mSv averaged over 5 years, with no single year exceeding 50 mSv."
            },
            {
                "id": "radiation-2",
                "category": "radiation",
                "difficulty": 1,
                "question": "What is the annual effective dose limit for the public from radiation practices?",
                "options": [
                    "0.1 mSv",
                    "0.5 mSv",
                    "1 mSv",
                    "5 mSv"
                ],
                "correct_answer": 2,
                "explanation": "The annual effective dose limit for the public from radiation practices is 1 mSv."
            },
            {
                "id": "radiation-3",
                "category": "radiation",
                "difficulty": 2,
                "question": "Which of the following is the most effective shielding material for gamma radiation?",
                "options": [
                    "Concrete",
                    "Lead",
                    "Aluminum",
                    "Water"
                ],
                "correct_answer": 1,
                "explanation": "Lead is the most effective shielding material for gamma radiation due to its high density and high atomic number."
            },
            {
                "id": "radiation-4",
                "category": "radiation",
                "difficulty": 2,
                "question": "What is the half-value layer (HVL) used to measure?",
                "options": [
                    "The biological half-life of radiation",
                    "The effective half-life of radionuclides",
                    "The thickness required to reduce the radiation intensity by half",
                    "The distance at which exposure rate is reduced by half"
                ],
                "correct_answer": 2,
                "explanation": "The half-value layer (HVL) is the thickness of a specified material required to reduce the intensity of a beam of radiation to half its original value."
            },
            {
                "id": "radiation-5",
                "category": "radiation",
                "difficulty": 3,
                "question": "What is the primary factor that determines induced activity in a linear accelerator during high-energy photon beam operation?",
                "options": [
                    "Beam energy",
                    "Dose rate",
                    "Field size",
                    "Beam symmetry"
                ],
                "correct_answer": 0,
                "explanation": "Beam energy is the primary factor that determines photonuclear reactions leading to induced activity in a linear accelerator. Energies above 10 MV can produce photoneutrons that cause activation."
            },
            
            # Treatment Planning Questions
            {
                "id": "planning-1",
                "category": "planning",
                "difficulty": 1,
                "question": "Which of the following dose-volume metrics would be most relevant for evaluating the risk of radiation pneumonitis?",
                "options": [
                    "Lung V5",
                    "Lung V20",
                    "Lung V50",
                    "Lung Dmax"
                ],
                "correct_answer": 1,
                "explanation": "Lung V20 (the volume of lung receiving ≥20 Gy) is commonly used to evaluate the risk of radiation pneumonitis."
            },
            {
                "id": "planning-2",
                "category": "planning",
                "difficulty": 1,
                "question": "What is the main advantage of IMRT over 3D conformal radiotherapy?",
                "options": [
                    "Lower monitor units",
                    "Faster treatment delivery",
                    "Better dose conformity to the target",
                    "Simplified quality assurance"
                ],
                "correct_answer": 2,
                "explanation": "The main advantage of IMRT over 3D conformal radiotherapy is better dose conformity to the target volume, especially for complex shapes, allowing better sparing of adjacent normal tissues."
            },
            {
                "id": "planning-3",
                "category": "planning",
                "difficulty": 2,
                "question": "Which of the following is a potential disadvantage of using a non-coplanar beam arrangement?",
                "options": [
                    "Reduced dose conformity",
                    "Increased treatment time",
                    "Reduced skin sparing",
                    "Increased heterogeneity corrections"
                ],
                "correct_answer": 1,
                "explanation": "Non-coplanar beam arrangements generally increase treatment time due to the need for couch rotations between fields, although they may provide dosimetric advantages in certain cases."
            },
            {
                "id": "planning-4",
                "category": "planning",
                "difficulty": 2,
                "question": "In inverse planning for IMRT, what is typically specified as part of the optimization objectives?",
                "options": [
                    "The specific MLC positions",
                    "The number of monitor units per segment",
                    "Dose-volume constraints for targets and organs at risk",
                    "The exact beam angles"
                ],
                "correct_answer": 2,
                "explanation": "In inverse planning for IMRT, dose-volume constraints (or objectives) for targets and organs at risk are specified, and the treatment planning system optimizes the fluence patterns to meet these objectives."
            },
            {
                "id": "planning-5",
                "category": "planning",
                "difficulty": 3,
                "question": "Which of the following optimization objectives would be LEAST appropriate for a prostate IMRT plan?",
                "options": [
                    "Maximize target coverage with 95% of prescription dose",
                    "Minimize rectal volume receiving >70 Gy",
                    "Minimize femoral head maximum dose to <45 Gy",
                    "Maximize dose conformity to femoral heads"
                ],
                "correct_answer": 3,
                "explanation": "Maximizing dose conformity to femoral heads would be inappropriate as the femoral heads are critical structures to avoid, not targets for dose delivery."
            },
            
            # Calculations Questions
            {
                "id": "calculation-1",
                "category": "calculation",
                "difficulty": 1,
                "question": "What is the equivalent dose in Sv for a tissue exposed to 2 Gy of proton radiation with a radiation weighting factor of 2?",
                "options": [
                    "1 Sv",
                    "2 Sv",
                    "4 Sv",
                    "8 Sv"
                ],
                "correct_answer": 2,
                "explanation": "Equivalent dose (Sv) = Absorbed dose (Gy) × Radiation weighting factor. So, 2 Gy × 2 = 4 Sv."
            },
            {
                "id": "calculation-2",
                "category": "calculation",
                "difficulty": 1,
                "question": "If a radioisotope has a half-life of 8 days, approximately what fraction of the original activity will remain after 24 days?",
                "options": [
                    "1/8",
                    "1/4",
                    "1/6",
                    "1/3"
                ],
                "correct_answer": 0,
                "explanation": "After 24 days (3 half-lives), the remaining activity is (1/2)³ = 1/8 of the original activity."
            },
            {
                "id": "calculation-3",
                "category": "calculation",
                "difficulty": 2,
                "question": "A 6 MV photon beam has a PDD of 67.3% at 10 cm depth and 100 cm SSD. What is the approximate TMR at 10 cm depth and 100 cm SAD?",
                "options": [
                    "0.673",
                    "0.750",
                    "0.806",
                    "0.900"
                ],
                "correct_answer": 2,
                "explanation": "The TMR can be calculated from PDD using the relationship TMR = PDD × ((100+d)/100)². For 10 cm depth, TMR ≈ 0.673 × (110/100)² ≈ 0.806"
            },
            {
                "id": "calculation-4",
                "category": "calculation",
                "difficulty": 2,
                "question": "Using the inverse square law, if the dose rate at 100 cm from a source is 2.0 Gy/min, what would be the dose rate at 50 cm?",
                "options": [
                    "4.0 Gy/min",
                    "8.0 Gy/min",
                    "1.0 Gy/min",
                    "0.5 Gy/min"
                ],
                "correct_answer": 1,
                "explanation": "According to the inverse square law, the dose rate varies inversely with the square of the distance. So, 2.0 Gy/min × (100/50)² = 2.0 Gy/min × 4 = 8.0 Gy/min."
            },
            {
                "id": "calculation-5",
                "category": "calculation",
                "difficulty": 3,
                "question": "A patient is prescribed 50 Gy in 25 fractions with an α/β ratio of 3 Gy for late effects. What is the equivalent dose in 2 Gy fractions (EQD2) for late effects?",
                "options": [
                    "46.9 Gy",
                    "50.0 Gy",
                    "53.1 Gy",
                    "56.3 Gy"
                ],
                "correct_answer": 2,
                "explanation": "Using the EQD2 formula: EQD2 = D × (d + (α/β)) / (2 + (α/β)), where D is the total dose, d is the dose per fraction, and α/β is the tissue-specific ratio. EQD2 = 50 × (2 + 3) / (2 + 3) = 50 Gy."
            },
            
            # Imaging Physics Questions
            {
                "id": "imaging-1",
                "category": "imaging",
                "difficulty": 1,
                "question": "Which of the following imaging modalities uses ionizing radiation?",
                "options": [
                    "Ultrasound",
                    "MRI",
                    "Computed Tomography",
                    "Functional MRI"
                ],
                "correct_answer": 2,
                "explanation": "Computed Tomography (CT) uses X-rays, which are a form of ionizing radiation."
            },
            {
                "id": "imaging-2",
                "category": "imaging",
                "difficulty": 1,
                "question": "What is the typical slice thickness used in CT simulation for radiotherapy planning?",
                "options": [
                    "0.5-1 mm",
                    "2-3 mm",
                    "5-10 mm",
                    "15-20 mm"
                ],
                "correct_answer": 1,
                "explanation": "Typical slice thickness for CT simulation in radiotherapy planning is 2-3 mm, balancing spatial resolution with imaging dose and data size."
            },
            {
                "id": "imaging-3",
                "category": "imaging",
                "difficulty": 2,
                "question": "Which of the following parameters is NOT directly adjusted by the automatic exposure control (AEC) in a CT scanner?",
                "options": [
                    "Tube current (mA)",
                    "Tube voltage (kVp)",
                    "Pitch",
                    "Rotation time"
                ],
                "correct_answer": 3,
                "explanation": "Automatic exposure control (AEC) in CT primarily modulates the tube current (mA) based on patient attenuation to maintain image quality. Rotation time is typically set manually."
            },
            {
                "id": "imaging-4",
                "category": "imaging",
                "difficulty": 2,
                "question": "In MRI, what is the primary purpose of the gradient coils?",
                "options": [
                    "To generate the main magnetic field",
                    "To excite the hydrogen nuclei",
                    "To spatially encode the MR signal",
                    "To shield from external RF interference"
                ],
                "correct_answer": 2,
                "explanation": "Gradient coils in MRI create controlled variations in the magnetic field strength, which are used to spatially encode the MR signal."
            },
            {
                "id": "imaging-5",
                "category": "imaging",
                "difficulty": 3,
                "question": "In cone-beam CT reconstruction, what artifact can occur due to insufficient projection data when scanning long objects?",
                "options": [
                    "Ring artifacts",
                    "Beam hardening",
                    "Scatter artifacts",
                    "Truncation artifacts"
                ],
                "correct_answer": 3,
                "explanation": "Truncation artifacts occur in cone-beam CT when the object extends beyond the field of view, resulting in incomplete projection data and reconstruction errors at the edges."
            },
            
            # Regulations Questions
            {
                "id": "regulations-1",
                "category": "regulations",
                "difficulty": 1,
                "question": "Which organization is responsible for accrediting radiation oncology practices in the United States?",
                "options": [
                    "FDA",
                    "ACR",
                    "AAPM",
                    "NRC"
                ],
                "correct_answer": 1,
                "explanation": "The American College of Radiology (ACR) provides accreditation for radiation oncology practices, though other organizations like ASTRO also offer accreditation programs."
            },
            {
                "id": "regulations-2",
                "category": "regulations",
                "difficulty": 1,
                "question": "According to regulatory requirements, how often must a linear accelerator's calibration be verified?",
                "options": [
                    "Daily",
                    "Weekly",
                    "Monthly",
                    "Annually"
                ],
                "correct_answer": 0,
                "explanation": "Daily output constancy checks are required by regulatory agencies to ensure that the linear accelerator's calibration remains within acceptable limits."
            },
            {
                "id": "regulations-3",
                "category": "regulations",
                "difficulty": 2,
                "question": "According to NRC regulations, how soon must a medical event be reported to the NRC Operations Center?",
                "options": [
                    "Immediately",
                    "Within 24 hours",
                    "Within 48 hours",
                    "Within 30 days"
                ],
                "correct_answer": 1,
                "explanation": "According to NRC regulations, a medical event must be reported to the NRC Operations Center within 24 hours of discovery."
            },
            {
                "id": "regulations-4",
                "category": "regulations",
                "difficulty": 2,
                "question": "What is the frequency of full calibration required after a source exchange for an HDR unit?",
                "options": [
                    "Immediately before the first patient treatment",
                    "Within 24 hours before the first patient treatment",
                    "Within 7 days before the first patient treatment",
                    "Within 30 days before the first patient treatment"
                ],
                "correct_answer": 0,
                "explanation": "A full calibration of an HDR unit is required immediately before the first patient treatment following a source exchange."
            },
            {
                "id": "regulations-5",
                "category": "regulations",
                "difficulty": 3,
                "question": "According to TG-100, what is the primary method recommended for identifying potential failure modes in a radiotherapy process?",
                "options": [
                    "Root Cause Analysis (RCA)",
                    "Failure Mode and Effects Analysis (FMEA)",
                    "Process Mapping",
                    "Fault Tree Analysis (FTA)"
                ],
                "correct_answer": 1,
                "explanation": "TG-100 recommends Failure Mode and Effects Analysis (FMEA) as the primary method for proactively identifying potential failure modes in radiotherapy processes."
            }
        ]
    
    def get_questions_by_category(self, category, difficulty=None):
        """Get questions filtered by category and optionally by difficulty."""
        filtered = [q for q in self.questions if q["category"] == category]
        
        if difficulty is not None:
            filtered = [q for q in filtered if q["difficulty"] == difficulty]
        
        return filtered
    
    def get_random_question(self, category=None, difficulty=None):
        """Get a random question, optionally filtered by category and/or difficulty."""
        filtered = self.questions
        
        if category:
            filtered = [q for q in filtered if q["category"] == category]
        
        if difficulty is not None:
            filtered = [q for q in filtered if q["difficulty"] == difficulty]
        
        if not filtered:
            return None
        
        return random.choice(filtered)
    
    def add_question(self, question):
        """Add a new question to the bank."""
        self.questions.append(question)
        self._save_questions(self.questions)
        return True
    
    def update_question(self, question_id, updated_question):
        """Update an existing question."""
        for i, question in enumerate(self.questions):
            if question["id"] == question_id:
                self.questions[i] = updated_question
                self._save_questions(self.questions)
                return True
        return False
    
    def delete_question(self, question_id):
        """Delete a question by ID."""
        self.questions = [q for q in self.questions if q["id"] != question_id]
        self._save_questions(self.questions)
        return True